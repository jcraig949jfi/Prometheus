"""PAN-32: how much of the program's text is a copy of other text, and which copy is
canonical (the earliest-committed). Exact duplicates after whitespace/case
normalisation, at chunk level, over git artifacts only.

Writes pan.chunk_dup (chunk_id -> canonical chunk_id, cluster size) and reports:
duplicated chunks and characters, the largest clusters, and which kinds/seats hold
the most copies. Retrieval already collapses near-duplicates at query time
(search.collapse_copies); this is the corpus-level measurement behind that choice.

ORACLE: every cluster has exactly one canonical member, and members + canonicals
partition the duplicated chunks (checked in SQL after the build).
"""
import json
import time

SQL_BUILD = """
drop table if exists pan.chunk_dup;
create table pan.chunk_dup as
with norm as (
  select c.chunk_id, c.artifact_id, c.n_chars,
         md5(regexp_replace(lower(c.body), '\\s+', ' ', 'g')) as h,
         coalesce(a.first_commit_at, a.last_commit_at) as t, a.path
  from pan.chunk c join pan.artifact a on a.artifact_id = c.artifact_id
  where a.source = 'git' and c.n_chars >= 200),
dup as (select h from norm group by h having count(distinct artifact_id) > 1),
mem as (select n.* from norm n join dup using (h)),
canon as (select distinct on (h) h, chunk_id as canonical_id from mem order by h, t nulls last, path, chunk_id)
select m.chunk_id, m.artifact_id, m.n_chars, m.h, c.canonical_id,
       count(*) over (partition by m.h) as cluster_size
from mem m join canon c using (h);
create index on pan.chunk_dup (canonical_id);
comment on table pan.chunk_dup is 'Exact duplicate chunks (>= 200 chars, normalised whitespace/case) across git artifacts; canonical = earliest-committed member. Producer: python -m pan dupes.';
"""


def run(out=print):
    from . import db
    t0 = time.time()
    with db.cursor(statement_timeout_ms=1800000) as cur:
        cur.execute(SQL_BUILD)
        cur.execute("""select count(*), sum(n_chars), count(distinct h),
                              sum(n_chars) filter (where chunk_id <> canonical_id) from pan.chunk_dup""")
        n, chars, clusters, copy_chars = cur.fetchone()
        cur.execute("select count(*), sum(n_chars) from pan.chunk c join pan.artifact a on a.artifact_id=c.artifact_id "
                    "where a.source='git' and c.n_chars >= 200")
        n_all, chars_all = cur.fetchone()
        cur.execute("select count(*) from (select h, count(*) filter (where chunk_id = canonical_id) k "
                    "from pan.chunk_dup group by h) x where k <> 1")
        bad = cur.fetchone()[0]
        cur.execute("""select a.kind, count(*), sum(d.n_chars) from pan.chunk_dup d join pan.artifact a
                       on a.artifact_id = d.artifact_id where d.chunk_id <> d.canonical_id
                       group by 1 order by 3 desc limit 8""")
        by_kind = cur.fetchall()
        cur.execute("""select coalesce(a.seat, '(none)'), count(*), sum(d.n_chars) from pan.chunk_dup d
                       join pan.artifact a on a.artifact_id = d.artifact_id where d.chunk_id <> d.canonical_id
                       group by 1 order by 3 desc limit 8""")
        by_seat = cur.fetchall()
        cur.execute("""select d.cluster_size, ca.path, left(regexp_replace(c.body, '\\s+', ' ', 'g'), 80)
                       from (select distinct on (h) h, canonical_id, cluster_size from pan.chunk_dup
                             order by h, cluster_size desc) d
                       join pan.chunk c on c.chunk_id = d.canonical_id join pan.artifact ca on ca.artifact_id = c.artifact_id
                       order by d.cluster_size desc limit 8""")
        top = cur.fetchall()
    copies = n - clusters
    res = dict(chunks_considered=n_all, duplicated_chunks=n, clusters=clusters, copies=copies,
               copy_share_of_chunks=round(copies / n_all, 4) if n_all else None,
               copy_chars=int(copy_chars or 0), copy_share_of_chars=round(int(copy_chars or 0) / int(chars_all), 4)
               if chars_all else None, oracle_one_canonical_per_cluster=(bad == 0),
               by_kind=[(k, c, int(ch)) for k, c, ch in by_kind], by_seat=[(s, c, int(ch)) for s, c, ch in by_seat],
               largest=[(sz, p, t) for sz, p, t in top], seconds=round(time.time() - t0, 1))
    out(json.dumps(res, default=str, indent=1))
    return res
