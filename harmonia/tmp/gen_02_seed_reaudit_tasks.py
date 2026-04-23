"""gen_02 — seed re-audit tasks under the null family.

One task per eligible non-calibration +1/+2 cell. Claim class is
inferred per F-ID via a small table; cells with no-null-applies (Class 5
or scorer-bookkeeping) are skipped.

Expected ~33 seeds (current non-calibration +1/+2 count).
"""
import os
os.environ.setdefault("PYTHONPATH", ".")
os.environ.setdefault("AGORA_REDIS_HOST", "192.168.1.176")
os.environ.setdefault("AGORA_REDIS_PASSWORD", "prometheus")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from agora.tensor import features, projections, feature_meta, resolve_row
from agora.helpers import seed_task, canonical_instance_name


# Claim-class assignment per F-ID, derived from null_protocol_v1.md §Claim classes.
# Class 5 F-IDs are skipped (theorem/identity — no null applies).
CLAIM_CLASS_MAP = {
    # Class 1 — moment/ratio under conductor scaling
    "F011": 1,
    # Class 2 — rank-slope interactions
    "F013": 2,
    "F041a": 2,
    # Class 3 — stratum-uniform
    "F015": 3,
    "F042": 1,   # calibration-refinement, treat as Class 1 default
    # Class 4 — construction-biased
    "F044": 4,
    "F045": 3,   # multiple-testing caveat; default Class 3
    # Class 5 — algebraic identity (skip re-audit under nonparametric family)
    "F001": 5, "F002": 5, "F003": 5, "F004": 5, "F005": 5,
    "F008": 5, "F009": 5, "F014": 5, "F043": 5,
    # Scorer-bookkeeping — skip
    "F022": "scorer_bookkeeping",
}


DEFAULT_CLAIM_CLASS = 1   # Most surviving live_specimens are Class 1; update per-case.


def main():
    worker = canonical_instance_name("Harmonia_M2_sessionA")
    feats = features()
    eligible = []
    for f in feats:
        m = feature_meta(f)
        tier = m.get("tier", "")
        if tier == "calibration":
            continue
        row = resolve_row(f)
        for p, v in row.items():
            if v in (1, 2):
                eligible.append({"F": f, "P": p, "v": v, "tier": tier,
                                 "label": m.get("label", "")})

    seeded = 0
    skipped_class_5 = 0
    skipped_scorer_bk = 0
    for cell in eligible:
        f = cell["F"]
        claim_class = CLAIM_CLASS_MAP.get(f, DEFAULT_CLAIM_CLASS)

        if claim_class == 5:
            skipped_class_5 += 1
            continue
        if claim_class == "scorer_bookkeeping":
            skipped_scorer_bk += 1
            continue

        task_id = f"reaudit_null_family_{f}_{cell['P']}_20260420"
        goal = (
            f"Rerun {f}:{cell['P']} (current value={cell['v']}) under gen_02 "
            f"null family; produce SIGNATURE@v2 record."
        )
        acceptance = [
            "family_result computed for every applicable null per null_protocol_v1 Class "
            + str(claim_class),
            "SIGNATURE@v2 record with family_verdict and discordance_flag",
            "commit citation in record",
            "Pattern 21 review flagged if discordance_flag is true",
        ]
        composes_with = ["gen_02", "gen_05", "gen_06"]
        if claim_class == 4:
            caveats = [
                "Class 4: NULL_BSWCD/PLAIN/BOOT are N/A; NULL_FRAME required.",
                "frame resampler for F044's lmfdb_r4 frame NOT yet shipped — "
                "expect frame_spec_required_but_not_supplied until that lands.",
            ]
        else:
            caveats = [
                "claim class derived from null_protocol_v1.md §Claim classes; "
                "refine per-cell if the claim sentence doesn't match the default.",
                "record stratifier choice explicitly in SIGNATURE@v2.null_family_result",
            ]

        try:
            seed_task(
                task_id=task_id,
                task_type="reaudit_null_family",
                spec="docs/prompts/gen_02_null_family.md",
                goal=goal,
                acceptance=acceptance,
                priority=-0.8,
                composes_with=composes_with,
                epistemic_caveats=caveats,
                required_qualification="harmonia_session",
                posted_by=worker,
                extra={
                    "feature_id": f,
                    "projection_id": cell["P"],
                    "current_value": cell["v"],
                    "feature_tier": cell["tier"],
                    "claim_class": claim_class,
                },
            )
            seeded += 1
        except Exception as e:
            print(f"FAILED: {task_id} — {e}")

    print(f"Eligible cells: {len(eligible)}")
    print(f"Seeded:         {seeded}")
    print(f"Skipped (Class 5):            {skipped_class_5}")
    print(f"Skipped (scorer-bookkeeping): {skipped_scorer_bk}")


if __name__ == "__main__":
    main()
