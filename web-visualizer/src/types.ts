export type RegisterState = {
  A: number;
  B: number;
  X: number;
  Y: number;
  SP: number;
  PC: number;
  FLAGS: number;
};

export type MachineSnapshot = {
  registers: RegisterState;
  trace: string[];
  bus: string[];
  memory: number[];
};
