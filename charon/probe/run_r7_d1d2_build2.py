"""F-null build #2 for D1/D2 — measuring BOTH horns of the bind rather than asserting it.

Charon's contract (spec R7). Run:

    python charon/probe/run_r7_d1d2_build2.py

Build #1 (Ergon, `cd2254d2`) drew D1/D2 nulls from the whole pre-pass pool with surface
matching, so the null crossed domains and the classifier separated on topic vocabulary:
D1 0.967, D2 0.917. His diagnosis was that a domain-relational stratum cannot take the D0
strategy. This harness tests that diagnosis instead of inheriting it — and tests the horn he
did not name.

THE BIND, stated as a dilemma with both horns measured:

  * Break the relation  -> the null changes domain -> separable on topic vocabulary.
  * Preserve the topic  -> the null is drawn from F-prom's OWN relation -> it is not a null.

So each stratum is built twice, and the second build is the one nobody would ship — it exists
to demonstrate that passing R7 is NECESSARY AND NOT SUFFICIENT. A same-relation "null" should
pass both R7 layers at chance while measuring nothing at all, which is why this session
proposes R7 layer (c): `relation_overlap`, the fraction of the null that would have been
eligible as F-prom for the same target.

  D1-topic          cross-domain                          (build #1's construction)
  D1-same-relation  same domain, different task           (preserves D1's relation)
  D2-mechanism      cross-domain AND mechanism-disjoint   (the real relation break)
  D2-same-relation  cross-domain WITH a shared tag        (preserves D2's relation)

D0 is re-measured unchanged as the positive control: its F-prom is selected by TASK IDENTITY,
which is the only stratum where "wrong problem" is well defined.
"""

from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ergon.probe.assemble import (  # noqa: E402
    DOMAIN_MECHANISM_TAGS,
    assemble_retrieved,
    load_prepass,
    select_residue,
)
from ergon.probe.f_null import (  # noqa: E402
    CLASSIFIER_CEILING,
    R7_C_MAX_OVERLAP,
    build_f_null,
    classifier_auc,
    relation_break_pool,
    relation_overlap,
)

LEDGER = ROOT / "ergon" / "probe" / "ledgers" / "probe_prepass.jsonl"
MANIFEST_DIR = ROOT / "ergon" / "probe" / "manifests"
OUT = ROOT / "charon" / "probe" / "r7_d1d2_build2_2026-08-16.json"

SEED = 20260816
N_PAIRS = 30
RECORDS_PER_PACKET = 8

MODES = [
    ("D0", "D0-identity", "positive control — F-prom is selected by task identity"),
    ("D1", "D1-topic", "break the relation: cross-domain (build #1)"),
    ("D1", "D1-same-relation", "preserve topic: same domain, different task"),
    ("D2", "D2-mechanism", "break the relation: cross-domain AND mechanism-disjoint"),
    ("D2", "D2-same-relation", "preserve the relation: cross-domain WITH a shared tag"),
]


def main() -> int:
    pool = load_prepass(LEDGER)
    manifest_path = sorted(MANIFEST_DIR.glob("manifest_L1_*.jsonl"))[-1]
    rows = [json.loads(x) for x in manifest_path.read_text(encoding="utf-8").splitlines()]
    gen_of = {r["uid"]: r["domain"] for r in rows}
    tau = {"probe_prepass": 10_000}

    print(f"[build#2] pre-pass pool {len(pool)} rep-1 records · manifest {manifest_path.name}\n")
    results = []

    for stratum, mode, note in MODES:
        prom_texts, null_texts, overlaps, empties = [], [], [], 0

        for i, row in enumerate(rows[:N_PAIRS]):
            recs = select_residue(pool, stratum=stratum, target_uid=row["uid"],
                                  target_domain=row["domain"], generator_of=gen_of)
            if not recs:
                continue
            recs = recs[:RECORDS_PER_PACKET]
            cand = relation_break_pool(
                pool, mode, target_uid=row["uid"], target_domain=row["domain"],
                domain_tags=DOMAIN_MECHANISM_TAGS,
            )
            if len(cand) < len(recs):
                empties += 1
                continue
            prom = assemble_retrieved(task_uid=row["uid"], stratum=stratum, records=recs, tau=tau)
            null = build_f_null(task_uid=row["uid"], stratum=stratum, prom_records=recs,
                                prom_packet_text=prom.text, pool=cand, tau=tau, seed=SEED + i)
            prom_texts.append(prom.text)
            null_texts.append(null.text)
            overlaps.append(relation_overlap(
                null.records, stratum=stratum, target_uid=row["uid"],
                target_domain=row["domain"], domain_tags=DOMAIN_MECHANISM_TAGS,
            ))

        if not prom_texts:
            print(f"  {mode:<20} NOT-RUN — candidate pool too small on every task "
                  f"({empties} targets starved)")
            results.append({"stratum": stratum, "mode": mode, "note": note,
                            "verdict": "NOT-RUN-CANDIDATE-POOL-EMPTY", "starved_targets": empties})
            continue

        clf = classifier_auc(prom_texts, null_texts, seed=SEED)
        ov = sum(overlaps) / len(overlaps)
        layer_b = clf.passed
        layer_c = ov <= R7_C_MAX_OVERLAP
        verdict = ("R7-PASS" if (layer_b and layer_c) else
                   "NOT-A-CONTROL-SAME-RELATION" if layer_b and not layer_c else
                   "R7-FAIL-SEPARABLE")
        print(f"  {mode:<20} n={len(prom_texts):<3} clf={clf.score:.3f} "
              f"(<= {CLASSIFIER_CEILING})  relation_overlap={ov:.3f}  "
              f"starved={empties:<3} -> {verdict}")
        results.append({
            "stratum": stratum, "mode": mode, "note": note, "n_pairs": len(prom_texts),
            "classifier": round(float(clf.score), 4), "ceiling": CLASSIFIER_CEILING,
            "layer_b_pass": layer_b, "relation_overlap": round(ov, 4),
            "layer_c_pass": layer_c, "starved_targets": empties, "verdict": verdict,
        })

    OUT.write_text(json.dumps({
        "seed": SEED, "n_pairs_requested": N_PAIRS, "records_per_packet": RECORDS_PER_PACKET,
        "ledger": LEDGER.name, "manifest": manifest_path.name,
        "r7_c_max_overlap": R7_C_MAX_OVERLAP, "results": results,
    }, indent=2), encoding="utf-8")
    print(f"\n[build#2] -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
