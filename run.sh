#!/usr/bin/env bash
# Usage: ./run.sh <SIM_URL>   (runs the controller until the scenario finishes)
# Needs python3 plus requirements.txt (numpy, httpx). State lives in $CONTROLLER_DB (default ./controller_state.db);
# re-running with the same file resumes from the last durable checkpoint.
set -euo pipefail
SIM_URL="${1:?usage: ./run.sh <SIM_URL>}"
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
[ -x .venv/bin/python ] && PY=.venv/bin/python
exec "$PY" -m controller.main --url "$SIM_URL" --db "${CONTROLLER_DB:-controller_state.db}"
