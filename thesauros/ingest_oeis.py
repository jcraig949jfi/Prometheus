"""
Load OEIS sequences into analysis.oeis from cartography/oeis/data/.

Sources:
  - oeis_names.json: 394K seq_id -> name
  - oeis_keywords.json: 394K seq_id -> keyword list
  - stripped_new.txt: 394K seq_id -> first terms (comma-separated integers)

Computed features (from first_terms):
  - growth_rate: ratio of last to first nonzero term (log scale)
  - entropy: Shannon entropy of term frequency distribution
  - is_monotone: whether terms are non-decreasing
"""
import json
import math
import time
import psycopg2
import psycopg2.extras
from collections import Counter
from pathlib import Path

REPO = Path(__file__).parent.parent
DATA = REPO / "cartography" / "oeis" / "data"
PG_DSN = dict(host='localhost', port=5432, dbname='prometheus_sci',
              user='postgres', password='prometheus')


def parse_terms(terms_str):
    """Parse comma-separated integers, handle large values gracefully."""
    terms = []
    for t in terms_str.split(","):
        t = t.strip()
        if not t:
            continue
        try:
            val = int(t)
            # Postgres BIGINT max is ~9.2e18
            if abs(val) <= 9_000_000_000_000_000_000:
                terms.append(val)
            else:
                terms.append(None)  # overflow marker
        except ValueError:
            continue
    return terms


def compute_growth_rate(terms):
    """Log ratio of last to first nonzero absolute value."""
    nonzero = [abs(t) for t in terms if t is not None and t != 0]
    if len(nonzero) < 2:
        return None
    try:
        return math.log1p(nonzero[-1]) - math.log1p(nonzero[0])
    except (ValueError, OverflowError):
        return None


def compute_entropy(terms):
    """Shannon entropy of term frequency distribution."""
    valid = [t for t in terms if t is not None]
    if len(valid) < 2:
        return None
    counts = Counter(valid)
    total = len(valid)
    entropy = 0.0
    for c in counts.values():
        p = c / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def is_monotone(terms):
    """Check if terms are non-decreasing."""
    valid = [t for t in terms if t is not None]
    if len(valid) < 2:
        return None
    for i in range(1, len(valid)):
        if valid[i] < valid[i - 1]:
            return False
    return True


def load_names():
    """Load seq_id -> name mapping."""
    with open(DATA / "oeis_names.json", encoding="utf-8") as f:
        return json.load(f)


def load_keywords():
    """Load seq_id -> keywords mapping."""
    with open(DATA / "oeis_keywords.json", encoding="utf-8") as f:
        return json.load(f)


def load_terms():
    """Load seq_id -> first_terms from stripped_new.txt."""
    terms_map = {}
    with open(DATA / "stripped_new.txt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ,", 1)
            if len(parts) < 2:
                continue
            seq_id = parts[0].strip()
            terms_str = parts[1].rstrip(",")
            terms_map[seq_id] = terms_str
    return terms_map


if __name__ == "__main__":
    start = time.time()
    print("=" * 60)
    print("Loading OEIS sequences into analysis.oeis")
    print("=" * 60)

    print("Loading names...")
    names = load_names()
    print(f"  {len(names):,} names")

    print("Loading keywords...")
    keywords = load_keywords()
    print(f"  {len(keywords):,} keyword sets")

    print("Loading terms...")
    terms_map = load_terms()
    print(f"  {len(terms_map):,} term sequences")

    # Merge all sources by seq_id
    all_ids = set(names.keys()) | set(terms_map.keys())
    print(f"  {len(all_ids):,} unique sequence IDs")

    conn = psycopg2.connect(**PG_DSN)
    conn.autocommit = False
    cur = conn.cursor()

    # Clear existing
    cur.execute("DELETE FROM analysis.oeis")
    conn.commit()

    count = 0
    batch = []
    batch_size = 5000

    for seq_id in sorted(all_ids):
        name = names.get(seq_id, "")
        terms_str = terms_map.get(seq_id, "")
        terms = parse_terms(terms_str) if terms_str else []

        # Take first 20 terms for the array column
        first_terms = [t for t in terms[:20] if t is not None]

        growth = compute_growth_rate(terms)
        entropy = compute_entropy(terms)
        mono = is_monotone(terms)

        batch.append((seq_id, name, first_terms if first_terms else None, growth, entropy, mono))
        count += 1

        if len(batch) >= batch_size:
            psycopg2.extras.execute_batch(
                cur,
                """INSERT INTO analysis.oeis (oeis_id, name, first_terms, growth_rate, entropy, is_monotone)
                   VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (oeis_id) DO NOTHING""",
                batch,
                page_size=1000,
            )
            conn.commit()
            batch = []
            if count % 50000 == 0:
                elapsed = time.time() - start
                print(f"  {count:,} / {len(all_ids):,} ({elapsed:.0f}s)")

    # Final batch
    if batch:
        psycopg2.extras.execute_batch(
            cur,
            """INSERT INTO analysis.oeis (oeis_id, name, first_terms, growth_rate, entropy, is_monotone)
               VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (oeis_id) DO NOTHING""",
            batch,
            page_size=1000,
        )
        conn.commit()

    elapsed = time.time() - start

    cur.execute("SELECT count(*) FROM analysis.oeis")
    final = cur.fetchone()[0]

    print(f"\nDone: {final:,} sequences loaded in {elapsed:.0f}s")

    # Quick stats
    cur.execute("SELECT avg(growth_rate), avg(entropy), sum(case when is_monotone then 1 else 0 end) FROM analysis.oeis WHERE growth_rate IS NOT NULL")
    avg_g, avg_e, n_mono = cur.fetchone()
    print(f"  avg growth_rate: {avg_g:.2f}")
    print(f"  avg entropy: {avg_e:.2f}")
    print(f"  monotone sequences: {n_mono:,}")

    conn.close()
