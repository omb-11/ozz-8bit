# Emulator Guide

## Run Source Directly

```powershell
python -m ozzemu.emulator programs/hello_world.ozz --assemble --trace
```

## Debugging Model

- step execution through `CPU.step()`
- breakpoint execution through `Debugger`
- console output collected from MMIO `0xE000`
