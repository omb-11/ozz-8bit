from __future__ import annotations

import argparse
from pathlib import Path

from ozzasm.assembler import assemble_file
from ozzemu.cpu import CPU
from ozzemu.debugger import Debugger
from ozzemu.memory import Memory


def run_binary(payload: bytes, start_address: int = 0x0000, trace: bool = False, max_steps: int = 10000) -> tuple[CPU, Debugger]:
    memory = Memory()
    memory.load(start_address, payload)
    cpu = CPU(memory)
    cpu.write_reg(5, start_address)
    debugger = Debugger(cpu)
    debugger.run(max_steps=max_steps)
    if trace:
        for event in debugger.trace:
            print(event)
    return cpu, debugger


def main() -> int:
    parser = argparse.ArgumentParser(description="Run OZZ-8BIT binaries or source files.")
    parser.add_argument("input")
    parser.add_argument("--assemble", action="store_true")
    parser.add_argument("--trace", action="store_true")
    parser.add_argument("--max-steps", type=int, default=10000)
    args = parser.parse_args()

    path = Path(args.input)
    if args.assemble or path.suffix.lower() in {".ozz", ".oz"}:
        assembled = assemble_file(path)
        payload = assembled.image.code
        start_address = assembled.image.start_address
    else:
        payload = path.read_bytes()
        start_address = 0x0000

    cpu, _ = run_binary(payload, start_address=start_address, trace=args.trace, max_steps=args.max_steps)
    if cpu.memory.console_output:
        print("".join(cpu.memory.console_output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
