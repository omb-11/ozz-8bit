from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Token:
    kind: str
    value: str
    line: int
    column: int


def tokenize_line(text: str, line: int) -> list[Token]:
    tokens: list[Token] = []
    current = []
    column = 1
    start = 1
    for char in text:
        if char in " \t,":
            if current:
                tokens.append(Token("word", "".join(current), line, start))
                current = []
            column += 1
            start = column
            continue
        current.append(char)
        column += 1
    if current:
        tokens.append(Token("word", "".join(current), line, start))
    return tokens
