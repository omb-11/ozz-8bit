# OZZ-8BIT

An open-source educational 8-bit computer architecture designed for learning, experimentation, and modern hardware development.

Author: Om Mahendra Bute  
GitHub: `omyaaa1`

## Overview

OZZ-8BIT is a ground-up architecture redesign built inside this repository after auditing the original MK1 homebrew CPU project. The result is not a rename of the legacy design. It introduces a distinct instruction set, memory map, microcode model, assembler, emulator, documentation set, tests, and project structure.

The legacy MK1 hardware and tooling are still present in this repository as historical reference material:

- `MK1_CPU/`
- `bus_breakout/`
- `eeprom_programmer/`
- `helix_display_interface/`
- `start9_programming_interface/`

Everything new for OZZ-8BIT lives in the new top-level directories:

- `microcode/`
- `ozz8bit/`
- `ozzasm/`
- `ozzemu/`
- `web-visualizer/`
- `hardware/`
- `docs/`
- `programs/`
- `tests/`

## OZZ-8BIT Architecture

### Register File

- `A`: 8-bit accumulator
- `B`: 8-bit general purpose register
- `X`: 16-bit index register
- `Y`: 16-bit index register
- `SP`: 16-bit stack pointer
- `PC`: 16-bit program counter
- `FLAGS`: status register
- `TEMP`: internal temporary register
- `IR`: instruction register

### Flags

- `CF`: carry
- `ZF`: zero
- `NF`: negative
- `OF`: overflow
- `IF`: interrupt enable

### Memory Map

```text
0000-7FFF  Program memory
8000-BFFF  Data memory
C000-DFFF  Stack memory
E000-FFFF  Memory-mapped I/O
```

### Supported Operations

- Data movement: `MOV`, `LOAD`, `STORE`, `PUSH`, `POP`
- Arithmetic: `ADD`, `SUB`, `MUL`, `DIV`, `MOD`, `INC`, `DEC`, `NEG`, `ABS`
- Logic: `AND`, `OR`, `XOR`, `NOT`
- Shift/rotate: `SHL`, `SHR`, `ROL`, `ROR`
- Compare: `CMP`
- Flow control: `JMP`, `JE`, `JNE`, `JG`, `JL`, `JGE`, `JLE`, `CALL`, `RET`
- Interrupts: `INT`, `IRET`
- System: `NOP`, `HLT`

## Toolchain

### Microcode

Abstract microcode tables and export tooling are in `microcode/`.

```powershell
python -m microcode.microcode_generator --format json --output build/microcode.json
python -m microcode.microcode_export --format markdown --output MICROCODE.generated.md
```

### Assembler

The OZZASM toolchain supports:

- labels
- constants
- macros
- include files
- comments
- binary generation
- listing files
- symbol table export

Example:

```powershell
python -m ozzasm.assembler programs/hello_world.ozz --output build/hello_world.bin --listing build/hello_world.lst --symbols build/hello_world.sym
```

### Emulator

The OZZEMU emulator supports:

- machine-code execution
- step mode
- breakpoints
- register and memory inspection
- trace logging
- interrupt injection

Example:

```powershell
python -m ozzemu.emulator programs/hello_world.ozz --assemble --trace
```

## Web Visualizer

`web-visualizer/` contains a React + TypeScript + Vite frontend for visualizing register state, memory, bus activity, and trace history.

```powershell
cd web-visualizer
npm install
npm run dev
```

## Verification

```powershell
python -m unittest discover -s tests -v
```

## Documentation

- [Architecture Guide](docs/Architecture-Guide.md)
- [Instruction Set Reference](docs/Instruction-Set-Reference.md)
- [Assembler Guide](docs/Assembler-Guide.md)
- [Emulator Guide](docs/Emulator-Guide.md)
- [Hardware Guide](docs/Hardware-Guide.md)
- [Developer Guide](docs/Developer-Guide.md)
- [Microcode Notes](MICROCODE.md)
- [Assembler Notes](OZZASM.md)
- [Emulator Notes](OZZEMU.md)

## Repository Forensics

- [Architecture Analysis](ARCHITECTURE_ANALYSIS.md)
- [Improvement Roadmap](IMPROVEMENT_ROADMAP.md)
- [Fork Differences](FORK_DIFFERENCES.md)

## Status

This repository now contains:

- a documented original architecture definition for OZZ-8BIT
- a reference assembler implementation
- a reference emulator implementation
- a microcode generation model
- a modernized repository layout
- initial test coverage for the new software stack

The hardware redesign is currently documented as a modular plan and interface contract. The legacy MK1 KiCad assets remain preserved until dedicated OZZ-8BIT schematics and PCB files are produced.
