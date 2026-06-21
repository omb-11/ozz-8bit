import "./styles.css";
import { snapshot } from "./mockMachine";

function formatHex(value: number, width: number) {
  return `0x${value.toString(16).toUpperCase().padStart(width, "0")}`;
}

export default function App() {
  const entries = Object.entries(snapshot.registers);

  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">OZZ-8BIT</p>
        <h1>Machine State Visualizer</h1>
        <p className="lede">
          A frontend shell for register state, memory inspection, bus activity, and instruction trace.
        </p>
      </section>

      <section className="grid">
        <article className="panel">
          <h2>Registers</h2>
          <div className="registers">
            {entries.map(([name, value]) => (
              <div className="register-card" key={name}>
                <span>{name}</span>
                <strong>{formatHex(value, value > 0xff ? 4 : 2)}</strong>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <h2>Trace</h2>
          <ol className="trace-list">
            {snapshot.trace.map((entry) => (
              <li key={entry}>{entry}</li>
            ))}
          </ol>
        </article>

        <article className="panel">
          <h2>Bus Activity</h2>
          <ul className="trace-list">
            {snapshot.bus.map((entry) => (
              <li key={entry}>{entry}</li>
            ))}
          </ul>
        </article>

        <article className="panel">
          <h2>Memory Inspector</h2>
          <div className="memory-grid">
            {snapshot.memory.map((value, index) => (
              <div className="memory-cell" key={index}>
                <span>{index.toString(16).padStart(2, "0")}</span>
                <strong>{value.toString(16).padStart(2, "0")}</strong>
              </div>
            ))}
          </div>
        </article>
      </section>
    </main>
  );
}
