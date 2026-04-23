"""
Mnemosyne — Priority 1 data ingestion into prometheus_sci.

Loads well-structured cartography data files into their target Postgres tables.
Each loader validates data before insertion and logs results.

Usage:
    python mnemosyne/ingest_priority1.py --table knots
    python mnemosyne/ingest_priority1.py --table all
    python mnemosyne/ingest_priority1.py --table knots --dry-run  # validate only
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from thesauros.prometheus_data.pool import get_sci


# ============================================================
# Data source registration
# ============================================================

def register_source(cur, name, origin_url, file_path, row_count, checksum=""):
    """Register a data source in core.data_source. Returns source_id."""
    cur.execute("""
        INSERT INTO core.data_source (name, origin_url, file_path, row_count, checksum)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (name) DO UPDATE SET
            row_count = EXCLUDED.row_count,
            loaded_at = now()
        RETURNING source_id
    """, (name, origin_url, file_path, row_count, checksum))
    return cur.fetchone()[0]


# ============================================================
# Individual loaders
# ============================================================

CART = Path(__file__).resolve().parent.parent / "cartography"


def load_knots(cur, dry_run=False):
    """Load knots from cartography/knots/data/knots.json -> topology.knots"""
    path = CART / "knots" / "data" / "knots.json"
    with open(path) as f:
        data = json.load(f)

    knots = data["knots"]
    print(f"  Knots: {len(knots)} records from {path.name}")

    valid = 0
    skipped = 0
    for k in knots:
        name = k.get("name")
        if not name:
            skipped += 1
            continue
        valid += 1

    print(f"  Valid: {valid}, Skipped: {skipped}")
    if dry_run:
        return valid

    source_id = register_source(
        cur, "knotinfo", "https://www.indiana.edu/~knotinfo/",
        str(path), valid
    )

    cur.execute("DELETE FROM topology.knots WHERE source_id = %s", (source_id,))

    for k in knots:
        name = k.get("name")
        if not name:
            continue
        cur.execute("""
            INSERT INTO topology.knots
                (name, crossing_number, determinant, alexander_coeffs,
                 jones_coeffs, conway_coeffs, source_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE SET
                crossing_number = EXCLUDED.crossing_number,
                determinant = EXCLUDED.determinant,
                alexander_coeffs = EXCLUDED.alexander_coeffs,
                jones_coeffs = EXCLUDED.jones_coeffs,
                conway_coeffs = EXCLUDED.conway_coeffs
        """, (
            name,
            k.get("crossing_number"),
            k.get("determinant"),
            k.get("alex_coeffs"),
            k.get("jones_coeffs"),
            k.get("conway_coeffs"),
            source_id,
        ))

    print(f"  Loaded {valid} knots.")
    return valid


def load_qm9(cur, dry_run=False):
    """Load QM9 molecules from cartography/chemistry/data/qm9.csv -> chemistry.qm9"""
    path = CART / "chemistry" / "data" / "qm9.csv"

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"  QM9: {len(rows)} records from {path.name}")
    if dry_run:
        return len(rows)

    source_id = register_source(
        cur, "qm9", "https://doi.org/10.6084/m9.figshare.978904",
        str(path), len(rows)
    )

    cur.execute("DELETE FROM chemistry.qm9 WHERE source_id = %s", (source_id,))

    for r in rows:
        cur.execute("""
            INSERT INTO chemistry.qm9
                (smiles, homo, lumo, homo_lumo_gap, zpve, polarizability,
                 n_atoms, source_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            r["smiles"],
            float(r["homo"]),
            float(r["lumo"]),
            float(r["gap"]),
            float(r["zpve"]),
            float(r["alpha"]),
            None,  # n_atoms not in this CSV, could compute from SMILES
            source_id,
        ))

    print(f"  Loaded {len(rows)} molecules.")
    return len(rows)


def load_space_groups(cur, dry_run=False):
    """Load space groups from cartography/spacegroups/data/space_groups.json -> algebra.space_groups"""
    path = CART / "spacegroups" / "data" / "space_groups.json"
    with open(path) as f:
        data = json.load(f)

    print(f"  Space groups: {len(data)} records from {path.name}")
    if dry_run:
        return len(data)

    # space_groups has no source_id FK, it's a reference table
    cur.execute("DELETE FROM algebra.space_groups")

    for sg in data:
        cur.execute("""
            INSERT INTO algebra.space_groups
                (number, symbol, point_group_order, crystal_system,
                 lattice_type, is_symmorphic)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (number) DO UPDATE SET
                symbol = EXCLUDED.symbol,
                point_group_order = EXCLUDED.point_group_order,
                crystal_system = EXCLUDED.crystal_system,
                lattice_type = EXCLUDED.lattice_type,
                is_symmorphic = EXCLUDED.is_symmorphic
        """, (
            sg["number"],
            sg["symbol"],
            sg["point_group_order"],
            sg["crystal_system"],
            sg["lattice_type"],
            sg["is_symmorphic"],
        ))

    print(f"  Loaded {len(data)} space groups.")
    return len(data)


def load_lattices(cur, dry_run=False):
    """Load lattices from cartography/lattices/data/*.json -> algebra.lattices"""
    data_dir = CART / "lattices" / "data"
    all_lattices = []

    for f in sorted(data_dir.glob("*.json")):
        with open(f) as fh:
            content = json.load(fh)
        if isinstance(content, list):
            all_lattices.extend(content)
        elif isinstance(content, dict):
            if "lattices" in content:
                all_lattices.extend(content["lattices"])
            else:
                # Single lattice or dict of lattices
                for k, v in content.items():
                    if isinstance(v, dict):
                        v["label"] = v.get("label", k)
                        all_lattices.append(v)

    print(f"  Lattices: {len(all_lattices)} records from {data_dir}")
    if dry_run:
        return len(all_lattices)

    source_id = register_source(
        cur, "lattices_cartography", "",
        str(data_dir), len(all_lattices)
    )

    cur.execute("DELETE FROM algebra.lattices WHERE source_id = %s", (source_id,))

    loaded = 0
    for lat in all_lattices:
        label = lat.get("label") or lat.get("name")
        if not label:
            continue
        cur.execute("""
            INSERT INTO algebra.lattices
                (label, dimension, determinant, level, class_number,
                 kissing_number, source_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (label) DO UPDATE SET
                dimension = EXCLUDED.dimension,
                determinant = EXCLUDED.determinant
        """, (
            str(label),
            lat.get("dimension") or lat.get("dim"),
            lat.get("determinant") or lat.get("det"),
            lat.get("level"),
            lat.get("class_number"),
            lat.get("kissing_number"),
            source_id,
        ))
        loaded += 1

    print(f"  Loaded {loaded} lattices.")
    return loaded


def load_groups(cur, dry_run=False):
    """Load groups from cartography/groups/data/groups.json -> algebra.groups"""
    path = CART / "groups" / "data" / "abstract_groups.json"
    with open(path) as f:
        data = json.load(f)

    groups = data if isinstance(data, list) else data.get("groups", [])
    print(f"  Groups: {len(groups)} records from {path.name}")
    if dry_run:
        return len(groups)

    source_id = register_source(
        cur, "small_groups", "https://www.gap-system.org/",
        str(path), len(groups)
    )

    cur.execute("DELETE FROM algebra.groups WHERE source_id = %s", (source_id,))

    loaded = 0
    for g in groups:
        label = g.get("label") or g.get("name") or g.get("id")
        if not label:
            continue
        cur.execute("""
            INSERT INTO algebra.groups
                (label, order_val, exponent, n_conjugacy,
                 is_abelian, is_solvable, source_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (label) DO UPDATE SET
                order_val = EXCLUDED.order_val,
                exponent = EXCLUDED.exponent
        """, (
            str(label),
            g.get("order") or g.get("order_val"),
            g.get("exponent"),
            g.get("n_conjugacy") or g.get("num_conjugacy_classes"),
            g.get("is_abelian"),
            g.get("is_solvable"),
            source_id,
        ))
        loaded += 1

    print(f"  Loaded {loaded} groups.")
    return loaded


# ============================================================
# Runner
# ============================================================

LOADERS = {
    "knots": load_knots,
    "qm9": load_qm9,
    "space_groups": load_space_groups,
    "lattices": load_lattices,
    "groups": load_groups,
}


def main():
    parser = argparse.ArgumentParser(description="Mnemosyne Priority 1 ingestion")
    parser.add_argument("--table", required=True, help="Table to load (or 'all')")
    parser.add_argument("--dry-run", action="store_true", help="Validate only, don't load")
    args = parser.parse_args()

    tables = list(LOADERS.keys()) if args.table == "all" else [args.table]

    if args.dry_run:
        print("=== DRY RUN (validation only) ===\n")
        for table in tables:
            if table not in LOADERS:
                print(f"  Unknown table: {table}")
                continue
            try:
                count = LOADERS[table](None, dry_run=True)
                print(f"  -> {table}: {count} records ready\n")
            except Exception as e:
                print(f"  -> {table}: ERROR - {e}\n")
        return

    print("=== INGESTING into prometheus_sci ===\n")
    with get_sci() as conn:
        # Need write access for ingestion
        conn.set_session(readonly=False, autocommit=False)
        cur = conn.cursor()
        total = 0
        for table in tables:
            if table not in LOADERS:
                print(f"  Unknown table: {table}")
                continue
            t0 = time.time()
            try:
                count = LOADERS[table](cur)
                total += count
                elapsed = time.time() - t0
                print(f"  -> {table}: {count} records in {elapsed:.1f}s\n")
            except Exception as e:
                print(f"  -> {table}: ERROR - {e}\n")
                conn.rollback()
                raise
        conn.commit()
        print(f"\n=== DONE: {total} total records loaded ===")


if __name__ == "__main__":
    main()
