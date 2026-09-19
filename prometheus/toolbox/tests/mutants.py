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
    ("M10", "ref/substrates.py", "    def write(self, value: int) -> None:\n        self._c[\"ws_refused\"] += 1\n\n    def create(self, program):\n        self._c[\"ws_refused\"] += 1; return None", "    def write(self, value: int) -> None:\n        pass\n\n    def create(self, program):\n        self._c[\"ws_refused\"] += 1; return None", "flat substrate hides refused writes"),
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
    # second wave (C42): tonight's later modules
    ("M21", "ref/worlds_grid.py", "st[\"cells\"][n] = 0; st[\"owner\"][n] = -1", "pass", "grid tools are never consumed"),
    ("M22", "ref/worlds.py", "if keep and self._state is not None:", "if False:", "world lifetime state silently ignored"),
    ("M23", "search.py", "elif k == \"GEN_ABANDONED\":\n            buf = []", "elif False:\n            buf = []", "abandoned rows committed"),
    ("M24", "backends/local.py", "self._t += 1\n        self._apply()", "self._apply()", "schedule wrapper never advances"),
    ("M25", "state.py", "if len(self._ev) > self.max_events:", "if False:", "event buffer unbounded again"),
    ("M27", "backends/local.py", "\"pre_checkpoint_trace\": world.trace_hash()}", "\"pre_checkpoint_trace\": \"\"}", "checkpoint forgets the pre-checkpoint hash"),
    ("M28", "ref/worlds_grid.py", "others = sum(1 for q in range(self.n_players) if q != pid and st[\"alive\"][q] and st[\"pos\"][q] == n)", "others = 0", "grid observation hides neighbours"),
    # third wave (C61): mailbox, ablation, series columns, chain, per-player columns
    ("M29", "ref/substrates.py", "            if rec[0] != self.player:\n                v = rec[1]; break", "            v = rec[1]; break", "mailbox echoes a player its own messages"),
    ("M30", "ref/controls.py", "        if p == 0:\n            return {\"outcome\": \"INDETERMINATE\"", "        if False:\n            return {\"outcome\": \"INDETERMINATE\"", "ablation claims MET with nothing to ablate"),
    ("M31", "series.py", "    if columns and width and len(columns) != width:", "    if False:", "series layout mismatch not flagged"),
    ("M32", "receipt.py", "        r = dict(r); r[\"prev_receipt_id\"] = self.prev", "        r = dict(r); r[\"prev_receipt_id\"] = None", "receipt chain never links"),
    ("M33", "ref/observers.py", "                rec += [sum(actions.get(pid, [])), self._ep_yield_by.get(pid, 0), 1 if self._alive_by.get(pid, False) else 0]", "                rec += [0, 0, 1]", "per-player series columns are zeros"),
    ("M34", "ref/observers.py", "        c = cols.index(\"yield_cum\")                              # C53: by NAME, never by habit", "        c = 2", "objective reads column 2 by habit"),
    # fourth wave (C66): artifacts, pendulum quantum, ablation coverage
    ("M35", "ref/substrates.py", "            if rid - 1 == aid:", "            if True:", "invoke ignores the artifact id (runs the first program)"),
    ("M36", "ref/worlds_pendulum.py", "        return int(round(x / self.p[\"quantum\"]))", "        return int(round(x / 1e-6))", "pendulum ignores the declared quantum"),
    ("M37", "ref/controls.py", "        e.players = [{k: v for k, v in p.items() if k != \"substrate\"} for p in e.players]", "        e.players = list(e.players)", "ablation leaves per-player workspaces in place"),
    ("M38", "ref/substrates.py", "        self._c[\"ws_invocations_failed\"] += 1\n        return None", "        return None", "failed invocations uncounted"),
    # fifth wave (C91): resume identity, zero players, eligibility
    ("M39", "backends/local.py", "            if prior_ids and job.experiment_id not in prior_ids:", "            if False:", "resume into another experiment's file allowed"),
    ("M40", "ref/worlds.py", "or (self.n_players > 0 and not any(st[\"alive\"]))     # C84", "or not any(st[\"alive\"])", "zero-player world ends at tick 1"),
    ("M41", "backends/local.py", "    if max_runs is not None and n_runs > int(max_runs):", "    if False:", "max_runs never refuses"),
    # sixth wave (C92): the batch path
    ("M42", "admission.py", "        res.failed.append(\"registry\"); return res                                  # the row keeps its import reason for the next asker", "        res.failed.append(\"registry\"); row.admission = dict(row.admission, **res.as_dict()); return res", "absent-machinery row loses its import reason on re-admission (then constructs)"),
    ("M43", "backends/local.py", "    if delay or permutes or schedule:\n        return None, \"WRAPPERS_NOT_BATCHED\"", "    if False:\n        return None, \"WRAPPERS_NOT_BATCHED\"", "kernel wrappers silently dropped on the batch path"),
    ("M44", "ref/worlds_integer_batch.py", "        for i in range(n):\n            if actions[i] is None:\n                act[i] = False", "        pass", "an abandoned env is stepped with None actions"),
    ("M45", "backends/local.py", "                        if evs:\n                            ob.on_events(evs)                                   # same ORDER contract as _loop (C1)\n                        ob.on_tick(ticks, obs_env[i], acts[i])", "                        ob.on_tick(ticks, obs_env[i], acts[i])\n                        if evs:\n                            ob.on_events(evs)", "batch path delivers observer events after the tick"),
    ("M46", "registry.py", "            if r.state == \"ADMITTED\":\n                return k", "            return k", "an UNAVAILABLE batch world is chosen"),
    ("M47", "backends/local.py", "                if pending and (group_of(pending[0]) != group_of(spec) or len(pending) >= int(spec.experiment.budget[\"batch\"])):", "                if pending and len(pending) >= int(spec.experiment.budget[\"batch\"]):", "runs of different arms batched behind one world"),
    # seventh wave (C94): objective shapes
    ("M48", "backends/local.py", "    if isinstance(v, dict) and v and all(isinstance(k, str) and (x is None or (isinstance(x, (int, float)) and not isinstance(x, bool))) for k, x in v.items()):\n        return \"vector\"", "    if False:\n        return \"vector\"", "vector objectives summarised as UNSUPPORTED"),
    ("M49", "search.py", "    if all(isinstance(v, dict) for v in vals) and len({tuple(sorted(v)) for v in vals}) == 1:", "    if False:", "search rows drop vector objectives (None)"),
    ("M50", "search.py", "        for r in new_rows:                                          # C94: refuse with the keys named BEFORE the generation is written\n            scalar_objective(r, getattr(sel, \"rank\", None))\n", "", "an unrankable generation is committed before the refusal"),
    ("M51", "admission.py", "            obj = row.factory(**row.admission_params); out = obj.evaluate(", "            obj = row.factory(); out = obj.evaluate(", "admission ignores a component's admission params"),
    # eighth wave (C96): identity vs behaviour class, survival v2
    ("M52", "backends/local.py", "\"spec_hash\": component_manifest_hash(specs[pid].manifest())}", "\"spec_hash\": inst.fingerprint()}", "spec identity is the behavioural probe hash again"),
    ("M53", "ref/observers.py", "        return {\"value\": ticks, \"components\": {\"ticks\": ticks, \"alive\": alive, \"n_alive\": sum(1 for a in alive if a)}}", "        return {\"value\": ticks * sum(1 for a in alive if a), \"components\": {\"ticks\": ticks, \"alive\": alive, \"n_alive\": sum(1 for a in alive if a)}}", "survival.v2 is the v1 step function"),
    ("M54", "search.py", "\"player_hash\": fp.get(\"spec_hash\") or component_manifest_hash(r[\"_player_manifest\"]),", "\"player_hash\": fp[\"hash\"],", "archive rows key identity by behaviour class"),
    # ninth wave (C97): control power
    ("M55", "ref/controls.py", "        if not differs:                                            # C97: a shuffle that changed no behaviour tested nothing", "        if False:", "sham reads MET when the shuffle changed nothing"),
    ("M56", "ref/controls.py", "        if not has_obj:                                            # C97: an abstainer with nothing to compare against is not a failed control", "        if False:", "negative control without an objective reads MET/NOT_MET instead of INDETERMINATE"),
    ("M57", "ref/controls.py", "        if same:                                                   # C97: a \"fresh\" player with the primary's genome is not fresh", "        if False:", "scratch accepts a fresh player with the primary's genome"),
    ("M58", "ref/controls.py", "        if eq:                                                     # C97: a permutation that changed nothing (one-element observations) tested nothing", "        if False:", "permutation reads MET when it changed nothing"),
    ("M59", "backends/local.py", "    if \"registry\" in params or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()):", "    if False:", "control arms built against the process-global registry"),
]


def run_suite() -> tuple:
    t0 = time.time()
    # C95: the anchor-drift test (C87) fails for EVERY applied mutant -- with it in the run a mutant no real test
    # catches still reads CAUGHT (18 of 46 rows had it as their first failure). It is deselected here; only tests
    # of BEHAVIOUR may catch a mutant.
    r = subprocess.run([sys.executable, "-m", "pytest", "prometheus/toolbox/tests", "-q", "-x", "-p", "no:cacheprovider", "--ignore=prometheus/toolbox/tests/mutants.py",
                        "--deselect", "prometheus/toolbox/tests/test_integrity.py::test_every_mutant_anchor_still_exists"],
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
