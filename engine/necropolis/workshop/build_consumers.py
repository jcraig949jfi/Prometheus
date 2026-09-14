"""Measure historical_consumers for every registry path with adapters/consumer_trace.py -> CONSUMERS.json."""
import json, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
from engine.necropolis.workshop import registry_source as RS  # noqa: E402
from engine.necropolis.workshop.adapters import consumer_trace as CT  # noqa: E402
out = {}
paths = sorted({r["path"] for r in RS.ROWS if r["path"]})
for i, p in enumerate(paths, 1):
    t0 = time.time()
    try:
        tr = CT.trace(p, REPO)
        imps = [h for h in tr.get("importers", []) if not h.startswith("engine/necropolis/workshop")]
        out[p] = imps[:40]
        print(i, len(paths), p, len(imps), round(time.time() - t0, 1), flush=True)
    except Exception as e:  # noqa: BLE001
        out[p] = ["TRACE_ERROR: " + str(e)[:80]]
        print(i, len(paths), p, "ERROR", e, flush=True)
    (HERE / "CONSUMERS.json").write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
print("done", len(out))
