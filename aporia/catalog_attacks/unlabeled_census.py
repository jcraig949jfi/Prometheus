"""Hash-keyed census of the NULL-label rows (P103 residue, run P104).

The 46,439 unlabeled rows are the one population no label-keyed scan reaches:
GROUP BY collapses their NULLs to one group, JOIN matches none of them. This
censuses them by CONTENT instead of by label.

Pre-stated readings (BEFORE running):
  UNLABELED-PURE-DUP  the rows collapse to FEW distinct zero-vectors (a
                      handful of repeated contents) with no differing raw
                      text inside any hash group -> they are copies, and the
                      DISTINCT ON advice stands as amended.
  UNLABELED-DISTINCT  MANY distinct vectors (order of the row count) -> these
                      are real unlabeled objects, not copies; the audit's
                      advice changes again: dropping them via
                      WHERE label IS NOT NULL DISCARDS DATA, and consumers
                      need an id-keyed path.
  CONFLICT            two rows sharing an md5 but carrying different raw
                      text -> instrument-first: an md5 collision at this
                      scale is ~impossible, so suspect the fetch/encoding
                      before the data.

Also recorded: how many of these rows carry NULL positive_zeros at all
(the empty-content class), and their degree/conductor spread, so the audit
can say WHAT they are, not just how many.
"""
import collections
import json
import pathlib

import psycopg2

OUT = pathlib.Path(r'F:\Prometheus\aporia\catalog_attacks\unlabeled_census_results.json')

conn = psycopg2.connect(host='localhost', port=5432, dbname='lmfdb', user='postgres')
cur = conn.cursor()
cur.execute("SET statement_timeout='900s'")

cur.execute("SELECT count(*) FROM public.lfunc_lfunctions WHERE label IS NULL")
n_rows = cur.fetchone()[0]
cur.execute("SELECT count(*) FROM public.lfunc_lfunctions WHERE label IS NULL AND positive_zeros IS NULL")
n_nullzeros = cur.fetchone()[0]
print(f"unlabeled rows: {n_rows:,}; of which positive_zeros IS NULL: {n_nullzeros:,}", flush=True)

# content census by md5, keeping one exemplar id per hash
cur.execute("""
  SELECT md5(coalesce(positive_zeros::text, '')) AS h, count(*), min(id), max(id)
  FROM public.lfunc_lfunctions
  WHERE label IS NULL
  GROUP BY 1
  ORDER BY 2 DESC""")
groups = cur.fetchall()
mult = collections.Counter(int(c) for _, c, _, _ in groups)
print(f"distinct zero-vector contents among unlabeled rows: {len(groups):,}", flush=True)
print(f"multiplicity distribution (copies -> #contents): {dict(sorted(mult.items()))}", flush=True)
print(f"top groups: {[(h[:8], int(c)) for h, c, _, _ in groups[:5]]}", flush=True)

# instrument-first: for every hash group with >1 row, verify the raw texts agree
conflicts = []
checked = 0
for h, c, id_lo, id_hi in groups:
    if c < 2:
        continue
    cur.execute("""
      SELECT count(DISTINCT coalesce(positive_zeros::text, ''))
      FROM public.lfunc_lfunctions
      WHERE label IS NULL AND md5(coalesce(positive_zeros::text, '')) = %s""", (h,))
    n_distinct_text = cur.fetchone()[0]
    checked += 1
    if n_distinct_text > 1:
        conflicts.append((h, int(c), n_distinct_text))
print(f"multi-row hash groups checked for raw-text agreement: {checked:,}; conflicts: {len(conflicts)}", flush=True)

# what ARE these rows? degree / conductor spread
cur.execute("""
  SELECT degree::text, count(*) FROM public.lfunc_lfunctions
  WHERE label IS NULL GROUP BY 1 ORDER BY 2 DESC LIMIT 8""")
deg = cur.fetchall()
print(f"degree spread: {deg}", flush=True)
conn.close()

many = len(groups) > 0.5 * n_rows
verdict = ("CONFLICT" if conflicts else
           "UNLABELED-DISTINCT" if many else
           "UNLABELED-PURE-DUP")
print(f"-> {verdict}", flush=True)

OUT.write_text(json.dumps({
    "protocol": "content census of NULL-label rows: md5(positive_zeros) grouping in SQL, raw-text agreement verified per multi-row group (instrument-first against md5 collision), degree spread recorded",
    "n_unlabeled_rows": int(n_rows),
    "n_with_null_zeros": int(n_nullzeros),
    "n_distinct_contents": len(groups),
    "multiplicity_distribution": {str(k): int(v) for k, v in sorted(mult.items())},
    "multi_row_groups_checked": checked,
    "raw_text_conflicts": conflicts,
    "degree_spread": [[d, int(c)] for d, c in deg],
    "verdict": verdict}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
