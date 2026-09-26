"""Launch PTE-C1b v2 (frozen at 5bd6c3945) under the OPERATOR's direct release.

Why this exists: the frozen driver's release gate (c1b_run.check_release)
accepts only a comms ruling FROM Aporia. On 2026-09-26 the operator
restored direct control and released C1b himself, recorded verbatim at
roles/Ananke/prompts/2026-09-26_c1b_operator_release/ (f6fff610c). The
operator chose (2026-09-26, in session) this launcher over a v3 re-freeze.

What it changes: ONLY the release check. Every other frozen guard is kept:
a clean tree, prometheus/ananke unchanged since the freeze, and the prereg
sha256 equal to FREEZE_C1b.json. The operator release is checked instead:
committed, its MANIFEST verifies, its first line starts with the exact
token "C1B HOLD RELEASE:", it names the freeze 5bd6c3945, and it was
committed after the freeze. The science code, prereg and artifacts are
used exactly as frozen. The run receipt records the override.

    python roles/Ananke/pte/c1b/launch_operator_release.py --check
    python roles/Ananke/pte/c1b/launch_operator_release.py --home <H> [--device cuda]
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from prometheus.ananke import c1b_run  # noqa: E402

RELEASE_DIR = REPO / "roles/Ananke/prompts/2026-09-26_c1b_operator_release"
RELEASE = RELEASE_DIR / "01_OPERATOR_RELEASE_verbatim.md"
FROZEN = "5bd6c3945"


def operator_guard() -> dict:
    problems = []
    try:
        c1b_run.guard(None)
    except SystemExit as e:
        kept = [ln.strip() for ln in str(e).splitlines()[1:]
                if not ln.strip().startswith("no --release")]
        problems += kept
    fz = json.loads(c1b_run.FREEZE.read_text())
    commit, frozen_at = c1b_run.freeze_commit()
    if not commit.startswith(FROZEN):
        problems.append(f"freeze commit is {commit[:9]}, the operator released {FROZEN}")
    rel = str(RELEASE.relative_to(REPO))
    if c1b_run.git("status", "--porcelain", str(RELEASE_DIR.relative_to(REPO))):
        problems.append("operator release directory is dirty")
    rc = subprocess.run([sys.executable, "-m", "comms.manifest", "verify", str(RELEASE_DIR)],
                        cwd=REPO, capture_output=True, text=True).returncode
    if rc != 0:
        problems.append("operator release MANIFEST does not verify")
    text = RELEASE.read_text(encoding="utf-8")
    if not text.startswith(c1b_run.RELEASE_TOKEN):
        problems.append(f"operator release does not start with {c1b_run.RELEASE_TOKEN!r}")
    if FROZEN not in text:
        problems.append(f"operator release does not name {FROZEN}")
    rsha = c1b_run.git("log", "-1", "--format=%H", "--", rel)
    if not rsha:
        problems.append("operator release is not committed")
    else:
        when = datetime.datetime.fromisoformat(c1b_run.git("show", "-s", "--format=%cI", rsha))
        if when <= frozen_at:
            problems.append("operator release committed before the freeze")
    if problems:
        raise SystemExit("C1b operator launch REFUSES:\n  " + "\n  ".join(problems))
    fz["head"] = c1b_run.git("rev-parse", "HEAD")
    fz["release_override"] = {
        "by": "operator (direct control restored 2026-09-26)",
        "release_record": rel, "release_commit": rsha,
        "replaces": "c1b_run.check_release (Aporia comms ruling) -- that check only",
        "choice": "operator chose this launcher over a v3 re-freeze (session 2026-09-26)"}
    return fz


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--home")
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args(argv)
    fz = operator_guard()
    if a.check:
        print("operator launch guard: OK", json.dumps(fz["release_override"]))
        return 0
    c1b_run.guard = lambda release: fz              # the release check only; see operator_guard
    return c1b_run.main(["--home", a.home, "--release", "operator:" + fz["release_override"]["release_commit"][:9],
                         "--device", a.device])


if __name__ == "__main__":
    raise SystemExit(main())
