#!/usr/bin/env bash
# Dev helper: serve a public scenario on a port. Usage: scripts/serve.sh 01_dev [port]
set -euo pipefail
cd "$(dirname "$0")/.."
S="${1:?scenario suffix e.g. 01_dev}"; PORT="${2:-8700}"
fuser -k "$PORT"/tcp >/dev/null 2>&1 || true
.venv/bin/python -m sim serve --scenario "scenarios/public_$S.yaml" --run-dir "runs/mine_public_$S" --force --port "$PORT"
