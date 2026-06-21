from __future__ import annotations

from dataclasses import dataclass

from ozzasm.preprocessor import SourceLine


@dataclass
class Statement:
    label: str | None
    kind: str
    name: str
    operands: list[str]
    source: SourceLine


def parse_lines(lines: list[SourceLine]) -> list[Statement]:
    statements: list[Statement] = []
    for line in lines:
        text = line.text.strip()
        label = None
        if ":" in text:
            prefix, suffix = text.split(":", 1)
            if prefix.strip():
                label = prefix.strip()
                text = suffix.strip()
                if not text:
                    statements.append(Statement(label, "label", "", [], line))
                    continue
        if not text:
            statements.append(Statement(label, "label", "", [], line))
            continue
        parts = text.split(maxsplit=1)
        name = parts[0]
        operands = [item.strip() for item in parts[1].split(",")] if len(parts) > 1 else []
        kind = "directive" if name.startswith(".") else "instruction"
        statements.append(Statement(label, kind, name.upper() if kind == "instruction" else name, operands, line))
    return statements
