"""
Ethnomathematics Primitive Vector Enrichment
=============================================
Scans text fields of all 153 ethnomathematics entries for structural
indicators mapped to the 11 Noesis primitives, producing enriched
11-dimensional vectors stored as JSON arrays of [primitive, score] pairs.
"""

import duckdb
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

DB_PATH = Path(__file__).parent / "noesis_v2.duckdb"
JOURNAL_PATH = Path(__file__).resolve().parent.parent.parent / "journal" / "2026-03-29-overnight.md"

# Signal words for each primitive (case-insensitive matching)
PRIMITIVE_SIGNALS = {
    "COMPOSE": [
        "compose", "combine", "aggregate", "assemble", "layer", "chain",
        "sequence", "step", "procedure", "algorithm", "iterate", "recursive",
        "concatenate", "multi-step", "build", "construct"
    ],
    "MAP": [
        "map", "encode", "represent", "convert", "translate", "notation",
        "positional", "base", "symbol", "correspond", "morphism", "digit",
        "numeral", "transform", "cipher", "table", "lookup"
    ],
    "EXTEND": [
        "extend", "generalize", "fractal", "hierarchy", "higher-order",
        "adjoin", "construct", "tower", "infinite", "transfinite",
        "recursive struct", "expand", "augment", "enlarge", "add dimension"
    ],
    "REDUCE": [
        "reduce", "decompose", "extract", "project", "classify", "count",
        "eliminate", "simplify", "quotient", "factor", "sum", "total",
        "aggregate", "compress", "collapse", "condense", "distill"
    ],
    "LIMIT": [
        "limit", "convergence", "series", "asymptot", "iterative refine",
        "precision", "tends to", "infinite series", "approximat", "approach",
        "converge", "settle"
    ],
    "DUALIZE": [
        "dual", "inverse", "conjugate", "fourier", "transform pair",
        "frequency", "opposite", "mirror", "deficit", "complement",
        "reciprocal", "negat", "reverse", "adjoint"
    ],
    "LINEARIZE": [
        "linear", "tangent", "differential", "perturbat", "jacobian",
        "first-order", "local approx", "matrix method", "rod", "board",
        "flatten", "interpolat"
    ],
    "STOCHASTICIZE": [
        "random", "probabilist", "stochastic", "divination", "gambling",
        "noise", "uncertain", "estimation", "approximate number", "oracle",
        "chance", "fortune", "lot", "dice"
    ],
    "SYMMETRIZE": [
        "symmetr", "invariant", "group action", "wallpaper", "reflection",
        "rotation", "periodic", "tiling", "pattern repeat", "balance",
        "harmony", "regular", "congruence"
    ],
    "BREAK_SYMMETRY": [
        "break", "subtractive", "asymmetr", "non-standard", "irregular",
        "modified base", "selection", "non-equal", "deviation", "exception",
        "anomal", "defect"
    ],
    "COMPLETE": [
        "complete", "closure", "universal", "unique determin", "all roots",
        "fills", "maximal", "al-jabr", "balancing", "satisfy", "exhaust"
    ],
}

# Pre-compile regex patterns for each primitive
PRIMITIVE_PATTERNS = {}
for prim, signals in PRIMITIVE_SIGNALS.items():
    # Build alternation pattern; signals with spaces are treated as phrases
    escaped = [re.escape(s) for s in signals]
    PRIMITIVE_PATTERNS[prim] = re.compile(
        r'\b(?:' + '|'.join(escaped) + r')', re.IGNORECASE
    )

TEXT_FIELDS = ["description", "key_operations", "structural_features", "unique_aspects"]
ALL_PRIMITIVES = list(PRIMITIVE_SIGNALS.keys())


def scan_entry(row_dict):
    """Count signal matches per primitive across all text fields."""
    combined_text = " ".join(str(row_dict.get(f) or "") for f in TEXT_FIELDS)
    counts = {}
    for prim, pattern in PRIMITIVE_PATTERNS.items():
        matches = pattern.findall(combined_text)
        counts[prim] = len(matches)
    return counts


def normalize_vector(counts):
    """Normalize by max count, yielding 0-1 scores."""
    max_val = max(counts.values()) if counts else 0
    if max_val == 0:
        return {p: 0.0 for p in ALL_PRIMITIVES}
    return {p: round(counts[p] / max_val, 3) for p in ALL_PRIMITIVES}


def to_json_pairs(norm_vec):
    """Convert to sorted [name, score] pairs, nonzero only."""
    pairs = [[p, s] for p, s in norm_vec.items() if s > 0]
    pairs.sort(key=lambda x: -x[1])
    return pairs


def main():
    DB_BAK = DB_PATH.with_suffix(".duckdb.bak")
    # Try read-write on main DB; fall back to read-only on backup
    db_locked = False
    try:
        con = duckdb.connect(str(DB_PATH))
    except Exception:
        db_locked = True
        con = duckdb.connect(str(DB_BAK), read_only=True)
        print("NOTE: Main DB locked. Reading from backup.")

    # ── 1. Read existing vectors ──
    rows = con.execute("""
        SELECT system_id, description, key_operations, structural_features,
               unique_aspects, candidate_primitives_noesis
        FROM ethnomathematics
    """).fetchall()
    col_names = ["system_id", "description", "key_operations",
                 "structural_features", "unique_aspects",
                 "candidate_primitives_noesis"]

    before_counts = []
    after_counts = []
    enriched = {}
    changes = []  # (system_id, before_nz, after_nz, delta)
    prim_distribution = Counter()

    for row in rows:
        d = dict(zip(col_names, row))
        sid = d["system_id"]

        # Before: parse existing vector
        existing = json.loads(d["candidate_primitives_noesis"]) if d["candidate_primitives_noesis"] else []
        existing_dict = {p: s for p, s in existing}
        before_nz = len(existing)
        before_counts.append(before_nz)

        # Scan text fields for additional signals
        raw_counts = scan_entry(d)
        norm_vec = normalize_vector(raw_counts)

        # Merge: take max of existing score and text-scanned score for each primitive
        merged = {}
        for p in ALL_PRIMITIVES:
            old_score = existing_dict.get(p, 0.0)
            new_score = norm_vec.get(p, 0.0)
            best = max(old_score, new_score)
            if best > 0:
                merged[p] = round(best, 3)

        pairs = [[p, s] for p, s in merged.items()]
        pairs.sort(key=lambda x: -x[1])

        after_nz = len(pairs)
        after_counts.append(after_nz)
        enriched[sid] = json.dumps(pairs)
        changes.append((sid, before_nz, after_nz, after_nz - before_nz))

        for p, _ in pairs:
            prim_distribution[p] += 1

    # ── 2. Store results ──
    con.close()

    # Write enriched vectors back to DB
    if db_locked:
        # Save to staging JSON; also write to the backup DB
        staging_path = DB_PATH.parent / "enriched_vectors_staging.json"
        with open(staging_path, "w", encoding="utf-8") as f:
            json.dump(enriched, f)
        # Write column to the backup DB (which we can open r/w)
        con2 = duckdb.connect(str(DB_BAK))
        try:
            con2.execute("ALTER TABLE ethnomathematics ADD COLUMN enriched_primitive_vector VARCHAR")
        except Exception:
            pass
        for sid, vec_json in enriched.items():
            con2.execute(
                "UPDATE ethnomathematics SET enriched_primitive_vector = ? WHERE system_id = ?",
                [vec_json, sid]
            )
        con2.close()
        print(f"Enriched vectors written to backup DB and staging JSON.")
        print(f"When main DB unlocks, run this script again to apply to main DB.")
    else:
        con = duckdb.connect(str(DB_PATH))
        try:
            con.execute("ALTER TABLE ethnomathematics ADD COLUMN enriched_primitive_vector VARCHAR")
        except Exception:
            pass
        for sid, vec_json in enriched.items():
            con.execute(
                "UPDATE ethnomathematics SET enriched_primitive_vector = ? WHERE system_id = ?",
                [vec_json, sid]
            )
        con.close()
        print("Enriched vectors written to main DB.")

    # ── 3. Report ──
    mean_before = sum(before_counts) / len(before_counts)
    mean_after = sum(after_counts) / len(after_counts)

    changes.sort(key=lambda x: -x[3])
    top10 = changes[:10]

    report_lines = []
    report_lines.append("## Task 4: Ethnomathematics Primitive Vector Enrichment")
    report_lines.append("")
    report_lines.append(f"- **Entries processed**: {len(rows)}")
    report_lines.append(f"- **Mean nonzero primitives BEFORE**: {mean_before:.2f}")
    report_lines.append(f"- **Mean nonzero primitives AFTER**: {mean_after:.2f}")
    report_lines.append(f"- **Enrichment factor**: {mean_after/mean_before:.1f}x")
    report_lines.append("")
    report_lines.append("### Top 10 entries with largest enrichment")
    report_lines.append("")
    report_lines.append("| System ID | Before | After | Delta |")
    report_lines.append("|-----------|--------|-------|-------|")
    for sid, b, a, delta in top10:
        report_lines.append(f"| {sid} | {b} | {a} | +{delta} |")
    report_lines.append("")
    report_lines.append("### Primitive distribution across enriched vectors")
    report_lines.append("")
    report_lines.append("| Primitive | Entries with nonzero |")
    report_lines.append("|-----------|---------------------|")
    for prim in ALL_PRIMITIVES:
        report_lines.append(f"| {prim} | {prim_distribution.get(prim, 0)} |")
    report_lines.append("")

    report = "\n".join(report_lines)
    print(report)

    # Append to journal
    with open(JOURNAL_PATH, "a", encoding="utf-8") as f:
        f.write("\n" + report)

    print(f"\nResults appended to {JOURNAL_PATH}")


if __name__ == "__main__":
    main()
