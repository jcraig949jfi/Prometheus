"""R7 verification harness — builds F-null against the real D3 pool and runs both layers.

Charon's contract (spec R7, prereg §7 step 5). Run:

    python charon/probe/run_r7_verification.py

Writes `charon/probe/r7_verification_2026-08-16.json` and prints the two layer reports.

SCOPE, stated up front. This discharges R7 for **D3 only**, because D3 is the only stratum with
real residue today: `probe_prepass` does not exist, so D0/D1 have no records, and D2's source
pool is blocked pending Ergon's F1 ruling. R7 must be re-run for D0/D1/D2 once their residue
exists. The machinery is stratum-agnostic; the evidence is not.

F-PROM CONSTRUCTION, and why it is not production's. Production's `select_residue(D3)` is
target-independent and `_order` sorts by ledger id, so head-truncation gives **every task the
same packet** (Charon co-sign §5, condition C5). A classifier test against identical F-prom
packets is not a test — any variation on the F-null side separates the arms trivially, and any
lack of it hides a real tell. So F-prom packets here are built by **seeded stratified draw from
the frozen pool**, which is the C5-corrected sampling. If C5 is declined, this verification does
not transfer and R7 must be re-run against whatever selection ships.
"""

from __future__ import annotations

import json
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ergon.probe.assemble import ResidueRecord, assemble_retrieved  # noqa: E402
from ergon.probe.f_null import (  # noqa: E402
    STRATEGY_BY_STRATUM,
    TOLERANCES,
    build_f_null,
    calibrate_tolerances,
    classifier_auc,
    r7_verdict,
)

POOL = ROOT / "pivot" / "probe_d3_pool_2026-08-16.jsonl"
OUT = ROOT / "charon" / "probe" / "r7_verification_2026-08-16.json"

SEED = 20260816
N_PAIRS = 40
RECORDS_PER_PACKET = 25
#: Build #0 categorical-only (clf 0.575), #1 nearest-neighbour matched (clf 0.662, worse),
#: #2 exchangeable draw. Spec §7 counts REBUILDS of F-NULL against the classifier ceiling.
BUILD_INDEX = 2


def load_pool() -> list[ResidueRecord]:
    """Rebuild `ResidueRecord`s from the frozen pool, mirroring `assemble.load_theseus_rejected`
    body construction exactly so the surface the classifier sees is production's surface."""
    out = []
    for line in POOL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        null_fields = tuple(
            f for f in ("kill_pattern", "kill_vector", "step_trace", "precision_dps", "method")
            if d.get(f) in (None, "", [])
        )
        body = [f"  claim: {d.get('canonical_claim_text', '(not recorded)')}",
                f"  kind: {d.get('claim_kind', '(not recorded)')}",
                f"  kill_pattern: {d.get('kill_pattern') or '(null)'}"]
        if d.get("method"):
            body.append(f"  method: {d['method']}")
        if d.get("step_trace"):
            body.append(f"  trace: {d['step_trace']}")
        out.append(
            ResidueRecord(
                ledger_id=str(d["ledger_id"]),
                seq=int(d["seq"]),
                source=str(d["source"]),
                record_id=str(d["record_id"])[:16],
                body="\n".join(body),
                obstruction_class=d.get("obstruction_class"),
                null_fields=null_fields,
                sampling=str(d.get("sampling", "full-scan")),
            )
        )
    return out


def main() -> int:
    pool = load_pool()
    tau = {}
    for r in pool:
        tau[r.ledger_id] = max(tau.get(r.ledger_id, 0), r.seq)

    # BOTH arms draw from the SAME pool (build #2). Builds #0 and #1 partitioned the pool into
    # halves and matched across them; that is what made F-null a matched copy rather than an
    # exchangeable draw, and it is what the classifier found. At D3, F-prom is not task-linked,
    # so a uniform disjoint draw from one pool is exact exchangeability. See f_null
    # STRATEGY_BY_STRATUM and charon/probe/R7_CONSTRUCTION_2026-08-16.md.
    # Calibrate layer (a) against the same-distribution reference BEFORE testing anything.
    cal = calibrate_tolerances(
        pool, n_records=RECORDS_PER_PACKET, tau=tau, stratum="D3", seed=SEED, reps=200
    )
    calibrated = cal.thresholds
    print("R7(a) tolerance calibration — p95 divergence between two same-pool draws:")
    for d in sorted(calibrated):
        kind, absolute = TOLERANCES[d]
        floor = " <- absolute tolerance is BELOW the noise floor" if absolute < calibrated[d] else ""
        print(f"    {d:<28} p95={calibrated[d]:.4f}  absolute={absolute}{floor}")
    print()

    prom_texts, null_texts, balances, rows = [], [], [], []
    for i in range(N_PAIRS):
        draw = random.Random(SEED + i)
        prom_records = draw.sample(pool, RECORDS_PER_PACKET)
        prom_packet = assemble_retrieved(
            task_uid=f"R7-VERIFY-{i:03d}", stratum="D3", records=prom_records, tau=tau,
            sampling_note="charon R7 verification: seeded stratified draw (C5-corrected)",
        )
        null = build_f_null(
            task_uid=f"R7-VERIFY-{i:03d}", stratum="D3",
            prom_records=prom_records, prom_packet_text=prom_packet.text,
            pool=pool, tau=tau, seed=SEED + i, calibrated=calibrated,
            sampling_note="charon R7 verification: seeded stratified draw (C5-corrected)",
        )
        prom_texts.append(prom_packet.text)
        null_texts.append(null.text)
        balances.append(null.balance)
        rows.append({
            "pair": i,
            "passed": null.balance.passed,
            "failures": null.balance.failures,
            "prom_tokens": prom_packet.header["token_count"],
            "null_tokens": null.packet.header["token_count"],  # type: ignore[attr-defined]
        })

    clf = classifier_auc(prom_texts, null_texts, seed=0)
    verdict = r7_verdict(balances, clf, rebuilds=BUILD_INDEX, calibration=cal)

    n_pass = sum(b.passed for b in balances)
    dim_fail: dict[str, int] = {}
    for b in balances:
        for d in b.failures:
            dim_fail[d] = dim_fail.get(d, 0) + 1

    print(balances[0].render())
    print()
    obs_rate = (N_PAIRS - n_pass) / N_PAIRS
    print(f"R7(a) across {N_PAIRS} pairs — {n_pass}/{N_PAIRS} packets pass every dimension")
    print(f"      family-wise failure rate: observed {obs_rate:.3f} vs calibrated "
          f"{cal.family_failure_rate:.3f} (same-distribution reference, {cal.reps} reps) -> "
          f"{'PASS' if obs_rate <= cal.family_failure_rate else 'FAIL'}")
    print("      note: with 12 dimensions each at p95, a large minority of same-distribution")
    print("      pairs exceed at least one threshold — the rate is the test, not a clean sweep.")
    if dim_fail:
        for d, c in sorted(dim_fail.items(), key=lambda kv: -kv[1]):
            print(f"    {d}: failed in {c}/{N_PAIRS}")
    print()
    print(clf.render())
    print()
    print(f"R7 VERDICT: {verdict}")

    OUT.write_text(json.dumps({
        "seed": SEED,
        "stratum": "D3",
        "scope": "D3 only — probe_prepass absent (D0/D1), D2 blocked pending F1 ruling",
        "n_pairs": N_PAIRS,
        "records_per_packet": RECORDS_PER_PACKET,
        "strategy": STRATEGY_BY_STRATUM["D3"],
        "tolerances_absolute": {k: {"kind": v[0], "value": v[1]} for k, v in TOLERANCES.items()},
        "tolerances_calibrated_p95": calibrated,
        "calibration": {"reps": cal.reps, "percentile": cal.percentile,
                        "family_failure_rate": cal.family_failure_rate},
        "build_index": BUILD_INDEX,
        "layer_a": {"packets_passing_all_dimensions": n_pass,
                    "observed_family_failure_rate": (N_PAIRS - n_pass) / N_PAIRS,
                    "calibrated_family_failure_rate": cal.family_failure_rate,
                    "dimension_failures": dim_fail,
                    "per_pair": rows},
        "layer_b": {"balanced_accuracy": clf.score, "ceiling": clf.ceiling, "folds": clf.folds,
                    "n_prom": clf.n_prom, "n_null": clf.n_null, "passed": clf.passed},
        "verdict": verdict,
    }, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0 if verdict == "R7-PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
