from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ozzasm.assembler import assemble_file


class AssemblerTests(unittest.TestCase):
    def test_assemble_hello_world(self) -> None:
        result = assemble_file("programs/hello_world.ozz")
        self.assertGreater(len(result.image.code), 0)
        self.assertEqual(result.image.start_address, 0)

    def test_macro_and_include(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "defs.inc").write_text("%define PORT 0xE000\n", encoding="utf-8")
            (tmp_path / "main.ozz").write_text(
                '%include "defs.inc"\n%macro PUT 1\nMOV A, {0}\nSTORE [PORT], A\n%endmacro\n.org 0x0000\nstart:\nPUT #65\nHLT\n',
                encoding="utf-8",
            )
            result = assemble_file(tmp_path / "main.ozz")
            self.assertIn("start", result.image.symbols)
            self.assertGreater(len(result.image.code), 0)
