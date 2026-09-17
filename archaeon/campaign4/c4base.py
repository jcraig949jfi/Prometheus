"""Campaign 4 identity. The SEED is the datum PEW, Proteus and Vivarium were waiting on.

CAMPAIGN_SEED 20260921 continues the campaign-seed sequence (cmp1 20260917, cmp2 20260918,
cmp3 20260920; 20260916 and 20260919 are already present in REACHABILITY.jsonl from survey
work, so 20260921 is the first unused value). The seed is part of RUN IDENTITY: every
reachability row, corridor row, engine record and PEW envelope carries it, and two runs that
share (campaign_seed, rng_label, cell_seed) are the same run under common random numbers.

Nothing here is science. The science spec is preregistered per slot as in campaigns 2 and 3.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
C4 = REPO / "archaeon" / "campaign4"

CAMPAIGN_SEED = 20260921
CAMPAIGN_4 = {
    "root": C4,
    "seed": CAMPAIGN_SEED,
    "client": "cmp4-archaeon",
    "config": C4 / "config.local.json",      # gitignored; engine token lives here
    "ledger_prefix": "L4",
    "campaign": "cmp4",
}
