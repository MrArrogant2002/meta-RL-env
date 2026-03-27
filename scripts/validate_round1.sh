#!/usr/bin/env bash
set -euo pipefail

python3 -m compileall app.py src baseline tests
python3 -m pytest

if command -v openenv >/dev/null 2>&1; then
  echo "Running OpenEnv validator..."
  openenv validate || true
else
  echo "OpenEnv CLI not installed yet. Install project deps with:"
  echo "  python3 -m pip install -r requirements.txt"
fi

echo "Local scaffold validation completed."
