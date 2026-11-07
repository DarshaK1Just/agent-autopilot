#!/usr/bin/env bash
# Dev helper: serve a public scenario, run the controller against it, grade it. Usage: scripts/run_scenario.sh 01_dev [port]
set -euo pipefail
cd "$(dirname "$0")/.."
S="${1:?scenario suffix}"; PORT="${2:-8700}"; DB="runs/ctl_$S.db"
mkdir -p reports runs; rm -f "$DB" "$DB-wal" "$DB-shm"
(scripts/serve.sh "$S" "$PORT" > "runs/serve_$S.log" 2>&1 &)
for i in $(seq 1 120); do curl -sf "localhost:$PORT/health" >/dev/null && break; sleep 1; done
/usr/bin/time -v env CONTROLLER_DB="$DB" ./run.sh "http://127.0.0.1:$PORT" 2> "runs/time_$S.txt" || { echo "controller failed"; tail -20 "runs/time_$S.txt"; exit 1; }
grep -E "Elapsed|Maximum resident" "runs/time_$S.txt"
fuser -k "$PORT"/tcp >/dev/null 2>&1 || true; sleep 1
.venv/bin/python -m sim grade --run "runs/mine_public_$S" --baseline "runs/base_public_$S" --out "reports/public_${S%%_*}.md" > /dev/null
sed -n 1,40p "reports/public_${S%%_*}.md"
