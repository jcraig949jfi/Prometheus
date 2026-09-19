"""Mutation ledger (overnight C36; directive s7): apply one plausible WRONG implementation at a time to the
kernel, run the suite, record whether any test caught it. A surviving mutant is a false-green risk and becomes
the next failing test. Not a pytest module; run:  python -m prometheus.toolbox.tests.mutants [--only N]
Restores every file (asserts the tree is byte-identical afterwards)."""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
TB = "prometheus/toolbox/"

MUTANTS = [
    # (id, file, old, new, what a designer would see if this were live)
    ("M01", "backends/local.py", "for ep in range(exp.budget[\"episodes\"]):", "for ep in range(1):", "executor runs one episode whatever the budget says"),
    ("M02", "ref/controls.py", "return {\"outcome\": \"MET\" if ok else \"NOT_MET\", \"detail\": detail}", "return {\"outcome\": \"MET\", \"detail\": detail}", "every control expectation reads MET"),
    ("M03", "ref/worlds.py", "self._trace.update(json.dumps([t, st[\"regs\"], st[\"charge\"], st[\"alive\"]]).encode())", "self._trace.update(json.dumps([t, st[\"regs\"]]).encode())", "trace hash ignores charge and survival"),
    ("M04", "ref/worlds.py", "if cost > st[\"charge\"][pid]:\n                mag, cost = 0, 0", "if False:\n                mag, cost = 0, 0", "players act beyond their charge"),
    ("M05", "series.py", "if max_records is not None and total > max_records:", "if False:", "declared series bound never applied"),
    ("M06", "series.py", "rec[\"inline\"] = episodes\n    else:", "rec[\"inline\"] = episodes[:1]\n    else:", "inline series keeps only the first episode"),
    ("M07", "receipt.py", "if r[\"receipt_id\"] != receipt_id(r):\n        raise ReceiptError(\"receipt_id does not match content\")", "pass", "edited receipts validate"),
    ("M08", "capabilities.py", "missing = frozenset(c for c in req if c not in prov)", "missing = frozenset()", "negotiation never blocks"),
    ("M09", "state.py", "def _exp(self, ttl: Optional[int]) -> Optional[int]:\n        return None if ttl is None else self._tick + int(ttl)", "def _exp(self, ttl: Optional[int]) -> Optional[int]:\n        return None", "ttl never expires"),
    ("M10", "ref/substrates.py", "self._c[\"ws_refused\"] += 1\n\n    def cost(self):\n        return dict(self._c)\n\n    def snapshot(self) -> bytes:\n        import json\n        return json.dumps(self._c).encode()", "pass\n\n    def cost(self):\n        return dict(self._c)\n\n    def snapshot(self) -> bytes:\n        import json\n        return json.dumps(self._c).encode()", "flat substrate hides refused writes"),
    ("M11", "backends/local.py", "if evs:\n                ob.on_events(evs)\n            ob.on_tick(ticks, observations, actions)", "ob.on_tick(ticks, observations, actions)\n            if evs:\n                ob.on_events(evs)", "observer delivery order reverted (pre-consequence records)"),
    ("M12", "backends/local.py", "delay += int(wr.get(\"observation_delay\", 0))", "delay = int(wr.get(\"observation_delay\", 0))", "delays replace instead of adding"),
    ("M13", "ref/players.py", "self.state = nxt\n        if mw >= 0:\n            self.ws.write(int(mw))", "self.state = nxt\n        if False:\n            self.ws.write(int(mw))", "v2 players never write memory"),
    ("M14", "ref/transforms.py", "for k in (\"substrate\",):", "for k in ():", "transforms drop per-player substrates again"),
    ("M15", "backends/local.py", "if prior[\"status\"] == \"FAILED\":\n                    n_fail += 1\n                continue", "continue", "resume forgets prior failed runs"),
    ("M16", "search.py", "out += [b for b in buf if b[\"gen\"] == r[\"gen\"]]; buf = []", "out += buf; buf = []", "committed view accepts rows of another generation"),
    ("M17", "ref/observers.py", "elif kind == EVENT_ID[\"YIELD\"]:\n                self._ep_yield += val", "elif False:\n                self._ep_yield += val", "series yield column frozen at zero"),
    ("M18", "admission.py", "det = ser and m0 == m1 and obs[0].describe() == obs[1].describe()", "det = True", "observer admission ignores non-determinism"),
    ("M19", "backends/local.py", "if op.exists() and op.stat().st_size > 0:\n        if resume:", "if False:\n        if resume:", "receipts files silently appended"),
    ("M20", "ir.py", "json.dumps(self.to_dict(), allow_nan=False)", "pass", "non-data IR accepted"),
]


def run_suite() -> tuple:
    t0 = time.time()
    r = subprocess.run([sys.executable, "-m", "pytest", "prometheus/toolbox/tests", "-q", "-x", "-p", "no:cacheprovider", "--ignore=prometheus/toolbox/tests/mutants.py"],
                       cwd=str(ROOT), capture_output=True, text=True, timeout=900)
    last = [l for l in r.stdout.splitlines() if l.strip()][-1:] or [""]
    failed = [l for l in r.stdout.splitlines() if l.startswith("FAILED")]
    return r.returncode, last[0], (failed[0][:140] if failed else ""), round(time.time() - t0, 1)


def main(argv):
    only = None
    if "--only" in argv:
        only = argv[argv.index("--only") + 1].split(",")
    ledger = []
    for mid, rel, old, new, what in MUTANTS:
        if only and mid not in only:
            continue
        p = ROOT / TB / rel; src = p.read_text(encoding="utf-8")
        if old not in src:
            ledger.append({"id": mid, "file": rel, "what": what, "result": "MUTANT_NOT_APPLICABLE (anchor text not found)"}); continue
        try:
            p.write_text(src.replace(old, new, 1), encoding="utf-8", newline="\n")
            rc, tail, first_fail, secs = run_suite()
        finally:
            p.write_text(src, encoding="utf-8", newline="\n")
        assert p.read_text(encoding="utf-8") == src
        ledger.append({"id": mid, "file": rel, "what": what, "result": "CAUGHT" if rc != 0 else "SURVIVED", "first_failure": first_fail, "suite_tail": tail, "seconds": secs})
        print(json.dumps(ledger[-1]))
    out = ROOT / "roles/Bellerophon/science/MUTATION_LEDGER_2026-09-19.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ledger, indent=1), encoding="utf-8", newline="\n")
    print("survivors:", [m["id"] for m in ledger if m["result"] == "SURVIVED"])
    return ledger


if __name__ == "__main__":
    main(sys.argv[1:])
