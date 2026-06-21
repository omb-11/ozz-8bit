# OZZASM

## Features

- labels
- `%define` constants
- `%macro ... %endmacro`
- `%include "file"`
- `.org`, `.byte`, `.word`, `.text`
- binary output
- listing files
- symbol table export

## Example

```asm
%define CONSOLE 0xE000

.org 0x0000

start:
    MOV A, #'H'
    STORE [CONSOLE], A
    HLT
```

## Commands

```powershell
python -m ozzasm.assembler programs/hello_world.ozz --output build/hello_world.bin --listing build/hello_world.lst --symbols build/hello_world.sym
```
