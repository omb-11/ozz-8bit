from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re

from ozz8bit.isa import REGISTER_IDS, register_id, register_width
from ozzasm.linker import ObjectImage
from ozzasm.parser import Statement, parse_lines
from ozzasm.preprocessor import Preprocessor


NUMBER_RE = re.compile(r"^([-+]?(?:0x[0-9a-fA-F]+|0b[01]+|\d+))$")
CHAR_RE = re.compile(r"^'(.)'$")


@dataclass
class AssemblyResult:
    image: ObjectImage
    listing: list[str]


def parse_number(token: str, symbols: dict[str, int]) -> int:
    token = token.strip()
    if token in symbols:
        return symbols[token]
    if NUMBER_RE.match(token):
        return int(token, 0)
    char_match = CHAR_RE.match(token)
    if char_match:
        return ord(char_match.group(1))
    raise ValueError(f"Unable to resolve expression: {token}")


def split_memory_operand(operand: str) -> tuple[str, str | None]:
    inner = operand.strip()[1:-1].strip()
    for base in ("X", "Y", "SP"):
        if inner.upper() == base:
            return base, None
        if inner.upper().startswith(base + "+"):
            return base, inner[len(base) + 1 :].strip()
        if inner.upper().startswith(base + "-"):
            return base, "-" + inner[len(base) + 1 :].strip()
    return inner, None


def instruction_size(statement: Statement) -> int:
    mnemonic = statement.name
    ops = statement.operands
    if mnemonic in {"NOP", "HLT", "IRET", "RET"}:
        return 1
    if mnemonic == "INT":
        return 2
    if mnemonic in {"PUSH", "POP", "INC", "DEC", "NEG", "ABS", "NOT", "SHL", "SHR", "ROL", "ROR"}:
        return 2
    if mnemonic in {"JMP", "JE", "JNE", "JG", "JL", "JGE", "JLE", "CALL"}:
        return 3
    if mnemonic == "MOV":
        dst, src = ops
        if src.upper() in REGISTER_IDS:
            return 3
        return 3 if register_width(register_id(dst)) == 8 else 4
    if mnemonic in {"LOAD", "STORE"}:
        left, right = ops
        memory = right if mnemonic == "LOAD" else left
        base, disp = split_memory_operand(memory)
        return 4 if disp is None and base.upper() not in {"X", "Y", "SP"} else 4
    if mnemonic in {"ADD", "SUB", "MUL", "DIV", "MOD", "AND", "OR", "XOR", "CMP"}:
        return 3
    raise ValueError(f"Unsupported instruction for sizing: {mnemonic}")


def encode_register(name: str) -> int:
    return register_id(name)


def encode_signed8(value: int) -> int:
    if not -128 <= value <= 255:
        raise ValueError(f"8-bit immediate out of range: {value}")
    return value & 0xFF


def encode_word(value: int) -> list[int]:
    return [value & 0xFF, (value >> 8) & 0xFF]


def first_pass(statements: list[Statement]) -> tuple[dict[str, int], int]:
    symbols: dict[str, int] = {}
    pc = 0
    start = 0
    for statement in statements:
        if statement.label:
            symbols[statement.label] = pc
        if statement.kind == "label":
            continue
        if statement.kind == "directive":
            if statement.name == ".org":
                pc = parse_number(statement.operands[0], symbols)
                if start == 0:
                    start = pc
            elif statement.name == ".byte":
                pc += len(statement.operands)
            elif statement.name == ".word":
                pc += 2 * len(statement.operands)
            elif statement.name == ".text":
                pc += len(bytes(statement.operands[0].strip('"'), "utf-8"))
            else:
                raise ValueError(f"Unsupported directive {statement.name}")
            continue
        pc += instruction_size(statement)
    return symbols, start


def assemble_statements(statements: list[Statement]) -> AssemblyResult:
    symbols, start_address = first_pass(statements)
    pc = 0
    output = bytearray()
    listing: list[str] = []

    def emit(*values: int) -> None:
        nonlocal pc
        output.extend(values)
        pc += len(values)

    for statement in statements:
        if statement.kind == "directive":
            if statement.name == ".org":
                target = parse_number(statement.operands[0], symbols)
                if not output:
                    pc = target
                    continue
                raise ValueError(".org is only supported before code emission in this reference assembler")
            if statement.name == ".byte":
                values = [parse_number(operand, symbols) & 0xFF for operand in statement.operands]
                emit(*values)
                listing.append(f"{pc - len(values):04X}: " + " ".join(f"{value:02X}" for value in values) + f"    {statement.source.text}")
                continue
            if statement.name == ".word":
                start_pc = pc
                encoded: list[int] = []
                for operand in statement.operands:
                    encoded.extend(encode_word(parse_number(operand, symbols)))
                emit(*encoded)
                listing.append(f"{start_pc:04X}: " + " ".join(f"{value:02X}" for value in encoded) + f"    {statement.source.text}")
                continue
            if statement.name == ".text":
                data = statement.operands[0].strip('"').encode("utf-8")
                start_pc = pc
                emit(*data)
                listing.append(f"{start_pc:04X}: " + " ".join(f"{value:02X}" for value in data) + f"    {statement.source.text}")
                continue

        if statement.kind != "instruction":
            continue

        mnemonic = statement.name
        operands = statement.operands
        start_pc = pc

        if mnemonic == "NOP":
            emit(0x00)
        elif mnemonic == "HLT":
            emit(0x01)
        elif mnemonic == "INT":
            emit(0x02, parse_number(operands[0], symbols) & 0xFF)
        elif mnemonic == "IRET":
            emit(0x03)
        elif mnemonic == "MOV":
            dst, src = operands
            if src.upper() in REGISTER_IDS:
                emit(0x10, encode_register(dst), encode_register(src))
            else:
                dst_id = encode_register(dst)
                value = parse_number(src.lstrip("#"), symbols)
                if register_width(dst_id) == 8:
                    emit(0x11, dst_id, value & 0xFF)
                else:
                    emit(0x12, dst_id, *encode_word(value))
        elif mnemonic == "LOAD":
            dst, src = operands
            base, disp = split_memory_operand(src)
            if disp is None and base.upper() not in {"X", "Y", "SP"}:
                emit(0x13, encode_register(dst), *encode_word(parse_number(base, symbols)))
            else:
                offset = 0 if disp is None else parse_number(disp, symbols)
                emit(0x15, encode_register(dst), encode_register(base), encode_signed8(offset))
        elif mnemonic == "STORE":
            dst, src = operands
            base, disp = split_memory_operand(dst)
            if disp is None and base.upper() not in {"X", "Y", "SP"}:
                emit(0x14, *encode_word(parse_number(base, symbols)), encode_register(src))
            else:
                offset = 0 if disp is None else parse_number(disp, symbols)
                emit(0x16, encode_register(base), encode_signed8(offset), encode_register(src))
        elif mnemonic == "PUSH":
            emit(0x17, encode_register(operands[0]))
        elif mnemonic == "POP":
            emit(0x18, encode_register(operands[0]))
        elif mnemonic in {"ADD", "SUB", "MUL", "DIV", "MOD", "AND", "OR", "XOR", "CMP"}:
            dst, src = operands
            rr_opcode = {
                "ADD": 0x20,
                "SUB": 0x22,
                "MUL": 0x24,
                "DIV": 0x26,
                "MOD": 0x28,
                "AND": 0x2A,
                "OR": 0x2C,
                "XOR": 0x2E,
                "CMP": 0x30,
            }[mnemonic]
            ri_opcode = rr_opcode + 1
            if src.upper() in REGISTER_IDS:
                emit(rr_opcode, encode_register(dst), encode_register(src))
            else:
                emit(ri_opcode, encode_register(dst), parse_number(src.lstrip("#"), symbols) & 0xFF)
        elif mnemonic in {"INC", "DEC", "NEG", "ABS", "NOT", "SHL", "SHR", "ROL", "ROR"}:
            emit(
                {
                    "INC": 0x32,
                    "DEC": 0x33,
                    "NEG": 0x34,
                    "ABS": 0x35,
                    "NOT": 0x36,
                    "SHL": 0x37,
                    "SHR": 0x38,
                    "ROL": 0x39,
                    "ROR": 0x3A,
                }[mnemonic],
                encode_register(operands[0]),
            )
        elif mnemonic in {"JMP", "JE", "JNE", "JG", "JL", "JGE", "JLE", "CALL"}:
            emit(
                {
                    "JMP": 0x40,
                    "JE": 0x41,
                    "JNE": 0x42,
                    "JG": 0x43,
                    "JL": 0x44,
                    "JGE": 0x45,
                    "JLE": 0x46,
                    "CALL": 0x47,
                }[mnemonic],
                *encode_word(parse_number(operands[0], symbols)),
            )
        elif mnemonic == "RET":
            emit(0x48)
        else:
            raise ValueError(f"Unsupported mnemonic: {mnemonic}")

        encoded = output[start_pc - start_address : pc - start_address]
        listing.append(f"{start_pc:04X}: " + " ".join(f"{value:02X}" for value in encoded) + f"    {statement.source.text}")

    image = ObjectImage(start_address=start_address, code=bytes(output), symbols=symbols)
    return AssemblyResult(image=image, listing=listing)


def assemble_file(path: str | Path) -> AssemblyResult:
    preprocessor = Preprocessor()
    lines = preprocessor.preprocess(path)
    statements = parse_lines(lines)
    return assemble_statements(statements)


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble OZZ-8BIT source code.")
    parser.add_argument("input")
    parser.add_argument("--output")
    parser.add_argument("--listing")
    parser.add_argument("--symbols")
    args = parser.parse_args()

    result = assemble_file(args.input)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_bytes(result.image.code)
    if args.listing:
        Path(args.listing).parent.mkdir(parents=True, exist_ok=True)
        Path(args.listing).write_text("\n".join(result.listing) + "\n", encoding="utf-8")
    if args.symbols:
        Path(args.symbols).parent.mkdir(parents=True, exist_ok=True)
        lines = [f"{name} = 0x{address:04X}" for name, address in sorted(result.image.symbols.items())]
        Path(args.symbols).write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not args.output:
        print(result.image.code.hex(" "))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
