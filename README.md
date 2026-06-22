# OZZ-8BIT

A compact, educational 8-bit computer architecture with a custom ISA, reference assembler, emulator, microcode tooling, and hardware redesign notes — intended for students, hobbyists, and hardware/software learners.

Author: Om Mahendra Bute

Highlights
- Custom 8-bit ISA with 16-bit address space and microcode-driven control.
- Reference assembler (ozzasm) and emulator (ozzemu).
- Microcode generator and export tooling for experimentation.
- Web visualizer for realtime register/memory/bus views.

Quick links
- Docs: docs/ (Architecture, Instruction set, Assembler, Emulator, Hardware, Developer)
- Microcode notes: MICROCODE.md
- Assembler notes: OZZASM.md
- Emulator notes: OZZEMU.md

Prerequisites
- Python 3.11+
- Node 18+ (for web visualizer)

Install (developer environment)
```bash
# create a virtualenv and install Python package (editable)
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Install web visualizer deps
cd web-visualizer
npm install
cd ..
```

Quickstart — assemble and run the example
```bash
# assemble using the Python package (creates binary)
python -m ozzasm.assembler programs/hello_world.ozz --output build/hello_world.bin

# run in emulator (assemble on the fly, enable trace)
python -m ozzemu.emulator programs/hello_world.ozz --assemble --trace
```

Microcode generation
```bash
# generate microcode JSON and a markdown export
python -m microcode.microcode_generator --format json --output build/microcode.json
python -m microcode.microcode_export --format markdown --output MICROCODE.generated.md
```

Web visualizer
```bash
cd web-visualizer
npm run dev
# open dev server at the printed URL
```

Run tests
```bash
python -m unittest discover -s tests -v
```

Contributing
- See CONTRIBUTING.md for contribution workflow and coding standards.
- For doc-only changes, create a branch named docs/your-topic and open a PR with a short description of the change.

Where to look in the repo
- ozz8bit/: ISA definitions and encoding helpers (ozz8bit/isa.py)
- ozzasm/: assembler implementation and preprocessor
- ozzemu/: emulator CPU core, memory model, debugger
- microcode/: generation and table definitions
- web-visualizer/: React + TypeScript UI for visualizing machine state
- hardware/: hardware design notes and modular breakdown

Status
- Software stack (assembler, emulator, microcode) is functional and covered by initial tests.
- Hardware redesign is documented conceptually; KiCad assets for MK1 are preserved.
