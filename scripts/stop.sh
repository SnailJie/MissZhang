#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$PROJECT_ROOT/run/gunicorn.pid"

if [ ! -f "$PID_FILE" ]; then
  echo "No PID file found ($PID_FILE). Is the app running?"
  exit 0
fi

PID=$(cat "$PID_FILE")
if kill -0 "$PID" 2>/dev/null; then
  echo "Stopping Gunicorn (PID $PID)..."
  kill "$PID"
  # Wait up to 10s
  for i in {1..10}; do
    if kill -0 "$PID" 2>/dev/null; then
      sleep 1
    else
      break
    fi
  done
  if kill -0 "$PID" 2>/dev/null; then
    echo "Force killing Gunicorn (PID $PID)"
    kill -9 "$PID" || true
  fi
else
  echo "Process $PID not running. Cleaning up PID file."
fi
rm -f "$PID_FILE"
echo "Stopped." 