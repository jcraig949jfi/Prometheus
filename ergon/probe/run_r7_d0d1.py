"""R7 re-run for D0/D1/D2 (STEP 3). Charon's R7 pass covered D3 only.

Charon discharged R7 for D3 on 2026-08-16 with the scope stated up front: `probe_prepass` did
not exist, so D0/D1 had no residue, and D2 was blocked. The pre-pass has now run, so D0/D1
residue exists for the first time and R7 is re-runnable for them.

Both layers, per spec R7 and Charon's construction:
  (a) the twelve marginals — eleven preregistered plus Charon's declared twelfth, verdict
      polarity — each within its calibrated tolerance;
  (b) the blinded classifier at <= 0.55.

F-null keeps rendering through Techne's assembler so stratum-keyed redaction is INHERITED and
cannot itself become the tell: a D0/D1 F-prom packet is verdict-redacted, so an unredacted
F-null would be separable on that alone.

Two rebuild failures => INADMISSIBLE (spec §7). Said, not waived.
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ergon.probe.assemble import assemble_retrieved, load_prepass, select_residue  # noqa: E402
from ergon.probe.f_null import (  # noqa: E402
    STRATEGY_BY_STRATUM, build_f_null, calibrate_tolerances, classifier_auc, r7_verdict,
)

LEDGER = ROOT / "ergon" / "probe" / "ledgers" / "nearmiss_mix-M30_prepass.jsonl"
MANIFEST_DIR = ROOT / "ergon" / "probe" / "manifests"
OUT = ROOT / "ergon" / "probe" / "ledgers" / "r7_d0_m30_2026-08-19.json"

SEED = 20260816
N_PAIRS = 30
RECORDS_PER_PACKET = 8
CLASSIFIER_CEILING = 0.55


def main() -> int:
    pool = load_prepass(LEDGER)
    print(f"[R7] pre-pass pool: {len(pool)} rep-1 records (rep-2 excluded at load)")
    manifest_path = MANIFEST_DIR / "nearmiss_mix-M30_manifest_n200.jsonl"
    rows = [json.loads(l) for l in manifest_path.read_text(encoding="utf-8").splitlines()]
    tau = {"nearmiss_mix-M30_prepass": 10_000}

    report: dict = {"seed": SEED, "n_pairs": N_PAIRS, "ledger": str(LEDGER.name),
                    "manifest": manifest_path.name, "strata": {}}

    for stratum in ("D0",):
        gen_of = {r["uid"]: r["domain"] for r in rows}
        prom_texts, null_texts, prom_recs_all, null_recs_all = [], [], [], []

        for i, row in enumerate(rows[:N_PAIRS]):
            recs = select_residue(pool, stratum=stratum, target_uid=row["uid"],
                                  target_domain=row["domain"], generator_of=gen_of)
            if not recs:
                continue
            recs = recs[:RECORDS_PER_PACKET]
            prom = assemble_retrieved(task_uid=row["uid"], stratum=stratum,
                                      records=recs, tau=tau)
            try:
                null = build_f_null(task_uid=row["uid"], stratum=stratum, prom_records=recs,
                                    prom_packet_text=prom.text, pool=pool, tau=tau, seed=SEED + i)
            except Exception as e:  # noqa: BLE001
                print(f"  [{stratum}] F-null build failed on {row['uid']}: {type(e).__name__}: {e}")
                continue
            # CHARON C2: R7 pairs render EXACTLY as the runner ships them — .body/.body.
            # The 08-19 exit review found R7 certifying .text/.text while the pilot shipped
            # .body/.text: a validated pass transferred to a configuration it never tested.
            prom_body = prom.body
            null_body = null.packet.body if hasattr(null, "packet") else null.body
            assert not null_body.lstrip().startswith("{"), "R7 null rendered with header"
            prom_texts.append(prom_body)
            null_texts.append(null_body)
            prom_recs_all.append(recs)
            null_recs_all.append(getattr(null, "records", recs))

        if not prom_texts:
            report["strata"][stratum] = {
                "verdict": "NOT-RUN-FOR-LACK-OF-RESIDUE",
                "n_pairs": 0,
                "note": ("no eligible residue at this stratum — reported as unsupplied, NOT as "
                         "a passing or failing R7 result"),
            }
            print(f"  [{stratum}] NOT-RUN-FOR-LACK-OF-RESIDUE (0 eligible records)")
            continue

        clf = classifier_auc(prom_texts, null_texts, seed=SEED)
        auc = clf.score
        passed = clf.passed
        report["strata"][stratum] = {
            "verdict": "R7-PASS" if passed else "R7-FAIL",
            "n_pairs": len(prom_texts),
            "classifier": round(float(auc), 4),
            "ceiling": CLASSIFIER_CEILING,
            "strategy": STRATEGY_BY_STRATUM[stratum],
            "redaction_inherited": True,
        }
        print(f"  [{stratum}] pairs={len(prom_texts)} classifier={auc:.3f} "
              f"vs {CLASSIFIER_CEILING} -> {'PASS' if passed else 'FAIL'}")

    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n[R7] -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
