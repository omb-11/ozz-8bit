# Security Policy

## Reporting

Do not open public issues for security-sensitive findings. Report them privately to the maintainer.

## Scope

The current software scope includes:

- assembler input handling
- emulator memory safety behavior
- build and release automation

## Current Notes

- The emulator intentionally executes untrusted binaries inside a simulated machine model only.
- The assembler does not execute source code; macros are textual expansion only.
