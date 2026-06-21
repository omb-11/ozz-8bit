import type { MachineSnapshot } from "./types";

export const snapshot: MachineSnapshot = {
  registers: {
    A: 72,
    B: 33,
    X: 0x8000,
    Y: 0x8008,
    SP: 0xdffd,
    PC: 0x0009,
    FLAGS: 0x12
  },
  trace: ["MOV A, #'H'", "STORE [0xE000], A", "MOV A, #'i'", "STORE [0xE000], A", "HLT"],
  bus: ["T0 PC->MAR", "T1 MEM->IR", "T2 decode", "T3 execute", "T4 writeback"],
  memory: Array.from({ length: 32 }, (_, index) => (index * 7) & 0xff)
};
