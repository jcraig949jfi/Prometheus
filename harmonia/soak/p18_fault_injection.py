"""Fault-inject the zoo-matrix Checkpoint instead of reasoning about it (soak P28).

HARMA-P18 found an inverted robustness gradient: a TRUNCATED line is tolerated
while a well-formed line missing a key raises from the constructor, killing the
whole resume. It rated impact LOW on the argument that record() always writes
both keys and that a mid-line kill produces truncation, which is the tolerated
case. P18 flagged that argument as the weakest claim in the pass -- it was
reached by READING record(), and P11 measured inspection at a 2-of-3 predictor.

This replaces the argument with two injections:

  1. EXHAUSTIVE TRUNCATION. Serialize a real record and cut it at EVERY byte
     offset. For each prefix, ask: is it valid JSON? If so, does it carry both
     required keys? A prefix that is valid JSON AND missing a key is the fatal
     shape, reachable by an ordinary kill.

  2. CONCURRENT WRITERS. Two Checkpoint instances appending to one file, with
     the flush-per-line discipline the class uses, to see whether interleaving
     can produce a valid-but-wrong line.

Read-only w.r.t. the repo; writes only to a temp dir.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "harmonia/experiments")
from run_zoo_matrix import Checkpoint  # noqa: E402

REC = {"examinee": "P:m", "probe_id": "0001", "ok": True, "score": 0.5}
REQUIRED = ("examinee", "probe_id")


def exhaustive_truncation():
    line = json.dumps(REC)
    valid_json, fatal = 0, []
    for cut in range(1, len(line) + 1):
        prefix = line[:cut]
        try:
            obj = json.loads(prefix)
        except Exception:
            continue                      # invalid JSON -> loader skips it (tolerated)
        valid_json += 1
        if not isinstance(obj, dict) or any(k not in obj for k in REQUIRED):
            fatal.append((cut, prefix))
    return len(line), valid_json, fatal


def concurrent_writers(n_each=200):
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "ck.jsonl"
        a, b = Checkpoint(path), Checkpoint(path)
        for i in range(n_each):
            a.record({"examinee": "A", "probe_id": f"{i:04d}", "ok": True})
            b.record({"examinee": "B", "probe_id": f"{i:04d}", "ok": True})
        a.close(); b.close()
        raw = path.read_text(encoding="utf-8").splitlines()
        bad_json, missing_key = 0, 0
        for ln in raw:
            if not ln.strip():
                continue
            try:
                obj = json.loads(ln)
            except Exception:
                bad_json += 1
                continue
            if any(k not in obj for k in REQUIRED):
                missing_key += 1
        # can the loader open what two writers produced?
        try:
            c = Checkpoint(path)
            loaded, err = len(c.records), None
            c.close()
        except Exception as e:
            loaded, err = None, f"{type(e).__name__}: {e}"
        return len(raw), bad_json, missing_key, loaded, err


if __name__ == "__main__":
    n, valid_json, fatal = exhaustive_truncation()
    print(f"1. EXHAUSTIVE TRUNCATION of a {n}-byte record")
    print(f"   prefixes that parse as valid JSON : {valid_json}")
    print(f"   of those, MISSING a required key  : {len(fatal)}  <- the fatal shape")
    for cut, pre in fatal[:3]:
        print(f"      cut={cut}: {pre}")

    total, bad_json, missing_key, loaded, err = concurrent_writers()
    print(f"\n2. CONCURRENT WRITERS (2 instances, 200 records each)")
    print(f"   lines on disk            : {total}")
    print(f"   unparseable lines        : {bad_json}")
    print(f"   valid JSON missing a key : {missing_key}  <- the fatal shape")
    print(f"   loader reopened the file : {'OK, ' + str(loaded) + ' records' if err is None else 'RAISED ' + err}")

    reachable = len(fatal) > 0 or missing_key > 0
    print(f"\nVERDICT: fatal shape reachable by ordinary faults = {reachable}")
    print("  P18 rated impact LOW by inspection; this is the injected test.")
