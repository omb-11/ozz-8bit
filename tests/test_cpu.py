from __future__ import annotations

import unittest

from ozzemu.cpu import CPU
from ozzemu.memory import Memory


class CPUTests(unittest.TestCase):
    def test_add_immediate(self) -> None:
        memory = Memory()
        memory.load(0x0000, bytes([0x11, 0x00, 0x05, 0x21, 0x00, 0x03, 0x01]))
        cpu = CPU(memory)
        cpu.step()
        cpu.step()
        self.assertEqual(cpu.read_reg(0), 8)

    def test_store_to_console_mmio(self) -> None:
        memory = Memory()
        memory.load(0x0000, bytes([0x11, 0x00, ord("A"), 0x14, 0x00, 0xE0, 0x00, 0x01]))
        cpu = CPU(memory)
        while not cpu.halted:
            cpu.step()
        self.assertEqual("".join(memory.console_output), "A")
