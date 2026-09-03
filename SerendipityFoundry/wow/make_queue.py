"""Generate WOW_ADMISSION_QUEUE.jsonl from the archaeology.

Every entry is a NOMINATION. None is certified. The verdict-entropy harness
cannot run yet (canonical reference sampler and context family for this
substrate do not exist), so every entry carries PENDING_ENTROPY_VALIDATION
and the strongest permitted label is SEALED_TEST_WORTHY_PENDING_VALIDATION.

The queue opens with a CALIBRATION TRANCHE, per adversarial review: the
first rights buy knowledge about the apparatus and the corpus->sealed
transfer function, not about phenomena. It includes an adversarial sham
whose registered prediction is its own death and whose survival triggers a
pre-registered program abort.
"""
from __future__ import annotations

import json
import sys

import boundary as B

PRE = B.PRE_CORPUS
BCN = B.BEACON

# Null paths are declared PreCorpusConstant/BeaconDerived ONLY. Any element
# fitted to the corpus would void the 1/K bound (see boundary.py).
CLEAN_NULL = {f: PRE for f in B.NULL_PATH_FIELDS}
CLEAN_NULL["context_rule"] = BCN
CLEAN_NULL["tie_rule"] = BCN

CANDIDATES = [
 {
  "candidate_id": "WOW-C-001",
  "tranche": "CALIBRATION",
  "claim": "ADVERSARIAL SHAM. A genotype drawn from the reproductively "
           "sterile 401-700 byte band (327 artifacts; used as a mutation "
           "parent exactly zero times in 40,796 lineage edges) confers NO "
           "advantage over canonical reference draws.",
  "sealed_prediction": "Under beacon-derived contexts, the sham candidate's "
      "conditional rank distribution is uniform: its wealth process does NOT "
      "reach K. THE REGISTERED PREDICTION IS THIS CANDIDATE'S OWN DEATH.",
  "if_it_survives": "PRE-REGISTERED PROGRAM ABORT. Survival is evidence the "
      "apparatus is broken (beacon-context leakage, mis-specified reference "
      "law, K miscomputed, or alpha accounting wrong), not evidence about "
      "any organism.",
  "structural": {"p_interval": [0.001, 0.02], "power_at_declared_delta": 0.90,
                 "q_boring": 0.10, "lr_effective": 1000,
                 "n_hypotheses_class": "1 (pre-specified sham)",
                 "substrate": "D13/stackvm-v1", "era": "objective_ga+map_elites",
                 "shared_nuisance_loading": 0.15},
  "proposed_K": 1000,
  "required_future_evidence": "canonical reference draws + beacon contexts; "
      "~32 blocks",
  "cheapest_falsification": "it dies, as predicted, at a cost of one right",
  "reason_for_priority": "The apparatus has never been exercised end to end "
      "on this substrate. An instrument that cannot be shown to kill a known "
      "nothing cannot be trusted when it spares something.",
 },
 {
  "candidate_id": "WOW-C-002",
  "tranche": "CALIBRATION",
  "claim": "TRANSFER-FUNCTION PROBE. Artifact 9bc2b861 -- the single "
           "strongest historical anomaly in the corpus: the ONLY success "
           "originating in the reproductively isolated >700-byte mode, "
           "created by create_random, carrying 11 parent edges that are ALL "
           "self-loops (neutral mutations returning byte-identical output) "
           "and zero real ancestors.",
  "sealed_prediction": "Under beacon-derived contexts from the declared "
      "family, 9bc2b861 outranks canonical reference draws matched on "
      "PRE-CORPUS length bands (band boundaries fixed before inspection, NOT "
      "fitted to where this artifact looks extreme).",
  "if_it_survives": "Estimates the corpus->sealed transfer function at its "
      "high-historical-evidence end -- a parameter shared by every remaining "
      "right, which no per-candidate score can represent.",
  "structural": {"p_interval": [0.05, 0.30], "power_at_declared_delta": 0.80,
                 "q_boring": 0.35, "lr_effective": 1000,
                 "n_hypotheses_class": "~10^4 (artifact x observable sweep)",
                 "substrate": "D13/stackvm-v1", "era": "map_elites",
                 "shared_nuisance_loading": 0.55},
  "proposed_K": 1000,
  "required_future_evidence": "beacon contexts + matched reference draws; "
      "~32 blocks",
  "cheapest_falsification": "one sealed test; death is informative because "
      "this is the corpus's strongest single anomaly",
  "reason_for_priority": "Deliberately spends an early right on the "
      "candidate most likely to be a hindsight artifact, because its outcome "
      "calibrates every later ranking.",
 },
 {
  "candidate_id": "WOW-C-003",
  "tranche": "PHENOMENON",
  "claim": "STERILE-BAND MECHANISM. The corpus contains 327 artifacts of "
           "length 401-700 and ZERO mutation events using any of them as a "
           "parent. The corpus therefore cannot distinguish 'evolution never "
           "went there' from 'the operator cannot go there'.",
  "sealed_prediction": "Mutation applied to 401-700 byte parents yields "
      "offspring whose viability rate is INDISTINGUISHABLE from that of "
      "51-150 byte parents under matched beacon contexts.",
  "if_it_survives": "The sterility was a sampling accident of the historical "
      "scheduler, and the historical failure landscape is missing a whole "
      "reachable region for non-biological reasons.",
  "structural": {"p_interval": [0.20, 0.60], "power_at_declared_delta": 0.85,
                 "q_boring": 0.25, "lr_effective": 1000,
                 "n_hypotheses_class": "~10^2 (band x operator grid)",
                 "substrate": "D13/stackvm-v1", "era": "both",
                 "shared_nuisance_loading": 0.30},
  "proposed_K": 1000,
  "required_future_evidence": "fresh mutation events from 401-700 parents -- "
      "a class of event that does not exist anywhere in the corpus",
  "cheapest_falsification": "a few hundred beacon-seeded mutations",
  "reason_for_priority": "The single cleanest independence in the corpus: "
      "the historical record contains literally zero observations of the "
      "event class the prediction is about.",
 },
 {
  "candidate_id": "WOW-C-004",
  "tranche": "PHENOMENON",
  "claim": "REPRODUCTIVE ISOLATION. Genotype length is bimodal (28,392 "
           "artifacts at 1-150; 1,393 above 700; 335 between). No mutation "
           "in 38,163 length-changing events crosses <=150 -> >700. The long "
           "mode was seeded independently by create_random (14 artifacts) "
           "and self-sustained thereafter.",
  "sealed_prediction": "Under beacon-derived contexts, mutation of <=150 "
      "byte parents produces >700 byte offspring at a rate BELOW a "
      "pre-declared threshold -- i.e. the modes are mechanically, not "
      "historically, disconnected.",
  "if_it_survives": "The corpus contained two non-interbreeding populations "
      "that every prior aggregate statistic silently pooled.",
  "structural": {"p_interval": [0.15, 0.55], "power_at_declared_delta": 0.75,
                 "q_boring": 0.30, "lr_effective": 1000,
                 "n_hypotheses_class": "~10^2 (band-pair grid)",
                 "substrate": "D13/stackvm-v1", "era": "both",
                 "shared_nuisance_loading": 0.60},
  "proposed_K": 1000,
  "required_future_evidence": "beacon-seeded mutation sweep across bands",
  "cheapest_falsification": "one crossing event falsifies it outright",
  "reason_for_priority": "Highest breadth: if true, every pooled statistic "
      "ever computed on this corpus mixed two populations.",
 },
 {
  "candidate_id": "WOW-C-005",
  "tranche": "PHENOMENON",
  "claim": "CONVERGENT SOLVABILITY. Task a768fad8 was solved by two "
           "artifacts with ZERO shared ancestry, from OPPOSITE length modes "
           "(eadcc0bd, 37 bytes, mutate; 9bc2b861, 707 bytes, create_random).",
  "sealed_prediction": "Under beacon-seeded sampling, the task family "
      "containing a768fad8 is solved at a rate exceeding the corpus-wide "
      "base rate by a pre-declared margin, from BOTH length modes.",
  "if_it_survives": "The task has a broad solution basin reachable from "
      "disjoint regions of genotype space -- a property of the task, not of "
      "any lineage.",
  "structural": {"p_interval": [0.10, 0.45], "power_at_declared_delta": 0.70,
                 "q_boring": 0.40, "lr_effective": 1000,
                 "n_hypotheses_class": "~10^3 (task x mode)",
                 "substrate": "D13/stackvm-v1", "era": "map_elites",
                 "shared_nuisance_loading": 0.50},
  "proposed_K": 1000,
  "required_future_evidence": "beacon-seeded task sampling in the declared "
      "family",
  "cheapest_falsification": "base-rate comparison on a few hundred draws",
  "reason_for_priority": "Only corpus event where independent lineages "
      "converged on one task; but the map_elites successes have weaker "
      "provenance (no linked execution records), so artifact risk is high.",
 },
]


def main(outpath):
    queue, refused = [], []
    for c in CANDIDATES:
        c["null_path_types"] = dict(CLEAN_NULL)
        try:
            B.check_null_path(c)
        except B.BoundaryViolation as e:
            refused.append({"candidate_id": c["candidate_id"],
                            "refused": str(e)})
            continue
        ent = B.verdict_entropy_check(c, harness=None)
        sc = B.rights_aware_score(c)
        rec = {
            "candidate_id": c["candidate_id"],
            "label": "SEALED_TEST_WORTHY_PENDING_VALIDATION",
            "tranche": c["tranche"],
            "claim": c["claim"],
            "sealed_prediction": c["sealed_prediction"],
            "if_it_survives": c["if_it_survives"],
            "entropy_validation": ent["status"],
            "entropy_validation_reason": ent["reason"],
            "null_path_types": c["null_path_types"],
            "proposed_K": c["proposed_K"],
            "expected_bits": sc["bits_expected"],
            "bits_per_right": sc["bits_per_right"],
            "log2_lr_effective": sc["log2_lr_effective"],
            "power_at_delta": sc["power_at_delta"],
            "q_boring": sc["q_boring"],
            "p_interval_structural": sc["p_interval"],
            "shared_nuisance_loading": c["structural"]["shared_nuisance_loading"],
            "n_hypotheses_class": c["structural"]["n_hypotheses_class"],
            "substrate": c["structural"]["substrate"],
            "era": c["structural"]["era"],
            "required_future_evidence": c["required_future_evidence"],
            "cheapest_falsification": c["cheapest_falsification"],
            "reason_for_priority": c["reason_for_priority"],
            "admission_blocker": "SUBSTRATE MISMATCH: this claim is about "
                "D13/stackvm-v1 operators, but the MHC admission protocol's "
                "canonical reference sampler (CANON-R-V1) and context family "
                "(CANON-W-V1) are defined for the World Foundry grammar. "
                "Either stackvm-v1 gets a GENESIS-pinned canonical sampler of "
                "its own, or the claim must be re-posed in the World Foundry "
                "grammar -- which changes the claim.",
        }
        queue.append(rec)
    # calibration tranche first, then by bits per right
    queue.sort(key=lambda r: (0 if r["tranche"] == "CALIBRATION" else 1,
                              -r["bits_per_right"]))
    # n_eff over the queue from shared-nuisance loadings (outcome
    # independence, not hypothesis-text independence)
    lam = [r["shared_nuisance_loading"] for r in queue]
    n_eff = (sum(lam) ** 2) / sum(x * x for x in lam) if lam else 0
    for i, r in enumerate(queue):
        r["queue_rank"] = i + 1
        r["queue_n_eff"] = round(n_eff, 2)
    with open(outpath, "w") as f:
        for r in queue:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    print("queued %d, refused %d" % (len(queue), len(refused)))
    print("queue n_eff (outcome independence) = %.2f of %d entries"
          % (n_eff, len(queue)))
    for r in queue:
        print("  %d. %-11s %-11s bits/right=%.4f  %s"
              % (r["queue_rank"], r["candidate_id"], r["tranche"],
                 r["bits_per_right"], r["entropy_validation"]))
    return queue


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "WOW_ADMISSION_QUEUE.jsonl")
