"""THEO-REQ-003 (comms #241): what a same-kind composition of two radius-3 CA rules would produce, counted exactly.

Theophrastus asked Proteus for a composition operation whose child is an executable rule of the SAME kind (a
rule_hex) carrying both parents and the operator. Nyx was copied for "organs / transformation candidates". This
reading does NOT design that operation and executes no cellular automaton. It takes the one accepted two-parent
organ in the atlas -- Avida's region-swap recombination (cBirthChamber.cc:178-224, 286-313; cut 2026-09-30) -- states
it on a fixed-length 128-entry rule table, and counts, for every pair of the six recovered EvCA genomes
(herakles/evca/genomes.py, read-only), what that operator can and cannot produce:

    D                 table entries at which the two parents differ
    distinct children how many different rule tables a one-region swap can yield (both children of every region)
    degenerate        probability, under the fossil's own draw (two uniform fractions, floored), that a child is
                      bit-identical to one of its parents -- the case in which Avida records no parents at all

Pure arithmetic on the published hex strings; deterministic; stdlib only.
    python -m nyx.readings.theo_req_003_composition [out.json]
"""
from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction

from herakles.evca.genomes import GENOMES, NAMES

N = 128


def table(name: str) -> str:
    return format(int(str(GENOMES[name]["hex"]), 16), "0128b")      # position = index into the written table


def swap(a: str, b: str, i: int, j: int):
    """Avida RegionSwap on equal lengths: the region [i, j) is exchanged; two children."""
    return a[:i] + b[i:j] + a[j:], b[:i] + a[i:j] + b[j:]


def pair(n1: str, n2: str) -> dict:
    a, b = table(n1), table(n2)
    diff = [k for k in range(N) if a[k] != b[k]]
    children = {}
    p_deg = Fraction(0)
    p_major_swap = Fraction(0)
    for i in range(N):
        for j in range(i, N):
            w = Fraction(1 if i == j else 2, N * N)                  # two uniform draws, sorted, each floored to an index
            c0, c1 = swap(a, b, i, j)
            if c0 in (a, b):                                         # then c1 is the other parent
                p_deg += w
            else:
                children.setdefault(c0, (i, j)); children.setdefault(c1, (i, j))
            if 2 * (j - i) > N:                                      # 'majority of the genome should stay': labels swap
                p_major_swap += w
    # closed form: a child is fixed by WHICH contiguous run of the differing entries it took from the other parent.
    # D(D+1)/2 runs, minus the full run (the parents exchanged), two children per run, and the D-1 proper prefixes
    # and D-1 proper suffixes each give a child that some other run also gives: 2(D(D+1)/2 - 1) - 2(D-1) = D(D-1).
    d = len(diff)
    return {"pair": f"{n1} x {n2}", "differing_entries": len(diff), "first_differing": diff[0] if diff else None,
            "last_differing": diff[-1] if diff else None, "distinct_nonparent_children": len(children),
            "closed_form_D_times_D_minus_1": d * (d - 1),
            "all_recombinants_by_any_mask": f"2^{len(diff)} - 2",
            "p_child_identical_to_a_parent": float(p_deg), "p_labels_swapped_majority_rule": float(p_major_swap)}


def run() -> dict:
    rows = [pair(x, y) for x, y in itertools.combinations(NAMES, 2)]
    for r in rows:                                                   # the closed form is a check on the enumeration
        assert r["distinct_nonparent_children"] == r["closed_form_D_times_D_minus_1"], r
    return {"schema": "nyx.reading.theo_req_003/1", "operator": "one-region swap at indices floor(128 u1), floor(128 u2), u ~ U(0,1) (Avida DoBasicRecombination on a fixed-length table)",
            "table_entries": N, "pairs": rows}


def main(argv) -> int:
    r = run()
    print(f"{'pair':24s} {'|D|':>4s} {'distinct children':>18s} {'P(child = a parent)':>20s}")
    for x in r["pairs"]:
        print(f"{x['pair']:24s} {x['differing_entries']:4d} {x['distinct_nonparent_children']:18d} {x['p_child_identical_to_a_parent']:20.4f}")
    if argv:
        open(argv[0], "w", encoding="utf-8", newline="\n").write(json.dumps(r, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
