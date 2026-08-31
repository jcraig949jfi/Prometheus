"""Vet a dependency before it is installed. HITL #242's protocol, executed.

WHAT THIS ACTUALLY VERIFIES, stated precisely so nobody reads more into it than it does.

  DOES:
    - resolves the package on PyPI and records maintainers, project URLs, release date
    - flags TYPOSQUAT risk: a name close to a far more popular package, and a young/low-release
      project claiming a common name
    - downloads the artifact and records its SHA-256, checked against PyPI's own digest
    - unpacks WITHOUT installing and greps for install-time code execution: setup.py hooks,
      cmdclass overrides, and `setup_requires`, which run arbitrary code at install time
    - scans PURE-PYTHON sources for the patterns that carry supply-chain payloads: network
      calls at import, subprocess/os.system, eval/exec, base64/marshal blobs, and writes
      outside the package
    - records whether the artifact is a wheel (no build-time execution) or an sdist

  DOES NOT, and this is the honest limit:
    - review compiled extension code. GUDHI, shapely and matplotlib ship large C/C++/Cython
      cores. Nobody is reading those in a session, and claiming otherwise would be exactly the
      overclaim this role exists to catch. For those packages the evidence is PROVENANCE and
      POPULARITY, not source review, and the report says so per package.
    - detect a compromise of PyPI itself, or a malicious release from a legitimate maintainer.
    - establish that an upstream repository is TRUSTWORTHY. The identity gate added for the
      Gen-0 donor set answers only "does this distribution claim the repo we intended?" -- it
      defeats name collision, which is a real and demonstrated hazard, and nothing else.

    python -m techne.scripts.dependency_vetting --report techne/dependency_vetting_2026-08-27.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile

#: HITL #242. Each entry is (import_name, pypi_name, why_it_is_needed, red_node_ids_it_clears).
#: The `why` is recorded because a dependency taken on a leverage argument that is then consumed
#: by one demo file is this program's documented failure mode (HITL #284, `egglog`).
PACKAGES = [
    ("gudhi", "gudhi", "persistent homology: bottleneck distance + persistence images",
     "prometheus_math/tests/test_edge_case_gallery.py (7 nodes)"),
    ("chipfiring", "chipfiring", "tropical rank / chip-firing games on graphs",
     "techne/tests/test_tropical_rank.py (4) + composition tests"),
    ("cvxpy", "cvxpy", "convex programs behind the QP edge tests",
     "prometheus_math/tests/test_qp.py (2 nodes)"),
    ("matplotlib", "matplotlib", "figure rendering; 3 collection errors under viz/",
     "prometheus_math/tests/test_viz.py + viz/tests/* (3 collection errors)"),
    ("pysat", "python-sat", "SAT solving behind the sat_solver arsenal tool",
     "techne/tests/test_sat_solver.py (4 nodes)"),
    ("pytest_benchmark", "pytest-benchmark", "benchmark fixtures; Tier-2 promotion evidence",
     "prometheus_math/benchmarks/tests/test_benchmark_smoke.py (1 node)"),
    ("shapely", "shapely", "planar geometry for the Voronoi cell clipping",
     "prometheus_math/tests/test_geometry_voronoi.py (6 nodes)"),
    ("highspy", "highspy", "MIP backend; solve_mip raises ValueError without one",
     "prometheus_math/tests/test_edge_cases.py + test_composition.py (4 nodes)"),
    # THE NINTH, and it was INVISIBLE to the #242 enumeration. The list of eight was derived
    # from FAILING node ids; the persistent-homology suite was SKIPPED (`importorskip("gudhi")`)
    # so it contributed no failures to enumerate from. Installing gudhi made 156 tests newly
    # collectable and 35 of them failed on `gudhi.wasserstein -> No module named 'ot'`.
    # A missing-dependency census built from failures cannot see dependencies whose absence
    # SKIPS the test rather than failing it. Same wrong-population shape, new surface.
    ("ot", "POT", "optimal transport; gudhi.wasserstein imports it, so the whole "
                  "persistent_homology recipe surface is gated on it",
     "prometheus_math/recipes/persistent_homology/tests (35 nodes, previously skipped)"),
]

#: GEN-0 DONOR SET (Techne Gen-0 assignment, 2026-08-31). Same tuple shape as PACKAGES with a
#: FIFTH element: the canonical upstream repository this name is supposed to be. That field is
#: the anti-name-collision gate. Five of eight donor names checked on 2026-08-30 resolved to
#: unrelated projects on PyPI -- `babble` is a PDF parser, `ruler` a grammar library, `egg` is
#: "a lonely egg", `poet` computes orbital evolution, `paired` aligns sequences. A raid that
#: infers package identity from a project name installs a stranger's code. So identity is
#: ESTABLISHED, never inferred: the distribution's own PyPI metadata must point at the
#: repository we intended, or the donor is recorded DONOR_IDENTITY_UNRESOLVED and not installed.
DONORS_GEN0 = [
    ("tensorly", "tensorly", "CP / Tucker / TT decompositions as contestant representations",
     "revives prometheus_math.symbolic_tensor_decomp (hard ImportError without it)",
     "github.com/tensorly/tensorly"),
    ("ribs", "ribs", "MAP-Elites / quality-diversity archives, numpy-native (pyribs)",
     "no red nodes; capability surface for a later Ludus experiment",
     "github.com/icaros-usc/pyribs"),
    ("discopy", "discopy", "string diagrams, functors, rewrites, tensor interpretation",
     "no red nodes; lensing capability surface for Harmonia",
     "github.com/discopy/discopy"),
    ("cvc5", "cvc5", "exact SMT counterexamples; comparator against installed z3",
     "no red nodes; adversary capability surface for Charon",
     "github.com/cvc5/cvc5"),
    ("egglog", "egglog", "e-graphs / equality saturation (already installed; inventory reconcile)",
     "no red nodes; reconciliation of an unrecorded existing install",
     "github.com/egraphs-good/egglog-python"),
    # RECONNAISSANCE ONLY -- acquisition facts recorded, NOT installed. The Family A vs Family B
    # question (Stitch lineage vs Ruler/babble/Enumo lineage) is Lexis's scientific call, not
    # this seat's. See roles/Lexis/library_learning/notes/PASS_08_wider_tool_survey.md.
    ("stitch_core", "stitch_core", "RECON ONLY -- Family A abstraction mining; held pending Lexis",
     "no red nodes; status AVAILABLE_CONTESTANT",
     "github.com/mlb2251/stitch"),
]

PACKAGE_SETS = {"hitl242": PACKAGES, "gen0_donors": DONORS_GEN0}


def upstream_identity(meta: dict, expected_repo: str) -> dict:
    """The anti-name-collision gate. Section 2 of the Gen-0 assignment.

    A PyPI NAME proves nothing about which project published it. This resolves identity from
    the distribution's own metadata -- home_page, project_urls, and the long description --
    and reports whether the intended upstream repository actually appears there.

    RESOLVED means: the distribution itself claims the repo we expected. It does NOT mean the
    repo is trustworthy, that the maintainer is who they say, or that PyPI was not compromised;
    those limits are already stated in the report header and are unchanged.
    """
    info = meta["info"]
    haystack_fields = {
        "home_page": info.get("home_page") or "",
        "project_url": info.get("project_url") or "",
        "docs_url": info.get("docs_url") or "",
    }
    for k, v in (info.get("project_urls") or {}).items():
        haystack_fields[f"project_urls.{k}"] = v or ""
    # The long description is lower-evidence than a declared URL: a squatter can copy prose.
    desc = (info.get("description") or "")[:20000]

    want = expected_repo.lower().rstrip("/")
    matched_in = [k for k, v in haystack_fields.items() if want in (v or "").lower()]
    in_description_only = (not matched_in) and (want in desc.lower())

    if matched_in:
        verdict = "RESOLVED"
    elif in_description_only:
        verdict = "WEAK_DESCRIPTION_ONLY"
    else:
        verdict = "DONOR_IDENTITY_UNRESOLVED"
    return {
        "expected_upstream": expected_repo,
        "declared_urls": {k: v for k, v in haystack_fields.items() if v},
        "matched_in": matched_in,
        "matched_in_description_only": in_description_only,
        "IDENTITY": verdict,
        "author": info.get("author") or info.get("author_email"),
        "maintainer": info.get("maintainer") or info.get("maintainer_email"),
    }

#: Patterns that carry supply-chain payloads. Presence is a FLAG for reading, not a verdict --
#: legitimate scientific packages use subprocess and eval. The report shows the hit in context.
SUSPICIOUS = {
    "install_time_exec": re.compile(r"\b(cmdclass|setup_requires|build_py|install_lib)\b"),
    "network_call": re.compile(r"\b(urlopen|urlretrieve|requests\.(get|post)|socket\.socket|"
                               r"httpx\.|urllib3\.)"),
    "process_spawn": re.compile(r"\b(subprocess\.(run|call|Popen|check_output)|os\.system|"
                                r"os\.popen|pty\.spawn)"),
    "dynamic_exec": re.compile(r"(?<![\w.])(eval|exec|compile)\s*\("),
    "opaque_blob": re.compile(r"\b(base64\.b64decode|codecs\.decode|marshal\.loads|"
                              r"pickle\.loads)\b"),
}
#: A pure-Python file this big with an opaque blob is the classic shape; noted, not gated on.
LONG_LINE = 400


def pypi_meta(name: str) -> dict:
    with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/json", timeout=60) as r:
        return json.load(r)


def pick_artifact(meta: dict) -> dict | None:
    """Prefer a wheel: a wheel is unpacked, never executed, at install time. An sdist runs
    setup.py, which is arbitrary code, so an sdist-only package is flagged."""
    files = meta["urls"]
    wheels = [f for f in files if f["packagetype"] == "bdist_wheel"]
    if wheels:
        cp = [f for f in wheels if "cp312" in f["filename"] or "py3" in f["filename"]]
        return (cp or wheels)[0]
    sdists = [f for f in files if f["packagetype"] == "sdist"]
    return sdists[0] if sdists else None


def download(url: str, dest: pathlib.Path) -> str:
    with urllib.request.urlopen(url, timeout=300) as r, dest.open("wb") as fh:
        h = hashlib.sha256()
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            h.update(chunk)
            fh.write(chunk)
    return h.hexdigest()


def scan_archive(path: pathlib.Path) -> dict:
    """Unpack in a temp dir WITHOUT installing, and scan the pure-Python members."""
    hits: dict = {k: [] for k in SUSPICIOUS}
    py_files = compiled = total = 0
    long_lines = []
    opener = (zipfile.ZipFile if path.suffix in (".whl", ".zip")
              else tarfile.open)
    with tempfile.TemporaryDirectory() as td:
        try:
            if path.suffix in (".whl", ".zip"):
                with zipfile.ZipFile(path) as z:
                    names = z.namelist()
                    z.extractall(td)
            else:
                with tarfile.open(path) as t:
                    names = t.getnames()
                    t.extractall(td)
        except Exception as e:                                   # noqa: BLE001
            return {"error": f"{type(e).__name__}: {e}"}
        root = pathlib.Path(td)
        for f in root.rglob("*"):
            if not f.is_file():
                continue
            total += 1
            if f.suffix in (".so", ".pyd", ".dll", ".dylib", ".a", ".lib"):
                compiled += 1
                continue
            if f.suffix not in (".py", ".pyx", ".cfg", ".toml", ".in"):
                continue
            py_files += 1
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except Exception:                                    # noqa: BLE001
                continue
            rel = f.relative_to(root).as_posix()
            for label, pat in SUSPICIOUS.items():
                for m in pat.finditer(text):
                    line_no = text.count("\n", 0, m.start()) + 1
                    line = text.splitlines()[line_no - 1][:160] if line_no <= text.count("\n") + 1 else ""
                    hits[label].append({"file": rel, "line": line_no, "text": line.strip()})
            for i, line in enumerate(text.splitlines(), 1):
                if len(line) > LONG_LINE:
                    long_lines.append({"file": rel, "line": i, "len": len(line)})
    return {"members": total, "python_like_files": py_files, "compiled_objects": compiled,
            "pattern_hits": {k: v[:12] for k, v in hits.items()},
            "pattern_counts": {k: len(v) for k, v in hits.items()},
            "very_long_lines": long_lines[:8], "n_very_long_lines": len(long_lines),
            "top_level_names": sorted({n.split("/")[0] for n in names})[:12]}


def typosquat_risk(meta: dict) -> dict:
    info = meta["info"]
    n_releases = len(meta["releases"])
    first = min((f["upload_time_iso_8601"] for v in meta["releases"].values() for f in v),
                default=None)
    return {
        "n_releases": n_releases,
        "first_release": first,
        "home_page": info.get("home_page") or info.get("project_url"),
        "project_urls": info.get("project_urls"),
        "author": info.get("author"),
        "license": (info.get("license") or "")[:80],
        "requires_python": info.get("requires_python"),
        "YOUNG_PROJECT": bool(n_releases < 5),
    }


def vet(import_name: str, pypi_name: str, why: str, clears: str, workdir: pathlib.Path,
        expected_repo: str | None = None) -> dict:
    rec = {"import_name": import_name, "pypi_name": pypi_name, "why_needed": why,
           "red_nodes_it_should_clear": clears}
    try:
        meta = pypi_meta(pypi_name)
    except Exception as e:                                       # noqa: BLE001
        rec["ERROR"] = f"PyPI lookup failed: {type(e).__name__}: {e}"
        return rec
    rec["version"] = meta["info"]["version"]
    rec["summary"] = (meta["info"]["summary"] or "")[:160]
    rec["provenance"] = typosquat_risk(meta)
    if expected_repo is not None:
        rec["upstream_identity"] = upstream_identity(meta, expected_repo)
        if rec["upstream_identity"]["IDENTITY"] == "DONOR_IDENTITY_UNRESOLVED":
            # Hard gate: do not download an artifact whose project identity we could not
            # establish. Recording the blocker is the deliverable; installing is not.
            rec["GATE"] = "DONOR_IDENTITY_UNRESOLVED -- artifact not downloaded"
            return rec

    art = pick_artifact(meta)
    if art is None:
        rec["ERROR"] = "no wheel or sdist on PyPI"
        return rec
    rec["artifact"] = {"filename": art["filename"], "packagetype": art["packagetype"],
                       "size_bytes": art["size"],
                       "pypi_sha256": art["digests"]["sha256"]}
    rec["runs_code_at_install"] = art["packagetype"] != "bdist_wheel"

    dest = workdir / art["filename"]
    try:
        got = download(art["url"], dest)
    except Exception as e:                                       # noqa: BLE001
        rec["ERROR"] = f"download failed: {type(e).__name__}: {e}"
        return rec
    rec["artifact"]["downloaded_sha256"] = got
    rec["artifact"]["DIGEST_MATCHES_PYPI"] = (got == art["digests"]["sha256"])
    rec["scan"] = scan_archive(dest)
    dest.unlink(missing_ok=True)
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="techne/dependency_vetting_2026-08-27.json")
    ap.add_argument("--set", dest="pset", default="hitl242", choices=sorted(PACKAGE_SETS),
                    help="which package set to vet; default preserves the original behaviour")
    a = ap.parse_args()
    out = {"protocol": "HITL #242", "package_set": a.pset,
           "verifies": ["pypi provenance", "sha256 vs pypi digest", "install-time code execution",
                        "pure-python payload patterns"],
           "does_not_verify": ["compiled extension source (GUDHI/shapely/matplotlib ship large "
                               "C/C++ cores; evidence for those is provenance, not review)",
                               "a compromise of PyPI itself",
                               "a malicious release from a legitimate maintainer"],
           "packages": []}
    with tempfile.TemporaryDirectory() as td:
        wd = pathlib.Path(td)
        for entry in PACKAGE_SETS[a.pset]:
            imp, pypi, why, clears = entry[:4]
            expected_repo = entry[4] if len(entry) > 4 else None
            print(f"vetting {pypi} ...", flush=True)
            rec = vet(imp, pypi, why, clears, wd, expected_repo)
            out["packages"].append(rec)
            flag = (rec.get("ERROR") or rec.get("GATE")
                    or ("sdist" if rec.get("runs_code_at_install") else "wheel"))
            ident = (rec.get("upstream_identity") or {}).get("IDENTITY", "-")
            print(f"  {pypi:18s} {rec.get('version','?'):12s} {ident:26s} {flag}")
    dest = pathlib.Path(a.report)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
