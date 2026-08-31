"""Grammar v0: the first meta-language candidate submitted to the census.

A grammar candidate is data: an ordered token inventory (order defines the
shortlex canonical enumeration), plus the introducer table. Semantics live in
the VM; the census treats this file as the candidate's identity, hashed over
GRAMMAR_SPEC's canonical serialization.
"""

GRAMMAR_ID = "gv0"

# Ordered token inventory (order is part of the frozen spec: it defines
# canonical rank).
TOKENS = (
    "d00", "d01", "d02",          # dup swap drop
    "d03", "d04", "d05", "d06", "d07",  # nil cat len splt qlit
    "d08", "d09", "d10", "d11",   # zero succ add half
    "t0", "t1", "t2", "t3", "t4",  # object-token introducers
)

GRAMMAR_SPEC = {
    "id": GRAMMAR_ID,
    "tokens": list(TOKENS),
    "introducers": {"t0": ["o0"], "t1": ["o1"], "t2": ["o2"],
                    "t3": ["o3"], "t4": ["o4"]},
    "meta_conditional": False,
    "meta_token_introducers": False,
    "notes": [
        "No meta-tier conditional: transforms cannot branch on content.",
        "No introducers for meta tokens: meta-code enters outputs only by "
        "harvesting from input or via qlit.",
    ],
}
