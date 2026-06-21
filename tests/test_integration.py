from __future__ import annotations

import unittest

from ozzasm.assembler import assemble_file
from ozzemu.emulator import run_binary


class IntegrationTests(unittest.TestCase):
    def test_assemble_and_run_program(self) -> None:
        result = assemble_file("programs/hello_world.ozz")
        cpu, _ = run_binary(result.image.code, start_address=result.image.start_address)
        self.assertEqual("".join(cpu.memory.console_output), "Hi!")
