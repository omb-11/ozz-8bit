from __future__ import annotations

import unittest

from microcode.microcode_generator import generate_microcode_payload
from microcode.microcode_tables import validate_tables


class MicrocodeTests(unittest.TestCase):
    def test_microcode_has_full_coverage(self) -> None:
        self.assertEqual(validate_tables(), [])

    def test_payload_is_not_empty(self) -> None:
        self.assertGreater(len(generate_microcode_payload()), 0)
