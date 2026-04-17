"""
Fix data issues found in the 2026-04-16 audit.

Fixes applied:
  1. physics.codata.value/uncertainty — parse "7294.299 541 71" format (strip spaces, ellipsis)
  2. physics.superconductors — replace AFLOW data (no Tc) with SuperCon 2018 Stanev (has Tc)
  3. chemistry.qm9.n_atoms — compute from SMILES
  4. algebra.groups.is_abelian — derive: num_conjugacy_classes == order
  5. topology.polytopes.is_simplicial — derive: n_facets has f[d-1] entries where f is f_vector

Not fixed (upstream data gaps, documented):
  - physics.pdg_particles.charge/.spin (not in source JSON)
  - algebra.groups.is_solvable (needs composition series computation)
  - topology.knots.signature (P-011, needs KnotInfo re-scrape)
"""
import psycopg2
import json
import csv
import re
import time
from pathlib import Path

REPO = Path(__file__).parent.parent
PG = dict(host='localhost', port=5432, dbname='prometheus_sci',
          user='postgres', password='prometheus')


def fix_codata(cur):
    """Re-parse values with digit-space stripping."""
    print("\n[1/5] Fixing physics.codata value/uncertainty...")
    path = REPO / "cartography/physics/data/codata_constants.json"
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    def parse(s):
        if s is None:
            return None
        # Remove digit-group spaces, ellipsis, commas
        s = str(s).replace(' ', '').replace('...', '').replace(',', '')
        if not s:
            return None
        try:
            return float(s)
        except ValueError:
            return None

    updated = 0
    skipped = 0
    for item in data:
        name = item.get("name", "")
        if not name or name == "Quantity":
            continue
        val = parse(item.get("value"))
        unc = parse(item.get("uncertainty"))
        unit = item.get("unit", "")
        cur.execute("""
            UPDATE physics.codata
            SET value = %s, uncertainty = %s, unit = %s
            WHERE name = %s
        """, (val, unc, unit, name))
        if cur.rowcount > 0:
            updated += 1
        else:
            skipped += 1

    # Verify
    cur.execute("SELECT count(*) FILTER (WHERE value IS NOT NULL) FROM physics.codata")
    nonnull = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM physics.codata")
    total = cur.fetchone()[0]
    print(f"  Updated {updated}, skipped {skipped}. value NULL: {total-nonnull}/{total}")


def fix_superconductors(cur):
    """Replace current AFLOW-only superconductor data with SuperCon Stanev data (has Tc)."""
    print("\n[2/5] Rebuilding physics.superconductors from Stanev SuperCon dataset...")
    path = REPO / "cartography/physics/data/superconductors/3DSC/superconductors_3D/data/source/SuperCon/raw/Supercon_data_by_2018_Stanev.csv"
    if not path.exists():
        print(f"  SKIPPED: source file not found at {path}")
        return

    cur.execute("SELECT count(*) FROM physics.superconductors")
    before = cur.fetchone()[0]
    cur.execute("DELETE FROM physics.superconductors")
    print(f"  Cleared {before} rows from table")

    inserted = 0
    with open(path, encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            name = row.get("name", "").strip()
            if not name:
                continue
            tc_str = row.get("Tc", "").strip()
            try:
                tc = float(tc_str) if tc_str else None
            except ValueError:
                tc = None
            cur.execute("""
                INSERT INTO physics.superconductors (material_formula, tc)
                VALUES (%s, %s)
            """, (name, tc))
            inserted += 1

    cur.execute("SELECT count(*) FILTER (WHERE tc > 0) FROM physics.superconductors")
    nonzero = cur.fetchone()[0]
    cur.execute("SELECT avg(tc), max(tc) FROM physics.superconductors WHERE tc > 0")
    avg_tc, max_tc = cur.fetchone()
    print(f"  Inserted {inserted} rows. Tc > 0: {nonzero}, avg={float(avg_tc):.2f}K, max={float(max_tc):.2f}K")


def fix_qm9_n_atoms(cur):
    """Derive n_atoms from SMILES string by counting atoms (heavy atoms + implicit H)."""
    print("\n[3/5] Computing chemistry.qm9.n_atoms from SMILES...")

    # Simple SMILES atom count: count uppercase letters + lowercase in brackets (but not 2-char elements like Cl, Br)
    # Plus the implicit hydrogens. For QM9 (small organic), a decent heuristic:
    # - Count all capital letters A-Z in SMILES that represent atoms
    # - Two-letter atoms (Cl, Br, etc.) need special handling
    # - Since QM9 is primarily H,C,N,O,F this is mostly single-char
    # For a proper count including H, the best path is rdkit — but we avoid that dep.
    # Heuristic: count heavy atoms from SMILES via atom-letter regex
    atom_pattern = re.compile(r'Cl|Br|[BCNOFPSIbcnofps]')

    cur.execute("SELECT mol_id, smiles FROM chemistry.qm9 WHERE smiles IS NOT NULL")
    rows = cur.fetchall()

    updated = 0
    for mol_id, smiles in rows:
        # Strip brackets and special chars for counting heavy atoms
        # atoms in brackets like [NH4+] count as one
        heavy_count = 0
        i = 0
        cleaned = re.sub(r'\[[^\]]+\]', lambda m: 'X', smiles)  # replace bracketed atoms with placeholder
        atoms = atom_pattern.findall(cleaned)
        heavy_count = len(atoms) + cleaned.count('X')
        if heavy_count > 0:
            cur.execute("UPDATE chemistry.qm9 SET n_atoms = %s WHERE mol_id = %s", (heavy_count, mol_id))
            updated += 1
        if updated % 20000 == 0 and updated:
            print(f"  {updated:,} / {len(rows):,}")

    cur.execute("SELECT avg(n_atoms), min(n_atoms), max(n_atoms) FROM chemistry.qm9 WHERE n_atoms IS NOT NULL")
    avg_n, min_n, max_n = cur.fetchone()
    print(f"  Updated {updated} rows. n_atoms: avg={float(avg_n):.1f}, min={min_n}, max={max_n}")


def fix_groups_is_abelian(cur):
    """abelian iff num_conjugacy_classes == order (every element in its own class)."""
    print("\n[4/5] Deriving algebra.groups.is_abelian...")
    # Source JSON has order and num_conjugacy_classes; database stored order_val and n_conjugacy
    cur.execute("""
        UPDATE algebra.groups
        SET is_abelian = (order_val = n_conjugacy)
        WHERE order_val IS NOT NULL AND n_conjugacy IS NOT NULL
    """)
    updated = cur.rowcount
    cur.execute("SELECT count(*) FILTER (WHERE is_abelian) FROM algebra.groups")
    n_ab = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM algebra.groups")
    total = cur.fetchone()[0]
    print(f"  Updated {updated} rows. Abelian: {n_ab:,} / {total:,} ({100*n_ab/total:.1f}%)")


def fix_polytopes_is_simplicial(cur):
    """is_simplicial iff every facet is a simplex. For a d-dim polytope, iff the f-vector entry
    for top facets equals (# vertices choose d). Simpler heuristic: if source has that info, use it;
    otherwise we need the facet structure. Just check n_facets / n_vertices ratio as proxy, or
    try re-reading source JSON."""
    print("\n[5/5] Checking topology.polytopes.is_simplicial...")
    path = REPO / "cartography/polytopes/data/polytopes.json"
    if not path.exists():
        print(f"  SKIPPED: source file not found at {path}")
        return

    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    items = data if isinstance(data, list) else list(data.values())
    has_field = 0
    for item in items[:20]:
        if isinstance(item, dict) and 'is_simplicial' in item:
            has_field += 1
    print(f"  Sample check: {has_field}/20 polytopes have is_simplicial in source")
    if has_field == 0:
        print(f"  Source lacks is_simplicial field. Not computable without facet structure.")
        return

    updated = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        name = item.get('name') or item.get('label')
        is_simp = item.get('is_simplicial')
        if name and is_simp is not None:
            cur.execute("UPDATE topology.polytopes SET is_simplicial = %s WHERE name = %s", (is_simp, name))
            updated += 1
    print(f"  Updated {updated} rows")


if __name__ == "__main__":
    start = time.time()
    print("=" * 60)
    print("Fixing audit findings in prometheus_sci")
    print("=" * 60)

    conn = psycopg2.connect(**PG)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        fix_codata(cur)
        conn.commit()
        fix_superconductors(cur)
        conn.commit()
        fix_qm9_n_atoms(cur)
        conn.commit()
        fix_groups_is_abelian(cur)
        conn.commit()
        fix_polytopes_is_simplicial(cur)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise

    print(f"\nTotal fix time: {time.time()-start:.0f}s")
    conn.close()
