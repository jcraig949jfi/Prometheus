"""prometheus_self scour: grep the Prometheus repo for tensor-related content
and emit candidate tesserae.

Simplest possible scour — local files, no HTTP. Establishes the pattern.

For each matching Python function, emit one CandidateTessera with:
    epistemic_status='EXTRACTED'  (parser pulled it out of source)
    data_modality='code'
    code_language='python'
    game_affordance=['code_lineage', 'frankenfactorization']  (hints to Agon)
"""
from __future__ import annotations

import ast
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from ._base import Scour
from ..tensor import CandidateTessera

REPO_ROOT = Path(__file__).resolve().parents[3]

WALK_ROOTS = [
    REPO_ROOT / "prometheus_math",
    REPO_ROOT / "charon",
    REPO_ROOT / "theseus",
    REPO_ROOT / "apollo",
    REPO_ROOT / "ergon",
    REPO_ROOT / "scripts",
    REPO_ROOT / "agents",
]

TENSOR_KEYWORDS = [
    r"\btensor\b", r"\brank\b", r"\bmultilinear\b", r"\bcontract(?:ion)?\b",
    r"\bkronecker\b", r"\btucker\b", r"\bhosvd\b",
    r"\bcp[\s_-]?decomp", r"\btensor[\s_-]?train\b", r"\btt[\s_-]?rank\b",
    r"\bmps\b", r"\bpeps\b", r"\bsecant\b",
    r"\bmahler\b", r"\blehmer\b", r"\bspectral\b",
    r"\beigenvalue\b", r"\bjordan\b", r"\bschmidt\b",
    r"\bnewton\s+polytope\b", r"\bdeterminant\b", r"\bpermanent\b",
    r"\bisogeny\b", r"\bgalois\b",
    r"\bbeta\s+function\b", r"\bgamma\s+function\b",
    r"\bquantum\b.{0,40}\bstate\b",
    r"\bkillvector\b", r"\bkill_vector\b",
    r"\bfingerprint\b",
]
KW_RE = re.compile("|".join(TENSOR_KEYWORDS), re.IGNORECASE)

PATH_TO_DISCIPLINE = [
    ("prometheus_math/lehmer", "math.NT"),
    ("prometheus_math/bsd", "math.NT"),
    ("prometheus_math/elliptic", "math.NT"),
    ("prometheus_math/modular", "math.NT"),
    ("prometheus_math/galois", "math.NT"),
    ("prometheus_math/knot", "math.GT"),
    ("prometheus_math/genus", "math.AG"),
    ("prometheus_math", "math.HO"),
    ("charon/diagnostics", "math.ST"),
    ("apollo", "cs.ML"),
    ("ergon/learner", "cs.LG"),
    ("agents/talos", "cs.ML"),
    ("scripts", "cs.DS"),
    ("agents", "cs.DS"),
    ("theseus", "math.HO"),
]


def _discipline_for(path: Path) -> str:
    rel = str(path).replace("\\", "/")
    for prefix, disc in PATH_TO_DISCIPLINE:
        if prefix in rel:
            return disc
    return "fringe"


def _walk(roots: Iterable[Path]) -> list[Path]:
    out = []
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*.py"):
            if "__pycache__" in p.parts or ".venv" in p.parts:
                continue
            if p.name in ("__init__.py", "__main__.py", "setup.py"):
                continue
            out.append(p)
    return out


def _extract_functions(text: str, source_path: str) -> list[dict]:
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return []
    src_lines = text.splitlines()
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        docstring = ast.get_docstring(node) or ""
        snippet = "\n".join(src_lines[node.lineno - 1: node.end_lineno or node.lineno])
        body_lines = (node.end_lineno or node.lineno) - node.lineno + 1
        haystack = f"{node.name} {docstring} {snippet[:500]}"
        if not KW_RE.search(haystack):
            continue
        out.append({
            "name": node.name,
            "docstring": docstring,
            "snippet": snippet,
            "body_lines": body_lines,
            "lineno": node.lineno,
        })
    return out


class PrometheusSelfScour(Scour):
    name = "prometheus_self"
    interval_hint_sec = 3600

    def discover(self, state: dict) -> list[CandidateTessera]:
        last_mtimes: dict[str, float] = (state or {}).get("path_mtimes", {})
        new_mtimes: dict[str, float] = {}
        candidates: list[CandidateTessera] = []
        files_scanned = 0
        files_skipped_unchanged = 0
        now_iso = datetime.now(timezone.utc).isoformat()
        for path in _walk(WALK_ROOTS):
            try:
                rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            except Exception:
                continue
            try:
                mtime = path.stat().st_mtime
            except Exception:
                continue
            new_mtimes[rel] = mtime
            if last_mtimes.get(rel) == mtime:
                files_skipped_unchanged += 1
                continue
            files_scanned += 1
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            year = datetime.fromtimestamp(mtime, tz=timezone.utc).year
            discipline = _discipline_for(path)
            for fn in _extract_functions(text, rel):
                obj_kind = "algorithm" if re.search(
                    r"(algo|compute|eval|search|score|fit|solve)",
                    fn["name"], re.IGNORECASE) else "implementation"
                title = f"{fn['name']} — {rel}"
                body = fn["docstring"] or f"(undocumented; {fn['body_lines']} lines)"
                # game affordance hint: this kind of tessera fits these games
                game_aff = ["code_lineage", "frankenfactorization"]
                if "test" in fn["name"].lower() or "benchmark" in body.lower():
                    game_aff.append("contraction_goblin")
                cand = CandidateTessera(
                    coords={
                        "time": year,
                        "discipline": discipline,
                        "object_kind": obj_kind,
                        "structural_rank": None,
                        "abstraction_level": "implementation",
                        "substrate_yield_type": None,
                        "epistemic_status": "EXTRACTED",  # parser pulled this from source
                        "data_modality": "code",
                        "code_language": "python",
                    },
                    content={
                        "title": title,
                        "body": body[:2000],
                        "equation_latex": [],
                        "code_snippets": [fn["snippet"][:4000]],
                    },
                    source={
                        "scour": self.name,
                        "source_path": rel,
                        "lineno": fn["lineno"],
                        "extracted_at": now_iso,
                    },
                    tags={
                        "researchers": [],
                        "lineage_ancestors": [],
                        "free_tags": sorted(set(
                            kw.lower()
                            for kw in re.findall(r"\b[A-Za-z][A-Za-z0-9_-]{3,}\b",
                                                 fn["docstring"][:200])
                            if KW_RE.search(kw)
                        )),
                        "citations": [],
                        "game_affordance": game_aff,
                    },
                    confidence=0.9,  # high — direct extraction from source
                )
                candidates.append(cand)
        state["path_mtimes"] = new_mtimes
        state["last_files_scanned"] = files_scanned
        state["last_files_skipped_unchanged"] = files_skipped_unchanged
        state["last_run_at"] = now_iso
        return candidates
