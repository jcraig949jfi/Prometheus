"""Grammar v1: second census candidate.

Changes from gv0 (rejected GRAMMAR_REJECTED_POVERTY under census v1.1):

1. Three generic structural combinators added — d12 unc (B -> B B),
   d13 tuck (a b -> b a b), d14 nip (a b -> b). These cheapen positional
   edits (insert/delete/perm/wrap) that gv0 could not reach or reached only
   at the horizon edge. None encodes a mutation category: they are
   decomposition and stack plumbing, and every leakage gate re-audits the
   result.

2. Canonical token order is decomposition-first (unc, splt, len before cat
   and the introducers). The order is an arbitrary designer choice that
   defines canonical rank for the census AND for M0's frozen enumeration;
   analysis-before-synthesis is the declared design philosophy. Introducers
   remain last, so pure fragment-injection is the lexicographically LATEST
   way to build anything.
"""

GRAMMAR_ID = "gv1"

TOKENS = (
    "d12",  # unc
    "d06",  # splt
    "d05",  # len
    "d04",  # cat
    "d13",  # tuck
    "d14",  # nip
    "d00", "d01", "d02",   # dup swap drop
    "d03",  # nil
    "d07",  # qlit
    "d08", "d09", "d10", "d11",  # zero succ add half
    "t0", "t1", "t2", "t3", "t4",
)

GRAMMAR_SPEC = {
    "id": GRAMMAR_ID,
    "tokens": list(TOKENS),
    "introducers": {"t0": ["o0"], "t1": ["o1"], "t2": ["o2"],
                    "t3": ["o3"], "t4": ["o4"]},
    "meta_conditional": False,
    "meta_token_introducers": False,
    "notes": [
        "gv0 + unc/tuck/nip; decomposition-first canonical order.",
        "No meta-tier conditional; no introducers for meta tokens.",
    ],
}
