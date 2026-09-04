"""Is the measurement surface able to SEE a composition at all?

run_ab_readiness found A+B never differs from BOTH parents (0/200). That is either a fact about
composition (B1: concatenation genuinely adds nothing) or a fact about the instrument (B2: the
probe transcript is degenerate, so nothing can differ from anything). Directive section 9 makes
this Proteus's problem, because the raw observable is Proteus's to expose.

The discriminator is the FLOOR: how much of the transcript space is occupied at all. If almost
every player emits the same empty transcript, then "A+B == A" is a statement about the probe
ensemble and carries no information about composition.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from proteus.compose.segments import compose, segment_from_instructions  # noqa: E402
from proteus.foundry.identity import hash_obj  # noqa: E402
from proteus.foundry.probes import DEFAULT_ENSEMBLE, build_probes, run_ensemble  # noqa: E402

REG = os.path.join(ROOT, "proteus", "integration", "PLAYER_REGISTRY.json")
IW = 4
ENVELOPE = {"n_regs": 8, "tape_words": 256, "code_writable": False,
            "persist": "none", "tick_budget": 256, "out_cap": 4}


def transcript_facts(ts):
    """Reduce a transcript to the things that could carry a signal."""
    n_vals = 0
    statuses = Counter()
    for probe in ts:
        for outs, status in probe:
            statuses[status] += 1
            for ch in outs:
                n_vals += len(ch)
    return n_vals, statuses


def main(seg_instr=2):
    reg = json.load(open(REG, encoding="utf-8"))
    probes = build_probes(DEFAULT_ENSEMBLE)

    classes = Counter()
    emitted_any = 0
    total_values = 0
    status_totals = Counter()
    per_player = []

    for e in reg["entries"]:
        g = e["manifest"]["genome"]
        if len(g) < seg_instr * IW:
            continue
        seg = segment_from_instructions(g[:seg_instr * IW])
        c = compose([("A", seg)], ENVELOPE)
        ts, h = run_ensemble(c["manifest"], probes, DEFAULT_ENSEMBLE)
        n_vals, statuses = transcript_facts(ts)
        classes[h] += 1
        status_totals.update(statuses)
        total_values += n_vals
        if n_vals > 0:
            emitted_any += 1
        per_player.append(n_vals)

    n = len(per_player)

    # the same measurement on the WHOLE committed specimens, not the 2-instruction segments,
    # so the degeneracy can be attributed to segment size or to the ensemble
    full_classes = Counter()
    full_emitted = 0
    for e in reg["entries"]:
        ts, h = run_ensemble(e["manifest"], probes, DEFAULT_ENSEMBLE)
        n_vals, _ = transcript_facts(ts)
        full_classes[h] += 1
        if n_vals > 0:
            full_emitted += 1

    out = {
        "ensemble_identity": hash_obj({"cfg": DEFAULT_ENSEMBLE, "probes": probes}),
        "segment_players": {
            "segment_instructions": seg_instr,
            "players": n,
            "distinct_transcript_classes": len(classes),
            "largest_class_share": round(max(classes.values()) / n, 4) if n else None,
            "players_emitting_at_least_one_value": emitted_any,
            "total_output_values_across_all_players_and_probes": total_values,
            "status_counts": dict(status_totals),
        },
        "full_specimens": {
            "players": len(reg["entries"]),
            "distinct_transcript_classes": len(full_classes),
            "largest_class_share": round(max(full_classes.values()) / len(reg["entries"]), 4),
            "players_emitting_at_least_one_value": full_emitted,
        },
        "floor_note": ("If players_emitting_at_least_one_value is ~0 the transcript carries only "
                       "the per-tick status word, so 'A+B == A' is a property of the instrument "
                       "and NOT evidence about composition."),
    }
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 2))
