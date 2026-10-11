"""PAN-42: provenance-sensitive access classes for Pan's retrieval (migration 014; design in
roles/Pan/docs/sagacity/SAGACITY_FOUNDATION_MAP.md s6).

The caller's clearance is a ROLE name (pan.clearance): generator | evaluator | adjudicator | infrastructure. It comes
from `with access.as_role(...)` (the MCP server sets it per call) or the environment variable PAN_CLEARANCE; the
default is the most restrictive role, generator. An unknown role fails closed (PermissionError), never open.

Derived objects inherit by join: a chunk, embedding, document vector, link or search hit is visible only if the
artifact it came from is visible (for a link: both ends must be). REFUSE rules keep matching files out of the index
entirely -- the chunker never reads them.

Honest limit: while every session connects as the database superuser, this is cooperative defence in depth.
`rls_proof()` shows the authoritative version (Postgres row-level security with inheritance by EXISTS) in a
throwaway database, using an existing non-superuser role and creating no role.
"""
import contextlib
import datetime as dt
import json
import os
import re
import threading

DEFAULT_ROLE = "generator"
_state = threading.local()
_CACHE = {}


def current_role():
    return getattr(_state, "role", None) or os.environ.get("PAN_CLEARANCE") or DEFAULT_ROLE


@contextlib.contextmanager
def as_role(role):
    prev = getattr(_state, "role", None)
    _state.role = role
    try:
        yield role
    finally:
        _state.role = prev


def classes_for(role=None):
    """Access classes visible to `role` (default: the current role). Unknown role -> PermissionError."""
    from . import db
    role = role or current_role()
    if "clearance" not in _CACHE:
        with db.cursor() as cur:
            cur.execute("select role, classes from pan.clearance")
            _CACHE["clearance"] = {r: list(c) for r, c in cur.fetchall()}
    if role not in _CACHE["clearance"]:
        raise PermissionError("pan: unknown clearance role {!r} (known: {})".format(role, sorted(_CACHE["clearance"])))
    return _CACHE["clearance"][role]


def filter_sql(alias="a", role=None):
    """(' and <alias>.access_class = any(%s)', [classes]) for the given or current role."""
    return " and {}.access_class = any(%s)".format(alias), [classes_for(role)]


def visible(access_class, role=None):
    return access_class in classes_for(role)


def rules():
    """[(rule_id, compiled regex, action, class)] from pan.access_rule (cached per process)."""
    from . import db
    if "rules" not in _CACHE:
        with db.cursor() as cur:
            cur.execute("select rule_id, pattern, action, class from pan.access_rule order by rule_id")
            _CACHE["rules"] = [(rid, re.compile(p, re.I), act, cls) for rid, p, act, cls in cur.fetchall()]
    return _CACHE["rules"]


def refused(path):
    """The id of the REFUSE rule matching `path`, or None. Called BEFORE any read of the file."""
    for rid, rx, act, _ in rules():
        if act == "REFUSE" and rx.search(path or ""):
            return rid
    return None


def apply_rules(out=print):
    """Classify every artifact by the CLASSIFY rules (a recorded declassification wins over a rule) and purge refused
    artifacts from the index (chunks -> embeddings cascade; document vectors; outgoing links). Returns counts."""
    from . import db
    counts = {}
    with db.cursor() as cur:
        cur.execute("select rule_id, pattern, action, class from pan.access_rule order by action, rule_id")
        for rid, pat, act, cls in cur.fetchall():
            if act == "CLASSIFY":
                cur.execute("""update pan.artifact a set access_class = %s, access_rule = %s
                               where a.path ~* %s and (a.access_class <> %s or a.access_rule is distinct from %s)
                                 and not exists (select 1 from pan.declassification d where d.artifact_id = a.artifact_id)""",
                            (cls, rid, pat, cls, rid))
                counts[rid] = dict(action=act, class_=cls, newly_classified=cur.rowcount)
                cur.execute("select count(*) from pan.artifact where access_rule = %s", (rid,))
                counts[rid]["total"] = cur.fetchone()[0]
            else:
                cur.execute("select artifact_id from pan.artifact where path ~* %s", (pat,))
                ids = [r[0] for r in cur.fetchall()]
                cur.execute("delete from pan.chunk where artifact_id = any(%s)", (ids,))
                n_chunks = cur.rowcount
                cur.execute("delete from pan.doc_embedding where artifact_id = any(%s)", (ids,))
                n_doc = cur.rowcount
                cur.execute("delete from pan.link where src_id = any(%s)", (ids,))
                n_link = cur.rowcount
                cur.execute("""update pan.artifact set n_chunks = 0, access_rule = %s, indexed_blob = blob_sha
                               where artifact_id = any(%s)""", (rid, ids))
                counts[rid] = dict(action=act, matched=len(ids), chunks_purged=n_chunks, doc_vectors_purged=n_doc,
                                   links_purged=n_link)
    out(json.dumps(counts))
    return counts


# ---------------------------------------------------------------- controls

def rls_proof(out=print):
    """Authoritative-enforcement proof in a THROWAWAY database (created and dropped here; no role created): RLS on an
    artifact table, a child chunk table whose policy is EXISTS on its parent (inheritance), queried under SET ROLE to
    the existing non-superuser role prometheus_read; and the superuser seeing everything (why RLS needs non-superuser
    logins). Returns a list of checks."""
    from . import db
    name = "pan_rls_proof"
    admin = db.connect(autocommit=True)
    cur = admin.cursor()
    cur.execute("select 1 from pg_database where datname = %s", (name,))
    if cur.fetchone():
        cur.execute("drop database " + name)
    cur.execute("create database " + name)
    checks = []
    try:
        conn = db.connect(name, autocommit=True)
        c = conn.cursor()
        c.execute("""
            create table art (id int primary key, access_class text not null, body text);
            create table chunk (id int primary key, art_id int references art, body text);
            insert into art values (1, 'PROGRAM', 'open'), (2, 'BURNED_HOLDOUT', 'burned'), (3, 'EMBARGOED_OUTCOME', 'embargoed');
            insert into chunk values (10, 1, 'open chunk'), (20, 2, 'burned chunk'), (30, 3, 'embargoed chunk');
            alter table art enable row level security;
            alter table chunk enable row level security;
            create policy generator_reads on art for select to prometheus_read using (access_class = 'PROGRAM');
            create policy inherit_from_parent on chunk for select to prometheus_read
                using (exists (select 1 from art a where a.id = chunk.art_id));
            grant select on art, chunk to prometheus_read;""")
        c.execute("select count(*) from art"); su_art = c.fetchone()[0]
        c.execute("select count(*) from chunk"); su_chunk = c.fetchone()[0]
        c.execute("set role prometheus_read")
        c.execute("select current_user"); who = c.fetchone()[0]
        c.execute("select id from art order by id"); r_art = [r[0] for r in c.fetchall()]
        c.execute("select id from chunk order by id"); r_chunk = [r[0] for r in c.fetchall()]
        c.execute("select count(*) from chunk c join art a on a.id = c.art_id where a.access_class <> 'PROGRAM'")
        r_join = c.fetchone()[0]
        c.execute("reset role")
        conn.close()
        checks.append(dict(kind="POSITIVE", name="RLS: the generator-like role sees only PROGRAM artifacts",
                           ok=who == "prometheus_read" and r_art == [1], detail="as {}: art ids {}".format(who, r_art)))
        checks.append(dict(kind="CHEAT", name="RLS inheritance: a chunk of a hidden artifact is invisible even when queried directly",
                           ok=r_chunk == [10], detail="chunk ids {}".format(r_chunk)))
        checks.append(dict(kind="CHEAT", name="RLS: a join cannot reach hidden rows through the child table", ok=r_join == 0,
                           detail="{} hidden rows via join".format(r_join)))
        checks.append(dict(kind="NEGATIVE", name="the superuser bypasses RLS (why non-superuser logins are required)",
                           ok=su_art == 3 and su_chunk == 3, detail="superuser sees {} art, {} chunk".format(su_art, su_chunk)))
    finally:
        cur.execute("drop database if exists " + name)
        admin.close()
    for x in checks:
        out("{:<8} {:<5} {}  ({})".format(x["kind"], "PASS" if x["ok"] else "FAIL", x["name"], x["detail"]))
    return checks


def controls(write=True, out=print):
    """Live controls on Pan's catalog + the RLS proof. POSITIVE: burned holdout files are classified; an evaluator finds
    them. NEGATIVE: a PROGRAM document stays visible to a generator. CHEAT: a generator cannot reach a burned chunk by
    full-text, by vector search with that chunk's OWN stored vector, through pivot/refs, or through cochange; refused
    credential files hold no chunks; an unknown role fails closed."""
    import numpy as np
    from . import REPO, db, embed, pgvec, search
    res = []
    counts = apply_rules(out=lambda *a: None)
    burned_rule = "C-cosmos-burned-holdout"
    with db.cursor() as cur:
        cur.execute("""select artifact_id, path from pan.artifact where access_rule = %s and coalesce(n_chunks, 0) > 0
                       order by path""", (burned_rule,))
        burned = cur.fetchall()
        cur.execute("""select count(*) from pan.chunk c join pan.artifact a on a.artifact_id = c.artifact_id
                       where a.access_rule = 'R-credential-file'""")
        refused_chunks = cur.fetchone()[0]
        cur.execute("select count(*) from pan.artifact where access_rule = 'R-credential-file'")
        refused_n = cur.fetchone()[0]
    res.append(dict(kind="POSITIVE", name="the declared-exposed Cosmos hidden sets are classified BURNED_HOLDOUT",
                    ok=len(burned) >= 1, detail="{} chunked files: {}".format(len(burned), [p for _, p in burned])))
    burned_ids = {a for a, _ in burned}
    # a query aimed squarely at the burned files: their own path words
    q = "sealed spec holdout worlds nonce intervention protocol family"
    with as_role("generator"):
        gen = search.fts(q, k=50, path="prometheus/cosmos")
    with as_role("evaluator"):
        ev = search.fts(q, k=50, path="prometheus/cosmos")
    gen_burned = [h["path"] for h in gen if h["path"] in {p for _, p in burned}]
    ev_burned = [h["path"] for h in ev if h["path"] in {p for _, p in burned}]
    res.append(dict(kind="POSITIVE", name="an evaluator's full-text search can reach the burned files", ok=len(ev_burned) >= 1,
                    detail="evaluator hits on burned files: {}".format(len(ev_burned))))
    res.append(dict(kind="CHEAT", name="a generator's full-text search never returns a burned file", ok=not gen_burned,
                    detail="generator hits on burned files: {}".format(len(gen_burned))))
    with as_role("generator"):
        fw = search.fts("holdout D2 firewall opaque successor ciphertext commitments", k=10, path="prometheus/cosmos")
    res.append(dict(kind="NEGATIVE", name="a PROGRAM document (the D2 FIREWALL.md) stays visible to a generator",
                    ok=any(h["path"].endswith("c3_holdout_D2/FIREWALL.md") for h in fw), detail=[h["path"] for h in fw[:3]]))
    # strongest retrieval attack: query with a burned chunk's own stored vector, both vector backends
    leak = {}
    if burned_ids:
        with db.cursor() as cur:
            cur.execute("""select e.vec from pan.embedding e join pan.chunk c on c.chunk_id = e.chunk_id
                           where c.artifact_id = any(%s) and e.model = %s limit 1""", (list(burned_ids), embed.default_model()))
            vec = np.asarray(cur.fetchone()[0], dtype=np.float32)
        for backend in ("pg", "local"):
            os.environ["PAN_VECTOR_BACKEND"] = backend
            try:
                for role in ("generator", "evaluator"):
                    with as_role(role):
                        rows = search_vector_with(vec)
                    leak[backend + "/" + role] = sum(1 for r in rows if r["path"] in {p for _, p in burned})
            finally:
                os.environ.pop("PAN_VECTOR_BACKEND", None)
    gen_leak = {k: v for k, v in leak.items() if k.endswith("/generator")}
    ev_hit = {k: v for k, v in leak.items() if k.endswith("/evaluator")}
    res.append(dict(kind="POSITIVE", name="the same own-vector query DOES reach the burned file at evaluator clearance (the CHEAT below is not vacuous)",
                    ok=bool(ev_hit) and all(v >= 1 for v in ev_hit.values()), detail="burned hits: {}".format(ev_hit)))
    res.append(dict(kind="CHEAT", name="vector search with a burned chunk's OWN vector returns no burned file to a generator (pg and local backends)",
                    ok=bool(gen_leak) and all(v == 0 for v in gen_leak.values()), detail="burned hits: {}".format(gen_leak)))
    res.append(dict(kind="CHEAT", name="refused credential-shaped files hold no chunks",
                    ok=refused_chunks == 0, detail="{} refused files, {} chunks".format(refused_n, refused_chunks)))
    try:
        with as_role("root"):
            classes_for()
        closed = False
    except PermissionError:
        closed = True
    res.append(dict(kind="CHEAT", name="an unknown clearance role fails closed", ok=closed, detail="PermissionError" if closed else "OPEN"))
    for x in rls_proof(out=lambda *a: None):
        res.append(x)
    verdict = "PASS" if all(x["ok"] for x in res) else "FAIL"
    at = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    doc = dict(control="PAN-42 access classes (live catalog + throwaway-database RLS proof)", at=at, verdict=verdict,
               rules_applied=counts, checks=res)
    if write:
        p = REPO / "roles" / "Pan" / "reports" / "controls" / "ACCESS_{}.json".format(at)
        p.write_text(json.dumps(doc, indent=1, default=str) + "\n", encoding="utf-8")
        out("wrote " + str(p))
    for x in res:
        out("{:<8} {:<5} {}  ({})".format(x["kind"], "PASS" if x["ok"] else "FAIL", x["name"], x["detail"]))
    out(verdict)
    return doc


def search_vector_with(vec, k=10, pool=400):
    """Chunk-vector retrieval for a raw query vector through the same filters search.vector applies (used by the
    CHEAT control; no encoder needed)."""
    from . import embed, pgvec, search
    model = embed.default_model()
    if pgvec.backend() == "pg":
        cand = pgvec.knn("chunk", model, vec, pool)
    else:
        ids, m = search.load_matrix(model)
        sc = (m.astype("float32") @ vec)
        import numpy as np
        top = np.argsort(-sc)[:pool]
        cand = [(int(ids[i]), float(sc[i])) for i in top]
    return search.hydrate_chunks(cand, k)
