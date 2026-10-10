"""PAN-37: review queue -- ranked review units from the catalog, so the agents that review the platform start
where a review is most likely to pay: code that changed recently, that no test imports, and that carries
static smells. Every signal is measured and shown with its line numbers; the score only orders the list.
Pan builds the queue; it never dispatches review work (QUESTIONS.md Q-011).

python -m pan review build               pan.review_unit at the catalog sha (reads blobs via git cat-file)
python -m pan review queue [--seat S] [-k N]

Score (documented, not tuned): churn = commits_7d + 0.25 * commits_30d; risk = 1 + (1 if no test imports the
module) + 0.5 * (number of smell kinds); score = churn * risk. A module untouched for 30 days scores 0.
"""
import ast
import datetime as dt
import json
import re
import time

from . import host

ABS = re.compile(r"(?:^|[^A-Za-z0-9_])[A-Za-z]:[\\/][A-Za-z0-9_.~$-]|(?:^|[^A-Za-z0-9_])/[cd]/Prometheus")
LAN = re.compile(r"\b192\.168\.\d{1,3}\.\d{1,3}\b")
KINDS = ("abs_path", "lan_ip", "bare_except", "except_pass", "shell_true", "eval_exec", "long_function",
         "syntax_error")


def smells(src):
    """kind -> sorted line numbers (at most 20 each). String constants are checked, docstrings and comments
    are not; a file that does not parse reports only syntax_error."""
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return {"syntax_error": [0]}
    docs = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            b = node.body
            if b and isinstance(b[0], ast.Expr) and isinstance(getattr(b[0], "value", None), ast.Constant) \
                    and isinstance(b[0].value.value, str):
                docs.add(id(b[0].value))
    out = {}

    def add(kind, line):
        out.setdefault(kind, set()).add(line)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docs:
            if ABS.search(node.value):
                add("abs_path", node.lineno)
            if LAN.search(node.value):
                add("lan_ip", node.lineno)
        elif isinstance(node, ast.ExceptHandler):
            if node.type is None:
                add("bare_except", node.lineno)
            elif len(node.body) == 1 and isinstance(node.body[0], ast.Pass) and isinstance(node.type, ast.Name) \
                    and node.type.id in ("Exception", "BaseException"):
                add("except_pass", node.lineno)
        elif isinstance(node, ast.Call):
            if any(kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True
                   for kw in node.keywords):
                add("shell_true", node.lineno)
            if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec"):
                add("eval_exec", node.lineno)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.end_lineno - node.lineno + 1 > 150:
            add("long_function", node.lineno)
    return {k: sorted(v)[:20] for k, v in out.items()}


def score(commits_7d, commits_30d, tested_by, smell_map):
    churn = commits_7d + 0.25 * commits_30d
    risk = 1 + (1 if tested_by == 0 else 0) + 0.5 * len(smell_map)
    return round(churn * risk, 3)


def build(out=print):
    from psycopg2.extras import execute_values
    from . import db
    from .chunker import BlobReader
    from .frontier import finish_run, new_run
    from .repobench import TEST_RE, imported_modules
    t0 = time.time()
    run_id = new_run("review-build", {})
    with db.cursor() as cur:
        cur.execute("select repo_sha from pan.artifact where source='git' limit 1")
        sha = cur.fetchone()[0]
        cur.execute("select path, blob_sha, seat from pan.artifact where source='git' and ext='.py'")
        py = {p: (b, s) for p, b, s in cur.fetchall()}
        cur.execute("""select f.path,
                              count(*) filter (where c.committed_at > now() - interval '7 days'),
                              count(*) filter (where c.committed_at > now() - interval '30 days'),
                              max(c.committed_at),
                              array_remove(array_agg(distinct c.seat) filter
                                           (where c.committed_at > now() - interval '30 days'), null)
                       from pan.commit_file f join pan.commit c using (sha)
                       where f.path like '%%.py' group by f.path""")
        churn = {p: (a, b, last, seats) for p, a, b, last, seats in cur.fetchall()}
        cur.execute("""select a.path, count(*) from pan.chunk_dup d join pan.artifact a using (artifact_id)
                       where d.canonical_id is not null and d.canonical_id <> d.chunk_id group by 1""")
        dups = dict(cur.fetchall())
    files = set(py)
    tests = [p for p in py if TEST_RE.search(p)]
    br = BlobReader()
    texts = {}
    try:
        for p, (b, _) in py.items():
            data = br.read(b)
            texts[p] = data.decode("utf-8", errors="replace") if data is not None else ""
    finally:
        br.close()
    tested = {}
    for tp in tests:
        try:
            for m in imported_modules(tp, texts[tp], files):
                tested[m] = tested.get(m, 0) + 1
        except (SyntaxError, ValueError):
            continue
    rows = []
    for p, (b, seat) in py.items():
        if TEST_RE.search(p) or p.endswith("conftest.py"):
            continue
        sm = smells(texts[p])
        a7, a30, last, seats = churn.get(p, (0, 0, None, []))
        tb = tested.get(p, 0)
        rows.append((p, sha, ",".join(seats) if seats else seat, texts[p].count("\n") + 1, a7, a30, last, tb,
                     json.dumps(sm), dups.get(p, 0), score(a7, a30, tb, sm), run_id))
    with db.cursor() as cur:
        cur.execute("delete from pan.review_unit")
        execute_values(cur, """insert into pan.review_unit (path, repo_sha, seat, lines, commits_7d, commits_30d,
                               last_commit_at, tested_by, smells, dup_chunks, score, run_id) values %s""",
                       rows, page_size=1000)
    c = dict(repo_sha=sha, modules=len(rows), tests=len(tests), tested=sum(1 for r in rows if r[7] > 0),
             changed_30d=sum(1 for r in rows if r[5] > 0), with_smells=sum(1 for r in rows if r[8] != "{}"),
             seconds=round(time.time() - t0, 1))
    finish_run(run_id, c, "OK")
    out(json.dumps(c))
    return c


def queue(seat=None, k=25, out=print):
    from . import db
    where, args = "score > 0", []
    if seat:
        where += " and seat ilike %s"
        args.append("%" + seat + "%")
    with db.cursor() as cur:
        cur.execute("""select path, seat, commits_7d, commits_30d, tested_by, smells, dup_chunks, lines, score, repo_sha
                       from pan.review_unit where {} order by score desc, commits_7d desc, path limit %s""".format(where),
                    args + [k])
        rows = cur.fetchall()
    if not rows:
        out("(no recently changed modules match)")
        return rows
    out("review queue at {} -- signals, not verdicts (score = churn x risk; see pan/review.py)".format(rows[0][9][:9]))
    for p, s, a7, a30, tb, sm, dup, lines, sc, _ in rows:
        smell = ", ".join("{} L{}".format(kk, ",".join(map(str, v[:3]))) for kk, v in sorted(sm.items()))
        out("{:>7.2f}  {}  [{}]".format(sc, p, (s or "?")[:30]))
        out("         {} lines; commits 7d/30d {}/{}; tests importing it {}; copied chunks {}{}".format(
            lines, a7, a30, tb, dup, "; " + smell if smell else ""))
    return rows
