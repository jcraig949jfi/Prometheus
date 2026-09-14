"""NEM-14 -- the instrument floor census, built on INDEX TRUTH.

    Find out how many of Prometheus's numbers are presently being
    interpreted without knowing what nothing scores.   (operator, 2026-09-11)

Preregistered in PREREGISTRATION_NEM14.md (commit 0548bde84) before any
instrument was classified.

AUDIT THE AUDITOR. Membership and content come from `git ls-files` and
`git show HEAD:<path>`, never from a filesystem walk. D-23 mandates a
worktree per seat and sparse worktrees are the norm, so an auditor that
enumerates the filesystem MANUFACTURES ABSENCE: measured in this very
worktree, 376 instrument-shaped modules exist in the index and 40 on
disk. `divergence()` reports that number and `_forbid_filesystem()` is
the control that fails if this module is ever asked to decide membership
from disk.

This module SCREENS. It does not classify. The screen extracts the lines
a human must read; the four-state classification is a hand-read recorded
in ATTACK_SURFACE.md, because the cheapest way to fake this census is to
grep for "null" and call every hit a floor.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))

from archaeon.workspace import assert_not_canonical, receipt  # noqa: E402

OUT = HERE / "census_screen.json"

#: Vocabulary that POINTS AT a line to read. A hit is not a floor.
FLOOR_VOCAB = (
    "chance", "baseline", "null", "floor", "majority", "random", "shuffle",
    "permutation", "control", "eligible", "expected under", "at random",
    "dead world", "degenerate", "constant responder",
)

#: Words suggesting the module SETTLES something rather than proposing it.
TERMINAL_VOCAB = (
    "promote", "demote", "admit", "admission", "gate", "disable", "retire",
    "accept", "refuse", "terminal", "verdict", "settle", "pass_overall",
)

INSTRUMENT_SHAPED = re.compile(
    r"scor|gate|eval|grade|metric|fitness|rank|judge|verif|valid|detect", re.I)


def _git(*args: str, timeout: int = 300) -> str:
    r = subprocess.run(["git", *args], cwd=str(REPO), capture_output=True,
                       text=True, timeout=timeout)
    if r.returncode not in (0, 1):
        raise RuntimeError("git {} failed: {}".format(args[0], r.stderr[:300]))
    return r.stdout


def _forbid_filesystem(paths: Sequence[str]) -> None:
    """CONTROL: membership must never come from disk.

    Fails loudly if the caller hands in paths that were discovered by a
    filesystem walk. Detected by the property that matters rather than by
    intent: every member must be in the index.
    """
    tracked = set(_git("ls-files").splitlines())
    strays = [p for p in paths if p not in tracked]
    if strays:
        raise AssertionError(
            "census membership contains {} path(s) not in the index, so it did "
            "not come from index truth: {}".format(len(strays), strays[:5]))


def divergence() -> Dict[str, int]:
    """How much an auditor would miss by enumerating the filesystem here."""
    from_index = [p for p in _git("ls-files", "*.py").splitlines()
                  if p and INSTRUMENT_SHAPED.search(p)
                  and "__init__" not in p and "/tests/" not in p
                  and not Path(p).name.startswith("test_")]
    on_disk = [p for p in from_index if (REPO / p).is_file()]
    return {
        "instrument_shaped_in_index": len(from_index),
        "instrument_shaped_on_disk": len(on_disk),
        "visible_fraction": round(len(on_disk) / max(1, len(from_index)), 4),
        "missed_by_a_filesystem_auditor": len(from_index) - len(on_disk),
    }


def tier1_paths() -> List[str]:
    out = []
    for pat in ("roles/*/science/*.py", "roles/*/contracts/*.py"):
        for p in _git("ls-files", pat).splitlines():
            p = p.strip()
            if not p:
                continue
            name = Path(p).name
            if name == "__init__.py" or name.startswith("test_") or "/tests/" in p:
                continue
            out.append(p)
    return sorted(set(out))


@dataclass
class Screened:
    path: str
    seat: str
    blob_lines: int
    emits_number: bool
    floor_hits: Dict[str, int] = field(default_factory=dict)
    terminal_hits: Dict[str, int] = field(default_factory=dict)
    floor_evidence: List[str] = field(default_factory=list)
    terminal_evidence: List[str] = field(default_factory=list)
    companion_docs: List[str] = field(default_factory=list)


NUMBER_EMITTING = re.compile(
    r"\breturn\s+.*(?:rate|score|mean|median|frac|ratio|pct|percent|count|n_|"
    r"p_value|pvalue|stat|delta|corr|r2|auc)|"
    r"\b(?:rate|score|fraction|ratio|accuracy|precision|recall|pass_rate)\s*=",
    re.I)


def screen(path: str) -> Screened:
    body = _git("show", "HEAD:" + path)
    lines = body.splitlines()
    seat = path.split("/")[1]
    low = body.lower()

    floor_hits = {w: low.count(w) for w in FLOOR_VOCAB if w in low}
    term_hits = {w: low.count(w) for w in TERMINAL_VOCAB if w in low}

    fev, tev = [], []
    for i, ln in enumerate(lines, 1):
        l = ln.lower()
        if any(w in l for w in FLOOR_VOCAB) and len(fev) < 14:
            fev.append("{}:{}".format(i, ln.strip()[:170]))
        if any(w in l for w in TERMINAL_VOCAB) and len(tev) < 8:
            tev.append("{}:{}".format(i, ln.strip()[:170]))

    companions = [p for p in _git("ls-files", "roles/{}/*.md".format(seat)).splitlines()
                  if p.strip()][:40]

    return Screened(
        path=path, seat=seat, blob_lines=len(lines),
        emits_number=bool(NUMBER_EMITTING.search(body)),
        floor_hits=floor_hits, terminal_hits=term_hits,
        floor_evidence=fev, terminal_evidence=tev,
        companion_docs=companions,
    )


def main() -> int:
    assert_not_canonical()
    paths = tier1_paths()
    _forbid_filesystem(paths)          # the control, before any work
    div = divergence()

    rows = [screen(p) for p in paths]
    kw_positive = [r for r in rows if r.floor_hits]
    numeric = [r for r in rows if r.emits_number]

    payload = {
        "census": "NEM-14",
        "built_from": _git("rev-parse", "HEAD").strip(),
        "workspace": receipt(),
        "membership_source": "git ls-files (index truth); filesystem never consulted",
        "audit_the_auditor": div,
        "tier1_count": len(rows),
        "tier1_by_seat": {s: sum(1 for r in rows if r.seat == s)
                          for s in sorted({r.seat for r in rows})},
        "emits_a_number": len(numeric),
        "keyword_positive": len(kw_positive),
        "rows": [asdict(r) for r in rows],
    }
    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2)
        fh.flush()

    print("tier 1 instruments (index truth): {}".format(len(rows)))
    print("  emitting a number (screen):     {}".format(len(numeric)))
    print("  keyword-positive for a floor:   {}".format(len(kw_positive)))
    print("audit-the-auditor: index {} vs on-disk {} ({:.1%} visible; {} missed)"
          .format(div["instrument_shaped_in_index"], div["instrument_shaped_on_disk"],
                  div["visible_fraction"], div["missed_by_a_filesystem_auditor"]))
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
