#!/usr/bin/env python3
"""SYNTHETIC ingest benchmark (not a simulator run, not comparable with the public_03 report).

Generates lead/call events in the simulator's shape and feeds them to the Ingestor through a fake client, so the cost
of ingestion, the SQLite size and the resident memory can be measured at 1x and 10x of the public_03 shape.
    .venv/bin/python scripts/bench_ingest.py --workflows 12 --days 2
    .venv/bin/python scripts/bench_ingest.py --workflows 120 --days 1      # ~10x
"""
import argparse
import json
import os
import random
import resource
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from controller.evidence import arm_counts  # noqa: E402
from controller.ingest import Ingestor  # noqa: E402
from controller.store import Store  # noqa: E402

LANG, TIER, AGE, VAL = ["hi", "en", "ta"], ["1", "2", "3"], ["18-30", "31-45", "46-60", "60+"], ["low", "mid", "high"]


class FakeClient:
    def __init__(self):
        self.metas, self.lines = [], {}

    def chunks(self, kind, after=-1):
        return [m for m in self.metas if m["kind"] == kind and m["chunk"] > after]

    def stream_chunk(self, n):
        yield from self.lines.pop(n)


def gen_day(rnd, day, workflows, leads_per_wf, eid):
    """Event ids ascend in line order: all leads of the day first, then all calls (as campaigns precede dialling)."""
    leads, calls, ids = [], [], []
    for w in range(workflows):
        wf = f"wf{w:03d}"
        for i in range(leads_per_wf):
            lid = f"{wf}:l{day}_{i}"
            ids.append((wf, lid))
            eid += 1
            leads.append(json.dumps({"type": "lead", "ts": f"2027-01-{4 + day:02d}T08:00:00+05:30", "workflow_id": wf, "campaign_id": f"{wf}:c{day}",
                                     "lead_id": lid, "person_id": f"{wf}:p{i}", "features": {"lang": rnd.choice(LANG), "city_tier": rnd.choice(TIER),
                                     "age_band": rnd.choice(AGE), "value_band": rnd.choice(VAL)}, "event_id": eid}))
    for wf, lid in ids:
        for a in range(3):
            eid += 1
            conn = rnd.random() < 0.3
            calls.append(json.dumps({"type": "call", "ts": f"2027-01-{4 + day:02d}T{rnd.randint(9, 20):02d}:{rnd.choice((0, 15, 30, 45)):02d}:00+05:30",
                "workflow_id": wf, "campaign_id": f"{wf}:c{day}", "lead_id": lid, "person_id": "p", "attempt_no": a, "config_version": 1,
                "cohort_id": "default", "variant": {"welcome_message": rnd.choice(("W1", "W2", "W3")), "voice": rnd.choice(("V1", "V2", "V3", "V4")),
                "caller_id": rnd.choice(("D1", "D2")), "prompt_version": "P1"}, "connected": conn, "engaged": conn and rnd.random() < 0.55,
                "qa": {"hallucination_flag": False} if conn else None, "event_id": eid}))
    return leads + calls, eid


def rss_mb():
    with open("/proc/self/statm") as f:
        return int(f.read().split()[1]) * os.sysconf("SC_PAGE_SIZE") / 1e6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflows", type=int, default=12)
    ap.add_argument("--leads", type=int, default=16000, help="leads per workflow per day")
    ap.add_argument("--days", type=int, default=2)
    a = ap.parse_args()
    rnd = random.Random(1)
    path = os.path.join(tempfile.mkdtemp(prefix="bench_"), "b.db")
    store = Store(path)
    cl = FakeClient()
    ing = Ingestor(store, cl)
    ing.set_d0("2027-01-04T00:00:00+05:30", 0)
    eid, chunk, total, t_ing, rss0 = 0, 0, 0, 0.0, rss_mb()
    for day in range(a.days):
        lines, eid = gen_day(rnd, day, a.workflows, a.leads, eid)
        for i in range(0, len(lines), 250_000):
            part = lines[i:i + 250_000]
            cl.metas.append({"chunk": chunk, "kind": "events", "last_event_id": json.loads(part[-1])["event_id"]})
            cl.lines[chunk] = part
            chunk += 1
        del lines
        t = time.perf_counter()
        for m in cl.chunks("events", store.get("cur_events", -1)):
            ing.ingest_chunk(m)
        t_ing += time.perf_counter() - t
        ing.prune_leads(day + 1, 4)
        total = ing.totals["events"]
        assert total == eid, f"ingested {total} of {eid} events"
        print(f"day {day}: cumulative {total:,} events, RSS {rss_mb():.0f} MB")
    t = time.perf_counter()
    for w in range(min(a.workflows, 20)):
        arm_counts(store, f"wf{w:03d}", "voice", min_ver=1, cohs=["default"])
        arm_counts(store, f"wf{w:03d}", "voice", min_ver=1, cohs=["default"], sl="age_band", sv="60+")
    q_ms = (time.perf_counter() - t) / min(a.workflows, 20) / 2 * 1000
    st = {k: round(v, 1) for k, v in getattr(ing, "stage", {}).items()}
    print(json.dumps({"label": "SYNTHETIC", "workflows": a.workflows, "events": total, "ingest_seconds": round(t_ing, 1),
                      "events_per_sec": round(total / t_ing), "stage_seconds": st,
                      "rss_start_mb": round(rss0), "rss_peak_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000),
                      "db_mb": round(os.path.getsize(path) / 1e6), "leads_rows": store.one("SELECT COUNT(*) n FROM leads")["n"],
                      "agg_rows": store.one("SELECT COUNT(*) n FROM agg")["n"], "evidence_query_ms": round(q_ms, 2),
                      "bytes_per_million_events_rss": round((rss_mb() - rss0) / max(total / 1e6, 1e-9) * 1e6)}, indent=1))


if __name__ == "__main__":
    main()
