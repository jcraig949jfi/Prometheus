"""Differential fault-injection: pre-fix vs post-fix Checkpoint (soak P28).

HARMA-P18 reported an inverted robustness gradient and rated its impact LOW by
INSPECTION. Aporia P44 fixed it 26 minutes later. This pass nearly measured the
wrong artifact -- the staleness guard reported "unchanged" because a UTC pass
timestamp was handed to `git --since`, which reads LOCAL time.

So the impact question is answered against the PRE-FIX loader (830a83a3), and
the fix is verified by EXECUTION rather than by reading it (the P26 discipline:
a guard that is only read is exactly the failure P12 reported).
"""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "harmonia/experiments")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod.Checkpoint


OLD = load("harmonia/soak/_prefix/run_zoo_matrix_prefix.py", "zoo_prefix")
NEW = load("harmonia/experiments/run_zoo_matrix.py", "zoo_current")

GOOD = json.dumps({"examinee": "P:m", "probe_id": "0001", "ok": True})
CASES = {
    "truncated (invalid JSON)":      GOOD[:40],
    "valid JSON, missing probe_id":  json.dumps({"examinee": "P:m", "ok": True}),
    "valid JSON, missing examinee":  json.dumps({"probe_id": "0001", "ok": True}),
    "valid JSON, not a dict":        json.dumps(["examinee", "probe_id"]),
    "valid JSON, null":              json.dumps(None),
}


def probe(cls, bad_line):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "ck.jsonl"
        p.write_text(GOOD + "\n" + bad_line + "\n" + GOOD.replace("0001", "0002") + "\n",
                     encoding="utf-8")
        try:
            c = cls(p)
            n, skipped = len(c.records), getattr(c, "n_skipped_malformed", 0)
            c.close()
            return f"loaded {n}/2 good, skipped {skipped}"
        except Exception as e:
            return f"RAISED {type(e).__name__}: {e}"


print(f"{'line shape':32s} {'PRE-FIX (830a83a3)':34s} POST-FIX (P44)")
print("-" * 92)
old_fatal = new_fatal = 0
for label, line in CASES.items():
    o, n = probe(OLD, line), probe(NEW, line)
    old_fatal += o.startswith("RAISED")
    new_fatal += n.startswith("RAISED")
    print(f"{label:32s} {o:34s} {n}")

print("-" * 92)
print(f"fatal shapes: PRE-FIX {old_fatal}/{len(CASES)}   POST-FIX {new_fatal}/{len(CASES)}")
print()
print("P18 impact question, answered on the artifact P18 actually examined:")
print(f"  the fatal shapes are REAL and numerous ({old_fatal} of {len(CASES)}) once a line reaches disk,")
print("  but P28's exhaustive-truncation result shows a kill cannot MANUFACTURE one,")
print("  so P18's LOW rating turns on reachability, not on severity.")
