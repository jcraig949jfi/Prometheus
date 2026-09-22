"""Campaign-4 harness: the campaign-3 Experiment (archaeon.campaign3.c3base.Experiment3)
parametrized for campaign 4 (D4-001): root archaeon/campaign4, campaign seed 20260921, engine
client cmp4-archaeon, ledger prefix L4. Same sealed contract (campaign-3 fields), same
reachability lookups, same corridor recording. Nothing here is science.

Kept apart from c4base.py (identity constants only, imported by the gate and the rehearsal
driver) so that reading the campaign identity never pulls the engine client in.

Execution path (D4-001): local evaluation with the frozen runtime, every world / experiment /
observation written to the engine under the campaign identity, PEW ingest by Mnemosyne's
campaign-4 reader. Not a Vivarium queue row: no admissible kind evaluates a program variant
(asked of Vivarium, roles/Archaeon/prompts/2026-09-17_c4_convergence/06_VIVARIUM_WSE_KIND.md).
"""
from __future__ import annotations

from archaeon.campaign3.c3base import Experiment3, FIELDS_3
from archaeon.campaign4.c4base import CAMPAIGN_4, CAMPAIGN_SEED  # noqa: F401


class Experiment4(Experiment3):
    CAMPAIGN = CAMPAIGN_4
    PREREG_FIELDS = FIELDS_3

    def corridor_row(self, **kw) -> None:
        arm = kw.pop("arm", None)
        kw.setdefault("source", {"campaign": "cmp4", "experiment": self.ID, "arm": arm, "attempt": self.att.number})
        super().corridor_row(arm=arm, **kw)
