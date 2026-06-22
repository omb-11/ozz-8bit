import "./styles.css";
import { snapshot as mockSnapshot } from "./mockMachine";
import WSClient from "./wsClient";
import { useEffect, useState, useRef } from "react";

function formatHex(value: number, width: number) {
  return `0x${value.toString(16).toUpperCase().padStart(width, "0")}`;
}

export default function App() {
  const [connected, setConnected] = useState(false);
  const [running, setRunning] = useState(false);
  const [state, setState] = useState<any>(mockSnapshot);
  const wsRef = useRef<WSClient | null>(null);

  useEffect(() => {
    // create client but don't auto-connect until user presses Connect
    wsRef.current = new WSClient("ws://127.0.0.1:8765");
    const client = wsRef.current;
    client.onOpen(() => setConnected(true));
    client.onError(() => setConnected(false));
    client.onState((payload) => {
      setState(payload);
    });
    client.onAck(() => {
      // could show notifications for ack
    });
    return () => {
      client.close();
      setConnected(false);
    };
  }, []);

  const connect = () => {
    wsRef.current?.connect();
  };
  const disconnect = () => {
    wsRef.current?.close();
    setConnected(false);
    setRunning(false);
  };

  const loadExample = (path: string) => {
    wsRef.current?.send({ type: "load", assemble_path: path });
  };

  const run = (delay = 0.01) => {
    wsRef.current?.send({ type: "run", step_delay: delay });
    setRunning(true);
  };
  const pause = () => {
    wsRef.current?.send({ type: "pause" });
    setRunning(false);
  };
  const step = () => {
    wsRef.current?.send({ type: "step" });
  };
  const reset = () => {
    wsRef.current?.send({ type: "reset" });
    setRunning(false);
  };
  const snapshot = () => {
    wsRef.current?.send({ type: "snapshot", memory_window: 256 });
  };

  const registers = state?.registers ?? {};
  const trace = state?.trace ?? [];
  const bus = state?.bus ?? [];
  const memory = state?.memory ?? [];

  const entries = Object.entries(registers);

  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">OZZ-8BIT</p>
        <h1>Machine State Visualizer</h1>
        <p className="lede">
          Live frontend for register state, memory, bus activity, and instruction trace.
        </p>
        <div className="controls">
          <span className={`status ${connected ? "ok" : "bad"}`}>
            {connected ? "Connected" : "Disconnected"}
          </span>
          {!connected ? (
            <button onClick={connect}>Connect</button>
          ) : (
            <button onClick={disconnect}>Disconnect</button>
          )}
          <select id="examples" defaultValue="programs/hello_world.ozz">
            <option value="programs/hello_world.ozz">hello_world.ozz</option>
            <option value="programs/fib.ozz">fib.ozz</option>
            <option value="programs/interrupt_demo.ozz">interrupt_demo.ozz</option>
          </select>
          <button
            onClick={() => {
              const sel = (document.getElementById("examples") as HTMLSelectElement)
                .value;
              loadExample(sel);
            }}
            disabled={!connected}
          >
            Load
          </button>
          {!running ? (
            <button onClick={() => run(0.02)} disabled={!connected}>
              Run
            </button>
          ) : (
            <button onClick={pause} disabled={!connected}>
              Pause
            </button>
          )}
          <button onClick={step} disabled={!connected}>
            Step
          </button>
          <button onClick={reset} disabled={!connected}>
            Reset
          </button>
          <button onClick={snapshot} disabled={!connected}>
            Snapshot
          </button>
        </div>
      </section>

      <section className="grid">
        <article className="panel">
          <h2>Registers</h2>
          <div className="registers">
            {entries.map(([name, value]) => (
              <div className="register-card" key={name}>
                <span>{name}</span>
                <strong>{formatHex(value as number, (value as number) > 0xff ? 4 : 2)}</strong>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <h2>Trace</h2>
          <ol className="trace-list">
            {trace.slice(-200).map((entry: any, idx: number) => (
              <li key={idx}>
                {entry.pc !== undefined ? `${formatHex(entry.pc, 4)}: ` : ""}{entry.mnemonic ?? JSON.stringify(entry)}
              </li>
            ))}
          </ol>
        </article>

        <article className="panel">
          <h2>Bus Activity</h2>
          <ul className="trace-list">
            {bus.slice(-200).map((entry: any, idx: number) => (
              <li key={idx}>{String(entry)}</li>
            ))}
          </ul>
        </article>

        <article className="panel">
          <h2>Memory Inspector (first 256 bytes)</h2>
          <div className="memory-grid">
            {memory.map((value: number, index: number) => (
              <div className="memory-cell" key={index}>
                <span>{index.toString(16).padStart(2, "0")}</span>
                <strong>{(value ?? 0).toString(16).padStart(2, "0")}</strong>
              </div>
            ))}
          </div>
        </article>
      </section>
    </main>
  );
}
