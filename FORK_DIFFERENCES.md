# Fork Differences

## Intent

This repository revision is designed to stop looking like a renamed MK1 fork and start behaving like a distinct architecture project.

## Legacy MK1 vs OZZ-8BIT

### Identity

- Legacy: MK1 8-bit computer by Vasco Fazza.
- OZZ-8BIT: original educational architecture by Om Mahendra Bute.

### Register Model

- Legacy: `A`, `B`, `C`, `D`, `SP`, `PC`, output register.
- OZZ-8BIT: `A`, `B`, `X`, `Y`, `SP`, `PC`, `FLAGS`, `TEMP`, `IR`.

### Memory Model

- Legacy: 1 KB split memory arrangement.
- OZZ-8BIT: 64 KB address space with program, data, stack, and MMIO regions.

### ISA

- Legacy: opcode layout driven by MK1 control-line packing.
- OZZ-8BIT: explicit mnemonic families for movement, arithmetic, logic, branching, stack, and interrupts.

### ALU

- Legacy: add, sub, AND, OR, NOT, shifts, rotates.
- OZZ-8BIT: add, sub, mul, div, mod, inc, dec, and, or, xor, not, shl, shr, rol, ror, cmp, neg, abs.

### Microcode

- Legacy: EEPROM byte-lane microcode tied to specific hardware lines.
- OZZ-8BIT: abstract micro-operations exported through Python tooling and documentation.

### Toolchain

- Legacy: customasm definition plus small Python helpers and Arduino upload tools.
- OZZ-8BIT: custom Python assembler, linker, emulator, debugger, and test suite.

### Frontend

- Legacy: no software visualizer.
- OZZ-8BIT: React + TypeScript + Vite visualizer scaffold.

### Hardware Plan

- Legacy: specific KiCad designs for MK1 and companion boards.
- OZZ-8BIT: modular hardware redesign directories and interface contracts, with legacy boards retained as reference.
