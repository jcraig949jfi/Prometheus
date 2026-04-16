"""
Load data into 6 empty prometheus_sci tables from cartography source files.
Tables: codata, pdg_particles, superconductors, fungrim, metabolism, lattices (reload).
"""
import psycopg2
import json
import csv
import time
from pathlib import Path

REPO = Path(__file__).parent.parent
PG_DSN = dict(host='localhost', port=5432, dbname='prometheus_sci',
              user='postgres', password='prometheus')


def load_codata(cur):
    """physics.codata <- codata_constants.json (356 constants)"""
    path = REPO / "cartography/physics/data/codata_constants.json"
    with open(path) as f:
        data = json.load(f)

    # Skip header-like entries
    count = 0
    for item in data:
        name = item.get("name", "")
        if not name or name == "Quantity":
            continue
        try:
            val = float(item["value"]) if item.get("value") else None
        except (ValueError, TypeError):
            val = None
        try:
            unc = float(item["uncertainty"]) if item.get("uncertainty") else None
        except (ValueError, TypeError):
            unc = None
        unit = item.get("unit", "")

        cur.execute("""
            INSERT INTO physics.codata (name, value, uncertainty, unit)
            VALUES (%s, %s, %s, %s) ON CONFLICT (name) DO NOTHING
        """, (name, val, unc, unit))
        count += 1
    print(f"  physics.codata: {count} rows")
    return count


def load_pdg_particles(cur):
    """physics.pdg_particles <- pdg/particles.json (226 particles)"""
    path = REPO / "cartography/physics/data/pdg/particles.json"
    with open(path) as f:
        data = json.load(f)

    count = 0
    for p in data:
        name = p.get("name", "")
        if not name:
            continue
        pdg_id = p.get("mc_ids", [None])[0] if p.get("mc_ids") else None
        try:
            mass = float(p["mass_GeV"]) if p.get("mass_GeV") is not None else None
        except (ValueError, TypeError):
            mass = None
        try:
            charge = float(p["charge"]) if p.get("charge") is not None else None
        except (ValueError, TypeError):
            charge = None
        try:
            spin = float(p["spin"]) if p.get("spin") is not None else None
        except (ValueError, TypeError):
            spin = None
        try:
            width = float(p["width_GeV"]) if p.get("width_GeV") is not None else None
            lifetime = 6.582e-25 / width if width and width > 0 else None
        except (ValueError, TypeError, ZeroDivisionError):
            lifetime = None
        is_stable = (width is None or width == 0)

        cur.execute("""
            INSERT INTO physics.pdg_particles (name, pdg_id, mass_gev, charge, spin, lifetime_s, is_stable)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, pdg_id, mass, charge, spin, lifetime, is_stable))
        count += 1
    print(f"  physics.pdg_particles: {count} rows")
    return count


def load_superconductors(cur):
    """physics.superconductors <- aflow_canonical_superconductors.csv (2012 rows)"""
    path = REPO / "cartography/physics/data/superconductors/aflow_canonical_superconductors.csv"
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            formula = row.get("aflow_compound", row.get("query_name", ""))
            sc_class = row.get("sc_class", "")
            spacegroup = row.get("aflow_sg", "")
            try:
                tc = float(row.get("Tc", 0) or 0)
            except (ValueError, TypeError):
                tc = None

            cur.execute("""
                INSERT INTO physics.superconductors (material_formula, tc, spacegroup, sc_class)
                VALUES (%s, %s, %s, %s)
            """, (formula, tc, spacegroup, sc_class))
            count += 1
    print(f"  physics.superconductors: {count} rows")
    return count


def load_fungrim(cur):
    """analysis.fungrim <- fungrim_formulas.json (3130 formulas)"""
    path = REPO / "cartography/fungrim/fungrim_formulas.json"
    with open(path) as f:
        data = json.load(f)

    count = 0
    for item in data:
        fid = item.get("id", "")
        ftype = item.get("type", "")
        module = item.get("module", "")
        n_symbols = len(item.get("symbols", []))
        formula_text = item.get("formula_text", "")

        cur.execute("""
            INSERT INTO analysis.fungrim (fungrim_id, formula_type, module, n_symbols, formula_text)
            VALUES (%s, %s, %s, %s, %s) ON CONFLICT (fungrim_id) DO NOTHING
        """, (fid, ftype, module, n_symbols, formula_text))
        count += 1
    print(f"  analysis.fungrim: {count} rows")
    return count


def load_metabolism(cur):
    """biology.metabolism <- metabolism/data/*.json (109 BiGG models)"""
    data_dir = REPO / "cartography/metabolism/data"
    model_files = [f for f in data_dir.glob("*.json")
                   if not f.name.startswith("constrained")
                   and not f.name.startswith("metabolism_universal")]

    count = 0
    for path in sorted(model_files):
        try:
            with open(path) as f:
                model = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue

        bigg_id = model.get("id", path.stem)
        n_reactions = len(model.get("reactions", []))
        n_metabolites = len(model.get("metabolites", []))
        n_genes = len(model.get("genes", []))
        compartments = model.get("compartments", {})
        n_compartments = len(compartments) if isinstance(compartments, dict) else 0

        # Fraction reversible
        reactions = model.get("reactions", [])
        if reactions:
            reversible = sum(1 for r in reactions
                           if r.get("lower_bound", 0) < 0 and r.get("upper_bound", 0) > 0)
            frac_rev = reversible / len(reactions)
        else:
            frac_rev = None

        cur.execute("""
            INSERT INTO biology.metabolism (bigg_id, n_reactions, n_metabolites, n_genes, n_compartments, frac_reversible)
            VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (bigg_id) DO NOTHING
        """, (bigg_id, n_reactions, n_metabolites, n_genes, n_compartments, frac_rev))
        count += 1
    print(f"  biology.metabolism: {count} rows")
    return count


def reload_lattices(cur):
    """algebra.lattices <- lattices_full.json (reload, currently only 26 rows)"""
    path = REPO / "cartography/lattices/data/lattices_full.json"
    if not path.exists():
        print("  algebra.lattices: lattices_full.json not found, skipping")
        return 0

    with open(path) as f:
        data = json.load(f)

    items = data if isinstance(data, list) else list(data.values())

    # Clear and reload
    cur.execute("DELETE FROM algebra.lattices")

    count = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        label = item.get("label", item.get("name", ""))
        dim = item.get("dim", item.get("dimension"))
        det = item.get("det", item.get("determinant"))
        level = item.get("level")
        cn = item.get("class_number")
        kiss = item.get("kissing", item.get("kissing_number"))

        try:
            cur.execute("""
                INSERT INTO algebra.lattices (label, dimension, determinant, level, class_number, kissing_number)
                VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (label) DO NOTHING
            """, (str(label), dim, det, level, cn, kiss))
            count += 1
        except Exception:
            cur.connection.rollback()
            continue
    print(f"  algebra.lattices: {count} rows (reloaded)")
    return count


if __name__ == "__main__":
    start = time.time()
    print("=" * 60)
    print("Loading 6 empty prometheus_sci tables")
    print("=" * 60)

    conn = psycopg2.connect(**PG_DSN)
    conn.autocommit = False
    cur = conn.cursor()

    totals = {}
    try:
        totals['codata'] = load_codata(cur)
        conn.commit()
        totals['pdg'] = load_pdg_particles(cur)
        conn.commit()
        totals['superconductors'] = load_superconductors(cur)
        conn.commit()
        totals['fungrim'] = load_fungrim(cur)
        conn.commit()
        totals['metabolism'] = load_metabolism(cur)
        conn.commit()
        totals['lattices'] = reload_lattices(cur)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

    elapsed = time.time() - start
    total = sum(totals.values())
    print(f"\nLoaded {total:,} rows in {elapsed:.1f}s")
    for k, v in totals.items():
        print(f"  {k}: {v:,}")

    # Verify
    print("\nVerification:")
    for table in ['physics.codata', 'physics.pdg_particles', 'physics.superconductors',
                  'analysis.fungrim', 'biology.metabolism', 'algebra.lattices']:
        cur.execute(f"SELECT count(*) FROM {table}")
        print(f"  {table}: {cur.fetchone()[0]:,}")

    conn.close()
