#!/usr/bin/env bash
# Runs public_01 twice with different Python hash seeds and compares the controller's audit trail (evidence JSON included).
set -euo pipefail
cd "$(dirname "$0")/.."
for seed in 1 2; do PYTHONHASHSEED=$seed scripts/run_scenario.sh 01_dev >/dev/null 2>&1; cp runs/ctl_01_dev.db "runs/det_$seed.db"; done
.venv/bin/python - <<'PY'
import sqlite3
q = "select minute, wf, kind, actor, summary, detail from audit where kind != 'controller_start' order by id"
a, b = (sqlite3.connect(f"runs/det_{s}.db").execute(q).fetchall() for s in (1, 2))
print(f"audit rows {len(a)} / {len(b)}; identical across hash seeds: {a == b}")
raise SystemExit(0 if a == b else 1)
PY
