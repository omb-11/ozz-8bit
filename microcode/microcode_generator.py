from __future__ import annotations

import argparse
import json
from pathlib import Path

from microcode.microcode_tables import MICROCODE_TABLES, validate_tables
from ozz8bit.isa import INSTRUCTION_SET


def generate_microcode_payload() -> list[dict[str, object]]:
    payload = []
    for opcode, spec in sorted(INSTRUCTION_SET.items()):
        payload.append(
            {
                "opcode": opcode,
                "mnemonic": spec.mnemonic,
                "mode": spec.mode,
                "cycles": spec.cycles,
                "microsteps": MICROCODE_TABLES[opcode],
            }
        )
    return payload


def write_output(path: Path, fmt: str) -> None:
    payload = generate_microcode_payload()
    path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return
    lines = []
    for entry in payload:
        lines.append(f"0x{entry['opcode']:02X} {entry['mnemonic']} ({entry['mode']})")
        for index, step in enumerate(entry["microsteps"]):
            lines.append(f"  T{index}: {step}")
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate OZZ-8BIT abstract microcode tables.")
    parser.add_argument("--format", choices=["json", "text"], default="text")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    errors = validate_tables()
    if errors:
        for error in errors:
            print(error)
        return 1

    write_output(Path(args.output), args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
