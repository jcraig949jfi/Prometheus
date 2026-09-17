"""The campaign-2 harness base: every C2-SFE-NN harness is an Experiment subclass that
declares its preregistration, runs its arms through the runner, and closes through the
accounting. What the base guarantees for every experiment (Phase A obligations):

  - PREREG.json sealed (digest) and published on the engine as a hypothesis-kind artifact
    BEFORE any search runs; re-validated at close (PREREG_CHANGED_AFTER_SEAL is an error)
  - reachability_estimate filled from the table (reachability.lookup) for every target the
    harness declares, never typed by hand; every search row appended to the table at close
  - common random numbers: run_cell's default; the base's search() helper refuses an
    init_pop without gen0 provenance
  - typed states + disposition candidate computed from rows, counters and maturity blocks
  - attempts / resume / receipts / RECORD.md / ledger candidates / FUNNEL.json generated
"""
from __future__ import annotations

import json
import multiprocessing as mp
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from archaeon.wse import reachability as R                                 # noqa: E402
from archaeon.wse import states as S                                       # noqa: E402
from archaeon.wse.evolve import FOUNDRY                                    # noqa: E402
from archaeon.wse.worlds import WorldSpec                                  # noqa: E402
from archaeon.campaign2 import accounting as A                             # noqa: E402
from archaeon.campaign2 import prereg as P                                 # noqa: E402
from archaeon.campaign2.runner import Attempt, Engine, C2, CAMPAIGN_SEED   # noqa: E402

FOUNDRY_C2 = dict(FOUNDRY, genome_instr_range=[1, 16], tape_words_choices=[16, 32, 64, 128, 256], tick_budget_choices=[16, 64, 256])
FUNNEL = C2 / "FUNNEL.json"


class Experiment:
    ID = "C2-SFE-00"
    TITLE = ""
    PARENTS: List[str] = []
    ARM_FIELD = "arm"
    METRICS: Sequence[str] = ("competence_heldout",)

    def __init__(self, *, dry_run: bool = False, procs: int = 12, purpose: str = ""):
        self.dry_run, self.procs = dry_run, procs
        self.att = Attempt(self.ID, dry_run=dry_run, purpose=purpose or ("dry run" if dry_run else "engine"))
        self.eng = Engine(dry_run=dry_run)
        self.receipt = self.att.receipt
        self.prereg: Dict[str, Any] = {}
        self.rows: List[dict] = []
        self.reach_rows: List[dict] = []
        self.decisions: List[str] = []
        self.session_id: Optional[str] = None
        self.group_id: Optional[str] = None
        self.T = time.time()

    # -- preregistration ----------------------------------------------------
    def reachability_for(self, targets: Sequence[tuple]) -> dict:
        """targets = [(spec, N, G, E, regime), ...] -> {cell: lookup} straight from the table."""
        out = {}
        rows = R.load()
        for spec, N, G, E, regime in targets:
            L = R.lookup(spec.name, value_bits=spec.value_bits, N=N, G=G, E=E, regime=regime, rows=rows)
            pooled = R.lookup(spec.name, value_bits=spec.value_bits, regime=regime, rows=rows)
            out[spec.name] = {"at_budget": {k: L[k] for k in ("n", "k", "freq", "band95", "class", "first_solved_gens")},
                              "pooled_any_budget": {k: pooled[k] for k in ("n", "k", "freq", "band95", "class", "budgets")}}
        return out

    def seal(self, prereg: dict) -> dict:
        prereg = dict(prereg, experiment=self.ID, title=self.TITLE, parents=self.PARENTS)
        path = P.save(prereg, self.att.dir)
        self.prereg = json.loads(path.read_text(encoding="utf-8"))
        self.receipt["prereg_digest"] = self.prereg["prereg_digest"]
        self.att.save()
        return self.prereg

    # -- engine lifecycle (each step keyed, replayable) ---------------------
    def open(self, session_note: str, group_note: Optional[str] = None) -> None:
        if self.dry_run:
            return
        t0 = time.time()
        self.receipt["engine_version"] = self.att.step("version", self.eng.version, kind="engine")
        self.session_id = self.att.step("session", lambda: self.eng.session(session_note), kind="engine")
        if group_note:
            self.group_id = self.att.step("group", lambda: self.eng.group(group_note), kind="engine")
        self.att.timing("startup_s", t0)

    def world(self, name: str, policy: str, use_group: bool = True) -> str:
        if self.dry_run:
            return "dry:" + name
        w = self.att.step("world", lambda: self.eng.world(self.session_id, "%s-%s" % (self.ID.lower(), name), policy,
                                                          self.group_id if use_group else None), parts=(name,), kind="world",
                          verify=lambda r: self.eng.alive(r["world_id"]))
        self.receipt["worlds"][name] = w["world_id"]
        self.att.save()
        return w["world_id"]

    def publish_prereg(self, wid: str) -> None:
        """The seal goes on the engine before any measurement (hypothesis-kind artifact)."""
        if self.dry_run:
            return
        body = {k: self.prereg[k] for k in P.FIELDS} | {"prereg_digest": self.prereg["prereg_digest"]}
        self.receipt["hypothesis"] = self.att.step("hypothesis", lambda: self.eng.hypothesis(wid, self.prereg["question"][:900]), kind="engine")
        art = self.att.step("prereg_artifact", lambda: self.eng.publish(wid, "cmp2.prereg.v1", body, {"info_kind": "hypothesis"},
                                                                         idem_key=self.att.key("prereg_artifact")), kind="engine")
        self.receipt["artifacts"]["prereg"] = art
        self.att.save()

    def publish(self, wid: str, name: str, kind: str, obj: Any, meta: Optional[dict] = None, maturity: Optional[dict] = None) -> dict:
        if self.dry_run:
            return {"artifact_id": "dry:" + name, "declared": None, "bytes": 0, "hash_ok": None}
        art = self.att.step("publish", lambda: self.eng.publish(wid, kind, obj, meta, maturity=maturity, idem_key=self.att.key("publish", name)),
                            parts=(name,), kind="engine")
        self.receipt["artifacts"][name] = art
        self.att.save()
        return art

    def import_fetch(self, name: str, dst: str, src: str, art: dict) -> Any:
        """Returns the object the CONSUMER fetched back (the experiment runs on those bytes)."""
        if self.dry_run:
            return None
        obj, info = self.att.step("import_fetch", lambda: self.eng.import_fetch(dst, src, art["artifact_id"], expected=art["declared"]),
                                  parts=(name,), kind="engine")
        self.receipt["imports"][name] = info
        self.att.save()
        return obj

    def record(self, wid: str, row: dict, spec: dict, content: dict, outcome: str, key_parts: tuple) -> None:
        if self.dry_run:
            return
        try:
            rec = self.att.step("record", lambda: self.eng.record(wid, spec, content, outcome, idem_key=self.att.key("obs", *key_parts),
                                                                  hyp_id=self.receipt.get("hypothesis")), parts=key_parts, kind="engine")
            row["engine"] = rec
            self.receipt["records"]["/".join(str(k) for k in key_parts)] = rec
        except Exception:                                            # noqa: BLE001
            pass                                                     # the step recorded the error in the receipt
        self.att.save()

    def teardown(self) -> None:
        if self.dry_run:
            return
        t0 = time.time()
        self.receipt["teardown"] = self.eng.terminate_all(self.receipt["worlds"])
        self.att.timing("teardown_s", t0)

    # -- search helpers -------------------------------------------------------
    def pool_map(self, fn: Callable, jobs: list, timing: str) -> list:
        t0 = time.time()
        if not jobs:
            return []
        if self.procs <= 1 or len(jobs) == 1:
            out = [fn(j) for j in jobs]
        else:
            with mp.Pool(processes=min(self.procs, len(jobs))) as pool:
                out = pool.map(fn, jobs)
        self.att.timing(timing, t0)
        return out

    def reach_row(self, spec: WorldSpec, res: dict, *, N: int, G: int, E: int, regime: str, seed: int, arm: str,
                  heldout: Optional[float] = None) -> None:
        self.reach_rows.append(R.row_from_result(spec, res, N=N, G=G, E=E, regime=regime, seed=seed, heldout=heldout,
                                                 source={"campaign": "cmp2", "experiment": self.ID, "arm": arm, "attempt": self.att.number}))

    def decision(self, text: str) -> None:
        self.decisions.append(text)

    # -- close ----------------------------------------------------------------
    def close(self, rows: List[dict], *, addendum: Optional[Dict[str, str]] = None, meas_extra: Optional[dict] = None,
              of_record: bool = True, funnel_extra: Optional[dict] = None) -> dict:
        self.rows = rows
        of_record = of_record and not self.dry_run            # a dry run is never the attempt of record
        if not P.unchanged(self.prereg, self.prereg["prereg_digest"]):
            self.att.error("prereg", error="PREREG_CHANGED_AFTER_SEAL")
        meas = {"rows": rows, "arm_field": self.ARM_FIELD,
                "engine_errors": [e for e in self.receipt["errors"] if e.get("kind") in ("engine", "world")],
                "harness_errors": [e for e in self.receipt["errors"] if e.get("kind") not in ("engine", "world")]}
        meas.update(meas_extra or {})
        states = S.assay_states(self.prereg["decl"], meas)
        disp = S.disposition_candidate(self.prereg["decl"], meas, states)
        self.receipt["typed_states"] = states
        self.receipt["reachability_rows_appended"] = R.record(self.reach_rows)
        self.receipt["decisions"] = list(self.decisions)
        self.teardown()
        idx = self.att.finalize(rows=rows, of_record=of_record, disposition=disp)
        # generated record, ledger candidates, funnel row
        text = A.render_record(self.prereg, self.receipt, rows, idx, arm_field=self.ARM_FIELD, metrics=self.METRICS, states=states,
                               disposition=disp, addendum=addendum or {}, decisions=self.decisions)
        (self.att.path / "RECORD.generated.md").write_text(text, encoding="utf-8", newline="\n")
        if of_record:
            (self.att.dir / "RECORD.md").write_text(text, encoding="utf-8", newline="\n")
            cands = A.ledger_candidates(self.ID, self.receipt, states, idx)
            ids = A.append_ledger(cands)
            self.receipt["ledger_ids"] = ids
            f = A.funnel_row(self.ID, self.prereg, self.receipt, states, disp, idx, decisions=self.decisions, **(funnel_extra or {}))
            funnel = json.loads(FUNNEL.read_text(encoding="utf-8")) if FUNNEL.exists() else {}
            funnel[self.ID] = f
            FUNNEL.write_text(json.dumps(funnel, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
            self.att.save()
        return {"disposition": disp, "states": [s["state"] for s in states], "attempt": self.att.number, "errors": len(self.receipt["errors"]),
                "timings": self.receipt["timings"], "teardown": self.receipt.get("teardown")}
