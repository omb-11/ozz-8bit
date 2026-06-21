from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class SourceLine:
    text: str
    path: str
    line_no: int


@dataclass
class Macro:
    name: str
    arity: int
    body: list[str]


class Preprocessor:
    def __init__(self) -> None:
        self.defines: dict[str, str] = {}
        self.macros: dict[str, Macro] = {}

    def preprocess(self, path: str | Path) -> list[SourceLine]:
        return self._load(Path(path).resolve(), [])

    def _strip_comment(self, line: str) -> str:
        return re.split(r";|//", line, maxsplit=1)[0].rstrip()

    def _apply_defines(self, line: str) -> str:
        for name, value in sorted(self.defines.items(), key=lambda item: len(item[0]), reverse=True):
            line = re.sub(rf"\b{re.escape(name)}\b", value, line)
        return line

    def _expand_macro(self, macro: Macro, args: list[str]) -> list[str]:
        expanded = []
        for line in macro.body:
            new_line = line
            for index, value in enumerate(args):
                new_line = new_line.replace(f"{{{index}}}", value.strip())
            expanded.append(new_line)
        return expanded

    def _load(self, path: Path, stack: list[Path]) -> list[SourceLine]:
        if path in stack:
            raise ValueError(f"Include cycle detected: {' -> '.join(str(item) for item in stack + [path])}")
        stack = [*stack, path]
        output: list[SourceLine] = []
        lines = path.read_text(encoding="utf-8").splitlines()
        index = 0
        while index < len(lines):
            raw = lines[index]
            index += 1
            line = self._strip_comment(raw).strip()
            if not line:
                continue
            if line.startswith("%define "):
                _, name, value = line.split(maxsplit=2)
                self.defines[name] = value
                continue
            if line.startswith("%include "):
                include_name = line.split(maxsplit=1)[1].strip().strip('"')
                output.extend(self._load((path.parent / include_name).resolve(), stack))
                continue
            if line.startswith("%macro "):
                _, name, arity_text = line.split(maxsplit=2)
                body: list[str] = []
                while index < len(lines):
                    body_raw = lines[index]
                    index += 1
                    body_line = self._strip_comment(body_raw).rstrip()
                    if body_line.strip() == "%endmacro":
                        break
                    body.append(body_line)
                self.macros[name.upper()] = Macro(name.upper(), int(arity_text), body)
                continue

            line = self._apply_defines(line)
            parts = line.split(maxsplit=1)
            macro = self.macros.get(parts[0].upper())
            if macro:
                arg_text = parts[1] if len(parts) > 1 else ""
                args = [item.strip() for item in arg_text.split(",")] if arg_text else []
                if len(args) != macro.arity:
                    raise ValueError(f"Macro {macro.name} expected {macro.arity} args, got {len(args)}")
                for expanded in self._expand_macro(macro, args):
                    output.append(SourceLine(self._apply_defines(expanded), str(path), index))
                continue

            output.append(SourceLine(line, str(path), index))
        return output
