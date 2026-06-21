# Hardware Redesign

This directory defines the modular OZZ-8BIT hardware breakdown.

- `cpu/`: control and datapath integration
- `alu/`: arithmetic and flag generation
- `memory/`: ROM, RAM, stack window, address decoding
- `clock/`: manual and oscillator-driven clocking
- `io/`: memory-mapped peripheral interface
- `pcb/`: board-level integration notes

The legacy KiCad files remain in their original MK1 directories. These folders define the new target hardware structure and interfaces before schematic capture.
