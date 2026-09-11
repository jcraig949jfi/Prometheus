"""Characterize the Talos corpus shards (operator ruling on TALOS-01, 2026-09-11).

Reads the byte-identical copies under roles/Talos/ledgers/corpus_shards_2026-09-11/
and writes roles/Talos/ledgers/CORPUS_CHARACTERIZATION_2026-09-11.json. Every
number in the summary comes from this file; nothing is read from the May
manifest except to compare against it.

Measured, per stream and overall:
  identity        rows, bytes, sha256 (must equal the ledger's provenance hashes)
  duplication     exact fingerprint dups; exact snippet-text dups; whitespace-
                  normalised snippet dups; (function_name, docstring) dups
  provenance      unique source files; rows per file; whether each source file
                  still exists on the tree this runs from; top directories
  representation  ast-parseable raw and after dedent (an indented snippet was
                  extracted from inside a class or nested scope: it is not a
                  standalone unit); is a def; method (first arg self/cls);
                  test function; stub (body <= 2 lines or body is pass/...);
                  free names not bound locally and not builtins (closure under
                  builtins = 0 free names); docstring length; body lines
  diversity       distinct docstrings; top repeated docstrings and their share;
                  distinct function names; top names
  subpopulations  by source-path family (declared below) with the same
                  representation stats per family

Controls (section 2 of the base role): a planted-row positive control and a
cheat control run on a synthetic 6-row shard before the real shards, so the
dedup and free-name measurements are shown to fire.

Run from a linked worktree:  python roles/Talos/science/characterize_corpus.py
"""
from __future__ import annotations

import ast
import builtins
import collections
import hashlib
import json
import re
import statistics
import subprocess
import sys
import textwrap
import warnings
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SHARDS = REPO / "roles" / "Talos" / "ledgers" / "corpus_shards_2026-09-11"
OUT = REPO / "roles" / "Talos" / "ledgers" / "CORPUS_CHARACTERIZATION_2026-09-11.json"
BUILTINS = set(dir(builtins))

# Source-path families: the first matching prefix wins. Declared before the
# rows are read (this is the pre-registration of the subpopulation cut).
FAMILIES = [
    ("hephaestus_forge_tools", "agents/hephaestus/forge"),
    ("hephaestus_humanreadable", "agents/hephaestus/humanreadable/"),
    ("hephaestus_code_from_claude", "agents/hephaestus/code_from_claude/"),
    ("hephaestus_other", "agents/hephaestus/"),
    ("prometheus_math_tests", "prometheus_math/tests/"),
    ("prometheus_math_modules", "prometheus_math/"),
    ("charon_diagnostics", "charon/diagnostics/"),
    ("theseus_scripts", "theseus/scripts/"),
    ("scripts_agora_persist", "scripts/"),
]


def family_of(path: str) -> str:
    for name, prefix in FAMILIES:
        if path.startswith(prefix):
            return name
    return "unclassified"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def quantiles(xs):
    if not xs:
        return None
    xs = sorted(xs)
    n = len(xs)
    q = lambda f: xs[min(n - 1, int(f * n))]
    return {"min": xs[0], "p10": q(0.10), "p50": q(0.50), "p90": q(0.90), "max": xs[-1],
            "mean": round(statistics.fmean(xs), 2)}


class SnippetFacts:
    """AST facts about one snippet; parse failure is a fact, not an error."""

    def __init__(self, snippet: str):
        self.parses = False
        self.is_def = False
        self.is_method = False
        self.is_test = False
        self.is_stub = False
        self.free_names = None
        self.has_return = False
        self.indented = snippet[:1] in (" ", "\t")   # extracted from inside a class or a nested scope
        self.parses_raw = False
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                tree = ast.parse(snippet)
                self.parses_raw = True
            except SyntaxError:
                try:
                    tree = ast.parse(textwrap.dedent(snippet))
                except SyntaxError:
                    return
        self.parses = True
        if not tree.body or not isinstance(tree.body[0], (ast.FunctionDef, ast.AsyncFunctionDef)):
            return
        fn = tree.body[0]
        self.is_def = True
        args = fn.args
        first = (args.posonlyargs + args.args)[0].arg if (args.posonlyargs + args.args) else None
        self.is_method = first in ("self", "cls")
        self.is_test = fn.name.startswith("test_") or fn.name.startswith("test")
        body = fn.body
        if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                and isinstance(body[0].value.value, str):
            body = body[1:]
        self.is_stub = (not body) or all(isinstance(s, ast.Pass) or
                                         (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and s.value.value is Ellipsis)
                                         for s in body)
        self.has_return = any(isinstance(n, ast.Return) and n.value is not None for n in ast.walk(fn))
        bound = set()
        for a in args.posonlyargs + args.args + args.kwonlyargs:
            bound.add(a.arg)
        if args.vararg:
            bound.add(args.vararg.arg)
        if args.kwarg:
            bound.add(args.kwarg.arg)
        bound.add(fn.name)
        for n in ast.walk(fn):
            if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
                bound.add(n.id)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                bound.add(n.name)
            elif isinstance(n, ast.arg):
                bound.add(n.arg)
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                for al in n.names:
                    bound.add((al.asname or al.name).split(".")[0])
            elif isinstance(n, ast.ExceptHandler) and n.name:
                bound.add(n.name)
            elif isinstance(n, ast.comprehension):
                for t in ast.walk(n.target):
                    if isinstance(t, ast.Name):
                        bound.add(t.id)
        free = set()
        for n in ast.walk(fn):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id not in bound and n.id not in BUILTINS:
                free.add(n.id)
        self.free_names = sorted(free)


def norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def measure(rows, label, tree_files=None):
    n = len(rows)
    fps = collections.Counter(r["fingerprint"] for r in rows)
    snip_h = collections.Counter(hashlib.sha1(r["snippet"].encode("utf-8")).hexdigest() for r in rows)
    norm_h = collections.Counter(hashlib.sha1(norm_ws(r["snippet"]).encode("utf-8")).hexdigest() for r in rows)
    nd = collections.Counter((r["function_name"], norm_ws(r["docstring"] or "")) for r in rows)
    files = collections.Counter(r["source_path"] for r in rows)
    docs = collections.Counter(norm_ws(r["docstring"] or "") for r in rows if r.get("docstring"))
    names = collections.Counter(r["function_name"] for r in rows)
    facts = [SnippetFacts(r["snippet"]) for r in rows]
    parses = sum(f.parses for f in facts)
    defs = sum(f.is_def for f in facts)
    free_counts = [len(f.free_names) for f in facts if f.free_names is not None]
    free_name_freq = collections.Counter(nm for f in facts if f.free_names for nm in f.free_names)
    exists = None
    if tree_files is not None:
        exists = {"files_present_on_tree": sum(1 for p in files if p in tree_files),
                  "files_absent_from_tree": sum(1 for p in files if p not in tree_files),
                  "rows_whose_file_is_present": sum(c for p, c in files.items() if p in tree_files),
                  "rows_whose_file_is_absent": sum(c for p, c in files.items() if p not in tree_files)}
    top_dirs = collections.Counter("/".join(r["source_path"].split("/")[:3]) for r in rows)
    return {
        "label": label,
        "rows": n,
        "duplication": {
            "unique_fingerprints": len(fps),
            "rows_beyond_first_fingerprint": n - len(fps),
            "unique_snippet_text": len(snip_h),
            "rows_beyond_first_snippet_text": n - len(snip_h),
            "unique_snippet_ws_normalised": len(norm_h),
            "rows_beyond_first_ws_normalised": n - len(norm_h),
            "unique_name_docstring_pairs": len(nd),
            "rows_beyond_first_name_docstring": n - len(nd),
            "largest_ws_normalised_cluster": norm_h.most_common(1)[0][1] if norm_h else 0,
        },
        "provenance": {
            "unique_source_files": len(files),
            "rows_per_file": quantiles(list(files.values())),
            "top_files": files.most_common(8),
            "top_dirs_depth3": top_dirs.most_common(12),
            "tree_check": exists,
        },
        "representation": {
            "ast_parses_raw": sum(f.parses_raw for f in facts),
            "indented_extracted_from_class_or_nested_scope": sum(f.indented for f in facts),
            "ast_parses_after_dedent": parses, "ast_parse_ratio_after_dedent": round(parses / n, 4) if n else None,
            "is_function_def": defs,
            "is_method_self_or_cls": sum(f.is_method for f in facts),
            "is_test_function": sum(f.is_test for f in facts),
            "is_stub_pass_or_empty": sum(f.is_stub for f in facts),
            "has_value_return": sum(f.has_return for f in facts),
            "has_docstring_flag_true": sum(1 for r in rows if r.get("has_docstring")),
            "docstring_nonempty": sum(1 for r in rows if (r.get("docstring") or "").strip()),
            "body_lines": quantiles([r["body_lines"] for r in rows]),
            "snippet_chars": quantiles([len(r["snippet"]) for r in rows]),
            "docstring_chars": quantiles([len(r.get("docstring") or "") for r in rows]),
            "free_names_per_snippet": quantiles(free_counts),
            "closed_under_builtins": sum(1 for c in free_counts if c == 0),
            "closed_under_builtins_ratio": round(sum(1 for c in free_counts if c == 0) / len(free_counts), 4) if free_counts else None,
            "top_free_names": free_name_freq.most_common(15),
        },
        "diversity": {
            "distinct_docstrings": len(docs),
            "top_docstrings": [(d[:90], c) for d, c in docs.most_common(10)],
            "top10_docstring_share": round(sum(c for _, c in docs.most_common(10)) / n, 4) if n else None,
            "distinct_function_names": len(names),
            "top_function_names": names.most_common(15),
        },
    }


def controls():
    """Positive: two exact duplicates and one whitespace-variant are counted. Cheat: a
    snippet whose only free name is a builtin must count as closed; one with an
    unbound name must not. Negative: six distinct rows report zero duplicates."""
    def row(i, fn, snip, doc="d", path="x/y.py"):
        return {"fingerprint": "f%d" % i, "stream": "ctl", "weight": 0, "extracted_at": "", "function_name": fn,
                "docstring": doc, "snippet": snip, "lineno": 1, "body_lines": 2, "has_docstring": True, "source_path": path}
    a = "def f(x):\n    return len(x)"
    b = "def g(x):\n    return helper(x)"
    pos = [row(1, "f", a), row(2, "f", a), row(3, "f", "def f(x):\n    return  len(x)"), row(4, "g", b),
           row(5, "h", "    def h(self):\n        pass"), row(6, "t", "def test_t():\n    assert 1")]
    m = measure(pos, "control_positive")
    d = m["duplication"]; rp = m["representation"]
    checks = {
        "positive_exact_snippet_dups_detected": d["rows_beyond_first_snippet_text"] == 1,
        "positive_ws_normalised_dups_detected": d["rows_beyond_first_ws_normalised"] == 2,
        "cheat_builtin_only_is_closed": SnippetFacts(a).free_names == [],
        "cheat_unbound_name_is_open": SnippetFacts(b).free_names == ["helper"],
        "method_and_test_and_stub_detected": rp["is_method_self_or_cls"] == 1 and rp["is_test_function"] == 1 and rp["is_stub_pass_or_empty"] == 1,
        "parse_failure_is_a_fact": SnippetFacts("def (:").parses is False,
        "indented_method_parses_after_dedent_and_is_method": (lambda f: f.indented and not f.parses_raw and f.parses and f.is_method)(SnippetFacts("    def h(self):\n        pass")),
    }
    neg = [row(i, "f%d" % i, "def f%d(x):\n    return x + %d" % (i, i)) for i in range(6)]
    mn = measure(neg, "control_negative")["duplication"]
    checks["negative_no_dups_on_distinct_rows"] = mn["rows_beyond_first_ws_normalised"] == 0
    return checks


def main():
    ctl = controls()
    if not all(ctl.values()):
        print("CONTROLS FAILED", ctl)
        sys.exit(2)
    tree = subprocess.run(["git", "ls-tree", "-r", "--name-only", "HEAD"], cwd=str(REPO),
                          capture_output=True, text=True, timeout=120).stdout.split("\n")
    tree_files = set(tree)
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(REPO), capture_output=True, text=True).stdout.strip()
    result = {"generated_from": "roles/Talos/science/characterize_corpus.py", "tree_head": head, "controls": ctl,
              "families_declared": FAMILIES, "shards": {}, "families": {}, "overall": None}
    all_rows = []
    for name in ("hephaestus_forge", "prometheus_substrate"):
        p = SHARDS / (name + ".jsonl")
        raw = p.read_bytes()
        rows = [json.loads(l) for l in raw.decode("utf-8").splitlines() if l.strip()]
        m = measure(rows, name, tree_files)
        m["identity"] = {"path": str(p.relative_to(REPO)).replace("\\", "/"), "bytes": len(raw), "sha256": sha256_file(p),
                         "crlf_rows": raw.count(b"\r\n"), "manifest_2026_05_30_claimed_rows": None}
        result["shards"][name] = m
        all_rows.extend(rows)
    manifest = json.loads((REPO / "agents/talos/corpus/manifest_latest.json").read_text(encoding="utf-8"))
    for name in result["shards"]:
        result["shards"][name]["identity"]["manifest_2026_05_30_claimed_rows"] = manifest["corpus_size"].get(name)
    result["overall"] = measure(all_rows, "overall", tree_files)
    # cross-stream duplication: a snippet present in both shards
    per_stream_norm = {}
    for r in all_rows:
        per_stream_norm.setdefault(hashlib.sha1(norm_ws(r["snippet"]).encode()).hexdigest(), set()).add(r["stream"])
    result["overall"]["duplication"]["ws_normalised_snippets_in_both_streams"] = sum(1 for s in per_stream_norm.values() if len(s) == 2)
    fam_rows = collections.defaultdict(list)
    for r in all_rows:
        fam_rows[family_of(r["source_path"])].append(r)
    for fam, rows in sorted(fam_rows.items(), key=lambda kv: -len(kv[1])):
        result["families"][fam] = measure(rows, fam, tree_files)
    OUT.write_text(json.dumps(result, indent=1), encoding="utf-8", newline="\n")
    print("wrote", OUT.relative_to(REPO), "rows", len(all_rows), "controls", all(ctl.values()))


if __name__ == "__main__":
    main()
