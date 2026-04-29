#!/usr/bin/env python3
"""
End-to-end Sigma kernel demo.

Walks every opcode through five scenarios that exercise the discipline:
  1. CLEAR verdict  -> successful PROMOTE; substrate gains a new symbol
  2. WARN verdict   -> PROMOTE succeeds, warning bubbled up
  3. BLOCK verdict  -> GATE raises; PROMOTE refuses even if GATE skipped
  4. Double-spend   -> second PROMOTE with the same cap rejected
  5. Overwrite      -> re-PROMOTE same name+version rejected by storage

Plus a recursive TRACE of the first promoted symbol's provenance graph.

Run:  python demo.py
"""

from __future__ import annotations

import json
from pathlib import Path

from sigma_kernel import (
    BlockedError,
    Capability,
    CapabilityError,
    FalsificationError,
    ImmutabilityError,
    SigmaKernel,
    Symbol,
    Tier,
    Verdict,
    VerdictResult,
)


# Use an on-disk DB so the substrate persists; reset each run.
DB_PATH = Path(__file__).parent / "demo_substrate.db"


def banner(s: str) -> None:
    print()
    print("=" * 72)
    print(s)
    print("=" * 72)


def section(s: str) -> None:
    print()
    print(f"--- {s} ---")


def print_substrate(k: SigmaKernel) -> None:
    rows = k.list_symbols()
    if not rows:
        print("  (empty)")
        return
    for name, version, hash_short, tier in rows:
        print(f"  {name}@v{version}  hash={hash_short}...  tier={tier}")


def main() -> None:
    # Fresh DB for this run.
    if DB_PATH.exists():
        DB_PATH.unlink()
    k = SigmaKernel(DB_PATH)

    # ------------------------------------------------------------------
    # Genesis: seed the substrate with two starter symbols.
    # In the real architecture this would be CALIBRATE on an anchor suite;
    # here we hardcode it.
    # ------------------------------------------------------------------
    banner("GENESIS -- bootstrap starter substrate")
    dataset_sym = k.bootstrap_symbol(
        name="dataset_A",
        version=1,
        def_obj={
            "type": "numeric_dataset",
            "values": [4, 5, 6, 5, 5],
            "true_mean": 5.0,
            "description": "toy dataset, mean 5",
        },
        tier=Tier.WorkingTheory,
    )
    null_sym = k.bootstrap_symbol(
        name="null_model",
        version=1,
        def_obj={
            "type": "permutation_null",
            "n_replicates": 1000,
            "description": "toy null model",
        },
        tier=Tier.WorkingTheory,
    )
    print(f"  bootstrapped: {dataset_sym.ref}  hash={dataset_sym.def_hash[:12]}...")
    print(f"  bootstrapped: {null_sym.ref}     hash={null_sym.def_hash[:12]}...")

    # Mint capabilities the demo will spend.
    cap_a = k.mint_capability()
    cap_b = k.mint_capability()
    cap_c = k.mint_capability()
    print(f"  minted: {cap_a.cap_id}  {cap_b.cap_id}  {cap_c.cap_id}")

    section("Initial substrate state")
    print_substrate(k)

    # ------------------------------------------------------------------
    # Scenario 1: CLEAR verdict -> successful PROMOTE
    # ------------------------------------------------------------------
    banner("SCENARIO 1 -- CLEAR verdict -> PROMOTE succeeds")

    evidence = {
        "dataset_hash": dataset_sym.def_hash,
        "null_model_hash": null_sym.def_hash,
        "true_mean": 5.0,
    }

    claim_1 = k.CLAIM(
        target_name="prop_mean_gt4",
        hypothesis="mean > 4",
        evidence=evidence,
        kill_path="permutation_null_test",
        target_tier=Tier.Possible,
    )
    print(f"  CLAIM allocated: {claim_1.id}")
    print(f"    hypothesis: {claim_1.hypothesis!r}")

    section("RESOLVE dependencies")
    d = k.RESOLVE("dataset_A", 1)
    n = k.RESOLVE("null_model", 1)
    print(f"  RESOLVE  {d.ref}   (hash verified)")
    print(f"  RESOLVE  {n.ref}   (hash verified)")

    section("FALSIFY (subprocess to omega_oracle.py)")
    v1 = k.FALSIFY(claim_1)
    print(f"  verdict: {v1.status.value}")
    print(f"  rationale: {v1.rationale}")
    print(f"  input_hash: {v1.input_hash[:12]}...  seed: {v1.seed}  runtime: {v1.runtime_ms}ms")

    section("GATE")
    flow = k.GATE(v1)
    print(f"  flow: {flow}")

    section("PROMOTE")
    sym_1 = k.PROMOTE(claim_1, cap_a)
    print(f"  promoted: {sym_1.ref}")
    print(f"  def_hash: {sym_1.def_hash[:12]}...")
    print(f"  provenance: {[h[:12] + '...' for h in sym_1.provenance]}")

    # ------------------------------------------------------------------
    # Scenario 2: WARN verdict -> PROMOTE still succeeds (with warning)
    # ------------------------------------------------------------------
    banner("SCENARIO 2 -- WARN verdict -> PROMOTE succeeds (warning bubbled)")

    claim_2 = k.CLAIM(
        target_name="prop_mean_gt5p5",
        hypothesis="mean > 5.5",   # true mean is 5.0 -> near miss
        evidence=evidence,
        kill_path="permutation_null_test",
        target_tier=Tier.Conjecture,
    )
    v2 = k.FALSIFY(claim_2)
    print(f"  verdict: {v2.status.value}  (rationale: {v2.rationale})")
    flow = k.GATE(v2)   # prints WARN line
    print(f"  GATE flow: {flow}")
    sym_2 = k.PROMOTE(claim_2, cap_b)
    print(f"  promoted (despite warning): {sym_2.ref}")

    # ------------------------------------------------------------------
    # Scenario 3: BLOCK verdict -> GATE raises; PROMOTE refuses
    # ------------------------------------------------------------------
    banner("SCENARIO 3 -- BLOCK verdict -> GATE raises and PROMOTE refuses")

    claim_3 = k.CLAIM(
        target_name="prop_mean_lt2",
        hypothesis="mean < 2",   # true mean is 5.0 -> strong falsification
        evidence=evidence,
        kill_path="permutation_null_test",
        target_tier=Tier.Conjecture,
    )
    v3 = k.FALSIFY(claim_3)
    print(f"  verdict: {v3.status.value}  (rationale: {v3.rationale})")

    section("GATE should raise")
    try:
        k.GATE(v3)
        print("  ERROR: GATE did not raise on BLOCK!")
    except BlockedError as e:
        print(f"  GATE raised BlockedError: {e}")

    section("Defense in depth -- PROMOTE refuses BLOCKED claim even if GATE skipped")
    try:
        k.PROMOTE(claim_3, cap_c)
        print("  ERROR: PROMOTE accepted a BLOCKED claim!")
    except FalsificationError as e:
        print(f"  PROMOTE refused: {e}")

    # cap_c is still unspent (PROMOTE rejected before consuming it). Verify.
    spent = k.conn.execute(
        "SELECT consumed FROM capabilities WHERE cap_id=?", (cap_c.cap_id,)
    ).fetchone()
    print(f"  cap {cap_c.cap_id} consumed? {bool(spent[0])}  (expected: False)")

    # ------------------------------------------------------------------
    # Scenario 4: Double-spend rejected
    # ------------------------------------------------------------------
    banner("SCENARIO 4 -- Double-spend rejected")

    claim_4 = k.CLAIM(
        target_name="prop_mean_eq5",
        hypothesis="mean == 5",
        evidence=evidence,
        kill_path="permutation_null_test",
        target_tier=Tier.Possible,
    )
    v4 = k.FALSIFY(claim_4)
    print(f"  verdict: {v4.status.value}")
    k.GATE(v4)

    print(f"  attempting PROMOTE with cap_a (already consumed in scenario 1)...")
    try:
        k.PROMOTE(claim_4, cap_a)
        print("  ERROR: double-spend succeeded!")
    except CapabilityError as e:
        print(f"  PROMOTE refused: {e}")

    # ------------------------------------------------------------------
    # Scenario 5: Overwrite rejected (storage-level immutability)
    # ------------------------------------------------------------------
    banner("SCENARIO 5 -- Overwrite rejected (append-only storage)")

    print(f"  trying to bootstrap_symbol over existing {sym_1.ref} ...")
    try:
        k.bootstrap_symbol(
            name="prop_mean_gt4",
            version=1,
            def_obj={"tampered": True},
            tier=Tier.Validated,
        )
        print("  ERROR: overwrite succeeded!")
    except ImmutabilityError as e:
        print(f"  rejected: {e}")

    print(f"  trying direct INSERT for {sym_1.ref} ...")
    import sqlite3 as _sqlite3
    try:
        k.conn.execute(
            "INSERT INTO symbols VALUES (?,?,?,?,?,?,?)",
            ("prop_mean_gt4", 1, "deadbeef", '{"tampered":true}', "[]", "Validated", 0.0),
        )
        k.conn.commit()
        print("  ERROR: direct overwrite succeeded!")
    except _sqlite3.IntegrityError as e:
        print(f"  rejected by storage: {e}")

    # ------------------------------------------------------------------
    # Scenario 6: ERRATA -- corrected v2 supersedes v1; v1 stays immutable
    # ------------------------------------------------------------------
    banner("SCENARIO 6 -- ERRATA: corrected v2 supersedes v1; v1 stays immutable")

    # We discovered that prop_mean_gt5p5@v1 (WARN, near-miss) was actually
    # produced from a draft that had a typo in the kill_path label. We
    # promote v2 with a clarified def_blob; v1 remains queryable forever.
    cap_errata = k.mint_capability()
    sym_2_v2 = k.ERRATA(
        prior_name="prop_mean_gt5p5",
        prior_version=1,
        corrected_def={
            "hypothesis": "mean > 5.5",
            "kill_path": "permutation_null_test",
            "verdict": "WARN",
            "verdict_rationale": "near miss: true mean 5.0 vs claim 'mean > 5.5'",
            "clarified_note": "kill_path label normalized; semantics unchanged",
        },
        fault_description="kill_path label was inconsistent across v1 promotions",
        cap=cap_errata,
    )
    print(f"  promoted errata: {sym_2_v2.ref}")
    print(f"  v1 still resolves: {k.RESOLVE('prop_mean_gt5p5', 1).ref}")
    print(f"  v2 errata pointer in def_blob: {json.loads(sym_2_v2.def_blob)['errata_correcting']}")

    # ------------------------------------------------------------------
    # TRACE the first promoted symbol's provenance
    # ------------------------------------------------------------------
    banner("TRACE -- recursive provenance walk of prop_mean_gt4@v1")
    trace_tree = k.TRACE(sym_1)
    print(json.dumps(trace_tree, indent=2))

    # ------------------------------------------------------------------
    # Final state
    # ------------------------------------------------------------------
    banner("FINAL SUBSTRATE")
    print_substrate(k)

    section("Capabilities ledger")
    rows = k.conn.execute(
        "SELECT cap_id, cap_type, consumed FROM capabilities ORDER BY cap_id"
    ).fetchall()
    for cap_id, cap_type, consumed in rows:
        print(f"  {cap_id}  {cap_type}  consumed={bool(consumed)}")

    section("Claims ledger")
    rows = k.conn.execute(
        "SELECT id, target_name, status, verdict_status FROM claims ORDER BY id"
    ).fetchall()
    for cid, tn, status, vs in rows:
        print(f"  {cid}  target={tn}  status={status}  verdict={vs}")

    print()
    print("Demo complete.")
    k.close()


if __name__ == "__main__":
    main()
