"""Which malformed lines in the pin actually DISCRIMINATE? (soak P30)

P54's pin carries 7 malformed shapes and scores 2/4 on mutations; the patched
version carries 9 and scores 4/4. If shape count were coverage those numbers
would track. This measures each line's discriminating power directly: build a
pin containing ONLY that line (plus the two good records) and see which
mutations it catches alone.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SRC = Path("harmonia/experiments/run_zoo_matrix.py")
original = SRC.read_text(encoding="utf-8")
GUARD = '''                if not isinstance(rec, dict) or "examinee" not in rec or "probe_id" not in rec:
                    self.n_skipped_malformed = getattr(self, "n_skipped_malformed", 0) + 1
                    continue'''
assert original.count(GUARD) == 1

MUTATIONS = {
 "M1": "",
 "M2": '''                if "examinee" not in rec or "probe_id" not in rec:
                    self.n_skipped_malformed = getattr(self, "n_skipped_malformed", 0) + 1
                    continue''',
 "M3": '''                if not isinstance(rec, dict) or "examinee" not in rec:
                    self.n_skipped_malformed = getattr(self, "n_skipped_malformed", 0) + 1
                    continue''',
 "M4": '''                if not isinstance(rec, dict) or "examinee" not in rec or "probe_id" not in rec:
                    continue''',
}

LINES = [
 ('truncated  {"truncat',            '{"truncat',                              "P54"),
 ('{"wrong": "shape"}',              json.dumps({"wrong": "shape"}),           "P54"),
 ('{}  (empty object)',              json.dumps({}),                           "P54"),
 ('{"unrelated":1,"keys":2}',        json.dumps({"unrelated": 1, "keys": 2}),  "P54"),
 ('[1,2,3]  (list)',                 json.dumps([1, 2, 3]),                    "P54"),
 ('"just a string"',                 json.dumps("just a string"),              "P54"),
 ('null',                            json.dumps(None),                         "ADDED"),
 ('{"examinee":"a"} (no probe_id)',  json.dumps({"examinee": "a"}),            "ADDED"),
]
GOOD = [json.dumps({"examinee": "a", "probe_id": "p1"}),
        json.dumps({"examinee": "b", "probe_id": "p2"})]

RUNNER = '''import json, sys, os, tempfile
from pathlib import Path
sys.path.insert(0, os.path.abspath("harmonia/experiments"))
from run_zoo_matrix import Checkpoint
p = Path(tempfile.mkdtemp()) / "ck.jsonl"
p.write_text(open(sys.argv[1], encoding="utf-8").read(), encoding="utf-8")
ck = Checkpoint(p)
assert len(ck.records) == 2, ck.records
assert ck.done == {("a", "p1"), ("b", "p2")}
assert getattr(ck, "n_skipped_malformed", 0) == 1
print("ok")
'''
rp = Path(tempfile.mkdtemp()) / "r.py"
rp.write_text(RUNNER, encoding="utf-8")


def run(fixture):
    r = subprocess.run([sys.executable, str(rp), str(fixture)],
                       capture_output=True, text=True, timeout=60)
    return r.returncode


print(f"{'malformed line':34s} {'src':>6s}  {'catches alone':22s} power")
print("-" * 78)
rows = []
try:
    for label, line, src in LINES:
        fx = Path(tempfile.mkdtemp()) / "f.jsonl"
        fx.write_text(GOOD[0] + "\n" + line + "\n" + GOOD[1] + "\n", encoding="utf-8")
        SRC.write_text(original, encoding="utf-8")
        if run(fx) != 0:
            print(f"{label:34s} {src:>6s}  (not green at baseline — skipped)")
            continue
        caught = [m for m, repl in MUTATIONS.items()
                  if (SRC.write_text(original.replace(GUARD, repl), encoding="utf-8"), run(fx))[1] != 0]
        rows.append((label, src, caught))
        print(f"{label:34s} {src:>6s}  {(','.join(caught) or '— none —'):22s} {len(caught)}/4")
finally:
    SRC.write_text(original, encoding="utf-8")
    assert SRC.read_text(encoding="utf-8") == original, "RESTORE FAILED"

print("-" * 78)
p54_union = sorted({m for l, s, c in rows if s == "P54" for m in c})
all_union = sorted({m for l, s, c in rows for m in c})
dead = [l for l, s, c in rows if not c]
print(f"P54's 6 testable lines catch, in union : {p54_union}")
print(f"with the 2 added lines                 : {all_union}")
print(f"lines catching NOTHING on their own    : {len(dead)} of {len(rows)}")
for d in dead:
    print(f"   {d}")
print("\nfile restored byte-identical: True")
