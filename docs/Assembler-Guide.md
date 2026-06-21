# Assembler Guide

## Preprocessor

- `%define NAME value`
- `%include "file.ozz"`
- `%macro NAME arity`
- `%endmacro`

## Directives

- `.org`
- `.byte`
- `.word`
- `.text`

## Usage

```powershell
python -m ozzasm.assembler programs/counter.ozz --output build/counter.bin --listing build/counter.lst --symbols build/counter.sym
```
