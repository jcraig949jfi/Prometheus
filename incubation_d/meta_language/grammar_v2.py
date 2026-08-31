"""Grammar v2: third census candidate.

Changes from gv1 (rejected: only `insert` — min length 5, lexicographically
late — missed the first-200 cheap window; every other gate passed):

1. d15 icat added (B B -> B, argument-swapped cat, Joy's swoncat family):
   brings insert to length 4 (d12 t0 d15 d04) and prepend to length 2.
   Generic concatenation plumbing, not a mutation category; leakage gates
   re-audit (prepend at 2 tightens CK2/CK4 against THIS grammar's favor,
   which is the honest direction for a leakage test).

2. Canonical order: structural edits first (unc, splt, cat, icat, tuck,
   nip, stack ops), fragment injection second (t0..t4), measurement and
   arithmetic third (len, zero, succ, add, half), construction-from-nothing
   and reflection last (nil, qlit). Rationale: quote-nesting junk dominated
   gv1's cheap window; reflection is the most powerful and least edit-like
   capability, so it prices last in canonical search. The order is frozen
   into M0's enumeration identically.
"""

GRAMMAR_ID = "gv2"

TOKENS = (
    "d12",  # unc
    "d06",  # splt
    "d04",  # cat
    "d15",  # icat
    "d13",  # tuck
    "d14",  # nip
    "d00", "d01", "d02",   # dup swap drop
    "t0", "t1", "t2", "t3", "t4",
    "d05",  # len
    "d08", "d09", "d10", "d11",  # zero succ add half
    "d03",  # nil
    "d07",  # qlit
)

GRAMMAR_SPEC = {
    "id": GRAMMAR_ID,
    "tokens": list(TOKENS),
    "introducers": {"t0": ["o0"], "t1": ["o1"], "t2": ["o2"],
                    "t3": ["o3"], "t4": ["o4"]},
    "meta_conditional": False,
    "meta_token_introducers": False,
    "notes": [
        "gv1 + icat; edits-first canonical order, reflection last.",
        "No meta-tier conditional; no introducers for meta tokens.",
    ],
}
