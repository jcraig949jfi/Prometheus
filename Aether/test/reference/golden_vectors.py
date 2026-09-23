"""
Aether AETH-00 (semantics_id aeth00.v1) -- FROZEN golden arbitration
vectors (AETHER_TEST_PLAN.md test 23).

These integers are frozen evidence: hand/tool-derived once against the
chained-SplitMix64 formula in AETHER_SPEC.md ("Collision arbitration"),
then hardcoded here. Tests compare oracle.arbitration_priority's LIVE
output against these frozen constants -- never the reverse -- so a
future accidental change to oracle.py's math is caught.

Two of these (PRIORITY_VECTORS[0] and PRIORITY_VECTORS[3], tagged
"hand-verified" below) were independently re-derived by hand, digit by
digit, outside of and before running any code in this repository; see
AETH-00A_RECEIPT.md, "Manual golden-vector review", for the full
worked arithmetic. The rest were produced by the same formula run
through a standalone one-off script (not committed -- its output is
these frozen literals, which is what is actually tested), then sanity-
checked for internal consistency (e.g. the four PRIORITY_VECTORS[0..3]
share every input except target_field, and their values are pairwise
distinct, as the tie-freedom proof requires).

Each entry: (seed, tick, target_row, target_col, target_field,
source_row, source_col, expected_priority).
"""

MASK64 = (1 << 64) - 1
MASK32 = (1 << 32) - 1

# seed=0, tick=0, target=(0,0), source=(0,0), field swept 0..3.
PRIORITY_VECTORS = [
    (0, 0, 0, 0, 0, 0, 0, 0x552D806A62B97855),  # hand-verified
    (0, 0, 0, 0, 1, 0, 0, 0x73A3EE95AACE0D70),
    (0, 0, 0, 0, 2, 0, 0, 0x43B92139006F3F88),
    (0, 0, 0, 0, 3, 0, 0, 0xE0FE093DD77E259B),  # hand-verified
    # High-bit / boundary seeds.
    (MASK64, 0, 0, 0, 0, 0, 0, 0x267D54DEDC53F876),
    (1 << 63, 0, 0, 0, 0, 0, 0, 0xEA8CD70B11A7995C),
    # High-bit / boundary ticks (MASK64 - 1 is the max VALID tick; MASK64
    # itself is never a valid `tick` argument to this function -- a step
    # attempted FROM tick == MASK64 is rejected before arbitration runs).
    (0, MASK64 - 1, 0, 0, 0, 0, 0, 0xF697364523DB3C99),
    (0, 1 << 63, 0, 0, 0, 0, 0, 0x94AC8C12A0FB9A79),
    # Coordinates near 2**32 - 1 (target, then source, then both).
    (7, 9, MASK32, MASK32, 1, 0, 0, 0x082E92929D54ED65),
    (7, 9, 0, 0, 1, MASK32, MASK32, 0xD9B71EC13BCB694F),
    (7, 9, MASK32 - 1, MASK32, 2, MASK32, MASK32 - 1, 0x415771CA0D07CDB6),
    # Coordinates containing 0 (target row 0; source col 0).
    (123, 456, 0, 5, 1, 3, 3, 0x3F1A1A4267CBAC0D),
    (123, 456, 3, 3, 1, 0, 9, 0x1001992D90CC362A),
    # Fully mixed, no zero component.
    (
        0xDEADBEEFCAFEBABE,
        0x1234567890ABCDEF,
        17,
        42,
        3,
        99,
        1,
        0x5A5F56F518F5D692,
    ),
]

# Winner-determination fixtures: (seed, tick, target, field,
# [(source, value), ...], expected_winning_source, expected_value).
# 2-way contest.
WINNER_VECTORS = [
    (
        111,
        1,
        (5, 5),
        0,
        [((0, 0), 0x10), ((9, 9), 0x20)],
        (9, 9),
        0x20,
    ),
    # 3-way contest.
    (
        222,
        2,
        (3, 3),
        2,
        [((0, 0), 0x01), ((1, 1), 0x02), ((2, 2), 0x03)],
        (1, 1),
        0x02,
    ),
    # 4-way contest: all four von Neumann neighbors of (5,5) contest field 3.
    (
        333,
        3,
        (5, 5),
        3,
        [((4, 5), 0x0A), ((5, 6), 0x0B), ((6, 5), 0x0C), ((5, 4), 0x0D)],
        (5, 4),
        0x0D,
    ),
]

# Unsigned-vs-signed ordering fixture (AETHER_TEST_PLAN.md test 24 /
# mutant catalog "signed priority comparison"): the CORRECT unsigned-max
# winner's priority has the high bit set (0xFFE5...), so it is NEGATIVE
# under a (buggy) signed 64-bit interpretation; a competitor with a
# strictly smaller unsigned priority but no high bit (0x7B53..., a large
# POSITIVE signed value) would incorrectly win under signed comparison.
SIGNED_VS_UNSIGNED_VECTOR = {
    "seed": 999,
    "tick": 5,
    "target": (2, 2),
    "field": 1,
    "sources": [(4, 0), (3, 4)],
    "priorities": {(4, 0): 0xFFE5A53FC4C88E1C, (3, 4): 0x7B5300E7F71E947B},
    "correct_unsigned_winner": (4, 0),
    "buggy_signed_winner": (3, 4),
}
