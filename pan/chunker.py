"""PAN-04: extract text from catalogued git blobs and split it into chunks with
line ranges and a heading path; pan.chunk stores them with a full-text vector.

Content comes from `git cat-file --batch` at the blob SHAs recorded by the
inventory (never a working tree). Incremental: an artifact whose
indexed_blob equals its blob_sha is skipped.

What is chunked (text) and what is not (data, for the lake):
  chunked   .md .txt .rst .tex .py and other code, config, small .json
            (<= JSON_MAX bytes: receipts, states, manifests, configs)
  skipped   .jsonl .csv and large .json (data: consolidated into Parquet by
            PAN-16), binaries, anything above TEXT_MAX bytes; every skip is
            counted by reason in the run record.
"""
import datetime as dt
import json
import re
import subprocess
import time

from . import REPO, host

TEXT_EXT = {".md", ".txt", ".rst", ".tex", ".org", ".py", ".rs", ".js", ".ts", ".c", ".h", ".cpp", ".hpp", ".go",
            ".java", ".jl", ".r", ".lean", ".sql", ".sh", ".bat", ".ps1", ".cmd", ".toml", ".yaml", ".yml",
            ".ini", ".cfg", ".conf", ".html", ".htm", ".gp", ".sage", ".m", ".asm", ".z80", ".s", ".mjs", ".cs",
            ".diff", ".patch", ".log", ".xml", ""}
JSON_MAX = 64 * 1024
TEXT_MAX = 4 * 1024 * 1024
CHUNK = 1800          # target characters per chunk
CODE_EXT = {".py", ".rs", ".js", ".ts", ".c", ".h", ".cpp", ".hpp", ".go", ".java", ".jl", ".r", ".lean", ".mjs",
            ".cs", ".gp", ".sage", ".m"}
MD_HEAD = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
CODE_TOP = re.compile(r"^(?:async\s+def|def|class|fn|pub\s+fn|function|impl|struct|theorem|lemma|def)\s+([A-Za-z_][\w]*)")


def eligible(ext: str, size: int):
    if ext == ".json":
        return (size or 0) <= JSON_MAX, "json_too_large"
    if ext not in TEXT_EXT:
        return False, "not_text_ext"
    if (size or 0) > TEXT_MAX:
        return False, "too_large"
    return True, ""


def _windows(lines, start_line, heading):
    """Group lines into chunks of about CHUNK characters, breaking on blank lines
    where possible. Yields (line_start, line_end, heading, text)."""
    buf, n, s = [], 0, start_line
    for i, ln in enumerate(lines):
        buf.append(ln)
        n += len(ln) + 1
        if n >= CHUNK and (not ln.strip() or n >= CHUNK * 1.6):
            yield s, start_line + i, heading, "\n".join(buf)
            buf, n, s = [], 0, start_line + i + 1
    if buf and "".join(buf).strip():
        yield s, start_line + len(lines) - 1, heading, "\n".join(buf)


def split_markdown(text):
    lines = text.split("\n")
    sections, path, cur, cur_start = [], [], [], 1
    for i, ln in enumerate(lines, 1):
        m = MD_HEAD.match(ln)
        if m:
            if cur:
                sections.append((cur_start, " > ".join(path), cur))
            level = len(m.group(1))
            path = path[:level - 1] + [m.group(2)[:120]]
            cur, cur_start = [ln], i
        else:
            cur.append(ln)
    if cur:
        sections.append((cur_start, " > ".join(path), cur))
    for start, heading, body in sections:
        yield from _windows(body, start, heading)


def split_code(text):
    lines = text.split("\n")
    blocks, cur, cur_start, heading = [], [], 1, "(module)"
    for i, ln in enumerate(lines, 1):
        m = CODE_TOP.match(ln)
        if m and cur:
            blocks.append((cur_start, heading, cur))
            cur, cur_start, heading = [], i, m.group(0)[:120]
        elif m:
            heading = m.group(0)[:120]
        cur.append(ln)
    if cur:
        blocks.append((cur_start, heading, cur))
    for start, h, body in blocks:
        yield from _windows(body, start, h)


def split(text, ext):
    if ext in (".md", ".rst", ".org"):
        return list(split_markdown(text))
    if ext in CODE_EXT:
        return list(split_code(text))
    return list(_windows(text.split("\n"), 1, ""))


def title_of(text, ext):
    for ln in text.split("\n")[:60]:
        s = ln.strip()
        if not s:
            continue
        if ext in (".md", ".rst", ".org"):
            m = MD_HEAD.match(s)
            if m:
                return m.group(2)[:200]
            continue
        if ext == ".py":
            s = s.strip("\"'#! ").strip()
            if s and not s.startswith(("import", "from ", "-*-", "!/usr")):
                return s[:200]
            continue
        return s[:200]
    return None


class BlobReader:
    """One long-lived `git cat-file --batch` process."""

    def __init__(self):
        self.p = subprocess.Popen(["git", "cat-file", "--batch"], cwd=REPO, stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE)

    def read(self, sha):
        self.p.stdin.write((sha + "\n").encode())
        self.p.stdin.flush()
        header = self.p.stdout.readline().split()
        if len(header) < 3 or header[1] == b"missing":
            return None
        size = int(header[2])
        data = self.p.stdout.read(size)
        self.p.stdout.read(1)
        return data

    def close(self):
        try:
            self.p.stdin.close()
            self.p.wait(timeout=30)
        except Exception:
            self.p.kill()


def run(limit: int = 0, kinds=None, out=print, batch_files: int = 400):
    from psycopg2.extras import execute_values
    from . import db
    t0 = time.time()
    run_id = "chunk-{}-{}".format(dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"), host().lower())
    with db.cursor() as cur:
        q = """select artifact_id, path, blob_sha, ext, size_bytes, repo_sha from pan.artifact
               where source='git' and (indexed_blob is distinct from blob_sha)"""
        args = []
        if kinds:
            q += " and kind = any(%s)"
            args.append(kinds)
        q += " order by artifact_id"
        if limit:
            q += " limit %d" % int(limit)
        cur.execute(q, args)
        todo = cur.fetchall()
        sha = todo[0][5] if todo else None
        cur.execute("insert into pan.run (run_id, kind, host, git_sha, params) values (%s,'chunk',%s,%s,%s)",
                    (run_id, host(), sha, json.dumps({"limit": limit, "kinds": kinds})))
    out("{} artifacts need (re)chunking".format(len(todo)))
    skipped, n_chunks, n_files, n_binary = {}, 0, 0, 0
    reader = BlobReader()
    conn = db.connect()
    try:
        cur = conn.cursor()
        for i in range(0, len(todo), batch_files):
            part = todo[i:i + batch_files]
            rows, updates = [], []
            for aid, path, bsha, ext, size, _ in part:
                ok, why = eligible(ext, size)
                if not ok:
                    skipped[why] = skipped.get(why, 0) + 1
                    updates.append((aid, False, None, 0, bsha))
                    continue
                data = reader.read(bsha)
                if data is None:
                    skipped["blob_missing"] = skipped.get("blob_missing", 0) + 1
                    continue
                if b"\x00" in data[:8192]:
                    n_binary += 1
                    updates.append((aid, False, None, 0, bsha))
                    continue
                text = data.decode("utf-8", "replace").replace("\x00", "").replace("\r\n", "\n")
                pieces = split(text, ext)
                for ord_, (ls, le, head, body) in enumerate(pieces):
                    rows.append((aid, ord_, ls, le, (head or None), body, len(body)))
                updates.append((aid, True, title_of(text, ext), len(pieces), bsha))
                n_files += 1
            ids = [u[0] for u in updates]
            cur.execute("delete from pan.chunk where artifact_id = any(%s)", (ids,))
            if rows:
                execute_values(cur, """insert into pan.chunk (artifact_id, ord, line_start, line_end, heading, body, n_chars)
                                       values %s""", rows, page_size=1000)
            execute_values(cur, """update pan.artifact a set is_text = v.is_text, title = v.title, n_chunks = v.n,
                                   indexed_blob = v.blob from (values %s) as v(id, is_text, title, n, blob)
                                   where a.artifact_id = v.id""", updates, page_size=1000)
            conn.commit()
            n_chunks += len(rows)
            out("  {}/{} files, {} chunks so far, {:.0f}s".format(min(i + batch_files, len(todo)), len(todo),
                                                                   n_chunks, time.time() - t0))
        counts = dict(files_chunked=n_files, chunks=n_chunks, binary=n_binary, skipped=skipped,
                      seconds=round(time.time() - t0, 1))
        cur.execute("update pan.run set finished_at=now(), status='OK', counts=%s where run_id=%s",
                    (json.dumps(counts), run_id))
        conn.commit()
    finally:
        reader.close()
        conn.close()
    out(json.dumps(counts))
    return counts
