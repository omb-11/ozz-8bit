# Instruction Set Reference

## Data Movement

- `MOV dst, src`
- `MOV dst, #imm`
- `LOAD dst, [addr]`
- `LOAD dst, [X+disp]`
- `STORE [addr], src`
- `STORE [Y+disp], src`
- `PUSH reg`
- `POP reg`

## Arithmetic

- `ADD`
- `SUB`
- `MUL`
- `DIV`
- `MOD`
- `INC`
- `DEC`
- `NEG`
- `ABS`

## Logic

- `AND`
- `OR`
- `XOR`
- `NOT`

## Shift and Rotate

- `SHL`
- `SHR`
- `ROL`
- `ROR`

## Compare and Branch

- `CMP`
- `JMP`
- `JE`
- `JNE`
- `JG`
- `JL`
- `JGE`
- `JLE`
- `CALL`
- `RET`

## Interrupts and System

- `INT`
- `IRET`
- `NOP`
- `HLT`
