"""Population-scale A / B / A+B readiness study over the frozen registry.

Directive section 14 asks for YES/NO answers. This produces the rows behind them rather than an
opinion. Segments are taken structurally from committed specimens; nothing here selects, scores,
ranks or interprets a specimen, and no phenotype is read or written.

    python -m proteus.compose.run_ab_readiness [n_pairs]
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from proteus.compose.segments import (CompositionError, ablate, ablation_report,  # noqa: E402
                                      activation_evidence, compose, decompose,
                                      segment_from_instructions, segment_id)
from proteus.foundry.identity import hash_obj  # noqa: E402
from proteus.foundry.probes import DEFAULT_ENSEMBLE, build_probes, run_ensemble  # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from  # noqa: E402

REG = os.path.join(ROOT, "proteus", "integration", "PLAYER_REGISTRY.json")
IW = 4
SEG_INSTR = 2                      # every segment is exactly 2 instructions: same alphabet for all
ENVELOPE = {"n_regs": 8, "tape_words": 256, "code_writable": False,
            "persist": "none", "tick_budget": 256, "out_cap": 4}


def main(n_pairs=200):
    reg = json.load(open(REG, encoding="utf-8"))
    entries = [e for e in reg["entries"]
               if len(e["manifest"]["genome"]) >= SEG_INSTR * IW]
    probes = build_probes(DEFAULT_ENSEMBLE)

    # deterministic pairing, seeded from the registry id so the study replays exactly
    rng = SplitMix64(seed_from("proteus.ab_readiness.v0", reg["registry_id"], SEG_INSTR))

    segs = []
    for e in entries:
        w = e["manifest"]["genome"][:SEG_INSTR * IW]
        segs.append((e["organism_id"], segment_from_instructions(w)))

    stats = Counter()
    ablation_verdicts = Counter()
    activation_verdicts = Counter()
    rows = []

    for _ in range(n_pairs):
        i = rng.randint(0, len(segs) - 1)
        j = rng.randint(0, len(segs) - 1)
        (oa, A), (ob, B) = segs[i], segs[j]
        try:
            cA = compose([("A", A)], ENVELOPE)
            cB = compose([("B", B)], ENVELOPE)
            cAB = compose([("A", A), ("B", B)], ENVELOPE)
        except CompositionError:
            stats["compose_failed"] += 1
            continue
        stats["composed"] += 1

        # exact reconstruction
        try:
            got = {n: segment_id(s) for n, s in decompose(cAB)}
            if got["A"] == segment_id(A) and got["B"] == segment_id(B):
                stats["decompose_exact"] += 1
        except CompositionError:
            stats["decompose_failed"] += 1

        _, hA = run_ensemble(cA["manifest"], probes, DEFAULT_ENSEMBLE)
        _, hB = run_ensemble(cB["manifest"], probes, DEFAULT_ENSEMBLE)
        _, hAB = run_ensemble(cAB["manifest"], probes, DEFAULT_ENSEMBLE)
        if hAB != hA:
            stats["AB_differs_from_A"] += 1
        if hAB != hB:
            stats["AB_differs_from_B"] += 1
        if hAB != hA and hAB != hB:
            stats["AB_differs_from_both"] += 1

        rep = ablation_report(cAB, "A", DEFAULT_ENSEMBLE, probes)
        ablation_verdicts[rep["verdict"]] += 1
        if rep["structural"]["changes_outside_declared_range"] == 0 and \
           rep["structural"]["other_components_byte_identical"]:
            stats["ablation_structurally_exact"] += 1
        if rep["transcript_changed_by_ablation"]:
            stats["ablating_A_changed_transcript"] += 1

        act = activation_evidence(cAB, "A", DEFAULT_ENSEMBLE, probes)
        activation_verdicts[act["verdict"]] += 1
        if act["verdict"] == "ACTIVATED" and not rep["transcript_changed_by_ablation"]:
            stats["A_activated_but_no_marginal_effect"] += 1

        if len(rows) < 3:
            rows.append({"A_from": oa[:12], "B_from": ob[:12],
                         "composition_id_AB": cAB["composition_id"][:16],
                         "organism_id_AB": hash_obj(cAB["manifest"])[:16],
                         "ablate_A_verdict": rep["verdict"],
                         "A_activation": act["verdict"],
                         "AB_differs_from_A": hAB != hA})

    n = stats["composed"]
    out = {
        "registry_id": reg["registry_id"],
        "segment_definition": "first %d instructions of each committed specimen" % SEG_INSTR,
        "envelope": ENVELOPE,
        "ensemble_identity": hash_obj({"cfg": DEFAULT_ENSEMBLE, "probes": probes}),
        "pairs_attempted": n_pairs,
        "counts": dict(sorted(stats.items())),
        "ablation_verdicts": dict(sorted(ablation_verdicts.items())),
        "activation_verdicts": dict(sorted(activation_verdicts.items())),
        "rates": {
            "decompose_exact": _rate(stats["decompose_exact"], n),
            "ablation_structurally_exact": _rate(stats["ablation_structurally_exact"], n),
            "ablation_certified_EXACT": _rate(ablation_verdicts["EXACT"], n),
            "AB_differs_from_both_A_and_B": _rate(stats["AB_differs_from_both"], n),
            "ablating_A_changed_transcript": _rate(stats["ablating_A_changed_transcript"], n),
            "A_activated_but_no_marginal_effect": _rate(
                stats["A_activated_but_no_marginal_effect"], n),
        },
        "example_rows": rows,
        "what_this_is_not": ("No specimen was selected, scored or interpreted. 'A+B differs from "
                             "A' is a transcript inequality on a noise ensemble, not a capability "
                             "claim, and 'ACTIVATED' means instructions executed, nothing more."),
    }
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


def _rate(k, n):
    return None if not n else {"k": k, "n": n, "rate": round(k / n, 4)}


if __name__ == "__main__":
    raise SystemExit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 200))
