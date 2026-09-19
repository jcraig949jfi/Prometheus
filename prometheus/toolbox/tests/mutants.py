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
    ("M43", "backends/local.py", "    if schedule and \"ext.world.mutable_params.v1\" not in registry.get(bk).capabilities:\n        return None, \"SCHEDULE_NOT_BATCHED\"", "    if False:\n        return None, \"SCHEDULE_NOT_BATCHED\"", "schedules run on a batch world that cannot take them"),
    ("M44", "ref/worlds_integer_batch.py", "        for i in range(n):\n            if actions[i] is None:\n                act[i] = False", "        pass", "an abandoned env is stepped with None actions"),
    ("M45", "backends/local.py", "                        if evs:\n                            ob.on_events(evs)                                   # same ORDER contract as _loop (C1)\n                        ob.on_tick(ticks, obs_env[i], acts[i])", "                        ob.on_tick(ticks, obs_env[i], acts[i])\n                        if evs:\n                            ob.on_events(evs)", "batch path delivers observer events after the tick"),
    ("M46", "registry.py", "            if r.state == \"ADMITTED\":\n                return k", "            return k", "an UNAVAILABLE batch world is chosen"),
    ("M47", "backends/local.py", "                if pending and (group_of(pending[0]) != group_of(spec) or len(pending) >= int(spec.experiment.budget[\"batch\"])):", "                if pending and len(pending) >= int(spec.experiment.budget[\"batch\"]):", "runs of different arms batched behind one world"),
    # seventh wave (C94): objective shapes
    ("M48", "backends/local.py", "    if isinstance(v, dict) and v and all(isinstance(k, str) and (x is None or (isinstance(x, (int, float)) and not isinstance(x, bool))) for k, x in v.items()):\n        return \"vector\"", "    if False:\n        return \"vector\"", "vector objectives summarised as UNSUPPORTED"),
    ("M49", "search.py", "    if all(isinstance(v, dict) for v in vals) and len({tuple(sorted(v)) for v in vals}) == 1:", "    if False:", "search rows drop vector objectives (None)"),
    ("M50", "search.py", "        for r in (new_rows if needs_scalar else []):                # C94: refuse with the keys named BEFORE the generation is written\n            scalar_objective(r, getattr(sel, \"rank\", None))\n", "", "an unrankable generation is committed before the refusal"),
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
    # tenth wave (C99): replay across paths
    ("M60", "backends/local.py", "    if batch is not None:\n        exp.budget = dict(exp.budget, batch=int(batch))", "    if False:\n        exp.budget = dict(exp.budget, batch=int(batch))", "replay re-runs the recorded batch policy instead of the scalar path"),
    # eleventh wave (C100): structured observations
    ("M61", "ref/players.py", "    for i, v in enumerate(flatten(obs)):                              # C100: structured observations fold through the canonical vector", "    for i, v in enumerate(obs):", "statemachines fold a structured observation as-is (keys, not values)"),
    ("M62", "backends/local.py", "            if permutes or ctrl_permutes:", "            if False:", "permute silently applied to a structured observation"),
    ("M63", "ref/worlds_grid.py", "        if self.p[\"obs_mode\"] == \"structured\":                    # C100: the same facts, named; the trace is the state and does not change", "        if False:", "grid obs_mode=structured returns the flat vector"),
    # twelfth wave (C110): per-player survival from the series
    ("M64", "ref/observers.py", "            value[c[:-len(\"_alive\")]] = sum(1 for rec in last if rec[i])", "            value[c[:-len(\"_alive\")]] = len(last)", "per-player survival reads the episode length, not the player's alive column"),
    # thirteenth wave (C111-C112): wrappers on the batch face
    ("M65", "ref/worlds_integer_batch.py", "            for i in range(self.n_envs):\n                # EVERY env records the change, finished ones too", "            for i in [j for j in range(self.n_envs) if self.regs is None or self.active[j]]:\n                # EVERY env records the change, finished ones too", "TASK_CHANGE skipped for an env finishing at the scheduled tick (fuzz seed 107)"),
    # fourteenth wave (C114): pareto selector
    ("M66", "search.py", "        dominated = any(all(a >= b for a, b in zip(w, v)) and any(a > b for a, b in zip(w, v)) for _, w in cand)", "        dominated = any(all(a > b for a, b in zip(w, v)) for _, w in cand)", "pareto front keeps rows dominated on all-but-one component"),
    ("M67", "search.py", "    needs_scalar = getattr(sel, \"needs_scalar\", True)", "    needs_scalar = True", "evolve refuses a vector archive even for a selector that needs no rank"),
    # fifteenth wave (C115): compact archives
    ("M68", "search.py", "    if not path.exists():\n        raise FileNotFoundError(\"compact archive row names %s which is not present\" % path)", "    if not path.exists():\n        from prometheus.toolbox.ref.players import random_statemachine; return random_statemachine(1).manifest()", "a compact row whose file is gone gets a silent fresh player"),
    ("M69", "search.py", "        r[\"_file\"] = path.name                                   # C115: rows may point here instead of embedding the player", "        r[\"_file\"] = \"gen_000_a0.jsonl\"", "compact rows all point at generation 0's file"),
    # sixteenth wave (C119): checkpoints carry wrapper state and mutable params
    ("M70", "backends/local.py", "        self._buf = {int(k): v for k, v in d[\"buf\"].items()}; self._perms = None        # permutations are re-derived from their seeds", "        self._buf = {}; self._perms = None", "a resumed delay wrapper starts with empty buffers"),
    ("M71", "backends/local.py", "        d = json.loads(snapshot.decode()); self.w.restore(bytes.fromhex(d[\"inner\"])); self._t = int(d[\"t\"]); self._i = int(d[\"i\"])", "        d = json.loads(snapshot.decode()); self.w.restore(bytes.fromhex(d[\"inner\"]))", "a resumed schedule fires its past entries again"),
    ("M72", "ref/worlds.py", "        self.p.update(d.get(\"params\", {}))\n        self._trace = hashlib.sha256((\"restored:\" + d[\"trace\"]).encode())", "        self._trace = hashlib.sha256((\"restored:\" + d[\"trace\"]).encode())", "a restored integer world forgets its runtime-mutable params"),
    # seventeenth wave (C121): committed receipts as fixtures
    ("M73", "ref/worlds.py", "                        st[\"pending\"].append((t + p[\"action_delay\"], pid, self.act_targets[i], x * 97))", "                        st[\"pending\"].append((t + p[\"action_delay\"], pid, self.act_targets[i], x * 98))", "a one-constant semantic change to the reference world (the committed receipts must diverge)"),
    ("M74", "ref/worlds_grid.py", "\"cells_nonzero\": sum(1 for c in st[\"cells\"] if c), \"pools\": list(st[\"pools\"])}", "\"cells_nonzero\": 0, \"pools\": list(st[\"pools\"])}", "grid summary lies about non-zero cells"),
    # eighteenth wave (C127): forensic scan property
    ("M75", "receipt.py", "                if isinstance(rec, dict) and isinstance(rec.get(\"receipt_id\"), str):\n                    chain.append(rec[\"receipt_id\"])", "                pass", "an edited receipt is reported twice (edit + a chain break on the next line)"),
    # nineteenth wave (C133): point mutation always changes one cell
    ("M76", "ref/transforms.py", "            cur = cell[2] + 1; cell[2] = (cur + 1 + s.below(pl[\"mem_range\"])) % (pl[\"mem_range\"] + 1) - 1", "            cell[2] = -1 if cell[2] >= 0 and s.below(4) == 0 else s.below(pl[\"mem_range\"])", "a v2 point mutation may return the parent unchanged"),
    # twentieth wave (C135): the substrate's clock in the checkpoint
    ("M77", "backends/local.py", "          \"substrates\": [so.snapshot().hex() if hasattr(so, \"snapshot\") else (so.dev.snapshot().hex() if hasattr(so, \"dev\") else None) for so in subs],   # C135: the substrate's clock too", "          \"substrates\": [so.dev.snapshot().hex() if hasattr(so, \"dev\") else None for so in subs],", "checkpoint carries the device but not the substrate's clock"),
    ("M78", "ref/substrates.py", "        d = json.loads(snap.decode()); self._t = d[\"t\"]; self._episode = d[\"episode\"]; self._tick_in_episode = d[\"tick_in_episode\"]", "        d = json.loads(snap.decode()); self._episode = d[\"episode\"]; self._tick_in_episode = d[\"tick_in_episode\"]", "a restored substrate's clock restarts at zero"),
    # twenty-first wave (C139): streams in the state model
    ("M79", "state.py", "        if len(s[\"r\"]) > s[\"maxlen\"]:\n            s[\"r\"].pop(0); self._c[\"discarded\"] += 1", "        if False:\n            s[\"r\"].pop(0); self._c[\"discarded\"] += 1", "streams grow past maxlen"),
    ("M80", "state.py", "        order = {\"ephemeral\": 0, \"episode\": 1, \"lifetime\": 2, \"persistent\": 3}\n        for store in (self._kv, self._h, self._s, self._z):", "        order = {\"ephemeral\": 0, \"episode\": 1, \"lifetime\": 2, \"persistent\": 3}\n        for store in (self._kv, self._h, self._z):", "end_scope leaves streams alive (anchor: end_scope, not advance -- the first anchor hit an equivalent mutant)"),
    ("M81", "state.py", "        self._s = {k: dict(e, r=[(rid, tuple(rec)) for rid, rec in e[\"r\"]]) for k, e in d[\"s\"].items()}", "        self._s = {}", "a restored device forgets its streams"),
    # twenty-second wave (C146): duplicate sweep values
    ("M82", "ir.py", "            elif len({json.dumps(v, sort_keys=True, default=str) for v in vals}) != len(vals):", "            elif False:", "duplicate sweep values accepted (a point runs twice; resume double-counts)"),
    # twenty-third wave (C148): failed rows, generator fallback, registry-scoped selectors
    ("M83", "search.py", "        fp = (r[\"science\"].get(\"player_fingerprints\") or {}).get(\"0\") or {}", "        fp = r[\"science\"][\"player_fingerprints\"][\"0\"]", "a FAILED run crashes row ingestion (generation never commits)"),
    ("M84", "search.py", "    gen = reg.get(parent[\"representation\"]).factory\n    return gen(seed, meta={\"fallback\": \"generator\", \"parent_representation\": parent[\"representation\"]})", "    return reg.make(\"transform.shuffle.v1\").apply(parent, seed)", "a representation no transform accepts crashes propose"),
    ("M85", "search.py", "    sel.workdir = workdir; sel.compact = compact; sel.registry = registry           # C148: selectors resolve generators and transforms here", "    sel.workdir = workdir; sel.compact = compact", "selectors use the process-global registry"),
    # twenty-fourth wave (C149): refused lowering inside a search
    ("M86", "search.py", "    if not low.ok:                                             # C149: a refused lowering is a stopped search with the reasons, never an AttributeError\n        raise GenerationIncomplete(\"generation %d refused at lowering (%s): %s\" % (gen, low.status, \"; \".join(low.reasons)[:300]), low.status)", "    pass", "a refused lowering crashes the search"),
    # twenty-fifth wave (atlas-bee S1-S5): the pilot scaffolding
    ("M87", "ref/players.py", "        a = self.actions[self.t % len(self.actions)] if self.actions else []", "        a = self.actions[0] if self.actions else []", "open-loop sequence player replays only its first action; never advances or wraps"),
    ("M88", "ref/substrates.py", "        self._c[\"ws_damage\"] += 1", "        pass", "kv weather does the damage but never counts a firing (erase reads zero ws_damage)"),
    ("M89", "ref/substrates.py", "            self.dev.put(self.key, v, scope=self.scope, ttl=self.ttl, player=self.player); self._c[\"ws_writes\"] += 1", "            self.dev.put(self.key, v, scope=self.scope, ttl=self.ttl, player=self.player)", "the sham rewrite is free: it restores the value but never pays the write it should"),
    ("M90", "search.py", "                w = sum(weights.values()); row[\"objective\"] = sum(weights[k] * per[k] for k in per) / w", "                w = sum(weights.values()); row[\"objective\"] = sum(per[k] for k in per) / len(per)", "the battery objective is the unweighted mean, ignoring the variant weights"),
    ("M91", "search.py", "                                  \"origin\": ((r[\"_player_manifest\"].get(\"meta\") or {}).get(\"origin\") or \"resident\"),          # atlas-bee S3", "                                  \"origin\": \"resident\",          # atlas-bee S3", "the archive cannot tell an import lineage from a resident one (every row reads resident)"),
    ("M92", "backends/local.py", "        ep = ep % max(1, int(pol.get(\"distinct\", 1)))", "        ep = ep", "recurring episode seeds do not cycle; every episode gets a distinct seed after all"),
]


def _purge_bytecode() -> None:
    """C122: a mutant of the SAME byte length restored within the same mtime second left a .pyc compiled from the
    mutated source that Python's timestamp+size check accepted for the restored file -- the suite then failed on an
    unmutated tree (27 replay fixtures diverged on a stale x*98). Mutant runs write no bytecode and purge what exists."""
    import shutil
    for d in (ROOT / TB).rglob("__pycache__"):
        shutil.rmtree(d, ignore_errors=True)


def run_suite() -> tuple:
    import os
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    t0 = time.time()
    # C95: the anchor-drift test (C87) fails for EVERY applied mutant -- with it in the run a mutant no real test
    # catches still reads CAUGHT (18 of 46 rows had it as their first failure). It is deselected here; only tests
    # of BEHAVIOUR may catch a mutant.
    r = subprocess.run([sys.executable, "-m", "pytest", "prometheus/toolbox/tests", "-q", "-x", "-p", "no:cacheprovider", "--ignore=prometheus/toolbox/tests/mutants.py",
                        "--deselect", "prometheus/toolbox/tests/test_integrity.py::test_every_mutant_anchor_still_exists"],
                       cwd=str(ROOT), capture_output=True, text=True, timeout=900, env=env)
    last = [l for l in r.stdout.splitlines() if l.strip()][-1:] or [""]
    failed = [l for l in r.stdout.splitlines() if l.startswith("FAILED")]
    return r.returncode, last[0], (failed[0][:140] if failed else ""), round(time.time() - t0, 1)


def main(argv):
    only = None
    if "--only" in argv:
        only = argv[argv.index("--only") + 1].split(",")
    ledger = []
    _purge_bytecode()
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
            p.write_text(src, encoding="utf-8", newline="\n"); _purge_bytecode()
        assert p.read_text(encoding="utf-8") == src
        ledger.append({"id": mid, "file": rel, "what": what, "result": "CAUGHT" if rc != 0 else "SURVIVED", "first_failure": first_fail, "suite_tail": tail, "seconds": secs})
        print(json.dumps(ledger[-1]))
    out = ROOT / "roles/Bellerophon/science/MUTATION_LEDGER_2026-09-19.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    if only and out.exists():                                     # C134: a --only run MERGES its rows; it never replaces the full ledger
        prior = {r["id"]: r for r in json.loads(out.read_text(encoding="utf-8"))}
        for r in ledger:
            prior[r["id"]] = r
        ledger_out = sorted(prior.values(), key=lambda r: int(r["id"][1:]))
    else:
        ledger_out = ledger
    out.write_text(json.dumps(ledger_out, indent=1), encoding="utf-8", newline="\n")
    print("survivors:", [m["id"] for m in ledger if m["result"] == "SURVIVED"])
    return ledger


if __name__ == "__main__":
    main(sys.argv[1:])
