"""Campaign-3 harness base: the campaign-2 Experiment (archaeon.campaign2.c2base) parametrized
for campaign 3 (D3-001): root archaeon/campaign3, campaign seed 20260920, engine client
cmp3-archaeon, ledger prefix L3. Adds the campaign-3 preregistration fields (why the slot is
still worth spending, kill condition, replacement condition, ancestry) to the SEALED body,
three-level reachability lookups, and corridor-table recording at close."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Optional, Sequence

from archaeon.wse import corridor as CT
from archaeon.wse import reachability as R
from archaeon.campaign2 import prereg as P
from archaeon.campaign2.c2base import FOUNDRY_C2, Experiment as _Experiment

C3 = Path(__file__).resolve().parent
CAMPAIGN_3 = {"root": C3, "seed": 20260920, "client": "cmp3-archaeon", "config": C3 / "config.local.json", "ledger_prefix": "L3", "campaign": "cmp3"}
CAMPAIGN_SEED = CAMPAIGN_3["seed"]
EXTRA_FIELDS = ["why_this_slot", "kill_condition", "replacement_condition", "ancestry"]
FIELDS_3 = list(P.FIELDS) + EXTRA_FIELDS


class Experiment3(_Experiment):
    CAMPAIGN = CAMPAIGN_3
    PREREG_FIELDS = FIELDS_3

    def __init__(self, *, dry_run: bool = False, procs: int = 12, purpose: str = ""):
        super().__init__(dry_run=dry_run, procs=procs, purpose=purpose)
        self.corridor_rows: List[dict] = []

    def reachability_for(self, targets: Sequence[tuple], foundry: Optional[dict] = None) -> dict:
        """Campaign-3 lookups carry the three levels (foothold / shelf / summit) and censoring."""
        out = {}
        rows = R.load()
        fid = R.foundry_id(foundry or FOUNDRY_C2)
        for spec, N, G, E, regime in targets:
            L = R.lookup(spec.name, value_bits=spec.value_bits, N=N, G=G, E=E, regime=regime, foundry=fid, rows=rows)
            pooled = R.lookup(spec.name, value_bits=spec.value_bits, regime=regime, foundry=fid, rows=rows)
            keys = ("n", "k", "freq", "band95", "class", "first_solved_gens", "k_shelf", "freq_shelf", "k_summit", "k_summit_any", "freq_summit",
                    "class_summit", "first_shelf_gens", "first_summit_gens", "levels", "shelf_hist", "n_censored_runs", "k_summit_candidate")
            out[spec.name] = {"foundry": fid, "at_budget": {k: L.get(k) for k in keys},
                              "pooled_any_budget": {k: pooled.get(k) for k in ("n", "k", "freq", "class", "k_summit", "k_summit_any", "class_summit", "budgets")}}
        return out

    def corridor_row(self, **kw: Any) -> None:
        arm = kw.pop("arm", None)
        kw.setdefault("source", {"campaign": "cmp3", "experiment": self.ID, "arm": arm, "attempt": self.att.number})
        self.corridor_rows.append(CT.row(**kw))

    def close(self, rows: List[dict], **kw: Any) -> dict:
        out = super().close(rows, **kw)
        if not self.dry_run and self.corridor_rows:
            self.receipt["corridor_rows_appended"] = CT.record(self.corridor_rows)
            self.att.save()
            (self.att.dir / "RECEIPT.json").write_text(json.dumps(self.receipt, indent=1, sort_keys=True, default=str), encoding="utf-8", newline="\n")
        return out


def level_fields(res: dict, heldout: Optional[float]) -> dict:
    """The three levels for one search result (D3-002/D3-006): summit needs the held-out."""
    tb = [t["best_reward"] for t in res["trace"]]
    best = max(tb) if tb else 0.0
    return {"best_train_max": round(best, 6), "level": R.level_of(best, heldout), "first_foothold_gen": res.get("first_solved_gen"),
            "first_shelf_gen": R.first_at(tb, R.SHELF_MIN), "summit_candidate_gen": R.first_at(tb, R.SUMMIT_MIN),
            "first_summit_gen": (R.first_at(tb, R.SUMMIT_MIN) if (heldout is not None and heldout >= R.SUMMIT_MIN) else None)}
