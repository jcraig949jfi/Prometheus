"""
Noesis v2 — Depth-2 Composition Discovery

Identifies named two-operator compositions (depth-2 chains) across all
complete hubs (9/9 damage operator coverage). For each hub where two
damage operators are both present, checks whether their combination
corresponds to a NAMED construction from the verified composition catalog.

Inserts composition_instances tagged with COMPOSITION: OP1 → OP2.
"""

import duckdb
import sys
import re
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

DB_PATH = Path(__file__).parent / "noesis_v2.duckdb"

# ── Named depth-2 compositions ──────────────────────────────────────────
# Each entry: (name, description, construction_op1, construction_op2, damage_op1, damage_op2)
# The construction operators are the "what you do" side.
# The damage operators are the "what breaks / what gets applied" side.
#
# Mapping from task:
#   EXTEND → REDUCE  (construction)  =  EXTEND → TRUNCATE  (damage)  = Variational principle
#   REDUCE → MAP     (construction)  =  TRUNCATE → QUANTIZE (damage) = Renormalization
#   MAP → EXTEND     (construction)  =  QUANTIZE → EXTEND  (damage)  = Quantization
#   DUALIZE → MAP    (construction)  =  HIERARCHIZE → QUANTIZE (damage) = Fourier analysis
#   EXTEND → SYMMETRIZE (construction) = EXTEND → DISTRIBUTE (damage) = Gauge theory
#   SYMMETRIZE → BREAK_SYMMETRY (construction) = DISTRIBUTE → CONCENTRATE (damage) = SSB
#   STOCHASTICIZE → REDUCE (construction) = RANDOMIZE → TRUNCATE (damage) = Path integral
#   STOCHASTICIZE → LIMIT  (construction) = RANDOMIZE → TRUNCATE (damage) = Statistical mechanics
#     (Note: STOCHASTICIZE→LIMIT and STOCHASTICIZE→REDUCE both map to RANDOMIZE→TRUNCATE;
#      we distinguish them by name but they share the damage pair)
#   EXTEND → COMPLETE (construction) — no direct damage pair listed, skip
#   BREAK_SYMMETRY → COMPLETE (construction) — no direct damage pair listed, skip

DEPTH2_COMPOSITIONS = [
    {
        "name": "Variational principle",
        "desc": "Extend to all paths, reduce to extremum",
        "construction": ("EXTEND", "REDUCE"),
        "damage": ("EXTEND", "TRUNCATE"),
    },
    {
        "name": "Renormalization",
        "desc": "Coarse-grain then rescale",
        "construction": ("REDUCE", "MAP"),
        "damage": ("TRUNCATE", "QUANTIZE"),
    },
    {
        "name": "Quantization",
        "desc": "Poisson bracket to commutator, extend to Hilbert space",
        "construction": ("MAP", "EXTEND"),
        "damage": ("QUANTIZE", "EXTEND"),
    },
    {
        "name": "Fourier analysis",
        "desc": "Transform domain then operate",
        "construction": ("DUALIZE", "MAP"),
        "damage": ("HIERARCHIZE", "QUANTIZE"),
    },
    {
        "name": "Gauge theory",
        "desc": "Enlarge symmetry group then constrain by gauge invariance",
        "construction": ("EXTEND", "SYMMETRIZE"),
        "damage": ("EXTEND", "DISTRIBUTE"),
    },
    {
        "name": "Spontaneous symmetry breaking",
        "desc": "Define symmetry then break it to select ground state",
        "construction": ("SYMMETRIZE", "BREAK_SYMMETRY"),
        "damage": ("DISTRIBUTE", "CONCENTRATE"),
    },
    {
        "name": "Path integral",
        "desc": "Sum over stochastic paths then reduce to amplitude",
        "construction": ("STOCHASTICIZE", "REDUCE"),
        "damage": ("RANDOMIZE", "TRUNCATE"),
    },
    {
        "name": "Statistical mechanics",
        "desc": "Introduce noise then take thermodynamic limit",
        "construction": ("STOCHASTICIZE", "LIMIT"),
        "damage": ("RANDOMIZE", "TRUNCATE"),
    },
    {
        "name": "Hierarchical decomposition",
        "desc": "Stratify into levels then partition within levels",
        "construction": ("DUALIZE", "BREAK_SYMMETRY"),
        "damage": ("HIERARCHIZE", "PARTITION"),
    },
    {
        "name": "Coarse-graining cascade",
        "desc": "Truncate detail then partition into blocks",
        "construction": ("REDUCE", "BREAK_SYMMETRY"),
        "damage": ("TRUNCATE", "PARTITION"),
    },
    {
        "name": "Duality inversion",
        "desc": "Hierarchize then invert to dual description",
        "construction": ("DUALIZE", "DUALIZE"),
        "damage": ("HIERARCHIZE", "INVERT"),
    },
    {
        "name": "Discretization",
        "desc": "Quantize continuous into discrete then truncate to finite",
        "construction": ("MAP", "REDUCE"),
        "damage": ("QUANTIZE", "TRUNCATE"),
    },
    {
        "name": "Noise injection",
        "desc": "Randomize then distribute across ensemble",
        "construction": ("STOCHASTICIZE", "SYMMETRIZE"),
        "damage": ("RANDOMIZE", "DISTRIBUTE"),
    },
    {
        "name": "Spectral concentration",
        "desc": "Hierarchize frequencies then concentrate to dominant mode",
        "construction": ("DUALIZE", "BREAK_SYMMETRY"),
        "damage": ("HIERARCHIZE", "CONCENTRATE"),
    },
]

# Deduplicate by damage pair — if two compositions share same damage pair,
# keep both but note it. We key on (damage_op1, damage_op2).
# Actually, we want ALL named compositions found, so no dedup needed.
# Build lookup: damage pair → list of compositions
PAIR_TO_COMPOSITIONS = {}
for comp in DEPTH2_COMPOSITIONS:
    pair = (comp["damage"][0], comp["damage"][1])
    if pair not in PAIR_TO_COMPOSITIONS:
        PAIR_TO_COMPOSITIONS[pair] = []
    PAIR_TO_COMPOSITIONS[pair].append(comp)

ALL_DAMAGE_OPS = [
    "DISTRIBUTE", "CONCENTRATE", "TRUNCATE", "EXTEND",
    "RANDOMIZE", "HIERARCHIZE", "PARTITION", "QUANTIZE", "INVERT"
]


def extract_damage_op(notes: str) -> str | None:
    """Extract damage operator from notes field."""
    if not notes:
        return None
    # Primary pattern: DAMAGE_OP: OPNAME
    m = re.search(r"DAMAGE_OP:\s*(\w+)", notes)
    if m:
        return m.group(1)
    # Also check ALSO_DAMAGE_OP
    m = re.search(r"ALSO_DAMAGE_OP:\s*(\w+)", notes)
    if m:
        return m.group(1)
    return None


def get_complete_hubs(db, min_coverage=9):
    """Get all hubs with >= min_coverage distinct damage operators."""
    rows = db.execute("""
        SELECT comp_id, instance_id, notes
        FROM composition_instances
        WHERE notes LIKE '%DAMAGE_OP%'
        ORDER BY comp_id
    """).fetchall()

    # Build hub → {damage_op: [instance_ids]}
    hubs = {}
    for comp_id, instance_id, notes in rows:
        op = extract_damage_op(notes)
        if op and op in ALL_DAMAGE_OPS:
            if comp_id not in hubs:
                hubs[comp_id] = {}
            if op not in hubs[comp_id]:
                hubs[comp_id][op] = []
            hubs[comp_id][op].append(instance_id)

    # Filter to complete hubs
    complete = {
        hub_id: ops
        for hub_id, ops in hubs.items()
        if len(ops) >= min_coverage
    }
    return complete


def find_compositions(complete_hubs):
    """For each complete hub, find all depth-2 composition pairs."""
    results = []

    for hub_id, hub_ops in sorted(complete_hubs.items()):
        ops_present = set(hub_ops.keys())

        for (op1, op2), compositions in PAIR_TO_COMPOSITIONS.items():
            if op1 in ops_present and op2 in ops_present:
                for comp in compositions:
                    # Get the source spoke instance_ids
                    spoke1_ids = hub_ops[op1]
                    spoke2_ids = hub_ops[op2]
                    results.append({
                        "hub_id": hub_id,
                        "op1": op1,
                        "op2": op2,
                        "name": comp["name"],
                        "desc": comp["desc"],
                        "construction": comp["construction"],
                        "spoke1_sample": spoke1_ids[0] if spoke1_ids else None,
                        "spoke2_sample": spoke2_ids[0] if spoke2_ids else None,
                    })

    return results


def insert_compositions(db, compositions):
    """Insert composition instances into the database."""
    inserted = 0
    skipped = 0

    for comp in compositions:
        hub_id = comp["hub_id"]
        op1 = comp["op1"]
        op2 = comp["op2"]
        name = comp["name"]
        desc = comp["desc"]
        c_op1, c_op2 = comp["construction"]

        instance_id = f"{hub_id}__COMP_{op1}_{op2}"

        # If same damage pair yields multiple named compositions,
        # append the composition name to disambiguate
        if len(PAIR_TO_COMPOSITIONS.get((op1, op2), [])) > 1:
            safe_name = name.replace(" ", "_").replace("/", "_")
            instance_id = f"{hub_id}__COMP_{op1}_{op2}__{safe_name}"

        notes = (
            f"{name}: {c_op1} then {c_op2} on this hub. "
            f"| COMPOSITION: {c_op1} → {c_op2} "
            f"| DAMAGE_PAIR: {op1} → {op2} "
            f"| SOURCE: composition_depth2"
        )

        # Check if already exists
        existing = db.execute(
            "SELECT 1 FROM composition_instances WHERE instance_id = ?",
            [instance_id]
        ).fetchone()

        if existing:
            skipped += 1
            continue

        db.execute(
            """INSERT INTO composition_instances (instance_id, comp_id, system_id, tradition, domain, notes)
               VALUES (?, ?, NULL, 'depth-2 composition', 'cross-domain', ?)""",
            [instance_id, hub_id, notes]
        )
        inserted += 1

    return inserted, skipped


def report(complete_hubs, compositions):
    """Print summary report."""
    print("=" * 70)
    print("DEPTH-2 COMPOSITION DISCOVERY REPORT")
    print("=" * 70)
    print(f"\nComplete hubs (9/9 coverage): {len(complete_hubs)}")
    print(f"Total depth-2 compositions found: {len(compositions)}")

    # Count by composition name
    name_counts = {}
    for c in compositions:
        name_counts[c["name"]] = name_counts.get(c["name"], 0) + 1
    print(f"\nComposition type distribution:")
    for name, count in sorted(name_counts.items(), key=lambda x: -x[1]):
        print(f"  {name}: {count} hubs")

    # Count by damage pair
    pair_counts = {}
    for c in compositions:
        pair = f"{c['op1']} → {c['op2']}"
        pair_counts[pair] = pair_counts.get(pair, 0) + 1
    print(f"\nDamage pair distribution:")
    for pair, count in sorted(pair_counts.items(), key=lambda x: -x[1]):
        print(f"  {pair}: {count}")

    # Hubs with most compositions
    hub_comp_counts = {}
    for c in compositions:
        hub_comp_counts[c["hub_id"]] = hub_comp_counts.get(c["hub_id"], 0) + 1

    print(f"\nHubs with most compositions:")
    top_hubs = sorted(hub_comp_counts.items(), key=lambda x: -x[1])[:15]
    for hub, count in top_hubs:
        print(f"  {hub}: {count} compositions")

    # Hubs with fewest
    bottom_hubs = sorted(hub_comp_counts.items(), key=lambda x: x[1])[:5]
    print(f"\nHubs with fewest compositions:")
    for hub, count in bottom_hubs:
        print(f"  {hub}: {count} compositions")

    # Average compositions per hub
    if hub_comp_counts:
        avg = sum(hub_comp_counts.values()) / len(hub_comp_counts)
        print(f"\nAverage compositions per hub: {avg:.1f}")

    return name_counts, hub_comp_counts


def main():
    db = duckdb.connect(str(DB_PATH))

    print("Loading complete hubs...")
    complete_hubs = get_complete_hubs(db, min_coverage=9)
    print(f"Found {len(complete_hubs)} hubs with 9/9 damage operator coverage")

    print("\nScanning for depth-2 composition patterns...")
    compositions = find_compositions(complete_hubs)

    print(f"Found {len(compositions)} composition instances")

    print("\nInserting into database...")
    inserted, skipped = insert_compositions(db, compositions)
    print(f"Inserted: {inserted}, Skipped (already exist): {skipped}")

    name_counts, hub_comp_counts = report(complete_hubs, compositions)

    db.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
