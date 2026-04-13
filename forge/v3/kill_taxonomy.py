#!/usr/bin/env python3
"""
Kill Taxonomy: Structured database of all kills and constraints.
The Nemesis layer's memory. Every kill tightens the search space.
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "kill_taxonomy.db"


def init_db(db_path=None):
    """Create the kill taxonomy database and seed with known kills."""
    if db_path is None:
        db_path = DB_PATH

    con = sqlite3.connect(str(db_path))
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS kills (
            kill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            hypothesis_type TEXT,
            failure_mode TEXT,
            f_test TEXT,
            domain TEXT,
            description TEXT,
            constraint_added TEXT,
            timestamp TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS negative_dimensions (
            dim_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dimension TEXT UNIQUE,
            description TEXT,
            kills_that_proved_it TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS constraints (
            constraint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            constraint_type TEXT,
            field TEXT,
            operator TEXT,
            value TEXT,
            source_kill INTEGER,
            FOREIGN KEY(source_kill) REFERENCES kills(kill_id)
        )
    """)

    # Seed with the 21 known kills
    known_kills = [
        ("cross_domain_transfer", "ordinal_alignment", "F33", "cross-domain", "Arithmos transfer rho=0.61 — random small integers give same", "NOT ordinal matching"),
        ("cross_domain_transfer", "trivial_baseline", "F34", "cross-domain", "Phoneme NN transfer rho=0.76 — trivial 1D predictor rho=1.0", "Must exceed trivial baseline"),
        ("cross_domain_coupling", "magnitude_mediation", "F35", "cross-domain", "Materials↔EC coupling via Megethos", "NOT magnitude mediation"),
        ("partial_correlation", "wrong_null", "F36", "within-domain", "h-R strengthening z=20.2 with wrong null", "Must use proper permutation null"),
        ("residual_structure", "known_math", "F27", "within-domain", "h-R residual = analytic class number formula", "Check known consequences"),
        ("integer_overlap", "tautology", "F27", "cross-domain", "PG-NF degree overlap = crystallographic restriction", "Check group tautologies"),
        ("cross_domain_correlation", "prime_mediation", "F31", "cross-domain", "Iso-MF r=-0.556 partially prime-mediated", "Condition on prime properties"),
        ("integer_overlap", "tabulation_bias", "F29", "cross-domain", "EC×Maass levels — shared LMFDB indexing", "Check tabulation bias"),
        ("cross_domain_transfer", "magnitude_mediation", "F35", "cross-domain", "Megethos-mediated bridges — sorted log-normals", "NOT sorted magnitude"),
        ("cross_domain_transfer", "no_shared_objects", "F33", "cross-domain", "ZPVE↔torsion — no shared objects, phoneme mediation", "Must have shared objects or distributional coupling"),
        ("feature_correlation", "not_significant", "F1", "cross-domain", "RMT↔MF feature-level z=0.6", "Must exceed permutation null"),
        ("distributional_claim", "preprocessing_artifact", "F38", "within-domain", "Knot root GUE var=0.180 was preprocessed data", "Verify on raw data"),
        ("pipeline_output", "noise", "F1", "pipeline", "Discovery candidates — zero survive z>3", "Generator needs recalibration"),
        ("interaction_effect", "no_effect", "F24", "within-domain", "Torsion-conductor interaction +0.0002", "Effect must exceed permutation null"),
        ("exact_identity", "tautology", "F27", "within-domain", "E_6 root number = CM forces it", "Check representation theory"),
        ("mathematical_formula", "false_claim", "F24", "within-domain", "S_n M4/M²=p(n)/n — ratio diverges", "Verify numerically"),
        ("feature_engineering", "feature_engineering", "F37", "within-domain", "3-prime fingerprint — any hash gives same", "Test alternative encodings"),
        ("compression_metric", "magnitude_proxy", "F35", "within-domain", "LZ compression — string length proxies conductor", "Use distribution-weighted compression"),
        ("learnability_metric", "distributional_not_sequential", "F33", "within-domain", "Mod-2 learnability — shuffled preserves signal", "Must survive shuffle control"),
        ("convergence_rate", "localized_to_small_primes", "custom", "within-domain", "Convergence rate in a_2 and a_3 only", "Test with prime ablation"),
        ("congruence_topology", "conductor_mediation", "F35", "within-domain", "Congruence graph z=37 killed by conductor matching", "Must survive conductor stratification"),
    ]

    cur.execute("SELECT COUNT(*) FROM kills")
    if cur.fetchone()[0] == 0:
        for hyp_type, fail_mode, f_test, domain, desc, constraint in known_kills:
            cur.execute(
                "INSERT INTO kills (hypothesis_type, failure_mode, f_test, domain, description, constraint_added, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (hyp_type, fail_mode, f_test, domain, desc, constraint, "2026-04-13")
            )

    # Seed negative dimensions
    neg_dims = [
        ("ordinal", "NOT ordinal matching of small integers", "1,10,19"),
        ("magnitude", "NOT magnitude/size mediation", "3,8,9,18"),
        ("distributional", "NOT distributional coincidence", "7,8,10"),
        ("preprocessing", "NOT preprocessing artifacts", "12"),
        ("engineering", "NOT hand-crafted feature engineering", "17"),
        ("tautology", "NOT group-theoretic tautologies", "6,15"),
        ("prime_mediated", "NOT prime-mediated confounds", "7"),
        ("partial_artifact", "NOT partial-correlation procedural artifacts", "4"),
        ("trivial_baseline", "NOT trivially achievable by nearest-integer matching", "2"),
        ("small_prime", "NOT localized to first 2-3 primes", "20"),
    ]

    cur.execute("SELECT COUNT(*) FROM negative_dimensions")
    if cur.fetchone()[0] == 0:
        for dim, desc, kill_ids in neg_dims:
            cur.execute(
                "INSERT INTO negative_dimensions (dimension, description, kills_that_proved_it) VALUES (?, ?, ?)",
                (dim, desc, kill_ids)
            )

    con.commit()
    con.close()
    return db_path


def add_kill(hypothesis_type, failure_mode, f_test, domain, description, constraint, db_path=None):
    """Add a new kill to the taxonomy."""
    if db_path is None:
        db_path = DB_PATH
    con = sqlite3.connect(str(db_path))
    cur = con.cursor()
    cur.execute(
        "INSERT INTO kills (hypothesis_type, failure_mode, f_test, domain, description, constraint_added, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (hypothesis_type, failure_mode, f_test, domain, description, constraint, datetime.now().isoformat())
    )
    con.commit()
    kill_id = cur.lastrowid
    con.close()
    return kill_id


def get_all_kills(db_path=None):
    """Get all kills as list of dicts."""
    if db_path is None:
        db_path = DB_PATH
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    kills = [dict(r) for r in con.execute("SELECT * FROM kills").fetchall()]
    con.close()
    return kills


def get_constraints_text(db_path=None):
    """Get a text summary of all constraints for LLM prompts."""
    kills = get_all_kills(db_path)
    lines = ["KILL TAXONOMY (hypotheses MUST NOT match these patterns):"]
    for k in kills:
        lines.append(f"  - {k['failure_mode']}: {k['description']}")
    return "\n".join(lines)


def check_hypothesis_against_kills(hypothesis, db_path=None):
    """Check if a hypothesis matches any known kill pattern. Returns list of matching kills."""
    kills = get_all_kills(db_path)
    matches = []
    for k in kills:
        # Simple pattern matching — can be made more sophisticated
        if k["failure_mode"] == "magnitude_mediation" and hypothesis.conditioning == "none":
            if any(f in hypothesis.feature_a for f in ["conductor", "log_conductor", "discriminant", "volume"]):
                matches.append(k)
        if k["failure_mode"] == "ordinal_alignment":
            if hypothesis.coupling == "spearman" and hypothesis.null_model == "permutation":
                # Not necessarily a match, but flag for attention
                pass
        if k["failure_mode"] == "tautology":
            # Check specific known tautologies
            if (hypothesis.domain_a == "elliptic_curves" and hypothesis.feature_a == "conductor"
                    and hypothesis.domain_b == "modular_forms" and hypothesis.feature_b == "level"):
                matches.append(k)
    return matches


if __name__ == "__main__":
    db = init_db()
    print(f"Kill taxonomy initialized at {db}")
    kills = get_all_kills()
    print(f"  {len(kills)} kills loaded")
    print(f"\nConstraints text (first 500 chars):")
    print(get_constraints_text()[:500])
