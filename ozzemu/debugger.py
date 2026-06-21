from __future__ import annotations

from dataclasses import dataclass, field

from ozzemu.cpu import CPU


@dataclass
class Debugger:
    cpu: CPU
    breakpoints: set[int] = field(default_factory=set)
    trace: list[dict[str, int | str]] = field(default_factory=list)

    def add_breakpoint(self, address: int) -> None:
        self.breakpoints.add(address & 0xFFFF)

    def run(self, max_steps: int = 10000) -> list[dict[str, int | str]]:
        for _ in range(max_steps):
            if self.cpu.read_reg(5) in self.breakpoints:
                break
            event = self.cpu.step()
            self.trace.append(event)
            if event.get("status") == "halted" or self.cpu.halted:
                break
        return self.trace
