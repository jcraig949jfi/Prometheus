"""Middle-case boundary probe for the zoo-matrix Checkpoint (Harmonia-A soak P18).

The suite covers two EXTREMES: a clean checkpoint, and a truncated final line
from a kill. SOAK-30 says a boundary case is only as good as its distance from
the degenerate corner, so this probes the middle -- lines that are perfectly
well-formed JSON but semantically wrong.

That gap matters because the loader's guard is asymmetric:

    try:  rec = json.loads(line)
    except json.JSONDecodeError: continue        # truncated line -> tolerated
    self.done.add((rec["examinee"], rec["probe_id"]))   # UNGUARDED

A truncated line is skipped; a well-formed line missing a key raises KeyError
from the CONSTRUCTOR, which means the whole checkpoint fails to open and a
thousands-of-call run cannot resume at all -- strictly worse than losing one line.

Read-only w.r.t. the repo; writes only to a temp dir.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "harmonia/experiments")
from run_zoo_matrix import Checkpoint  # noqa: E402

CASES = [
    ("clean (control)",            ['{"examinee":"P:m","probe_id":"0001","ok":true}']),
    ("truncated final (control)",  ['{"examinee":"P:m","probe_id":"0001","ok":true}',
                                    '{"examinee":"P:m","pr']),
    ("valid JSON, no probe_id",    ['{"examinee":"P:m","ok":true}']),
    ("valid JSON, no examinee",    ['{"probe_id":"0001","ok":true}']),
    ("valid JSON, empty object",   ['{}']),
    ("valid JSON, unrelated keys", ['{"foo":1,"bar":2}']),
    ("duplicate identical lines",  ['{"examinee":"P:m","probe_id":"0001","ok":true}',
                                    '{"examinee":"P:m","probe_id":"0001","ok":true}']),
    ("valid JSON, not an object",  ['["examinee","probe_id"]']),
]

print(f"{'case':30s} {'outcome':38s} records / done")
print("-" * 88)
for label, lines in CASES:
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "ck.jsonl"
        p.write_text("\n".join(lines), encoding="utf-8")
        try:
            c = Checkpoint(p)
            print(f"{label:30s} {'loaded OK':38s} {len(c.records)} / {len(c.done)}")
            c.close()
        except Exception as e:
            msg = f"{type(e).__name__}: {str(e)[:24]}"
            print(f"{label:30s} {'CONSTRUCTOR RAISES ' + msg:38s} -")
