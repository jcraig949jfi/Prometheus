"""
P7: Ingest remaining cartography data into prometheus_sci.
Batch A: CODATA, Fungrim, small groups (schema exists)
Batch B: Check what data files exist and report what's loadable.
"""
import psycopg2
import json
import csv
import time
from pathlib import Path

REPO = Path(__file__).parent.parent
PG_DSN = dict(host='localhost', port=5432, dbname='prometheus_sci', user='postgres', password='prometheus')

def find_data_files():
    """Scan cartography/ for loadable data files."""
    cart = REPO / "cartography"
    if not cart.exists():
        print(f"cartography/ not found at {cart}")
        return {}

    found = {}
    for f in cart.rglob("*"):
        if f.is_file() and f.suffix in ('.json', '.csv', '.jsonl'):
            rel = f.relative_to(REPO)
            size_mb = f.stat().st_size / (1024*1024)
            found[str(rel)] = {'path': f, 'size_mb': size_mb, 'suffix': f.suffix}
    return found

def load_codata(pg_cur):
    """Load CODATA constants if file exists."""
    candidates = [
        REPO / "cartography" / "physics" / "data" / "codata.json",
        REPO / "cartography" / "physics" / "data" / "codata_constants.json",
        REPO / "cartography" / "physics" / "data" / "constants.json",
    ]
    for path in candidates:
        if path.exists():
            print(f"  Loading CODATA from {path.name}...")
            with open(path) as f:
                data = json.load(f)
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = list(data.values()) if not isinstance(list(data.values())[0], str) else [data]
            else:
                print(f"  Unexpected format in {path.name}")
                return 0

            count = 0
            for item in items:
                if isinstance(item, dict):
                    pg_cur.execute("""
                        INSERT INTO physics.codata (name, value, uncertainty, unit)
                        VALUES (%s, %s, %s, %s) ON CONFLICT (name) DO NOTHING
                    """, (
                        item.get('name', item.get('quantity', '')),
                        item.get('value'),
                        item.get('uncertainty'),
                        item.get('unit', item.get('units', ''))
                    ))
                    count += 1
            print(f"  CODATA: {count} constants loaded")
            return count
    print("  CODATA: no data file found")
    return 0

def load_space_groups(pg_cur):
    """Load space groups from JSON if not already loaded."""
    path = REPO / "cartography" / "spacegroups" / "data" / "space_groups.json"
    if not path.exists():
        print("  Space groups: no data file found")
        return 0

    pg_cur.execute("SELECT count(*) FROM algebra.space_groups")
    existing = pg_cur.fetchone()[0]
    if existing > 0:
        print(f"  Space groups: already loaded ({existing} rows)")
        return 0

    with open(path) as f:
        data = json.load(f)

    items = data if isinstance(data, list) else list(data.values())
    count = 0
    for item in items:
        if isinstance(item, dict):
            pg_cur.execute("""
                INSERT INTO algebra.space_groups (number, symbol, point_group_order, crystal_system, lattice_type, is_symmorphic)
                VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
            """, (
                item.get('number'),
                item.get('symbol', item.get('international_symbol', '')),
                item.get('point_group_order'),
                item.get('crystal_system'),
                item.get('lattice_type', item.get('bravais_lattice', '')),
                item.get('is_symmorphic')
            ))
            count += 1
    print(f"  Space groups: {count} loaded")
    return count

def report_available(files):
    """Report what data files are available for future loading."""
    print("\nAvailable data files (not yet loaded):")
    for path, info in sorted(files.items()):
        print(f"  {path} ({info['size_mb']:.1f} MB)")

if __name__ == "__main__":
    start = time.time()
    print("=" * 60)
    print("P7: Cartography data ingestion")
    print("=" * 60)

    files = find_data_files()
    print(f"Found {len(files)} data files in cartography/")

    conn = psycopg2.connect(**PG_DSN)
    conn.autocommit = False
    cur = conn.cursor()

    totals = {}
    try:
        totals['codata'] = load_codata(cur)
        conn.commit()
        totals['space_groups'] = load_space_groups(cur)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")

    # Check what's already in prometheus_sci
    print("\nprometheus_sci current state:")
    for schema_table in ['topology.knots', 'chemistry.qm9', 'algebra.space_groups',
                         'algebra.lattices', 'algebra.groups', 'physics.codata',
                         'analysis.fungrim', 'analysis.oeis', 'physics.superconductors',
                         'physics.materials', 'biology.metabolism']:
        try:
            cur.execute(f"SELECT count(*) FROM {schema_table}")
            print(f"  {schema_table}: {cur.fetchone()[0]:,} rows")
        except Exception:
            conn.rollback()
            print(f"  {schema_table}: table does not exist")

    report_available(files)

    elapsed = time.time() - start
    print(f"\nP7 complete in {elapsed:.0f}s")
    total = sum(totals.values())
    print(f"Total loaded this run: {total:,} rows")

    conn.close()
