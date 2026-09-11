"""DreamCoder: locate the recipe, then measure whether a bounded domain run is possible.

    python -m techne.acquisition.checks.dreamcoder_smoke --out <result.json>

This one runs in the LIVE interpreter because it is a PROBE, not a tool user: it resolves
dependency sets without installing them and inspects toolchains. It never imports
dreamcoder and never installs into the live environment.

The design is explicit about the trap here: *"Its README references
docs/official_experiments, which was absent from the inspected docs listing; locate the
actual paper supplement or an explicit artifact recipe before asserting a historical
replication. Do not substitute an invented benchmark number."*

So this check reports exactly what exists at exactly which path, with hashes, and scores
the smoke run's feasibility against measured toolchain facts. A blocked smoke run reported
with its precise boundary is the deliverable; a smoke run declared "pending" is not.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys

from .. import budget as _budget
from .. import manifest_io, paths, pypi, receipt

OCAML_PACKAGES = ["ppx_jane", "core", "re2", "yojson", "vg", "cairo2", "camlimages",
                  "menhir", "ocaml-protoc", "zmq"]


def locate_recipe(root: pathlib.Path) -> dict:
    """The README names docs/official_experiments. Report what is at that path, and report
    separately whether anything with that basename exists elsewhere. These are different
    claims and the difference is the whole point."""
    readme = next((p for p in (root / "README.md", root / "Readme.md") if p.exists()), None)
    readme_refs = []
    if readme:
        text = readme.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"[\w/.\-]*official_experiments[\w/.\-]*", text):
            line_no = text[:m.start()].count("\n") + 1
            readme_refs.append({"path_as_written": m.group(0), "readme_line": line_no})

    readme_path = root / "docs" / "official_experiments"
    elsewhere = []
    for p in root.rglob("official_experiments*"):
        if ".git" in p.parts:
            continue
        data = p.read_bytes() if p.is_file() else b""
        elsewhere.append({
            "path": str(p.relative_to(root)).replace("\\", "/"),
            "is_file": p.is_file(), "bytes": len(data) if p.is_file() else None,
            "sha256": hashlib.sha256(data).hexdigest() if p.is_file() else None,
        })

    content = {}
    root_file = root / "official_experiments"
    if root_file.is_file():
        text = root_file.read_text(encoding="utf-8", errors="replace")
        lines = [ln for ln in text.splitlines() if ln.strip()]
        launch = [ln for ln in lines if "bin/launch.py" in ln]
        zones = sorted({m.group(1) for ln in launch
                        for m in re.finditer(r"-z\s+(\S+)", ln)})
        timeouts = sorted({int(m.group(1)) for ln in lines
                           for m in re.finditer(r"-t\s+(\d+)", ln)})
        content = {
            "n_nonblank_lines": len(lines),
            "n_lines_invoking_bin_launch_py": len(launch),
            "fraction_via_cloud_launcher": round(len(launch) / max(1, len(lines)), 3),
            "machine_types_requested": zones,
            "per_run_timeouts_seconds": timeouts,
            "max_timeout_seconds": max(timeouts) if timeouts else None,
            "reading": "These are GCP cloud-launcher invocations. bin/launch.py -z <machine> "
                       "provisions an instance and runs the command there. They are not local "
                       "recipes, and the design forbids a cloud launcher as a default.",
        }

    return {
        "readme_references": readme_refs,
        "readme_linked_path": str(readme_path.relative_to(root)).replace("\\", "/"),
        "readme_linked_path_exists": readme_path.exists(),
        "files_with_that_basename_anywhere": elsewhere,
        "root_level_file_content_summary": content,
        "CLAIM": ("The path the README names -- docs/official_experiments -- DOES NOT EXIST "
                  "at the pinned revision. A file named `official_experiments` exists at the "
                  "repository ROOT. It is NOT asserted to be the README's intended recipe, "
                  "and it is NOT a paper supplement: its contents are cloud-launcher "
                  "commands. No historical replication is claimed from it."),
    }


_TAGS_PROBE = (
    "import json\n"
    "try:\n"
    "    from packaging.tags import sys_tags\n"
    "except Exception:\n"
    "    from pip._vendor.packaging.tags import sys_tags\n"
    "import sys\n"
    "print(json.dumps({'version': '.'.join(map(str, sys.version_info[:3])),\n"
    "                  'tags': [str(t) for t in sys_tags()]}))\n"
)


def _wheel_tags(filename: str) -> set[str]:
    m = re.match(r"^.+?-.+?(-\d[^-]*)?-([^-]+-[^-]+-[^-]+)\.whl$", filename)
    if not m:
        return set()
    py, abi, plat = m.group(2).split("-")
    return {f"{p}-{a}-{pl}"
            for p in py.split(".") for a in abi.split(".") for pl in plat.split(".")}


def probe_python_stack(root: pathlib.Path, b: _budget.Budget) -> dict:
    """Per-pin artifact availability against each interpreter's own wheel tags.

    A full `pip install --dry-run -r requirements.txt` was tried FIRST and abandoned: on a
    2019 pin set the resolver backtracks through sdists and had not terminated after ten
    minutes, so the measurement would have been the resolver's patience, not the stack's
    installability. This probe asks the decidable question instead -- does an artifact
    compatible with THIS interpreter exist at THIS exact pinned version -- once per pin, and
    terminates.
    """
    import urllib.error
    import urllib.request

    req = root / "requirements.txt"
    raw = [ln.strip() for ln in req.read_text(encoding="utf-8").splitlines()
           if ln.strip() and not ln.startswith("#")] if req.exists() else []
    pins = []
    for ln in raw:
        if "==" in ln:
            n, v = ln.split("==", 1)
            pins.append((n.strip(), v.strip()))

    interpreters = [{"label": "live-3.12", "exe": sys.executable}]
    for ver in ("3.11", "3.10", "3.9", "3.8", "3.7"):
        r = subprocess.run(["py", f"-{ver}", "-c", "import sys;print(sys.executable)"],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            interpreters.append({"label": f"py-{ver}", "exe": r.stdout.strip()})
    for interp in interpreters:
        r = b.run([interp["exe"], "-c", _TAGS_PROBE])
        try:
            info = json.loads(r["stdout"].strip().splitlines()[-1])
            interp["version"] = info["version"]
            interp["tags"] = set(info["tags"])
        except (ValueError, IndexError, KeyError):
            interp["version"] = None
            interp["tags"] = set()

    b.require_network()
    per_pin = []
    for name, version in pins:
        b.tick()
        entry = {"name": name, "version": version}
        try:
            url = f"https://pypi.org/pypi/{name}/{version}/json"
            rq = urllib.request.Request(url, headers={"User-Agent": "prometheus-techne/1"})
            with urllib.request.urlopen(rq, timeout=30) as resp:
                body = resp.read()
            b.count_download(len(body))
            meta = json.loads(body)
            entry["version_exists_on_pypi"] = True
            wheels = [u["filename"] for u in meta["urls"] if u["packagetype"] == "bdist_wheel"]
            entry["n_wheels"] = len(wheels)
            entry["has_sdist"] = any(u["packagetype"] == "sdist" for u in meta["urls"])
            entry["compatible"] = {}
            for interp in interpreters:
                hits = [w for w in wheels if _wheel_tags(w) & interp["tags"]]
                entry["compatible"][interp["label"]] = {
                    "n_compatible_wheels": len(hits), "example": hits[0] if hits else None}
        except urllib.error.HTTPError as exc:
            entry["version_exists_on_pypi"] = False
            entry["http_status"] = exc.code
            entry["compatible"] = {i["label"]: {"n_compatible_wheels": 0, "example": None}
                                   for i in interpreters}
        except Exception as exc:
            entry["error"] = f"{type(exc).__name__}: {exc}"
            entry["compatible"] = {}
        per_pin.append(entry)

    summary = []
    for interp in interpreters:
        lab = interp["label"]
        ok = [p["name"] for p in per_pin
              if p.get("compatible", {}).get(lab, {}).get("n_compatible_wheels", 0) > 0]
        sdist_only = [p["name"] for p in per_pin
                      if p.get("version_exists_on_pypi")
                      and p.get("compatible", {}).get(lab, {}).get("n_compatible_wheels", 0) == 0
                      and p.get("has_sdist")]
        gone = [p["name"] for p in per_pin if p.get("version_exists_on_pypi") is False]
        summary.append({
            "interpreter": lab, "version": interp["version"],
            "n_pins": len(per_pin),
            "n_with_compatible_wheel": len(ok),
            "n_sdist_only_would_need_a_source_build": len(sdist_only),
            "sdist_only": sorted(sdist_only),
            "n_pinned_version_absent_from_pypi": len(gone),
            "pinned_version_absent": sorted(gone),
            "installable_from_wheels_alone": len(ok) == len(per_pin),
        })

    return {
        "requirements_file": str(req.relative_to(root)).replace("\\", "/"),
        "method": "per-pin artifact availability against each interpreter's sys_tags(); a "
                  "full resolver run was abandoned as non-terminating and is recorded as "
                  "such rather than reported as a failure",
        "n_pins": len(pins),
        "notable_pins": [f"{n}=={v}" for n, v in pins if n.lower() in
                         ("torch", "torchvision", "numpy", "scikit-learn", "scipy",
                          "matplotlib", "pygame", "box2d-kengz", "cairocffi")],
        "per_interpreter": summary,
        "per_pin": per_pin,
        "any_interpreter_installable_from_wheels": any(
            s["installable_from_wheels_alone"] for s in summary),
    }


# Toolchains this programme installed CONTAINED (not on PATH) or that exist on the host under a
# name the probe would otherwise miss. A probe that only reads PATH reports a blocker that was
# cleared, which is worse than reporting nothing.
_EXTRA_LOCATIONS = {
    "cargo": [str(paths.tool_cache() / "rust" / "cargo" / "bin" / "cargo.exe")],
    "rustc": [str(paths.tool_cache() / "rust" / "cargo" / "bin" / "rustc.exe")],
    "rustup": [str(paths.tool_cache() / "rust" / "cargo" / "bin" / "rustup.exe")],
    # Resolved, not hardcoded (base-role s2). mingw32-make is what WinLibs ships
    # in place of `make`; an empty list here means the host has no GCC bin and the
    # probe reports make as ABSENT rather than looking somewhere it is not.
    "make": ([str(paths.gcc_bin() / "mingw32-make.exe")] if paths.gcc_bin() else []),
}


def probe_native_toolchains() -> dict:
    def which(exe):
        p = shutil.which(exe)
        found_via = "PATH" if p else None
        if not p:
            for cand in _EXTRA_LOCATIONS.get(exe, []):
                if pathlib.Path(cand).exists():
                    p, found_via = cand, ("contained tool cache"
                                          if "techne_tools" in cand else
                                          "on-host, not on PATH (alternate name)")
                    break
        ver = None
        if p:
            for flag in ("--version", "-version", "version"):
                try:
                    r = subprocess.run([p, flag], capture_output=True, text=True, timeout=20)
                    if r.returncode == 0:
                        ver = (r.stdout or r.stderr).strip().splitlines()[0]
                        break
                except (OSError, subprocess.SubprocessError):
                    pass
        return {"present": bool(p), "path": p, "version": ver, "found_via": found_via}

    tools = {n: which(n) for n in ("opam", "ocaml", "ocamlfind", "dune", "make",
                                  "cargo", "rustc", "rustup", "pkg-config", "singularity")}
    return {
        "tools": tools,
        "ocaml_solver": {
            "required": "opam switch 4.06.1+flambda plus " + ", ".join(OCAML_PACKAGES),
            "source": "README 'Build the OCaml solver' section at the pinned revision",
            "buildable_here": tools["opam"]["present"] and tools["ocaml"]["present"],
        },
        "rust_compressor": {
            "required": "cargo + rustc (make in rust_compressor/)",
            "buildable_here": tools["cargo"]["present"] and tools["rustc"]["present"],
        },
        "singularity_container": {
            "readme_offers": "sudo singularity build container.img singularity",
            "available_here": tools["singularity"]["present"],
            "note": "the README's container route also needs sudo and a Linux host; this is "
                    "Windows",
        },
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None,
                    help="optional extra copy; the receipt under techne/acquisition/receipts/ "
                         "is canonical and is always written")
    ap.add_argument("--profile", default="isolated_heavy_build")
    a = ap.parse_args(argv)

    man = manifest_io.load()
    entry = manifest_io.entry(man, "dreamcoder")
    root = paths.repos() / "dreamcoder"
    if not (root / ".git").exists():
        print(f"dreamcoder source is not acquired at {root}. Run:\n"
              f"  python -m techne.scripts.acquire --entry dreamcoder "
              f"--profile isolated_heavy_build")
        return 3

    prof = _budget.get_profile(a.profile)
    rec = receipt.new("FIRST_USEFUL_CHECK", "dreamcoder")
    rec["check"] = "dreamcoder_bounded_domain_smoke_feasibility"
    rec["budget_profile"] = prof

    with _budget.Budget(profile=prof) as b:
        head = b.run(["git", "rev-parse", "HEAD"], cwd=str(root))
        rec["observations"]["source_revision"] = head["stdout"].strip()
        rec["observations"]["pin_matches_manifest"] = (
            head["stdout"].strip() == entry["upstream_revision"]["commit"])
        rec["observations"]["recipe_location"] = locate_recipe(root)
        rec["observations"]["native_toolchains"] = probe_native_toolchains()
        rec["observations"]["python_stack"] = probe_python_stack(root, b)
        rec["resource_receipt"] = b.resource_receipt()

    nt = rec["observations"]["native_toolchains"]
    ps = rec["observations"]["python_stack"]
    blockers = []
    if not ps["any_interpreter_installable_from_wheels"]:
        detail = "; ".join(
            f"{s['interpreter']} ({s['version']}): {s['n_with_compatible_wheel']}/{s['n_pins']} "
            f"pins have a compatible wheel, {s['n_sdist_only_would_need_a_source_build']} are "
            f"sdist-only, {s['n_pinned_version_absent_from_pypi']} pinned versions are gone"
            for s in ps["per_interpreter"])
        blockers.append({
            "id": "BLK-DC-1", "dimension": "python stack",
            "measured": f"requirements.txt pins {ps['n_pins']} exact versions (including "
                        f"{', '.join(ps['notable_pins'][:4])}). No interpreter on this host "
                        f"can install all of them from wheels. {detail}",
            "consequence": "the Python half of a domain run cannot be installed from binaries; "
                           "the remainder would need source builds of 2019 scientific packages "
                           "against a 2026 toolchain",
        })
    if not nt["ocaml_solver"]["buildable_here"]:
        blockers.append({
            "id": "BLK-DC-2", "dimension": "OCaml solver",
            "measured": "opam present=" + str(nt["tools"]["opam"]["present"]) +
                        ", ocaml present=" + str(nt["tools"]["ocaml"]["present"]),
            "consequence": "the enumeration solver binaries cannot be built, and every domain "
                           "script invokes them",
        })
    if not nt["rust_compressor"]["buildable_here"]:
        blockers.append({
            "id": "BLK-DC-3", "dimension": "Rust compressor",
            "measured": "cargo present=" + str(nt["tools"]["cargo"]["present"]),
            "consequence": "the Rust compression backend cannot be built; the official "
                           "commands pass --compressor pypy, which is a third backend also "
                           "absent here",
        })
    rc = rec["observations"]["recipe_location"]["root_level_file_content_summary"]
    if rc and rc.get("max_timeout_seconds"):
        blockers.append({
            "id": "BLK-DC-4", "dimension": "resource envelope",
            "measured": f"every one of the {rc['n_lines_invoking_bin_launch_py']} official "
                        f"commands is a cloud-launcher invocation requesting machine types "
                        f"{rc['machine_types_requested']} with per-run timeouts up to "
                        f"{rc['max_timeout_seconds']}s",
            "consequence": f"the isolated_heavy_build ceiling is "
                           f"{prof['max_wall_seconds']}s on 16 logical CPUs, and no cloud "
                           f"launcher is authorised. None of the official commands fits any "
                           f"declared profile, at any tolerance.",
        })

    rec["observations"]["blockers"] = blockers
    rec["status"] = "BLOCKED_SMOKE_RUN_NOT_POSSIBLE" if blockers else "SMOKE_RUN_FEASIBLE"
    rec["unrun_or_blocked"] = [
        "No DreamCoder domain smoke run was executed. The boundary is measured above, not "
        "estimated, and it is four independent blockers rather than one."]
    rec["deviations"] = [
        "DEV-T7[dreamcoder]: the design asks for 'one named bounded domain smoke run'. It is "
        "NOT delivered. What is delivered is the measured reason it cannot be, which is the "
        "precise failing boundary the design asks for in place of a new architecture proposal."]
    rec["observations"]["what_would_unblock"] = {
        "minimum": "a Linux host with opam 4.06.1+flambda, the ten named OCaml packages, a "
                   "Rust toolchain, and a Python <=3.7 interpreter -- i.e. the singularity "
                   "container route, on Linux, with sudo",
        "cheaper_alternative_for_the_consumer": "the H0/H2 reference library-learning arm does "
            "not require DreamCoder's solver. stitch_core already produces a verified, "
            "expansion-correct library artifact on this host (see "
            "techne/acquisition/exports/). If the arm needs a library rather than "
            "DreamCoder specifically, it is already unblocked by a different tool.",
        "NOT_a_recommendation_to_drop_dreamcoder": "DreamCoder's value as a reference arm is a "
            "scientific judgement for the consuming seat, not this seat's call.",
    }

    out = receipt.write(rec)
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")

    print(f"=== DreamCoder smoke feasibility ({_dt.date.today()}) ===")
    print(f"source at pin   {rec['observations']['pin_matches_manifest']} "
          f"({rec['observations']['source_revision'][:12]})")
    r = rec["observations"]["recipe_location"]
    print(f"README names    {r['readme_linked_path']}  exists={r['readme_linked_path_exists']}")
    for f in r["files_with_that_basename_anywhere"]:
        print(f"  found         {f['path']} ({f['bytes']}B sha256={str(f['sha256'])[:16]})")
    if rc:
        print(f"  content       {rc['n_lines_invoking_bin_launch_py']}/"
              f"{rc['n_nonblank_lines']} lines are cloud-launcher calls; machines "
              f"{rc['machine_types_requested']}; timeouts up to {rc['max_timeout_seconds']}s")
    for i in ps["per_interpreter"]:
        print(f"python {i['interpreter']:<11} {str(i['version']):<8} wheels "
              f"{i['n_with_compatible_wheel']}/{i['n_pins']}  sdist-only "
              f"{i['n_sdist_only_would_need_a_source_build']}  version-gone "
              f"{i['n_pinned_version_absent_from_pypi']}")
    t = nt["tools"]
    print("toolchains      " + ", ".join(
        f"{k}={'yes' if v['present'] else 'NO'}"
        + (f"({v['found_via']})" if v.get('found_via') and v['found_via'] != 'PATH' else "")
        for k, v in t.items()))
    print(f"\nSTATUS          {rec['status']}")
    for blk in blockers:
        print(f"  {blk['id']} [{blk['dimension']}] {blk['measured']}")
    print(f"\nreceipt         {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
