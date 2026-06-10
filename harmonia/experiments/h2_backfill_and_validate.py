"""Proposal E — h2 opaque-kill backfill + validation harness.

Pre-registration (binding decision rules, read first):
  D:\\Prometheus\\harmonia\\experiments\\h2_info_recovery_prereg.md

Three deliverables, mirroring the proposal's §3:

  §3.1 production emission — the live corpus is ABSENT on this host
       (theseus/corpus/ empty; daemon paused since 2026-05-29). Emission is
       instead verified by driving the production generator class directly:
       every kill emitted by H2TriangulationProtocolGenerator.next() must
       carry the structured pattern (refactor 487b611f).

  §3.2 backfill — backfill_structured_pattern(payload, step_trace) is the
       pure local rewrite that re-derives the structured label from a legacy
       flat row's retained payload. Schema archaeology (git 487b611f~1)
       proved the legacy payload is identical to the current one, so this
       function IS the historical backfill — validated here byte-for-byte
       against production emission (Q5: >= 5,000 kills, 100% match required).

  §3.3 signal validation lives in h2_info_recovery_law.py (the law harness);
       this file also computes the Q1 concentration stats and the frozen-gate
       costume_check on the emission-simulated kills.

Run:  python harmonia/experiments/h2_backfill_and_validate.py [n_attempts_per_seed]
Output: harmonia/experiments/_h2_backfill_validate_results.json (per-cell flush;
        no shell redirection — feedback_background_output_capture)
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from theseus.emit.record_schema import TheseusRecord, Verdict  # noqa: E402
from theseus.generators.h2_triangulation_protocol import (  # noqa: E402
    H2TriangulationProtocolGenerator,
    METHOD_VARIANTS,
)
from theseus.generators.a1_catalog_cross_product import (  # noqa: E402
    KNOT_INTEGER_INVARIANTS,
    EC_INTEGER_INVARIANTS,
)

# baseline_costume is not importable as a top-level module name from here;
# load it explicitly (py3.14 requires sys.modules registration pre-exec).
import importlib.util  # noqa: E402

_bc_spec = importlib.util.spec_from_file_location(
    "baseline_costume", _REPO / "harmonia" / "primitives" / "baseline_costume.py")
baseline_costume = importlib.util.module_from_spec(_bc_spec)
sys.modules["baseline_costume"] = baseline_costume
_bc_spec.loader.exec_module(baseline_costume)

SEEDS = (20260610, 20260611, 20260612)  # pre-registered; do not redraw
RESULTS_PATH = Path(__file__).parent / "_h2_backfill_validate_results.json"


# ---------------------------------------------------------------------------
# §3.2 — the backfill function (pure: payload -> structured kill_pattern)
# ---------------------------------------------------------------------------
def backfill_structured_pattern(payload: dict, step_trace=None):
    """Re-derive the post-refactor structured kill_pattern from a legacy flat
    row's retained claim_payload (+ optional step_trace).

    Returns the structured pattern string, or None if the row is not a
    triangulated kill / lacks the re-derivation fields.

    PRODUCTION-PARITY NOTE: when a method variant was skipped (r2 None),
    production code (h2_triangulation_protocol.py, REJECTED branch) aligns
    child_verdicts[i] to METHOD_VARIANTS[i] — an index-shift misattribution.
    For byte-for-byte parity we replicate that alignment when no step_trace
    is available. When step_trace IS available, the step_method names give
    the TRUE alignment; production order == true order whenever no method
    was skipped (the overwhelmingly common case: skip requires < 5 catalog
    values in 4n draws).
    """
    verdicts = payload.get("method_verdicts")
    ki = payload.get("knot_invariant")
    ei = payload.get("ec_invariant")
    if not verdicts or ki is None or ei is None:
        return None
    n = len(verdicts)
    if n < 2:
        return None
    counts = Counter(verdicts)
    top_v, top_n = counts.most_common(1)[0]
    if top_n / n < 2 / 3 or top_v != Verdict.REJECTED.value:
        return None  # not a triangulated kill

    agreement_class = "unanimous" if top_n == n else "majority"

    # Method-name alignment (see PRODUCTION-PARITY NOTE).
    if step_trace and len(step_trace) == n:
        names = [
            (st.get("step_method") or "").replace("polyfit_", "")
            for st in step_trace
        ]
        if not all(names):
            names = [METHOD_VARIANTS[i][0] for i in range(n)]
    else:
        names = [METHOD_VARIANTS[i][0] for i in range(n)]

    rej_methods = sorted({
        names[i] for i, v in enumerate(verdicts)
        if v == Verdict.REJECTED.value
    })
    method_tag = "_".join(m[0] for m in rej_methods)
    return (
        f"h2_triangulated_{agreement_class}_"
        f"{ki}_{ei}_methods_{method_tag}_rejected"
    )


# ---------------------------------------------------------------------------
# Parent injection — drive the PRODUCTION generator without a corpus
# ---------------------------------------------------------------------------
def make_parent(ki: str, ei: str, idx: int) -> TheseusRecord:
    canonical = f"synthetic_inconclusive_parent[{ki}|{ei}|{idx}]"
    return TheseusRecord(
        record_id=TheseusRecord.compute_record_id(
            canonical_claim_text=canonical, generator_id="a4"),
        generator_id="a4",
        batch_id="harmonia-E-h2-validate",
        emitted_at=datetime.now(timezone.utc).isoformat(),
        claim_kind="catalog_relation",
        claim_payload={"knot_invariant": ki, "ec_invariant": ei},
        canonical_claim_text=canonical,
        verdict=Verdict.INCONCLUSIVE.value,
    )


def run_emission(seed: int, n_attempts: int):
    """Drive production .next() over a uniform 24-pair parent pool."""
    gen = H2TriangulationProtocolGenerator(
        batch_id=f"harmonia-E-validate-{seed}", seed=seed)
    gen._loaded = True  # skip the (empty) corpus scan
    gen._inconclusive_parents = [
        make_parent(ki, ei, 0)
        for ki in KNOT_INTEGER_INVARIANTS
        for ei in EC_INTEGER_INVARIANTS
    ]
    kills, non_kills, emitted = [], 0, 0
    for _ in range(n_attempts):
        r = gen.next()
        if r is None:
            continue
        emitted += 1
        if r.verdict == Verdict.REJECTED.value and r.kill_pattern:
            kills.append(r)
        else:
            non_kills += 1
    return kills, non_kills, emitted


# ---------------------------------------------------------------------------
# Q1 concentration + label-component split
# ---------------------------------------------------------------------------
def split_label(kp: str):
    """h2_triangulated_{agr}_{ki}_{ei}_methods_{tag}_rejected -> components.
    ki/ei contain underscores, so parse from both ends + the methods anchor."""
    assert kp.startswith("h2_triangulated_") and kp.endswith("_rejected")
    body = kp[len("h2_triangulated_"):-len("_rejected")]
    agr, rest = body.split("_", 1)
    pair_part, tag = rest.rsplit("_methods_", 1)
    return agr, pair_part, tag


def shannon_entropy(counter: Counter) -> float:
    tot = sum(counter.values())
    if tot == 0:
        return 0.0
    return -sum((c / tot) * math.log2(c / tot) for c in counter.values() if c)


def concentration_stats(kills):
    full = Counter(r.kill_pattern for r in kills)
    agr_c, pair_c, tag_c = Counter(), Counter(), Counter()
    for r in kills:
        agr, pair, tag = split_label(r.kill_pattern)
        agr_c[agr] += 1
        pair_c[pair] += 1
        tag_c[tag] += 1
    def top1(c):
        return (c.most_common(1)[0][0], c.most_common(1)[0][1] / sum(c.values())) if c else (None, 0.0)
    return {
        "n_kills": len(kills),
        "full_label": {"distinct": len(full), "top1": top1(full), "H_bits": shannon_entropy(full)},
        "agreement": {"distinct": len(agr_c), "top1": top1(agr_c), "H_bits": shannon_entropy(agr_c)},
        "pair": {"distinct": len(pair_c), "top1": top1(pair_c), "H_bits": shannon_entropy(pair_c)},
        "tag": {"distinct": len(tag_c), "top1": top1(tag_c), "H_bits": shannon_entropy(tag_c),
                 "distribution": dict(tag_c.most_common())},
    }


# ---------------------------------------------------------------------------
# Q4 — frozen gate
# ---------------------------------------------------------------------------
def run_costume_check(kills):
    """Claim = {record -> tag}; key = pair. Does the tag refinement beat the
    cheap baselines, per the FROZEN contract?"""
    rows = []
    for r in kills:
        agr, pair, tag = split_label(r.kill_pattern)
        rows.append({"rec": r.record_id, "pair": pair, "tag": tag})
    claim = {row["rec"]: row["tag"] for row in rows}
    # key_fn maps a row to the key space of the claim (record id); the
    # baselines need the PAIR-level structure, so we give them pair as key
    # and evaluate the claim at pair level too: claim_pair = majority tag the
    # emitted records actually carry per pair vs baselines' per-pair label.
    pair_claim: dict = {}
    by_pair = defaultdict(Counter)
    for row in rows:
        by_pair[row["pair"]][row["tag"]] += 1
    for pair, c in by_pair.items():
        pair_claim[pair] = c.most_common(1)[0][0]
    v = baseline_costume.costume_check(
        pair_claim, rows,
        key_fn=lambda r: r["pair"],
        label_fn=lambda r: r["tag"],
        signature_fn=lambda r: r["tag"],  # co-occurrence context = shared tag
        seed=0,
    )
    return {
        "verdict": v.verdict,
        "headline": v.headline,
        "z_vs_null": v.z_vs_null,
        "per_baseline": {b.name: {"agreement": b.agreement_rate,
                                   "ties": b.ties_claim} for b in v.per_baseline},
        "n_claim_keys": v.n_claim_keys,
    }


# ---------------------------------------------------------------------------
def main():
    n_attempts = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    out = {
        "registered_at": "2026-06-10",
        "prereg": "h2_info_recovery_prereg.md",
        "corpus_scan": {
            "host_corpus_present": False,
            "note": ("theseus/corpus/ empty on this host; daemon paused since "
                      "2026-05-29 (BATCH_LOG Fire #234 LOOP PAUSED). "
                      "production_emission_rate over the live corpus: N/A here; "
                      "emission verified by driving the production class."),
        },
        "schema_archaeology": {
            "legacy_payload_identical": True,
            "evidence": "git show 487b611f~1 — payload fields byte-identical "
                         "to current; flat label withheld what payload retained",
            "backfill_recoverable_fraction_by_schema": 1.0,
        },
        "seeds": list(SEEDS),
        "per_seed": {},
    }
    grand_kills = []
    parity_total, parity_match, mismatches = 0, 0, []

    for seed in SEEDS:
        kills, non_kills, emitted = run_emission(seed, n_attempts)
        grand_kills.extend(kills)
        # Q5 — byte-for-byte parity: backfill(payload) == production label
        for r in kills:
            parity_total += 1
            bf = backfill_structured_pattern(r.claim_payload, r.step_trace)
            if bf == r.kill_pattern:
                parity_match += 1
            elif len(mismatches) < 10:
                mismatches.append({"prod": r.kill_pattern, "backfill": bf})
        out["per_seed"][str(seed)] = {
            "emitted": emitted, "kills": len(kills), "non_kills": non_kills,
            "kill_rate": len(kills) / emitted if emitted else 0.0,
            "structured_fraction": (
                sum(1 for r in kills if r.kill_pattern.startswith("h2_triangulated_"))
                / len(kills) if kills else 0.0),
            "concentration": concentration_stats(kills),
        }
        RESULTS_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"[seed {seed}] emitted={emitted} kills={len(kills)} "
              f"kill_rate={len(kills)/max(emitted,1):.3f}", flush=True)

    out["q5_backfill_parity"] = {
        "n": parity_total, "match": parity_match,
        "match_rate": parity_match / parity_total if parity_total else 0.0,
        "mismatches_sample": mismatches,
        "PASS": parity_total >= 5000 and parity_match == parity_total,
    }
    out["pooled_concentration"] = concentration_stats(grand_kills)
    out["q4_costume_check"] = run_costume_check(grand_kills)
    RESULTS_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("\n=== Q5 backfill parity ===", flush=True)
    print(json.dumps(out["q5_backfill_parity"], indent=2)[:800], flush=True)
    print("\n=== pooled concentration ===", flush=True)
    print(json.dumps(out["pooled_concentration"], indent=2), flush=True)
    print("\n=== Q4 frozen gate ===", flush=True)
    print(json.dumps(out["q4_costume_check"], indent=2), flush=True)
    print(f"\nresults -> {RESULTS_PATH}", flush=True)


if __name__ == "__main__":
    main()
