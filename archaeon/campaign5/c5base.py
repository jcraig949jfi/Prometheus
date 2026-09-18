"""Campaign 5 identity and harness. CAMPAIGN_SEED 20260922 continues the campaign-seed sequence
(cmp4 20260921). Engine client cmp5-archaeon (self-registered on first use by the campaign-2
Engine wrapper; the credential is written to the gitignored config.local.json beside this file
and never moves). Ledger prefix L5. The harness is the campaign-3 Experiment parametrized
(D3-001 pattern), exactly as campaign 4's (c4harness.py).

Execution path (D5-001): the campaign harness path (local evaluation with the frozen runtime for
Phase A; the campaign-scoped ISA-B interpreter for Phase B; every world / experiment / observation
written to the engine under the campaign identity; PEW ingest by Mnemosyne's reader once it
knows seed 20260922). Vivarium's wse_evaluate_v1 is a day away and wraps the old evaluator only.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
C5 = REPO / "archaeon" / "campaign5"

CAMPAIGN_SEED = 20260922
CAMPAIGN_5 = {
    "root": C5,
    "seed": CAMPAIGN_SEED,
    "client": "cmp5-archaeon",
    "config": C5 / "config.local.json",      # gitignored; engine token lives here (self-registered)
    "ledger_prefix": "L5",
    "campaign": "cmp5",
}


def harness():
    """Import lazily so reading the identity never pulls the engine client in."""
    from archaeon.campaign3.c3base import Experiment3, FIELDS_3          # noqa: PLC0415

    class Experiment5(Experiment3):
        CAMPAIGN = CAMPAIGN_5
        PREREG_FIELDS = FIELDS_3

        def corridor_row(self, **kw) -> None:
            arm = kw.pop("arm", None)
            kw.setdefault("source", {"campaign": "cmp5", "experiment": self.ID, "arm": arm, "attempt": self.att.number})
            super().corridor_row(arm=arm, **kw)

    return Experiment5
