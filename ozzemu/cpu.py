from __future__ import annotations

from dataclasses import dataclass, field

from ozz8bit.isa import (
    FLAG_CF,
    FLAG_IF,
    FLAG_NF,
    FLAG_OF,
    FLAG_ZF,
    INTERRUPT_VECTOR_BASE,
    INSTRUCTION_SET,
    REGISTER_NAMES,
    STACK_TOP,
    register_mask,
    register_width,
)
from ozzemu.memory import Memory


@dataclass
class CPU:
    memory: Memory
    registers: dict[int, int] = field(default_factory=dict)
    halted: bool = False
    cycles: int = 0
    pending_interrupts: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        for reg_id in REGISTER_NAMES:
            self.registers.setdefault(reg_id, 0)
        self.registers[4] = STACK_TOP
        self.registers[6] = FLAG_IF

    def snapshot(self) -> dict[str, int]:
        return {name: self.registers[reg_id] for reg_id, name in REGISTER_NAMES.items()}

    def get_flag(self, flag: int) -> bool:
        return bool(self.registers[6] & flag)

    def set_flag(self, flag: int, enabled: bool) -> None:
        if enabled:
            self.registers[6] |= flag
        else:
            self.registers[6] &= ~flag
        self.registers[6] &= 0xFF

    def fetch8(self) -> int:
        value = self.memory.read8(self.registers[5])
        self.registers[5] = (self.registers[5] + 1) & 0xFFFF
        return value

    def fetch16(self) -> int:
        lo = self.fetch8()
        hi = self.fetch8()
        return lo | (hi << 8)

    def read_reg(self, reg_id: int) -> int:
        return self.registers[reg_id] & register_mask(reg_id)

    def write_reg(self, reg_id: int, value: int) -> None:
        self.registers[reg_id] = value & register_mask(reg_id)

    def push8(self, value: int) -> None:
        self.memory.write8(self.registers[4], value)
        self.registers[4] = (self.registers[4] - 1) & 0xFFFF

    def pop8(self) -> int:
        self.registers[4] = (self.registers[4] + 1) & 0xFFFF
        return self.memory.read8(self.registers[4])

    def push16(self, value: int) -> None:
        self.push8((value >> 8) & 0xFF)
        self.push8(value & 0xFF)

    def pop16(self) -> int:
        lo = self.pop8()
        hi = self.pop8()
        return lo | (hi << 8)

    def request_interrupt(self, vector: int) -> None:
        self.pending_interrupts.append(vector & 0xFF)

    def _update_logic_flags(self, result: int, reg_id: int) -> None:
        mask = register_mask(reg_id)
        sign_bit = 1 << (register_width(reg_id) - 1)
        value = result & mask
        self.set_flag(FLAG_ZF, value == 0)
        self.set_flag(FLAG_NF, bool(value & sign_bit))
        self.set_flag(FLAG_OF, False)

    def _update_arithmetic_flags(self, lhs: int, rhs: int, result: int, reg_id: int, subtract: bool = False) -> None:
        mask = register_mask(reg_id)
        sign_bit = 1 << (register_width(reg_id) - 1)
        value = result & mask
        self.set_flag(FLAG_ZF, value == 0)
        self.set_flag(FLAG_NF, bool(value & sign_bit))
        self.set_flag(FLAG_CF, result < 0 if subtract else result > mask)
        lhs_sign = bool(lhs & sign_bit)
        rhs_sign = bool(rhs & sign_bit)
        result_sign = bool(value & sign_bit)
        if subtract:
            overflow = lhs_sign != rhs_sign and result_sign != lhs_sign
        else:
            overflow = lhs_sign == rhs_sign and result_sign != lhs_sign
        self.set_flag(FLAG_OF, overflow)

    def _branch_taken(self, opcode: int) -> bool:
        zf = self.get_flag(FLAG_ZF)
        nf = self.get_flag(FLAG_NF)
        of = self.get_flag(FLAG_OF)
        if opcode == 0x41:
            return zf
        if opcode == 0x42:
            return not zf
        if opcode == 0x43:
            return (not zf) and (nf == of)
        if opcode == 0x44:
            return nf != of
        if opcode == 0x45:
            return nf == of
        if opcode == 0x46:
            return zf or (nf != of)
        return True

    def _execute_binary(self, opcode: int, dst: int, rhs: int, immediate: bool) -> None:
        lhs = self.read_reg(dst)
        reg_id = dst
        op = opcode if immediate else opcode
        if op in {0x20, 0x21}:
            result = lhs + rhs
            self.write_reg(dst, result)
            self._update_arithmetic_flags(lhs, rhs, result, reg_id)
        elif op in {0x22, 0x23}:
            result = lhs - rhs
            self.write_reg(dst, result)
            self._update_arithmetic_flags(lhs, rhs, result, reg_id, subtract=True)
        elif op in {0x24, 0x25}:
            result = lhs * rhs
            self.write_reg(dst, result)
            self._update_logic_flags(result, reg_id)
        elif op in {0x26, 0x27}:
            if rhs == 0:
                raise ZeroDivisionError("DIV by zero")
            result = lhs // rhs
            self.write_reg(dst, result)
            self._update_logic_flags(result, reg_id)
        elif op in {0x28, 0x29}:
            if rhs == 0:
                raise ZeroDivisionError("MOD by zero")
            result = lhs % rhs
            self.write_reg(dst, result)
            self._update_logic_flags(result, reg_id)
        elif op in {0x2A, 0x2B}:
            result = lhs & rhs
            self.write_reg(dst, result)
            self._update_logic_flags(result, reg_id)
        elif op in {0x2C, 0x2D}:
            result = lhs | rhs
            self.write_reg(dst, result)
            self._update_logic_flags(result, reg_id)
        elif op in {0x2E, 0x2F}:
            result = lhs ^ rhs
            self.write_reg(dst, result)
            self._update_logic_flags(result, reg_id)
        elif op in {0x30, 0x31}:
            result = lhs - rhs
            self._update_arithmetic_flags(lhs, rhs, result, reg_id, subtract=True)
        else:
            raise ValueError(f"Unsupported binary opcode 0x{opcode:02X}")

    def _service_interrupt(self) -> bool:
        if not self.pending_interrupts or not self.get_flag(FLAG_IF):
            return False
        vector = self.pending_interrupts.pop(0)
        self.push16(self.read_reg(5))
        self.push8(self.read_reg(6))
        self.set_flag(FLAG_IF, False)
        self.write_reg(5, self.memory.read16(INTERRUPT_VECTOR_BASE + vector * 2))
        self.cycles += 6
        return True

    def step(self) -> dict[str, int | str]:
        if self.halted:
            return {"status": "halted"}
        self._service_interrupt()
        pc_before = self.read_reg(5)
        opcode = self.fetch8()
        spec = INSTRUCTION_SET.get(opcode)
        if spec is None:
            raise ValueError(f"Unknown opcode 0x{opcode:02X} at 0x{pc_before:04X}")

        if opcode == 0x00:
            pass
        elif opcode == 0x01:
            self.halted = True
        elif opcode == 0x02:
            vector = self.fetch8()
            self.push16(self.read_reg(5))
            self.push8(self.read_reg(6))
            self.set_flag(FLAG_IF, False)
            self.write_reg(5, self.memory.read16(INTERRUPT_VECTOR_BASE + vector * 2))
        elif opcode == 0x03:
            self.write_reg(6, self.pop8())
            self.write_reg(5, self.pop16())
        elif opcode == 0x10:
            dst, src = self.fetch8(), self.fetch8()
            self.write_reg(dst, self.read_reg(src))
        elif opcode == 0x11:
            dst, imm = self.fetch8(), self.fetch8()
            self.write_reg(dst, imm)
        elif opcode == 0x12:
            dst, imm = self.fetch8(), self.fetch16()
            self.write_reg(dst, imm)
        elif opcode == 0x13:
            dst, address = self.fetch8(), self.fetch16()
            if register_width(dst) == 8:
                self.write_reg(dst, self.memory.read8(address))
            else:
                self.write_reg(dst, self.memory.read16(address))
        elif opcode == 0x14:
            address, src = self.fetch16(), self.fetch8()
            if register_width(src) == 8:
                self.memory.write8(address, self.read_reg(src))
            else:
                self.memory.write16(address, self.read_reg(src))
        elif opcode == 0x15:
            dst, base, disp = self.fetch8(), self.fetch8(), self.fetch8()
            if disp >= 0x80:
                disp -= 0x100
            address = (self.read_reg(base) + disp) & 0xFFFF
            if register_width(dst) == 8:
                self.write_reg(dst, self.memory.read8(address))
            else:
                self.write_reg(dst, self.memory.read16(address))
        elif opcode == 0x16:
            base, disp, src = self.fetch8(), self.fetch8(), self.fetch8()
            if disp >= 0x80:
                disp -= 0x100
            address = (self.read_reg(base) + disp) & 0xFFFF
            if register_width(src) == 8:
                self.memory.write8(address, self.read_reg(src))
            else:
                self.memory.write16(address, self.read_reg(src))
        elif opcode == 0x17:
            src = self.fetch8()
            if register_width(src) == 8:
                self.push8(self.read_reg(src))
            else:
                self.push16(self.read_reg(src))
        elif opcode == 0x18:
            dst = self.fetch8()
            if register_width(dst) == 8:
                self.write_reg(dst, self.pop8())
            else:
                self.write_reg(dst, self.pop16())
        elif 0x20 <= opcode <= 0x31:
            dst = self.fetch8()
            if opcode % 2 == 0:
                rhs = self.read_reg(self.fetch8())
                self._execute_binary(opcode, dst, rhs, immediate=False)
            else:
                rhs = self.fetch8()
                self._execute_binary(opcode, dst, rhs, immediate=True)
        elif 0x32 <= opcode <= 0x3A:
            reg_id = self.fetch8()
            value = self.read_reg(reg_id)
            width = register_width(reg_id)
            mask = register_mask(reg_id)
            sign_bit = 1 << (width - 1)
            if opcode == 0x32:
                result = value + 1
            elif opcode == 0x33:
                result = value - 1
            elif opcode == 0x34:
                result = (-value) & mask
            elif opcode == 0x35:
                signed = value if value < sign_bit else value - (1 << width)
                result = abs(signed)
            elif opcode == 0x36:
                result = (~value) & mask
            elif opcode == 0x37:
                self.set_flag(FLAG_CF, bool(value & sign_bit))
                result = (value << 1) & mask
            elif opcode == 0x38:
                self.set_flag(FLAG_CF, bool(value & 0x1))
                result = value >> 1
            elif opcode == 0x39:
                carry_in = 1 if self.get_flag(FLAG_CF) else 0
                carry_out = bool(value & sign_bit)
                result = ((value << 1) & mask) | carry_in
                self.set_flag(FLAG_CF, carry_out)
            else:
                carry_in = sign_bit if self.get_flag(FLAG_CF) else 0
                carry_out = bool(value & 0x1)
                result = (value >> 1) | carry_in
                self.set_flag(FLAG_CF, carry_out)
            self.write_reg(reg_id, result)
            self._update_logic_flags(result, reg_id)
        elif 0x40 <= opcode <= 0x47:
            address = self.fetch16()
            if opcode == 0x47:
                self.push16(self.read_reg(5))
                self.write_reg(5, address)
            elif self._branch_taken(opcode):
                self.write_reg(5, address)
        elif opcode == 0x48:
            self.write_reg(5, self.pop16())
        else:
            raise ValueError(f"Unsupported opcode 0x{opcode:02X}")

        self.cycles += spec.cycles
        return {"status": "ok", "pc": pc_before, "opcode": opcode, "mnemonic": spec.mnemonic}
