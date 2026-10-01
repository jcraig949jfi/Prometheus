"""Class (f): single-seed certificates.

Incidents: W2-16 -- CVT-R (Artemis certificate) was recorded on ONE seed per genome. Reseeding 4x: q1_competent:19 and
:54 were recorded as FAIL and pass 4/4 reseeds; x_p2_bridge:5 and c_zero_specific:4 were recorded as PASS and pass
0/4. W2-31 flagged "CVT-R counts (single seed)" as moderate-confidence only; W2-36 audits CVT-R over 8 reseeds.

``check_certificate_seeds(units)`` with ``units = {unit: {"record": bool|None, "reseeds": [bool, ...]}}``:

Verdicts
    SINGLE_SEED       no unit has any reseed: every certificate verdict rests on one seed (unreplicated)
    SEED_UNSTABLE     some unit's recorded verdict disagrees with its reseed majority, or its reseed agreement is
                      below `min_agreement`: the one-seed verdict does not represent the genome
    OK                every unit has >= `min_seeds` total seeds and its record agrees with a stable majority
    NOT_VERIFIED      no units, or units with reseeds but fewer than `min_seeds` in total (cannot judge stability)
"""
from __future__ import annotations

from typing import Dict, List

from . import CheckResult, NOT_VERIFIED, OK

NAME = "certificate_seeds"


def check_certificate_seeds(units: Dict[str, Dict], min_seeds: int = 4, min_agreement: float = 0.75) -> CheckResult:
    if not units:
        return CheckResult(NAME, NOT_VERIFIED, "no certificate units supplied")
    rows: List[Dict] = []
    for u, d in units.items():
        rec = d.get("record")
        rs = [bool(x) for x in (d.get("reseeds") or [])]
        rows.append({"unit": u, "record": rec, "n_reseeds": len(rs), "reseed_pass": sum(rs)})
    if all(r["n_reseeds"] == 0 for r in rows):
        return CheckResult(NAME, "SINGLE_SEED",
                           "all %d certificate verdicts rest on a single seed: report an acceptance probability over "
                           ">= %d reseeds" % (len(rows), min_seeds), {"units": rows})
    bad, thin = [], []
    for r in rows:
        n = r["n_reseeds"]
        total = n + (r["record"] is not None)
        if total < min_seeds:
            thin.append(r["unit"])
            continue
        frac = r["reseed_pass"] / n if n else None
        maj = None if frac is None or frac == 0.5 else frac > 0.5
        agree = max(frac, 1 - frac) if frac is not None else None
        r.update({"reseed_majority": maj, "agreement": agree})
        if (r["record"] is not None and maj is not None and bool(r["record"]) != maj) or \
                (agree is not None and agree < min_agreement) or maj is None:
            bad.append(r)
    details = {"units": rows, "thin_units": thin, "min_seeds": min_seeds, "min_agreement": min_agreement}
    if bad:
        return CheckResult(NAME, "SEED_UNSTABLE",
                           "%d/%d units: the recorded single-seed verdict disagrees with the reseed majority or the "
                           "reseeds disagree among themselves" % (len(bad), len(rows)), details, bad)
    if thin:
        return CheckResult(NAME, NOT_VERIFIED, "%d units have < %d seeds: stability not assessable" % (len(thin), min_seeds),
                           details)
    return CheckResult(NAME, OK, "every unit's verdict is stable across >= %d seeds" % min_seeds, details)
