"""mathlib4 landscape — the formal-proof dependency graph.

Node:  "mathlib:<DeclName>"
Verb:  "uses"  (declaration A's body references declaration B)

Machine-checkable territory: edges here are grounded in real Lean source, which
is why this landscape is walked first (HARD-4 calibration). We do a lightweight
token-level parse, not a full Lean elaboration — good enough to weave a real
dependency subgraph and bounded in cost by a growing working set of files.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_ROOT = _REPO / "external_deps" / "mathlib4" / "Mathlib"

_DECL_RE = re.compile(r"^\s*(?:@\[[^\]]*\]\s*)?(?:theorem|lemma|def|instance|abbrev)\s+([A-Za-z_][\w.']*)", re.M)
_IDENT_RE = re.compile(r"[A-Za-z_][\w.']*")
_KEYWORDS = {
    "theorem", "lemma", "def", "instance", "abbrev", "by", "fun", "let", "in",
    "match", "with", "if", "then", "else", "do", "have", "show", "from", "at",
    "intro", "exact", "apply", "rfl", "simp", "rw", "calc", "this", "Prop",
    "Type", "Sort", "Nat", "Int", "True", "False", "And", "Or",
}


class MathlibLandscape:
    name = "mathlib"

    def __init__(self):
        self._files: list[Path] = []
        self._unparsed: list[Path] = []
        self._index: dict[str, str] = {}      # decl -> body slice
        self._reffreq: Counter = Counter()    # how often a decl is referenced
        if _ROOT.exists():
            self._files = list(_ROOT.rglob("*.lean"))
            self._unparsed = list(self._files)

    def available(self) -> bool:
        return bool(self._files)

    def _parse_file(self, path: Path) -> None:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return
        decls = list(_DECL_RE.finditer(text))
        for i, m in enumerate(decls):
            name = m.group(1)
            start = m.end()
            end = decls[i + 1].start() if i + 1 < len(decls) else min(len(text), start + 4000)
            body = text[start:end][:4000]
            # last writer wins; refs counted once per decl
            self._index[name] = body
            seen = set()
            for tok in _IDENT_RE.findall(body):
                if tok not in _KEYWORDS and len(tok) > 2 and tok != name:
                    if tok not in seen:
                        self._reffreq[tok] += 1
                        seen.add(tok)

    def _load_more(self, rng, n: int = 6) -> None:
        for _ in range(n):
            if not self._unparsed:
                break
            idx = rng.randrange(len(self._unparsed))
            self._parse_file(self._unparsed.pop(idx))

    def seeds(self, rng, k: int = 4) -> list[str]:
        # keep growing the working set so cross-file references accumulate into a
        # real dependency graph (capped to bound memory)
        if len(self._index) < 4000 and self._unparsed:
            self._load_more(rng, n=10)
        if not self._index:
            return []
        names = list(self._index.keys())
        return [f"mathlib:{rng.choice(names)}" for _ in range(min(k, len(names)))]

    def expand(self, node: str, rng, ruleset) -> list:
        if not node.startswith("mathlib:"):
            return []
        name = node.split(":", 1)[1]
        body = self._index.get(name)
        if body is None:
            # not in working set yet; pull more files in and retry once
            self._load_more(rng, n=4)
            body = self._index.get(name)
            if body is None:
                return []
        maxf = max(self._reffreq.values()) if self._reffreq else 1
        out = []
        seen = set()
        for tok in _IDENT_RE.findall(body):
            if tok in _KEYWORDS or len(tok) <= 2 or tok == name or tok in seen:
                continue
            if tok not in self._index:
                continue  # only link to known declarations (keeps frontier expandable)
            seen.add(tok)
            null_p = min(0.99, self._reffreq.get(tok, 1) / maxf)  # generic => high
            out.append((f"mathlib:{tok}", "uses", null_p))
        return out
