#!/usr/bin/env python3
"""
Postgres-backed Sigma kernel demo.

Same as demo.py but runs against the `sigma` schema in prometheus_fire
instead of a local SQLite file. Useful for:
  - Verifying Mnemosyne's migration (`migrations/001_create_sigma_schema.sql`)
    landed correctly.
  - Testing the kernel's discipline against shared substrate state that
    survives across processes.
  - End-to-end smoke check that the dual-backend refactor works.

Prerequisites:
  1. ~/.prometheus/db.toml + credentials.toml configured for `fire` DB
     (per thesauros.prometheus_data.config).
  2. Mnemosyne has applied migrations/001_create_sigma_schema.sql to
     prometheus_fire.
  3. The connecting user has SELECT/INSERT/UPDATE on schema `sigma`.

If any of those are missing, the kernel raises ConnectionError or
psycopg2.errors.* at __init__ time -- fail-closed, no half-state.

Run:  python demo_postgres.py [--keep]

By default this script PURGES its test-promoted symbols from the substrate
at exit so reruns don't accumulate cruft. Pass --keep to leave them in
the schema for inspection (you'll have to clean up manually next run, since
PROMOTE-overwrite is rejected by design).
"""

from __future__ import annotations

import sys
import uuid
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


def banner(s: str) -> None:
    print()
    print("=" * 72)
    print(s)
    print("=" * 72)


def section(s: str) -> None:
    print()
    print(f"--- {s} ---")


def main() -> int:
    keep = "--keep" in sys.argv

    banner("CONNECTING -- prometheus_fire / schema=sigma")
    try:
        k = SigmaKernel(backend="postgres")
    except (ConnectionError, RuntimeError) as e:
        print()
        print(f"  Cannot connect: {e}")
        print()
        print("  Likely fixes:")
        print("    1. Confirm ~/.prometheus/db.toml has [fire] section with host/port/dbname.")
        print("    2. Confirm ~/.prometheus/credentials.toml has [fire].password.")
        print("    3. Confirm Mnemosyne has applied")
        print("       sigma_kernel/migrations/001_create_sigma_schema.sql")
        print("       to prometheus_fire (creates schema `sigma` and three tables).")
        print()
        return 1

    print(f"  connected via thesauros.prometheus_data.pool")

    # Use a per-run prefix so test symbols don't collide with anything else
    # in the schema across reruns.
    run_id = uuid.uuid4().hex[:8]
    prefix = f"smoke_{run_id}_"
    minted_caps: list[str] = []
    promoted_keys: list[tuple[str, int]] = []

    try:
        # ------------------------------------------------------------------
        banner("GENESIS -- bootstrap starter substrate")
        dataset_sym = k.bootstrap_symbol(
            name=f"{prefix}dataset_A",
            version=1,
            def_obj={"type": "numeric_dataset", "values": [4, 5, 6, 5, 5], "true_mean": 5.0},
            tier=Tier.WorkingTheory,
        )
        promoted_keys.append((dataset_sym.name, dataset_sym.version))
        null_sym = k.bootstrap_symbol(
            name=f"{prefix}null_model",
            version=1,
            def_obj={"type": "permutation_null", "n_replicates": 1000},
            tier=Tier.WorkingTheory,
        )
        promoted_keys.append((null_sym.name, null_sym.version))
        print(f"  bootstrapped: {dataset_sym.ref}  hash={dataset_sym.def_hash[:12]}...")
        print(f"  bootstrapped: {null_sym.ref}     hash={null_sym.def_hash[:12]}...")

        cap_a = k.mint_capability()
        cap_b = k.mint_capability()
        cap_c = k.mint_capability()
        minted_caps.extend([cap_a.cap_id, cap_b.cap_id, cap_c.cap_id])
        print(f"  minted: {cap_a.cap_id}  {cap_b.cap_id}  {cap_c.cap_id}")

        # ------------------------------------------------------------------
        banner("SCENARIO 1 -- CLEAR verdict -> PROMOTE succeeds")
        evidence = {
            "dataset_hash": dataset_sym.def_hash,
            "null_model_hash": null_sym.def_hash,
            "true_mean": 5.0,
        }
        c1 = k.CLAIM(
            target_name=f"{prefix}prop_mean_gt4",
            hypothesis="mean > 4",
            evidence=evidence,
            kill_path="permutation_null_test",
            target_tier=Tier.Possible,
        )
        v1 = k.FALSIFY(c1)
        print(f"  verdict: {v1.status.value}  ({v1.rationale})")
        k.GATE(v1)
        sym1 = k.PROMOTE(c1, cap_a)
        promoted_keys.append((sym1.name, sym1.version))
        print(f"  promoted: {sym1.ref}")

        # ------------------------------------------------------------------
        banner("SCENARIO 2 -- BLOCK verdict -> PROMOTE refuses")
        c2 = k.CLAIM(
            target_name=f"{prefix}prop_mean_lt2",
            hypothesis="mean < 2",
            evidence=evidence,
            kill_path="permutation_null_test",
            target_tier=Tier.Conjecture,
        )
        v2 = k.FALSIFY(c2)
        print(f"  verdict: {v2.status.value}  ({v2.rationale})")
        try:
            k.GATE(v2)
            print("  ERROR: GATE should have raised")
            return 2
        except BlockedError as e:
            print(f"  GATE raised: {e}")
        try:
            k.PROMOTE(c2, cap_b)
            print("  ERROR: PROMOTE should have refused")
            return 2
        except FalsificationError as e:
            print(f"  PROMOTE refused (defense-in-depth): {e}")

        # ------------------------------------------------------------------
        banner("SCENARIO 3 -- Double-spend rejected")
        c3 = k.CLAIM(
            target_name=f"{prefix}prop_mean_eq5",
            hypothesis="mean == 5",
            evidence=evidence,
            kill_path="permutation_null_test",
            target_tier=Tier.Possible,
        )
        v3 = k.FALSIFY(c3)
        k.GATE(v3)
        try:
            k.PROMOTE(c3, cap_a)  # cap_a was consumed in scenario 1
            print("  ERROR: double-spend should have been rejected")
            return 2
        except CapabilityError as e:
            print(f"  PROMOTE refused: {e}")

        # ------------------------------------------------------------------
        banner("SCENARIO 4 -- Overwrite rejected (append-only)")
        try:
            k.bootstrap_symbol(
                name=f"{prefix}prop_mean_gt4",
                version=1,
                def_obj={"tampered": True},
                tier=Tier.Validated,
            )
            print("  ERROR: overwrite should have been rejected")
            return 2
        except ImmutabilityError as e:
            print(f"  rejected: {e}")

        # ------------------------------------------------------------------
        banner("SCENARIO 5 -- ERRATA (v2 supersedes v1; v1 stays)")
        c4 = k.CLAIM(
            target_name=f"{prefix}prop_mean_gt5p5",
            hypothesis="mean > 5.5",
            evidence=evidence,
            kill_path="permutation_null_test",
            target_tier=Tier.Conjecture,
        )
        v4 = k.FALSIFY(c4)
        k.GATE(v4)
        sym4_v1 = k.PROMOTE(c4, cap_c)
        promoted_keys.append((sym4_v1.name, sym4_v1.version))
        print(f"  promoted v1: {sym4_v1.ref}")

        cap_errata = k.mint_capability()
        minted_caps.append(cap_errata.cap_id)
        sym4_v2 = k.ERRATA(
            prior_name=f"{prefix}prop_mean_gt5p5",
            prior_version=1,
            corrected_def={"hypothesis": "mean > 5.5", "clarified_note": "errata smoke"},
            fault_description="smoke-test errata",
            cap=cap_errata,
        )
        promoted_keys.append((sym4_v2.name, sym4_v2.version))
        print(f"  promoted errata: {sym4_v2.ref}")
        print(f"  v1 still resolves: {k.RESOLVE(f'{prefix}prop_mean_gt5p5', 1).ref}")

        # ------------------------------------------------------------------
        banner("FINAL")
        print(f"  test symbols promoted (this run, prefix '{prefix}'):")
        for name, version in promoted_keys:
            print(f"    {name}@v{version}")

        print()
        print(f"  caps minted (this run): {len(minted_caps)}")
        consumed_count = k.conn.execute(
            "SELECT COUNT(*) FROM capabilities WHERE consumed=1 AND cap_id = ANY(%s)"
            if k.backend == "postgres"
            else "SELECT COUNT(*) FROM capabilities WHERE consumed=1 AND cap_id IN ({})".format(
                ",".join("?" * len(minted_caps))
            ),
            (minted_caps,) if k.backend == "postgres" else tuple(minted_caps),
        ).fetchone()[0]
        print(f"  caps consumed: {consumed_count}")

        print()
        print("  All scenarios passed against Postgres backend.")
        return 0

    finally:
        # Clean up unless --keep.
        if not keep:
            section("CLEANUP")
            print(f"  removing {len(promoted_keys)} test symbols, {len(minted_caps)} caps...")
            try:
                # Symbols: cascade not needed since claims/caps are FK-free.
                for name, version in promoted_keys:
                    k.conn.execute(
                        "DELETE FROM symbols WHERE name=? AND version=?",
                        (name, version),
                    )
                for cap_id in minted_caps:
                    k.conn.execute(
                        "DELETE FROM capabilities WHERE cap_id=?",
                        (cap_id,),
                    )
                # Claims have UUID prefixes scoped to this run, just clear via prefix.
                # (For SQLite this is fine; for Postgres, more conservative to skip.)
                k.conn.commit()
                print("  cleanup ok")
            except Exception as e:
                print(f"  cleanup failed (non-fatal): {e}")
                k.conn.rollback()
        else:
            print()
            print("  --keep specified; substrate retains test symbols.")
            print("  Manual cleanup required before next run with same prefix.")

        try:
            k.conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
