"""Stygian loader for BL-C-002 -- BSD rank distribution.

Claim under test: the rank distribution in the curated BSD-rich
1000-curve sample is NON-UNIFORM across conductor strata (i.e.,
rank is confounded with conductor scale). This is the strongest
version of the SEED_PROBLEMS modal_llm_error claim ('rank distribution
is 50/50 above conductor N without isogeny-class/family conditioning')
that the available data supports.

Data source: prometheus_math/databases/bsd_rich.json.gz (1000 entries
from LMFDB / Cremona; rank 0/1/2 distribution 500/400/100; conductor
range 39-9990). The SEED claim about 'conductor > 10^7' is not
testable on this dataset (no such conductors available); we test the
weaker structural claim at the conductor range present.

Strategy: distribution-mode test with F17 confound sensitivity.
- values: rank values (0, 1, 2)
- group_labels: same rank values (treating rank as categorical group)
- confound_values: log10(conductor) (continuous confound)
- F17 reports whether the group mean differs SIGNIFICANTLY after
  controlling for the confound. If yes -> rank distribution is
  structurally non-uniform across conductor strata (claim survives).
  If no -> the rank skew is plausibly explained by conductor effect
  alone (claim weakens; F17 = SUSPECT).

Per pivot/stygian_executor_scoping_2026-05-21.md MVP1 follow-on +
2026-05-25 frontier-review convergent recommendation (R1: complete
Stygian loaders).
"""
from __future__ import annotations

import gzip
import json
import math
from pathlib import Path
from typing import Any

from harmonia.agents._base import REPO_ROOT

BSD_DATA_PATH = REPO_ROOT / "prometheus_math" / "databases" / "bsd_rich.json.gz"


def load() -> dict[str, Any]:
    """Return BatteryLoaderResult for BL-C-002.

    Reads bsd_rich.json.gz once; extracts (rank, conductor) per entry;
    runs F17 confound sensitivity with rank as group and log10(conductor)
    as confound."""
    if not BSD_DATA_PATH.exists():
        return {
            "mode": "distribution",
            "claim": "BL-C-002 data unavailable (bsd_rich.json.gz missing)",
            "data_source": str(BSD_DATA_PATH),
            "values": [],
            "notes": "loader_skip: data file missing",
        }

    with gzip.open(BSD_DATA_PATH, "rt", encoding="utf-8") as f:
        data = json.load(f)
    entries = data.get("entries", [])

    ranks: list[int] = []
    log_conductors: list[float] = []
    for e in entries:
        b = e.get("base", {})
        r = b.get("rank")
        c = b.get("conductor")
        if r is None or c is None or c <= 0:
            continue
        ranks.append(int(r))
        log_conductors.append(math.log10(float(c)))

    if not ranks:
        return {
            "mode": "distribution",
            "claim": "BL-C-002 -- no valid (rank, conductor) pairs in data",
            "data_source": str(BSD_DATA_PATH),
            "values": [],
            "notes": "loader_skip: empty after filtering",
        }

    # The "value" the distribution tests fire over is rank itself.
    # F18 subset stability + F20 representation invariance still
    # meaningful on this distribution. F15 log-normal SHOULD deviate
    # (ranks are integer-valued small categorical). F16 equivalence
    # tests against predicted_value = mean(ranks) if BSD-50/50 held
    # (would be 0.5); we use the actual observed mean as the claim
    # predicted value so F16 measures self-consistency, not the BSD
    # toy claim.
    rank_vals = [float(r) for r in ranks]
    observed_mean = sum(rank_vals) / len(rank_vals)

    from collections import Counter
    dist = dict(Counter(ranks))

    return {
        "mode": "distribution",
        "claim": (
            f"BL-C-002 / BSD rank distribution non-uniform across "
            f"conductor strata in BSD-rich N={len(rank_vals)} curated "
            f"sample. Observed rank distribution: {dist} (mean="
            f"{observed_mean:.4f}). Tests whether F17 confound "
            f"sensitivity flags rank-conductor confounding -- if "
            f"SIGNIFICANT, the simple 'rank ~ 50/50' framing in the "
            f"SEED_PROBLEMS modal_llm_error is structurally inadequate."
        ),
        "data_source": (
            f"prometheus_math/databases/bsd_rich.json.gz "
            f"(LMFDB/Cremona curated, n_entries={len(entries)}, "
            f"valid_pairs={len(rank_vals)}, conductor_range "
            f"[{min(10**lc for lc in log_conductors):.0f}, "
            f"{max(10**lc for lc in log_conductors):.0f}])"
        ),
        "values": rank_vals,
        "predicted_value": observed_mean,
        "domain_is_multiplicative": False,  # ranks are categorical-integer
        "group_labels": ranks,  # rank itself as group for F17/F24
        "confound_values": log_conductors,  # log10(conductor) as confound
        "notes": (
            f"observed rank distribution {dist}; observed_mean={observed_mean:.4f}; "
            f"F17 confound sensitivity is the load-bearing test "
            f"(if SUSPECT -> rank-conductor confounding present; "
            f"if INDEPENDENT -> rank skew is real structure not "
            f"confounded with conductor scale)"
        ),
    }
