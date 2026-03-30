#!/usr/bin/env python3
"""
Populate INVERT damage operator instances in noesis_v2.duckdb.

INVERT = "Reverse the structural direction/vector" (primitive: DUALIZE + MAP)

Two strategies:
  1. Tag existing composition_instances whose notes describe structural inversion/reversal
  2. Insert new composition_instances for canonical INVERT resolutions

Author: Aletheia (overnight autonomous)
Date: 2026-03-29
"""

import duckdb
import re
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "noesis_v2.duckdb")

# --- Patterns that indicate structural inversion/reversal ---
INVERT_PATTERNS = [
    r'\brevers\w*',           # reverse, reversal, reversed, reversing
    r'\binvert\w*',           # invert, inversion, inverted, inverting
    r'\bopposite\s+direction',
    r'\bnegat\w*',            # negate, negation, negative (contextual)
    r'\banti-\w+',            # anti-clustering, anti-correlation, etc.
    r'\bcontra-\w+',          # contra-variant, contra-positive, etc.
    r'\breciprocal\s+\w+',    # reciprocal transform, reciprocal stretching
    r'\bflip\w*\b',           # flip, flipped, flipping
    r'\bbackward\w*',         # backward, backwards
    r'\bmirror\w*',           # mirror, mirrored, mirroring
    r'\bnegative\s+curvature',# geometric inversion
    r'\bdual\w*\b.*\bopposite',
    r'\bcomplement\w*\b',     # complementary (inversion of set)
]

# Entries to EXCLUDE from auto-tagging (false positives — "negative" in a
# non-inversion sense, "mirror" as metaphor, etc.)
EXCLUDE_IDS = set()

# --- New canonical INVERT instances to insert ---
NEW_INSTANCES = [
    {
        "instance_id": "FORCED_SYMMETRY_BREAK__NEGATIVE_HARMONY",
        "comp_id": "FORCED_SYMMETRY_BREAK",
        "system_id": None,
        "tradition": "Western music theory",
        "domain": "music",
        "notes": (
            "Ernst Levy's Negative Harmony inverts melodic intervals around an axis "
            "(typically the axis between the tonic and its fifth). Every interval is "
            "reflected: major becomes minor, dominant becomes subdominant, tension "
            "mirrors to release. The harmonic direction is literally reversed — "
            "ascending fifths become descending fourths. This is a pure structural "
            "inversion of the circle of fifths, producing functionally equivalent but "
            "perceptually 'darker' harmonic movement. The damage is the loss of "
            "conventional harmonic directionality: cadences resolve 'backwards.' "
            "| DAMAGE_OP: INVERT | STRATEGY: Reflect all intervals around a tonal axis, "
            "reversing harmonic gravity while preserving intervallic structure."
        ),
    },
    {
        "instance_id": "IMPOSSIBILITY_BELLS_THEOREM__RETROCAUSALITY",
        "comp_id": "IMPOSSIBILITY_BELLS_THEOREM",
        "system_id": None,
        "tradition": "Foundations of physics",
        "domain": "quantum_mechanics",
        "notes": (
            "Price & Wharton's retrocausal proposal resolves Bell's theorem by "
            "inverting the causal arrow: measurement settings at time t2 are allowed "
            "to influence the hidden-variable state at preparation time t1. This "
            "literally reverses the direction of causation — future boundary conditions "
            "constrain past states. The Bell inequality is no longer violated because "
            "the 'hidden variables' are not constrained to flow forward in time; they "
            "are time-symmetric. The damage is radical: the arrow of time becomes a "
            "convention rather than a physical law, and free choice of measurement "
            "settings is reinterpreted as constrained by future-to-past influence. "
            "| DAMAGE_OP: INVERT | STRATEGY: Reverse the causal arrow so correlations "
            "propagate backward from measurement to preparation, dissolving the need "
            "for nonlocality."
        ),
    },
    {
        "instance_id": "IMPOSSIBILITY_GOODHARTS_LAW__ADVERSARIAL_ROBUSTNESS",
        "comp_id": "IMPOSSIBILITY_GOODHARTS_LAW",
        "system_id": None,
        "tradition": "Machine learning",
        "domain": "computer_science",
        "notes": (
            "Adversarial robustness training inverts the optimization direction: "
            "instead of minimizing loss on natural inputs, the inner loop MAXIMIZES "
            "loss by searching for worst-case perturbations (adversarial examples). "
            "The outer loop then minimizes loss on these adversarial inputs. This "
            "min-max game is a structural inversion of standard training — the "
            "gradient direction is deliberately reversed in the inner loop. The "
            "result is a model that is robust to the exact gaming strategies that "
            "Goodhart's Law predicts: optimizing a metric creates exploitable "
            "shortcuts, so INVERT finds and patches them. The damage is reduced "
            "clean accuracy (typically 5-15% drop) and significantly higher "
            "computational cost (3-10x training time). "
            "| DAMAGE_OP: INVERT | STRATEGY: Reverse the optimization direction to "
            "find metric-gaming attacks, then train against them."
        ),
    },
]


def match_invert_pattern(notes: str) -> bool:
    """Check if notes text contains inversion/reversal semantics."""
    if not notes:
        return False
    nl = notes.lower()
    for pattern in INVERT_PATTERNS:
        if re.search(pattern, nl):
            return True
    return False


def already_has_invert_tag(notes: str) -> bool:
    """Check if notes already contain a DAMAGE_OP: INVERT tag."""
    if not notes:
        return False
    return bool(re.search(r'DAMAGE_OP:\s*INVERT', notes))


def main():
    con = duckdb.connect(DB_PATH)

    # ========== PHASE 1: Tag existing instances ==========
    print("=" * 60)
    print("PHASE 1: Scanning existing instances for INVERT patterns")
    print("=" * 60)

    rows = con.execute(
        "SELECT instance_id, comp_id, notes FROM composition_instances"
    ).fetchall()
    print(f"Total composition_instances: {len(rows)}")

    tagged_count = 0
    tagged_ids = []

    for instance_id, comp_id, notes in rows:
        if instance_id in EXCLUDE_IDS:
            continue
        if not notes:
            continue
        if already_has_invert_tag(notes):
            continue
        if match_invert_pattern(notes):
            # Append ALSO_DAMAGE_OP: INVERT (don't overwrite existing tags)
            new_notes = notes.rstrip() + " | ALSO_DAMAGE_OP: INVERT"
            con.execute(
                "UPDATE composition_instances SET notes = ? WHERE instance_id = ?",
                [new_notes, instance_id],
            )
            tagged_count += 1
            tagged_ids.append(instance_id)
            print(f"  TAGGED: {instance_id}")
            # Show the matching snippet
            nl = notes.lower()
            for pattern in INVERT_PATTERNS:
                m = re.search(pattern, nl)
                if m:
                    start = max(0, m.start() - 30)
                    end = min(len(notes), m.end() + 30)
                    print(f"         match: ...{notes[start:end]}...")
                    break

    print(f"\nPhase 1 complete: {tagged_count} existing instances tagged with ALSO_DAMAGE_OP: INVERT")

    # ========== PHASE 2: Insert new canonical instances ==========
    print()
    print("=" * 60)
    print("PHASE 2: Inserting new canonical INVERT instances")
    print("=" * 60)

    inserted_count = 0
    for inst in NEW_INSTANCES:
        # Check if already exists
        existing = con.execute(
            "SELECT instance_id FROM composition_instances WHERE instance_id = ?",
            [inst["instance_id"]],
        ).fetchone()
        if existing:
            print(f"  SKIPPED (already exists): {inst['instance_id']}")
            continue

        # Verify the comp_id hub exists
        hub_check = con.execute(
            "SELECT COUNT(*) FROM composition_instances WHERE comp_id = ?",
            [inst["comp_id"]],
        ).fetchone()
        if hub_check[0] == 0:
            print(f"  WARNING: comp_id '{inst['comp_id']}' has no existing instances, inserting anyway")

        con.execute(
            """INSERT INTO composition_instances (instance_id, comp_id, system_id, tradition, domain, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [
                inst["instance_id"],
                inst["comp_id"],
                inst["system_id"],
                inst["tradition"],
                inst["domain"],
                inst["notes"],
            ],
        )
        inserted_count += 1
        print(f"  INSERTED: {inst['instance_id']}")

    print(f"\nPhase 2 complete: {inserted_count} new INVERT instances inserted")

    # ========== SUMMARY ==========
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    # Verify total INVERT coverage
    invert_direct = con.execute(
        "SELECT COUNT(*) FROM composition_instances WHERE notes LIKE '%DAMAGE_OP: INVERT%'"
    ).fetchone()[0]
    invert_also = con.execute(
        "SELECT COUNT(*) FROM composition_instances WHERE notes LIKE '%ALSO_DAMAGE_OP: INVERT%'"
    ).fetchone()[0]

    total = invert_direct + invert_also
    print(f"  Existing instances tagged (ALSO_DAMAGE_OP: INVERT): {tagged_count}")
    print(f"  New instances inserted (DAMAGE_OP: INVERT):         {inserted_count}")
    print(f"  Total INVERT instances now in database:             {total}")
    print(f"    - Primary DAMAGE_OP: INVERT:                      {invert_direct}")
    print(f"    - Secondary ALSO_DAMAGE_OP: INVERT:               {invert_also}")

    if tagged_ids:
        print(f"\n  Tagged instance IDs:")
        for tid in tagged_ids:
            print(f"    - {tid}")

    print(f"\n  New instance IDs:")
    for inst in NEW_INSTANCES:
        print(f"    - {inst['instance_id']}")

    con.close()
    print("\nDone. Database committed.")


if __name__ == "__main__":
    main()
