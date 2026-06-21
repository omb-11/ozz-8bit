from __future__ import annotations

from dataclasses import dataclass


FLAG_CF = 0x01
FLAG_ZF = 0x02
FLAG_NF = 0x04
FLAG_OF = 0x08
FLAG_IF = 0x10

REGISTER_IDS = {
    "A": 0,
    "B": 1,
    "X": 2,
    "Y": 3,
    "SP": 4,
    "PC": 5,
    "FLAGS": 6,
    "TEMP": 7,
}

REGISTER_NAMES = {value: key for key, value in REGISTER_IDS.items()}

REGISTER_WIDTHS = {
    0: 8,
    1: 8,
    2: 16,
    3: 16,
    4: 16,
    5: 16,
    6: 8,
    7: 8,
}

MMIO_CONSOLE_DATA = 0xE000
MMIO_CONSOLE_STATUS = 0xE001
MMIO_TRACE_PORT = 0xE002
INTERRUPT_VECTOR_BASE = 0xFFF0
STACK_BASE = 0xC000
STACK_TOP = 0xDFFF


@dataclass(frozen=True)
class InstructionSpec:
    mnemonic: str
    opcode: int
    mode: str
    size: int
    cycles: int
    description: str


INSTRUCTION_SET: dict[int, InstructionSpec] = {}
SPECS_BY_MNEMONIC: dict[str, list[InstructionSpec]] = {}


def _add(spec: InstructionSpec) -> None:
    INSTRUCTION_SET[spec.opcode] = spec
    SPECS_BY_MNEMONIC.setdefault(spec.mnemonic, []).append(spec)


for spec in [
    InstructionSpec("NOP", 0x00, "none", 1, 2, "No operation."),
    InstructionSpec("HLT", 0x01, "none", 1, 1, "Stop execution."),
    InstructionSpec("INT", 0x02, "imm8", 2, 6, "Software interrupt."),
    InstructionSpec("IRET", 0x03, "none", 1, 6, "Return from interrupt."),
    InstructionSpec("MOV", 0x10, "rr", 3, 2, "Copy register to register."),
    InstructionSpec("MOV", 0x11, "ri8", 3, 2, "Load 8-bit immediate into register."),
    InstructionSpec("MOV", 0x12, "ri16", 4, 2, "Load 16-bit immediate into register."),
    InstructionSpec("LOAD", 0x13, "ra16", 4, 4, "Load register from absolute memory."),
    InstructionSpec("STORE", 0x14, "a16r", 4, 4, "Store register to absolute memory."),
    InstructionSpec("LOAD", 0x15, "rindex", 4, 4, "Load register from indexed memory."),
    InstructionSpec("STORE", 0x16, "indexr", 4, 4, "Store register to indexed memory."),
    InstructionSpec("PUSH", 0x17, "r", 2, 3, "Push register onto stack."),
    InstructionSpec("POP", 0x18, "r", 2, 3, "Pop register from stack."),
    InstructionSpec("ADD", 0x20, "rr", 3, 3, "Add register to register."),
    InstructionSpec("ADD", 0x21, "ri8", 3, 3, "Add immediate to register."),
    InstructionSpec("SUB", 0x22, "rr", 3, 3, "Subtract register from register."),
    InstructionSpec("SUB", 0x23, "ri8", 3, 3, "Subtract immediate from register."),
    InstructionSpec("MUL", 0x24, "rr", 3, 8, "Multiply register by register."),
    InstructionSpec("MUL", 0x25, "ri8", 3, 8, "Multiply register by immediate."),
    InstructionSpec("DIV", 0x26, "rr", 3, 10, "Divide register by register."),
    InstructionSpec("DIV", 0x27, "ri8", 3, 10, "Divide register by immediate."),
    InstructionSpec("MOD", 0x28, "rr", 3, 10, "Modulo register by register."),
    InstructionSpec("MOD", 0x29, "ri8", 3, 10, "Modulo register by immediate."),
    InstructionSpec("AND", 0x2A, "rr", 3, 3, "Bitwise AND."),
    InstructionSpec("AND", 0x2B, "ri8", 3, 3, "Bitwise AND with immediate."),
    InstructionSpec("OR", 0x2C, "rr", 3, 3, "Bitwise OR."),
    InstructionSpec("OR", 0x2D, "ri8", 3, 3, "Bitwise OR with immediate."),
    InstructionSpec("XOR", 0x2E, "rr", 3, 3, "Bitwise XOR."),
    InstructionSpec("XOR", 0x2F, "ri8", 3, 3, "Bitwise XOR with immediate."),
    InstructionSpec("CMP", 0x30, "rr", 3, 3, "Compare register with register."),
    InstructionSpec("CMP", 0x31, "ri8", 3, 3, "Compare register with immediate."),
    InstructionSpec("INC", 0x32, "r", 2, 2, "Increment register."),
    InstructionSpec("DEC", 0x33, "r", 2, 2, "Decrement register."),
    InstructionSpec("NEG", 0x34, "r", 2, 2, "Two's complement negate."),
    InstructionSpec("ABS", 0x35, "r", 2, 2, "Absolute value."),
    InstructionSpec("NOT", 0x36, "r", 2, 2, "Bitwise invert."),
    InstructionSpec("SHL", 0x37, "r", 2, 2, "Shift left."),
    InstructionSpec("SHR", 0x38, "r", 2, 2, "Shift right."),
    InstructionSpec("ROL", 0x39, "r", 2, 2, "Rotate left."),
    InstructionSpec("ROR", 0x3A, "r", 2, 2, "Rotate right."),
    InstructionSpec("JMP", 0x40, "addr16", 3, 3, "Unconditional jump."),
    InstructionSpec("JE", 0x41, "addr16", 3, 3, "Jump if equal."),
    InstructionSpec("JNE", 0x42, "addr16", 3, 3, "Jump if not equal."),
    InstructionSpec("JG", 0x43, "addr16", 3, 3, "Jump if greater."),
    InstructionSpec("JL", 0x44, "addr16", 3, 3, "Jump if less."),
    InstructionSpec("JGE", 0x45, "addr16", 3, 3, "Jump if greater or equal."),
    InstructionSpec("JLE", 0x46, "addr16", 3, 3, "Jump if less or equal."),
    InstructionSpec("CALL", 0x47, "addr16", 3, 5, "Call subroutine."),
    InstructionSpec("RET", 0x48, "none", 1, 5, "Return from subroutine."),
]:
    _add(spec)


def register_id(name: str) -> int:
    return REGISTER_IDS[name.upper()]


def register_name(reg_id: int) -> str:
    return REGISTER_NAMES[reg_id]


def register_width(reg_id: int) -> int:
    return REGISTER_WIDTHS[reg_id]


def register_mask(reg_id: int) -> int:
    return 0xFF if register_width(reg_id) == 8 else 0xFFFF


def is_wide_register(reg_id: int) -> bool:
    return register_width(reg_id) == 16


def normalize_value(value: int, reg_id: int) -> int:
    return value & register_mask(reg_id)
