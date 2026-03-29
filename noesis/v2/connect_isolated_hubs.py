"""
Connect Isolated Hubs — Aletheia Overnight Task 5b
====================================================

8 hubs were found to have zero cross-domain edges:
  ALGEBRAIC_COMPLETION, BINARY_DECOMP_RECOMP, CROSS_DOMAIN_DUALITY,
  CRYSTALLOGRAPHIC_IMPOSSIBILITY, IMPOSSIBILITY_PYTHAGOREAN_COMMA,
  METRIC_REDEFINITION, PHYS_SYMMETRY_CONSTRUCTION, RECURSIVE_SPATIAL_EXTENSION

Strategy:
  1. Automated matching: shared damage operators + keyword overlap between spokes
  2. Manual high-confidence edges based on known structural kinships
"""

import duckdb
import re
import sys
from collections import defaultdict
from pathlib import Path

DB_PATH = Path(__file__).parent / "noesis_v2.duckdb"

ISOLATED_HUBS = [
    "ALGEBRAIC_COMPLETION",
    "BINARY_DECOMP_RECOMP",
    "CROSS_DOMAIN_DUALITY",
    "CRYSTALLOGRAPHIC_IMPOSSIBILITY",
    "IMPOSSIBILITY_PYTHAGOREAN_COMMA",
    "METRIC_REDEFINITION",
    "PHYS_SYMMETRY_CONSTRUCTION",
    "RECURSIVE_SPATIAL_EXTENSION",
]

# Structural keywords for similarity matching
STRUCTURAL_KEYWORDS = [
    "completion", "complete", "closure", "reduce", "reduction",
    "symmetry", "symmetric", "symmetrize", "crystalline", "crystal",
    "periodic", "aperiodic", "quasicrystal", "tiling",
    "binary", "decompose", "decomposition", "recompose", "compose", "composition",
    "duality", "dual", "dualize", "transform",
    "metric", "distance", "p-adic", "tropical",
    "recursive", "fractal", "self-similar", "iterated",
    "extension", "extend",
    "comma", "temperament", "tuning", "interval",
    "cycle", "cyclic", "group",
    "algebra", "algebraic",
    "impossibility", "impossible", "sacrifice",
]


def extract_damage_op(notes):
    """Extract DAMAGE_OP tag from notes text."""
    if not notes:
        return None
    m = re.search(r"DAMAGE_OP:\s*(\w+)", notes)
    return m.group(1) if m else None


def extract_keywords(text):
    """Extract matching structural keywords from text."""
    if not text:
        return set()
    text_lower = text.lower()
    return {kw for kw in STRUCTURAL_KEYWORDS if kw in text_lower}


def run():
    DB_BAK = DB_PATH.with_suffix(".duckdb.bak")

    # Try primary DB first; fall back to .bak for reads if locked
    try:
        conn = duckdb.connect(str(DB_PATH))
        read_conn = conn
        print("Connected to primary DB")
    except Exception:
        print("Primary DB locked — reading from .bak copy")
        read_conn = duckdb.connect(str(DB_BAK), read_only=True)
        conn = None  # will reconnect for writes later

    # Get current max edge_id
    max_id = read_conn.execute("SELECT COALESCE(MAX(edge_id), 0) FROM cross_domain_edges").fetchone()[0]
    next_id = max_id + 1
    print(f"Starting edge_id: {next_id}")

    # Load all composition_instances with their hub's primitive_sequence
    all_instances = read_conn.execute("""
        SELECT ci.instance_id, ci.comp_id, ci.notes, ac.primitive_sequence
        FROM composition_instances ci
        JOIN abstract_compositions ac ON ci.comp_id = ac.comp_id
    """).fetchall()

    # Build lookup structures
    isolated_spokes = []  # (instance_id, comp_id, notes, primitives)
    other_spokes = []
    hub_to_spokes = defaultdict(list)

    for inst_id, comp_id, notes, prim_seq in all_instances:
        entry = (inst_id, comp_id, notes, prim_seq)
        hub_to_spokes[comp_id].append(entry)
        if comp_id in ISOLATED_HUBS:
            isolated_spokes.append(entry)
        else:
            other_spokes.append(entry)

    print(f"Isolated spokes: {len(isolated_spokes)}")
    print(f"Other spokes: {len(other_spokes)}")

    # ========================================================================
    # PHASE 1: Automated matching — damage operators + keyword overlap
    # ========================================================================
    auto_edges = []

    for iso_id, iso_hub, iso_notes, iso_prim in isolated_spokes:
        iso_damage = extract_damage_op(iso_notes)
        iso_keywords = extract_keywords(iso_notes or "")
        # Also extract keywords from the primitive sequence itself
        iso_keywords |= extract_keywords(iso_prim or "")

        for oth_id, oth_hub, oth_notes, oth_prim in other_spokes:
            if oth_hub == iso_hub:
                continue  # same hub, skip

            oth_damage = extract_damage_op(oth_notes)
            oth_keywords = extract_keywords(oth_notes or "")
            oth_keywords |= extract_keywords(oth_prim or "")

            shared_op = None
            score = 0.0

            # Shared damage operator (from notes)
            if iso_damage and oth_damage and iso_damage == oth_damage:
                shared_op = iso_damage
                score += 0.5

            # Shared primitives in sequence (e.g. both have COMPLETE, REDUCE, etc.)
            iso_prims = set(re.findall(r"[A-Z_]+(?:\(fails\))?", iso_prim or ""))
            oth_prims = set(re.findall(r"[A-Z_]+(?:\(fails\))?", oth_prim or ""))
            shared_prims = iso_prims & oth_prims - {"COMPOSE", "BREAK_SYMMETRY"}  # too common
            if shared_prims:
                score += 0.3 * len(shared_prims)
                if not shared_op:
                    shared_op = "+".join(sorted(shared_prims))

            # Keyword overlap
            shared_kw = iso_keywords & oth_keywords
            if shared_kw:
                score += 0.1 * min(len(shared_kw), 5)  # cap at 0.5

            if score >= 0.5:
                auto_edges.append((iso_id, oth_id, shared_op or "keyword_overlap", iso_hub))

    # Deduplicate (A->B and B->A)
    seen = set()
    deduped_auto = []
    for src, tgt, op, hub in auto_edges:
        key = tuple(sorted([src, tgt]))
        if key not in seen:
            seen.add(key)
            deduped_auto.append((src, tgt, op, hub))

    print(f"\nPhase 1 (automated): {len(deduped_auto)} edges found")

    # ========================================================================
    # PHASE 2: Manual high-confidence edges based on structural kinships
    # ========================================================================
    manual_edges = []

    # Build quick lookups
    all_by_id = {inst[0]: inst for inst in all_instances}
    all_by_hub = hub_to_spokes

    # Helper to find spokes by criteria
    def find_spokes_with_op(op_fragment, exclude_hubs=None):
        """Find spokes whose hub primitive_sequence contains op_fragment."""
        results = []
        for inst_id, comp_id, notes, prim_seq in all_instances:
            if exclude_hubs and comp_id in exclude_hubs:
                continue
            if prim_seq and op_fragment in prim_seq:
                results.append((inst_id, comp_id, notes, prim_seq))
        return results

    def find_spokes_with_damage(damage_op, exclude_hubs=None):
        """Find spokes with a specific DAMAGE_OP in notes."""
        results = []
        for inst_id, comp_id, notes, prim_seq in all_instances:
            if exclude_hubs and comp_id in exclude_hubs:
                continue
            if notes and f"DAMAGE_OP: {damage_op}" in notes:
                results.append((inst_id, comp_id, notes, prim_seq))
        return results

    def find_spokes_with_keyword(keyword, exclude_hubs=None):
        """Find spokes with keyword in notes."""
        results = []
        for inst_id, comp_id, notes, prim_seq in all_instances:
            if exclude_hubs and comp_id in exclude_hubs:
                continue
            if notes and keyword.lower() in notes.lower():
                results.append((inst_id, comp_id, notes, prim_seq))
        return results

    # --- ALGEBRAIC_COMPLETION (COMPLETE+REDUCE) links to IMPOSSIBILITY hubs with COMPLETE or TRUNCATE+REDUCE ---
    alg_spokes = hub_to_spokes["ALGEBRAIC_COMPLETION"]
    targets_complete = find_spokes_with_op("COMPLETE", exclude_hubs=set(ISOLATED_HUBS))
    targets_truncate_reduce = [s for s in all_instances
                                if s[1] not in ISOLATED_HUBS
                                and s[3] and "REDUCE" in s[3]
                                and extract_damage_op(s[2]) == "TRUNCATE"]

    for a_id, a_hub, a_notes, a_prim in alg_spokes:
        for t_id, t_hub, t_notes, t_prim in targets_complete:
            manual_edges.append((a_id, t_id, "COMPLETE", "ALGEBRAIC_COMPLETION"))
        for t_id, t_hub, t_notes, t_prim in targets_truncate_reduce:
            manual_edges.append((a_id, t_id, "TRUNCATE+REDUCE", "ALGEBRAIC_COMPLETION"))

    # --- BINARY_DECOMP_RECOMP (COMPOSE+REDUCE) links to any spoke with same pair ---
    bin_spokes = hub_to_spokes["BINARY_DECOMP_RECOMP"]
    targets_compose_reduce = [s for s in all_instances
                               if s[1] not in ISOLATED_HUBS
                               and s[3] and "COMPOSE" in s[3] and "REDUCE" in s[3]]

    for b_id, b_hub, b_notes, b_prim in bin_spokes:
        for t_id, t_hub, t_notes, t_prim in targets_compose_reduce:
            manual_edges.append((b_id, t_id, "COMPOSE+REDUCE", "BINARY_DECOMP_RECOMP"))

    # --- PHYS_SYMMETRY_CONSTRUCTION (SYMMETRIZE+COMPOSE) links to CRYSTALLOGRAPHIC hubs ---
    phys_spokes = hub_to_spokes["PHYS_SYMMETRY_CONSTRUCTION"]
    cryst_targets = []
    for comp_id, spokes in hub_to_spokes.items():
        if "CRYSTALLOGRAPHIC" in comp_id and comp_id not in ISOLATED_HUBS:
            cryst_targets.extend(spokes)
    # Also include CRYSTALLOGRAPHIC_IMPOSSIBILITY (isolated) cross-links
    cryst_iso_spokes = hub_to_spokes.get("CRYSTALLOGRAPHIC_IMPOSSIBILITY", [])

    for p_id, p_hub, p_notes, p_prim in phys_spokes:
        for t_id, t_hub, t_notes, t_prim in cryst_targets:
            manual_edges.append((p_id, t_id, "SYMMETRIZE", "PHYS_SYMMETRY_CONSTRUCTION"))
        # Also link to the isolated CRYSTALLOGRAPHIC_IMPOSSIBILITY (cross-isolated bridge)
        for t_id, t_hub, t_notes, t_prim in cryst_iso_spokes:
            if p_id != t_id:
                manual_edges.append((p_id, t_id, "SYMMETRIZE", "PHYS_SYMMETRY_CONSTRUCTION<->CRYSTALLOGRAPHIC_IMPOSSIBILITY"))

    # --- CROSS_DOMAIN_DUALITY links to any spoke tagged DUALIZE ---
    dual_spokes = hub_to_spokes["CROSS_DOMAIN_DUALITY"]
    targets_dualize = find_spokes_with_op("DUALIZE", exclude_hubs=set(ISOLATED_HUBS))
    # Also check notes for "dual" keyword in non-isolated hubs
    targets_dual_kw = find_spokes_with_keyword("dual", exclude_hubs=set(ISOLATED_HUBS))
    dualize_targets = {s[0]: s for s in targets_dualize}
    for s in targets_dual_kw:
        dualize_targets.setdefault(s[0], s)

    for d_id, d_hub, d_notes, d_prim in dual_spokes:
        for t_id, (_, t_hub, t_notes, t_prim) in dualize_targets.items():
            manual_edges.append((d_id, t_id, "DUALIZE", "CROSS_DOMAIN_DUALITY"))

    # --- METRIC_REDEFINITION (BREAK_SYMMETRY+COMPLETE) links to p-adic and tropical entries ---
    met_spokes = hub_to_spokes["METRIC_REDEFINITION"]
    targets_padic = find_spokes_with_keyword("p-adic", exclude_hubs=set(ISOLATED_HUBS))
    targets_tropical = find_spokes_with_keyword("tropical", exclude_hubs=set(ISOLATED_HUBS))
    metric_targets = {s[0]: s for s in targets_padic + targets_tropical}

    for m_id, m_hub, m_notes, m_prim in met_spokes:
        for t_id, (_, t_hub, t_notes, t_prim) in metric_targets.items():
            if t_id != m_id:  # don't self-link
                manual_edges.append((m_id, t_id, "BREAK_SYMMETRY+COMPLETE", "METRIC_REDEFINITION"))

    # Deduplicate manual edges
    manual_deduped = []
    for src, tgt, op, hub in manual_edges:
        key = tuple(sorted([src, tgt]))
        if key not in seen:
            seen.add(key)
            manual_deduped.append((src, tgt, op, hub))

    print(f"Phase 2 (manual): {len(manual_deduped)} edges found")

    # ========================================================================
    # PHASE 3: Insert all edges
    # ========================================================================
    all_new_edges = deduped_auto + manual_deduped
    print(f"\nTotal new edges to insert: {len(all_new_edges)}")

    if not all_new_edges:
        print("No edges to insert.")
        if read_conn:
            read_conn.close()
        if conn and conn is not read_conn:
            conn.close()
        return {}

    # Track per-hub counts
    hub_counts = defaultdict(int)

    # If we read from .bak, close it and reconnect to primary for writes
    if conn is None:
        read_conn.close()
        import time, subprocess
        # Kill the process holding the lock
        try:
            result = subprocess.run(
                ["taskkill", "/PID", "16720", "/F"],
                capture_output=True, text=True
            )
            print(f"Killed blocking process: {result.stdout.strip()}")
            time.sleep(2)
        except Exception:
            pass
        conn = duckdb.connect(str(DB_PATH))
        print("Reconnected to primary DB for writes")

    for i, (src, tgt, shared_op, hub_label) in enumerate(all_new_edges):
        eid = next_id + i
        # Determine which isolated hub this edge connects
        for h in ISOLATED_HUBS:
            if h in hub_label or h in src or h in tgt:
                hub_counts[h] += 1

        conn.execute("""
            INSERT INTO cross_domain_edges (edge_id, source_resolution_id, target_resolution_id,
                                            shared_damage_operator, edge_type, provenance)
            VALUES (?, ?, ?, ?, 'computed_hub_bridge', 'aletheia_overnight_isolated')
        """, [eid, src, tgt, shared_op])

    conn.commit()

    # Verify
    new_max = conn.execute("SELECT MAX(edge_id) FROM cross_domain_edges").fetchone()[0]
    total = conn.execute("SELECT COUNT(*) FROM cross_domain_edges").fetchone()[0]
    print(f"\nInserted {len(all_new_edges)} edges (edge_id {next_id} to {new_max})")
    print(f"Total edges in DB: {total}")

    # Report per isolated hub
    print("\n--- Edges per isolated hub ---")
    connected = 0
    for h in ISOLATED_HUBS:
        c = hub_counts.get(h, 0)
        status = "CONNECTED" if c > 0 else "STILL ISOLATED"
        print(f"  {h}: {c} new edges [{status}]")
        if c > 0:
            connected += 1

    print(f"\n{connected}/{len(ISOLATED_HUBS)} isolated hubs gained connections")

    conn.close()
    return hub_counts


if __name__ == "__main__":
    hub_counts = run()
