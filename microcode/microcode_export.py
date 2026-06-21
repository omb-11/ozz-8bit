from __future__ import annotations

import argparse
from pathlib import Path

from microcode.microcode_generator import generate_microcode_payload


def export_markdown() -> str:
    lines = [
        "# Generated Microcode",
        "",
        "| Opcode | Mnemonic | Mode | Microsteps |",
        "| --- | --- | --- | --- |",
    ]
    for entry in generate_microcode_payload():
        steps = "<br>".join(entry["microsteps"])
        lines.append(
            f"| `0x{entry['opcode']:02X}` | `{entry['mnemonic']}` | `{entry['mode']}` | {steps} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Export OZZ-8BIT microcode documentation.")
    parser.add_argument("--format", choices=["markdown"], default="markdown")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    output = export_markdown()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
