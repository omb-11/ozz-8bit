#!/usr/bin/env bash
# scripts/run-live-demo.sh
# Simple helper to run the emulator WebSocket server and the frontend dev server.
# Make executable: chmod +x scripts/run-live-demo.sh

set -e
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR"

# Start server in background
echo "Starting emulator websocket server..."
python -m ozzemu.server --host 127.0.0.1 --port 8765 &
SERVER_PID=$!
echo "Server PID: $SERVER_PID"

# Start frontend (will run in foreground)
cd web-visualizer
npm install --no-audit --no-fund
npm run dev

# When dev server exits, kill the backend
echo "Stopping server $SERVER_PID"
kill $SERVER_PID || true
