# Web Visualizer — OZZ-8BIT

This frontend connects to the emulator WebSocket server (ozzemu.server) and visualizes registers, memory, bus activity, and instruction trace in real time.

Quick start

1. Start the emulator server (from repo root):

```bash
pip install websockets
python -m ozzemu.server --host 127.0.0.1 --port 8765
```

2. Start the frontend (in another terminal):

```bash
cd web-visualizer
npm install
npm run dev
```

3. Open the Vite URL (usually http://localhost:5173), click Connect, Load an example, then Run or Step.

Notes
- If no server is available, the UI falls back to a mock snapshot.
- Use the Snapshot button to request an explicit state update from the server.
