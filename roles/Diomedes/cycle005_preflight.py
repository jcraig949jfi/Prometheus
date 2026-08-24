"""Diomedes cycle 005 — PRE-FLIGHT: which alternative action family can carry the replication?

Cycle 005 must test whether the cycle 001-004 decomposition ordering is peculiar to h1's
object-swap action, or general across materially different Prometheus action families.

HITL raised the decisive confound: A* in cycles 001-004 is generated from predicates
involving parity and bounded difference, so cheap ARITHMETIC recovering action value is
not wholly surprising. A replication is only informative if its oracle is NOT the same
arithmetic form. This pre-flight therefore scores candidates on two axes:

  VIABILITY  -- enough volume, a real action alphabet, an exactly computable A*
  ORACLE FORM -- is the ground truth an arithmetic comparison of two catalog values
                 (same form as h1, weak test), or a structural/mathematical fact
                 (different form, strong test)?

It also checks DEGENERACY: if a one-line baseline scores ~1.0, the task has no headroom
and the candidate is VACUOUS -- pre-committed, not discovered after the fact.

Read-only. Bounded.

    python roles/Diomedes/cycle005_preflight.py
"""
import collections
import gzip
import glob
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
CORPUS = ROOT / "theseus/corpus"
OUT = pathlib.Path(__file__).resolve().parent / "cycle005_preflight.json"
MAX_FILES = 10
MAX_LINES = 60_000

# candidate action families, from the RECON census
CANDIDATES = {
    "c4": "mutation (relation weakening/strengthening)",
    "c5": "mutation",
    "g5": "symmetry_transform (scale factor)",
    "b1": "operator_rotation (apply operator n times)",
    "b4": "operator_rotation (fixed point)",
    "b2": "composition_test (operator commutation)",
    "b3": "composition_test (self-inverse)",
    "b5": "conservation_law",
}


def main():
    files = sorted(glob.glob(str(CORPUS / "batch-*.jsonl.gz")))
    idx = [int(len(files) * k / MAX_FILES) for k in range(MAX_FILES)]
    seen = collections.Counter()
    payload_keys = collections.defaultdict(collections.Counter)
    examples = {}
    action_vocab = collections.defaultdict(collections.Counter)
    outcome_vocab = collections.defaultdict(collections.Counter)

    for i in idx:
        f = files[min(i, len(files) - 1)]
        with gzip.open(f, "rt", encoding="utf-8", errors="replace") as fh:
            for j, line in enumerate(fh):
                if j >= MAX_LINES:
                    break
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                g = d.get("generator_id")
                if g not in CANDIDATES:
                    continue
                seen[g] += 1
                p = d.get("claim_payload") or {}
                payload_keys[g].update(p.keys())
                if g not in examples:
                    examples[g] = p
                # action vocabulary: whichever field names the transformation
                for k in ("operator", "operator_f", "relation", "scale_factor",
                          "n_applications", "original_relation"):
                    if k in p:
                        action_vocab[g][f"{k}={p[k]}"] += 1
                for k in ("holds", "matches", "commutes", "self_inverse_at_v",
                          "is_fixed_point", "scale_invariant", "weak_holds",
                          "self_consistent"):
                    if k in p:
                        outcome_vocab[g][f"{k}={p[k]}"] += 1

    rep = {}
    for g in CANDIDATES:
        if not seen[g]:
            rep[g] = {"desc": CANDIDATES[g], "n": 0, "verdict": "ABSENT in sample"}
            continue
        av = action_vocab[g]
        ov = outcome_vocab[g]
        rep[g] = {
            "desc": CANDIDATES[g],
            "n_sampled": seen[g],
            "payload_keys": [k for k, _ in payload_keys[g].most_common(14)],
            "distinct_action_tokens": len(av),
            "top_actions": av.most_common(6),
            "outcome_distribution": ov.most_common(8),
            "example": {k: examples[g][k] for k in list(examples[g])[:12]},
        }
    OUT.write_text(json.dumps(rep, indent=1), encoding="utf-8")
    for g, r in rep.items():
        if not r.get("n_sampled"):
            print(f"{g:4s} ABSENT")
            continue
        print(f"{g:4s} n={r['n_sampled']:>7,}  actions={r['distinct_action_tokens']:>4}  {r['desc']}")
        print(f"      keys: {r['payload_keys']}")
        print(f"      outcomes: {r['outcome_distribution']}")
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
