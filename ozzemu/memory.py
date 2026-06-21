from __future__ import annotations

from dataclasses import dataclass, field

from ozz8bit.isa import MMIO_CONSOLE_DATA, MMIO_CONSOLE_STATUS, MMIO_TRACE_PORT


@dataclass
class Memory:
    size: int = 0x10000
    data: bytearray = field(default_factory=lambda: bytearray(0x10000))
    console_output: list[str] = field(default_factory=list)
    trace_output: list[int] = field(default_factory=list)

    def read8(self, address: int) -> int:
        address &= 0xFFFF
        if address == MMIO_CONSOLE_STATUS:
            return 1
        return self.data[address]

    def write8(self, address: int, value: int) -> None:
        address &= 0xFFFF
        value &= 0xFF
        if address == MMIO_CONSOLE_DATA:
            self.console_output.append(chr(value))
            return
        if address == MMIO_TRACE_PORT:
            self.trace_output.append(value)
            return
        self.data[address] = value

    def read16(self, address: int) -> int:
        lo = self.read8(address)
        hi = self.read8(address + 1)
        return lo | (hi << 8)

    def write16(self, address: int, value: int) -> None:
        self.write8(address, value & 0xFF)
        self.write8(address + 1, (value >> 8) & 0xFF)

    def load(self, start_address: int, payload: bytes) -> None:
        for offset, value in enumerate(payload):
            self.write8(start_address + offset, value)
