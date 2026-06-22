"""ozzemu WebSocket control server for the emulator.

Usage:
  python -m ozzemu.server --port 8765

Protocol (JSON over ws):
- Client -> Server messages (all JSON):
  {"type":"load", "assemble_path":"programs/hello_world.ozz"}
  {"type":"load_binary","base64":"...","start_address":0}
  {"type":"run","step_delay":0.01}
  {"type":"pause"}
  {"type":"step"}
  {"type":"reset"}
  {"type":"snapshot","memory_window":256}

- Server -> Client messages:
  {"type":"ack","id":..., "payload": {...}}
  {"type":"state","payload": { registers, pc, cycles, memory, trace, bus }}
  {"type":"error","message":"..."}

This is intentionally small and synchronous-friendly to keep integration simple.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
from pathlib import Path
from typing import Any, Dict, List, Set

import websockets
from websockets.server import WebSocketServerProtocol

from ozzasm.assembler import assemble_file
from ozzemu.cpu import CPU
from ozzemu.debugger import Debugger
from ozzemu.memory import Memory


DEFAULT_PORT = 8765
DEFAULT_MEMORY_WINDOW = 256


class EmulatorServer:
    def __init__(self) -> None:
        self.cpu: CPU | None = None
        self.debugger: Debugger | None = None
        self.clients: Set[WebSocketServerProtocol] = set()
        self._run_task: asyncio.Task | None = None
        self._run_lock = asyncio.Lock()

    async def handler(self, ws: WebSocketServerProtocol) -> None:
        self.clients.add(ws)
        try:
            await self._send_ack(ws, {"message": "connected"})
            async for raw in ws:
                try:
                    msg = json.loads(raw)
                except Exception as exc:
                    await self._send_error(ws, f"invalid json: {exc}")
                    continue
                await self._handle_message(ws, msg)
        finally:
            self.clients.discard(ws)

    async def _handle_message(self, ws: WebSocketServerProtocol, msg: Dict[str, Any]) -> None:
        typ = msg.get("type")
        try:
            if typ == "load":
                path = msg.get("assemble_path")
                if not path:
                    await self._send_error(ws, "load requires assemble_path")
                    return
                await self._load_from_path(ws, Path(path))
                await self.broadcast_state()
            elif typ == "load_binary":
                b64 = msg.get("base64")
                if not b64:
                    await self._send_error(ws, "load_binary requires base64 payload")
                    return
                start = msg.get("start_address", 0)
                payload = base64.b64decode(b64)
                await self._load_binary(ws, payload, start)
                await self.broadcast_state()
            elif typ == "run":
                delay = float(msg.get("step_delay", 0.01))
                await self._start_running(delay)
                await self._send_ack(ws, {"message": "running"})
            elif typ == "pause":
                await self._stop_running()
                await self._send_ack(ws, {"message": "paused"})
            elif typ == "step":
                await self._do_step()
                await self.broadcast_state()
            elif typ == "reset":
                await self._reset()
                await self.broadcast_state()
            elif typ == "snapshot":
                await self.broadcast_state(memory_window=int(msg.get("memory_window", DEFAULT_MEMORY_WINDOW)))
            else:
                await self._send_error(ws, f"unknown command type: {typ}")
        except Exception as exc:
            await self._send_error(ws, f"handler error: {exc}")

    async def _load_from_path(self, ws: WebSocketServerProtocol, path: Path) -> None:
        assembled = assemble_file(path)
        payload = assembled.image.code
        start_address = assembled.image.start_address
        await self._load_binary(ws, payload, start_address)

    async def _load_binary(self, ws: WebSocketServerProtocol, payload: bytes, start_address: int = 0x0000) -> None:
        memory = Memory()
        memory.load(start_address, payload)
        cpu = CPU(memory)
        cpu.write_reg(5, start_address)
        debugger = Debugger(cpu)
        self.cpu = cpu
        self.debugger = debugger
        await self._send_ack(ws, {"message": "loaded", "start_address": start_address, "size": len(payload)})

    async def _start_running(self, step_delay: float) -> None:
        async with self._run_lock:
            if self._run_task and not self._run_task.done():
                return
            self._run_task = asyncio.create_task(self._run_loop(step_delay))

    async def _stop_running(self) -> None:
        async with self._run_lock:
            if self._run_task:
                self._run_task.cancel()
                try:
                    await self._run_task
                except asyncio.CancelledError:
                    pass
                self._run_task = None

    async def _run_loop(self, step_delay: float) -> None:
        try:
            while True:
                await self._do_step()
                await self.broadcast_state()
                await asyncio.sleep(step_delay)
        except asyncio.CancelledError:
            return

    async def _do_step(self) -> None:
        if not self.cpu or not self.debugger:
            return
        event = self.cpu.step()
        # append to debugger trace
        self.debugger.trace.append(event)

    async def _reset(self) -> None:
        if not self.cpu:
            return
        mem = self.cpu.memory
        self.cpu = CPU(Memory())
        self.debugger = Debugger(self.cpu)

    async def broadcast_state(self, memory_window: int = DEFAULT_MEMORY_WINDOW) -> None:
        if not self.cpu or not self.debugger:
            return
        payload = self._build_state_payload(memory_window)
        data = json.dumps({"type": "state", "payload": payload})
        await self._broadcast(data)

    def _build_state_payload(self, memory_window: int) -> Dict[str, Any]:
        cpu = self.cpu
        assert cpu is not None
        snapshot = cpu.snapshot()
        pc = cpu.read_reg(5)
        cycles = cpu.cycles
        # memory slice from 0..memory_window
        mem = cpu.memory.read_slice(0, memory_window)
        trace = list(self.debugger.trace[-200:]) if self.debugger else []
        return {
            "registers": snapshot,
            "pc": pc,
            "cycles": cycles,
            "memory": mem,
            "trace": trace,
            "bus": [],
        }

    async def _broadcast(self, data: str) -> None:
        websockets_to_remove: List[WebSocketServerProtocol] = []
        for ws in list(self.clients):
            try:
                await ws.send(data)
            except Exception:
                websockets_to_remove.append(ws)
        for ws in websockets_to_remove:
            self.clients.discard(ws)

    async def _send_ack(self, ws: WebSocketServerProtocol, payload: Any) -> None:
        await ws.send(json.dumps({"type": "ack", "payload": payload}))

    async def _send_error(self, ws: WebSocketServerProtocol, message: str) -> None:
        await ws.send(json.dumps({"type": "error", "message": message}))


async def serve(host: str, port: int) -> None:
    server = EmulatorServer()
    print(f"Starting OZZ-8BIT emulator server on ws://{host}:{port}")
    async with websockets.serve(server.handler, host, port):
        await asyncio.Future()  # run forever


def main() -> int:
    parser = argparse.ArgumentParser(description="OZZ-8BIT emulator WebSocket server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    try:
        asyncio.run(serve(args.host, args.port))
    except KeyboardInterrupt:
        print("Server stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
