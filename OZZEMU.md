# OZZEMU

## Features

- machine-code execution
- register viewer through CPU snapshots
- memory viewer through the `Memory` API
- step execution
- breakpoints
- trace mode
- interrupt injection

## Example

```powershell
python -m ozzemu.emulator programs/hello_world.ozz --assemble --trace
```

## Notes

- Console output is memory-mapped at `0xE000`.
- Interrupt vectors start at `0xFFF0`.
- The emulator treats `X`, `Y`, `SP`, and `PC` as 16-bit registers.
