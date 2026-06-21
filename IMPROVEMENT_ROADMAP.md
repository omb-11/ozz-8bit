# Improvement Roadmap

## Phase 1

- Preserve legacy MK1 sources for reference only.
- Document legacy architecture and redesign boundaries.
- Define an original OZZ-8BIT ISA and memory map.

## Phase 2

- Implement shared ISA metadata in Python.
- Build microcode tables around abstract micro-operations.
- Export microcode in machine-readable and documentation-friendly formats.

## Phase 3

- Build OZZASM with:
  - preprocessing
  - parsing
  - symbol resolution
  - listing generation
  - symbol table export

## Phase 4

- Build OZZEMU with:
  - CPU core
  - memory model
  - debugger
  - trace logging
  - interrupt injection

## Phase 5

- Add sample software demonstrating:
  - console output
  - arithmetic
  - stack usage
  - indexed addressing
  - interrupt vectors

## Phase 6

- Raise test coverage with unit and integration tests.
- Add CI for lint-equivalent checks, tests, and frontend build.

## Phase 7

- Produce dedicated OZZ-8BIT schematics and PCB projects.
- Replace documentation-only hardware modules with real KiCad assets.
- Add programmable ROM and backplane integration details.

## Phase 8

- Connect the web visualizer to emulator state snapshots.
- Add live stepping, trace import, and memory inspection workflows.
