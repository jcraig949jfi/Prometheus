"""The Chop Shop catalogue: BIT records with a behavioural classification, v0 (Nyx, 2026-09-12).

Directive: roles/Nyx/prompts/2026-09-12_directive_catalogue_loop/ -- "the smallest components
computable ... Classification for searchability is the real gem ... match [a weird solution
produced by an organism] against a similar set of known algorithmic bits."

A BIT is one mechanism at PRIMITIVE or MECHANISM scale, described by WHAT IT DOES TO WHAT
UNDER WHAT REQUIREMENTS -- never by its name. Names, lineages and sources are provenance,
kept on the record but EXCLUDED from matching, because an organism's weird solution has no
name (program doctrine: residue is navigable by behaviour, not by semantic labels; verbs are
deeper bridges than nouns; discipline labels are docstrings, not coordinates).

The classification axes are small CONTROLLED VOCABULARIES so that a query is a point in the
same space as the records. Free text is allowed in `mechanism` (human description) but the
matcher never reads it. The behavioural SIGNATURE (verb, in-geometry, out-geometry, order,
metric, state, control, guarantee) is what makes two bits from different lineages the SAME
bit (a recurrence) -- the N2/N3 rulings' duplicate control, made mechanical.

Grades travel (NYX-25): a bit seeded from a list or wiki is T2 (a human description of a
mechanism believed to exist) until a chop (source read) or a run makes it T1-SOURCE /
T1-LOCAL. The grade is a field, never a filter on admission.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

SCHEMA = "nyx.bit/0"

# ---- controlled vocabularies (extend only by an entry in VOCAB_CHANGELOG below)
VERB = (  # what the bit DOES; the primary axis
    "SELECT",      # choose element(s) from a collection by a rule (argmax, sample, filter)
    "ORDER",       # impose or exploit an order (sort, rank, prioritise, orient)
    "PARTITION",   # split a domain into parts / assign keys (hash, bucket, cluster, discretise)
    "COMPRESS",    # shorter description of the same information (encode, factor, abstract)
    "SEARCH",      # explore a space for an element satisfying a predicate/objective
    "VERIFY",      # decide a property of an object (check, decide, certify)
    "REPAIR",      # restore an invariant after a change (realign, rebalance, reconcile)
    "TRANSFORM",   # rewrite an object to an equivalent/derived form (normalise, canonicalise)
    "ACCUMULATE",  # fold a stream into a summary/state (count, aggregate, integrate)
    "SAMPLE",      # draw from a distribution / population
    "BOUND",       # limit a quantity (budget, cap, rate-limit, threshold)
    "ROUTE",       # move an object to a destination by a rule (dispatch, forward, address)
    "SYNCHRONIZE", # coordinate independent actors/state (lock, consensus, barrier, merge)
    "ALLOCATE",    # assign a scarce resource (memory, time, slots)
    "DETECT",      # notice a condition or anomaly (loop, error, change, staleness)
    "CORRECT",     # recover the intended object from a corrupted one (ECC, retry, repair-by-redundancy)
    "PREDICT",     # estimate an unobserved quantity from observed ones
    "SCHEDULE",    # decide WHEN/in what order actions run under constraints
    "REMEMBER",    # store and retrieve by key/content (cache, index, archive)
    "RESUME",      # return to a previously recorded state (checkpoint/restore, replay)
    "GENERATE",    # produce candidates/objects from a grammar, model, or prior
    "COMPARE",     # measure a distance/similarity/alignment between two objects (added v0.1, see changelog)
)
GEOMETRY = (  # value geometry of inputs/outputs
    "SCALAR", "BOOLEAN", "SEQUENCE", "SET", "MULTISET", "MAP", "TREE", "DAG", "GRAPH", "MATRIX",
    "TENSOR", "STREAM", "STRING", "BITSTRING", "STATE_TOKEN", "FUNCTION", "PREDICATE",
    "DISTRIBUTION", "RECORD", "PROGRAM", "PROOF", "NONE",
)
ORDER_REQ = ("NONE", "PARTIAL", "TOTAL", "WELL_FOUNDED")
METRIC_REQ = ("NONE", "EQUALITY", "DISTANCE", "SIMILARITY", "INNER_PRODUCT")
STATE_REQ = ("NONE", "LOCAL", "GLOBAL", "EXTERNAL")  # EXTERNAL = held by the environment/world
CONTROL = ("PURE", "CALLBACK", "LOOP_OWNER", "REACTIVE", "SCHEDULED")  # who decides when it fires
GUARANTEE = (  # the strongest property the bit promises, chosen from this list
    "NONE", "TERMINATES", "SOUND", "COMPLETE", "OPTIMAL", "LOCAL_OPTIMUM", "MONOTONE",
    "IDEMPOTENT", "DETERMINISTIC", "PROBABILISTIC_BOUND", "EXACT", "APPROXIMATE",
)
STRATEGY = (  # HOW the work is organised (added v0.2 after batch 1 collapsed distinct mechanisms into one signature)
    "DIRECT",              # one pass / one formula / a table lookup; no organising idea beyond doing it
    "INCREMENTAL",         # grow a solution one element at a time, maintaining an invariant
    "EXCHANGE",            # local swaps/moves until an invariant holds everywhere
    "DIVIDE_CONQUER",      # split BY POSITION, solve parts independently, combine (the work is in the combine)
    "PARTITION_BY_VALUE",  # split BY VALUE against a chosen element so no combine is needed (the work is in the split); v0.3
    "DISTRIBUTION",        # use the key itself as an address (bucket, radix, hashing)
    "PRECOMPUTED_TABLE",   # preprocess one input into a table that speeds every later query
    "DYNAMIC_PROGRAMMING", # fill a table of overlapping subproblems
    "GREEDY",              # commit to the locally best choice, never revisit
    "RANDOMIZED",          # correctness or cost relies on random choices
    "DATA_INDEPENDENT",    # a fixed schedule of operations regardless of input values (networks, oblivious)
    "BIT_PARALLEL",        # word-level parallelism over sets encoded as bits
    "FIXPOINT_ITERATION",  # repeat a step until nothing changes
    "BACKTRACKING",        # depth-first choice with undo on failure
    "BRANCH_AND_BOUND",    # search with pruning by bounds
    "STREAMING",           # one pass with bounded state over a stream
    "ADAPTIVE_SWITCH",     # choose among strategies by observed behaviour/budget
    "UNKNOWN",
)
ITERATION = (  # the DISCIPLINE by which candidates are visited (added v0.4; the axis a matcher needs to tell level-by-level from deepest-first)
    "NONE",             # no visiting order is part of the mechanism (a formula, a single pass with no choice)
    "FIFO",             # oldest first (queue): level by level, rounds in arrival order
    "LIFO",             # newest first (stack): deepest first, undo-based
    "PRIORITY",         # best-scored first (heap / priority structure)
    "SORTED_GLOBAL",    # all candidates ordered once up front, then consumed in that order
    "PARALLEL_ROUNDS",  # every part acts in the same round, then all results are applied at once
    "REMOVAL",          # visit by taking things away from a complete object
    "SWEEP",            # a fixed spatial/positional scan (left to right, along an axis)
    "RANDOM",           # candidates visited in random order
    "UNKNOWN",
)
COST = ("CONSTANT", "LOG", "LINEAR", "LINEARITHMIC", "POLYNOMIAL", "EXPONENTIAL", "UNKNOWN")
SCALE = ("PRIMITIVE", "MECHANISM")
GRADES = ("T1-LOCAL", "T1-SOURCE", "T2", "T3", "unknown")

VOCAB_CHANGELOG = [
    "2026-09-12 v0: initial vocabularies, written before any external list was ingested; extension requires a dated entry here and a reason from a failed query or a failed recurrence check",
    "2026-09-12 v0.4: ITERATION axis added to the signature. Reason (two planted controls FAILED after batch 2, LOOP_LOG 2026-09-12): q.level_by_level_not_deepest returned deepest-first for a ring-by-ring story (BFS and DFS shared SEARCH|GRAPH|MAP|..|COMPLETE|INCREMENTAL), and q.grow_one_tree_not_rounds returned the sorted-edges mechanism for a grow-one-structure story (five greedy spanning-tree mechanisms shared SELECT|GRAPH|TREE|TOTAL|..|OPTIMAL|GREEDY). STRATEGY says how work is organised; ITERATION says in what DISCIPLINE candidates are visited (FIFO, LIFO, PRIORITY, SORTED_GLOBAL, PARALLEL_ROUNDS, REMOVAL, SWEEP, RANDOM, NONE). Backfilled onto all 84 bits at the same commit; the two controls were given their iteration values (FIFO; PRIORITY) with a ledgered note before rerun.",
    "2026-09-12 v0.3: STRATEGY += PARTITION_BY_VALUE (a refinement of DIVIDE_CONQUER). Reason (observed failure): planted control q.strategy_separates_sorts FAILED after v0.2 -- merge-runs and partition-around-pivot tied at 1.0 as DIVIDE_CONQUER; the control's story names the distinguishing feature ('splitting around a chosen element'): the split is decided by element VALUES and the work is in the split, versus a split by POSITION with the work in the combine. Retagged: bit.order.partition_around_pivot, bit.select.kth_by_partition. RESIDUAL recurrence pairs ACCEPTED and not refined until a control demands it: (extract_extreme_repeatedly, piles_then_merge) both GREEDY; (pattern_match_with_failure_links, pattern_match_skip_by_last_occurrence) both PRECOMPUTED_TABLE -- distinguishable only by what the table is keyed by.",
    "2026-09-12 v0.2: STRATEGY axis added to the signature. Reason (observed failure after batch 1 commit, LOOP_LOG 2026-09-12): the recurrence check merged SIX distinct sorting mechanisms (swap-adjacent, insert-into-prefix, partition-around-pivot, merge-runs, comparator network, restricted-move) under one signature ORDER|SEQUENCE|SEQUENCE|TOTAL|NONE|NONE|PURE|EXACT, and three pattern matchers (failure links, last-occurrence skips, bit-parallel) under another. A matcher that cannot tell 'split and recombine' from 'swap neighbours until done' is not matching mechanisms. The eight v0 axes describe WHAT and TO WHAT under WHICH requirements; STRATEGY describes HOW the work is organised. Backfilled onto all 50 bits at the same commit; the planted query q.strategy_separates_sorts must pass from then on.",
    "2026-09-12 v0.1: VERB += COMPARE. Reason (observed failure, batch 1 wikipedia_list_of_algorithms 'Sequence algorithms'): edit distance, Hamming distance, Jaro-Winkler, Dice, dynamic time warping and sequence alignment measure a distance/similarity/alignment between TWO objects; none of the 21 v0 verbs expressed 'measure how far apart two things are' -- ACCUMULATE, TRANSFORM and PREDICT were each wrong in a way a matcher would feel (a query for 'the organism scored how alike two strings were' had no verb to use).",
]

SIGNATURE_FIELDS = ("verb", "in_geometry", "out_geometry", "order_req", "metric_req", "state_req", "control", "guarantee", "strategy", "iteration")
REQUIRED = ("schema", "id", "name", "mechanism", "scale", "lineage", "sources", "grade",
            "verb", "in_geometry", "out_geometry", "order_req", "metric_req", "state_req", "control",
            "guarantee", "strategy", "iteration", "cost", "requires", "fails_when", "instances", "related")

Finding = Tuple[str, str]


def signature(rec: Dict[str, Any]) -> Tuple[str, ...]:
    """The behavioural signature: what makes two bits the same bit. Names and lineages are NOT in it."""
    return tuple(str(rec.get(k)) for k in SIGNATURE_FIELDS)


def validate(rec: Dict[str, Any]) -> List[Finding]:
    out: List[Finding] = []
    for k in REQUIRED:
        if k not in rec:
            out.append(("MISSING_FIELD", f"bit.{k} absent"))
    if out:
        return out
    if rec["schema"] != SCHEMA:
        out.append(("BAD_SCHEMA", f"schema must be {SCHEMA}"))
    for k, vocab in (("verb", VERB), ("in_geometry", GEOMETRY), ("out_geometry", GEOMETRY), ("order_req", ORDER_REQ),
                     ("metric_req", METRIC_REQ), ("state_req", STATE_REQ), ("control", CONTROL),
                     ("guarantee", GUARANTEE), ("strategy", STRATEGY), ("iteration", ITERATION), ("cost", COST), ("scale", SCALE), ("grade", GRADES)):
        if rec[k] not in vocab:
            out.append(("BAD_VOCAB", f"bit.{k}={rec[k]!r} not in {k} vocabulary"))
    if not isinstance(rec["mechanism"], str) or len(rec["mechanism"].split()) < 8:
        out.append(("THIN_MECHANISM", "bit.mechanism must be a behavioural description of at least 8 words"))
    low = rec["mechanism"].lower()
    if isinstance(rec.get("name"), str) and rec["name"].lower() in low and len(rec["name"]) > 3:
        out.append(("NAME_IN_MECHANISM", "bit.mechanism restates the name; describe the behaviour, not the label"))
    for k in ("lineage", "sources", "requires", "fails_when", "instances", "related"):
        if not isinstance(rec[k], list):
            out.append(("BAD_TYPE", f"bit.{k} must be a list"))
    if isinstance(rec["sources"], list) and not rec["sources"]:
        out.append(("NO_SOURCES", "bit.sources empty: a bit with no ancestry is an assertion"))
    if isinstance(rec["fails_when"], list) and not rec["fails_when"]:
        out.append(("NO_FAILURE", "bit.fails_when empty: every mechanism has a failure landscape (charter V)"))
    for r in rec.get("related", []):
        if not (isinstance(r, dict) and r.get("rel") in ("RECURRENCE_OF", "COMPOSES_WITH", "SPECIALIZES", "GENERALIZES", "REQUIRES", "CONTRASTS_WITH") and r.get("id")):
            out.append(("BAD_RELATED", "bit.related entries need {rel in RECURRENCE_OF|COMPOSES_WITH|SPECIALIZES|GENERALIZES|REQUIRES|CONTRASTS_WITH, id}"))
    return out


def load_all(root: Path) -> List[Dict[str, Any]]:
    bits = []
    for p in sorted(root.rglob("*.json")):
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if isinstance(rec, dict) and rec.get("schema") == SCHEMA:
            rec["_path"] = str(p)
            bits.append(rec)
    return bits


def recurrences(bits: List[Dict[str, Any]]) -> Dict[Tuple[str, ...], List[str]]:
    """Groups of bits sharing a behavioural signature: candidates for 'one bit, several ancestries'."""
    groups: Dict[Tuple[str, ...], List[str]] = {}
    for b in bits:
        groups.setdefault(signature(b), []).append(b["id"])
    return {k: v for k, v in groups.items() if len(v) > 1}


def main(argv: List[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path("nyx/catalog/bits")
    bits = load_all(root)
    bad = 0
    for b in bits:
        f = validate(b)
        if f:
            bad += 1
            print("FAIL", b.get("id"), b.get("_path"))
            for code, msg in f:
                print("  ", code, msg)
    rec = recurrences(bits)
    print(f"bits {len(bits)}  invalid {bad}  signature-groups-with->1 {len(rec)}")
    for sig, ids in rec.items():
        print("  RECURRENCE", ids, "sig", sig)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
