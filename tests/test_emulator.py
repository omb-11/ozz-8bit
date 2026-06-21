from __future__ import annotations

import unittest

from ozzemu.emulator import run_binary


class EmulatorTests(unittest.TestCase):
    def test_run_binary_halts(self) -> None:
        cpu, debugger = run_binary(bytes([0x00, 0x01]))
        self.assertTrue(cpu.halted)
        self.assertGreaterEqual(len(debugger.trace), 1)
