"""erebos_external_refs.py -- ONE question:

    Did anything OUTSIDE charon/agents/erebos/ and pivot/erebos_* ever
    reference Erebos or its composed claims, and does the P57 certificate's
    grep ("grep EREBOS across engine/, techne/, charon/BACKLOG.md and charon
    session docs: zero external hits") reproduce at the evidence baseline?

Two passes, both via scoped `git grep` (whole-tree ripgrep times out on
this 39K-file tree):
  A. P57 replication: case-SENSITIVE "EREBOS" over exactly the scope the
     certificate names.
  B. Extended census: case-INSENSITIVE "erebos" over the tracked tree,
     bucketed by top-level dir (second level under charon/), excluding the
     agent's own directory and pivot/erebos_* docs; plus the narrower
     "charon.agents.erebos" import census (who imports Erebos code).

Writes erebos_external_refs_result.json next to this file. Pure ASCII.
Repo root is resolved from __file__ (no drive letters). Read-only git.
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]

OWN_PREFIXES = ("charon/agents/erebos/", "pivot/erebos_",
                "engine/necropolis/dossiers/erebos")


def git_grep(args: list[str]) -> list[str]:
    cp = subprocess.run(["git", "grep"] + args, cwd=str(REPO),
                        capture_output=True, text=True, timeout=300)
    if cp.returncode not in (0, 1):
        raise RuntimeError(cp.stderr[:300])
    return [ln for ln in cp.stdout.splitlines() if ln]


def bucket(path: str) -> str:
    parts = path.split("/")
    if parts[0] == "charon" and len(parts) > 2:
        return "/".join(parts[:3]) if parts[1] == "agents" else "charon/" + parts[1]
    return parts[0] if len(parts) > 1 else "(root)"


def main() -> int:
    out: dict = {"question": __doc__.strip().splitlines()[0]}

    # A. P57 replication (case-sensitive, uppercase EREBOS, named scope).
    p57_scope = ["engine", "techne", "charon/BACKLOG.md"]
    sess = sorted(str(p.relative_to(REPO)).replace("\\", "/")
                  for p in (REPO / "charon").glob("CHARON_SESSION_*.md"))
    files = git_grep(["-l", "EREBOS", "--"] + p57_scope + sess)
    ext = [f for f in files if not f.startswith(OWN_PREFIXES)]
    out["A_p57_replication"] = {
        "pattern": "EREBOS (case-sensitive)", "scope": p57_scope + ["charon/CHARON_SESSION_*.md"],
        "session_docs_in_scope_n": len(sess),
        "files_with_hits": ext, "files_with_hits_n": len(ext),
        "note": ("Hits under engine/necropolis/dossiers/erebos* are this "
                 "investigation and are excluded; engine/ledger hits are the "
                 "certificates themselves."),
    }
    # A2. same scope, case-insensitive (what P57 would have seen with -i).
    files_i = git_grep(["-l", "-i", "erebos", "--"] + p57_scope + sess)
    out["A2_p57_scope_case_insensitive"] = {
        "files_with_hits": [f for f in files_i if not f.startswith(OWN_PREFIXES)],
    }
    out["A2_p57_scope_case_insensitive"]["files_with_hits_n"] = len(
        out["A2_p57_scope_case_insensitive"]["files_with_hits"])

    # B. Extended census over the tracked tree.
    allf = git_grep(["-l", "-i", "erebos"])
    external = [f for f in allf if not f.startswith(OWN_PREFIXES)]
    buckets = Counter(bucket(f) for f in external)
    out["B_extended_census"] = {
        "pattern": "erebos (case-insensitive), tracked tree",
        "files_total_n": len(allf),
        "files_own_n": len(allf) - len(external),
        "files_external_n": len(external),
        "external_by_bucket": dict(sorted(buckets.items(), key=lambda kv: -kv[1])),
    }
    # B2. who imports Erebos CODE (strongest form of external consumption).
    imp = git_grep(["-n", "-E", r"(from|import) charon\.agents\.erebos"])
    imp_ext = [ln for ln in imp if not ln.startswith(OWN_PREFIXES)]
    out["B2_code_importers"] = {
        "lines_n": len(imp_ext),
        "files": sorted({ln.split(":", 1)[0] for ln in imp_ext}),
        "sample": imp_ext[:12],
    }
    # B3. Stygian-side artifacts that name Erebos plugin families.
    styg = [f for f in external if f.startswith("charon/agents/stygian/")]
    out["B3_stygian_files_naming_erebos"] = {
        "n": len(styg),
        "loaders_n": sum(1 for f in styg if "/loaders/composition_" in f),
        "tests_n": sum(1 for f in styg if "/tests/test_composition_" in f),
        "other": [f for f in styg if "/loaders/composition_" not in f
                  and "/tests/test_composition_" not in f],
    }
    # B4. harmonia/ (the 2026-06-15 subsumption) and hecate/ hits.
    for key, pref in (("B4_harmonia_files", "harmonia/"),
                      ("B5_hecate_files", "charon/agents/hecate/")):
        out[key] = sorted(f for f in external if f.startswith(pref))
    (HERE / "erebos_external_refs_result.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({"A_n": out["A_p57_replication"]["files_with_hits_n"],
                      "A_files": ext,
                      "A2_n": out["A2_p57_scope_case_insensitive"]["files_with_hits_n"],
                      "B_external_n": len(external),
                      "B_buckets": out["B_extended_census"]["external_by_bucket"],
                      "B2_importers": out["B2_code_importers"]["files"],
                      "B3": out["B3_stygian_files_naming_erebos"],
                      "B4_harmonia": out["B4_harmonia_files"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
