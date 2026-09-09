"""Python-distribution acquisition: resolve, hash, license, lock, install ISOLATED.

The order of operations is the point. Hashes are computed from the bytes WE downloaded
and compared against PyPI's own declared digest -- two independent statements that can
disagree. The license is read out of the distributed METADATA, never inferred from a
repository API classifier, and an absent license is recorded as UNRESOLVED rather than
filled in from knowledge of what the project "is".

Nothing here touches the live interpreter. `ensure_env` builds a venv under the
host-local tool cache; `install_locked` runs that venv's pip with --require-hashes
against a lock this module wrote.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys
import urllib.request
import zipfile

from . import paths
from .budget import Budget

PYPI = "https://pypi.org/pypi"
_UA = {"User-Agent": "prometheus-techne-acquisition/1"}


# --------------------------------------------------------------------------- metadata
def release_metadata(distribution: str, version: str, budget: Budget) -> dict:
    budget.require_network()
    budget.tick()
    url = f"{PYPI}/{distribution}/{version}/json"
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    budget.count_download(len(raw))
    return json.loads(raw)


def host_tags() -> list[str]:
    """Compatible wheel tags for the interpreter that will RUN the tool."""
    try:
        from packaging.tags import sys_tags
        return [str(t) for t in sys_tags()]
    except Exception:
        # Refuse to guess a compatibility set. The caller records UNRESOLVED.
        return []


def select_artifact(meta: dict, prefer: str = "wheel") -> dict:
    """Pick the artifact this host can actually install, and say WHY.

    Returns a dict with `selected`, `reason`, and the full candidate list so a reviewer
    can see what was rejected. A platform with no compatible wheel gets selected=None
    and an explicit reason -- not a silent fall back to the sdist, because an sdist
    means a build, which means a different budget profile.
    """
    tags = set(host_tags())
    cands = []
    for u in meta["urls"]:
        fn = u["filename"]
        entry = {
            "filename": fn,
            "packagetype": u["packagetype"],
            "size": u["size"],
            "sha256_pypi": u["digests"]["sha256"],
            "url": u["url"],
            "yanked": u.get("yanked", False),
            "requires_python": u.get("requires_python"),
        }
        if u["packagetype"] == "bdist_wheel":
            m = re.match(r"^(?P<name>.+?)-(?P<ver>.+?)(-(?P<build>\d[^-]*))?-(?P<tags>[^-]+-[^-]+-[^-]+)\.whl$", fn)
            wtags = set()
            if m:
                py, abi, plat = m.group("tags").split("-")
                for p in py.split("."):
                    for a in abi.split("."):
                        for pl in plat.split("."):
                            wtags.add(f"{p}-{a}-{pl}")
            entry["wheel_tags"] = sorted(wtags)
            entry["host_compatible"] = bool(wtags & tags) if tags else None
        else:
            entry["wheel_tags"] = []
            entry["host_compatible"] = None
        cands.append(entry)

    wheels = [c for c in cands if c["packagetype"] == "bdist_wheel"
              and c["host_compatible"] and not c["yanked"]]
    if wheels:
        # Narrowest matching tag wins: prefer the tag appearing earliest in sys_tags().
        order = {t: i for i, t in enumerate(host_tags())}
        wheels.sort(key=lambda c: min(order.get(t, 10**6) for t in c["wheel_tags"]))
        return {"selected": wheels[0], "reason": "compatible wheel, narrowest host tag",
                "candidates": cands, "host_tag_count": len(tags)}
    if not tags:
        return {"selected": None, "reason": "host wheel tags UNRESOLVED (packaging unavailable); "
                                           "refusing to guess compatibility",
                "candidates": cands, "host_tag_count": 0}
    return {"selected": None,
            "reason": "NO compatible wheel for this host. An sdist would require a source "
                      "build, which is a different budget profile (isolated_heavy_build) "
                      "and a separate decision; not selected automatically.",
            "candidates": cands, "host_tag_count": len(tags)}


# --------------------------------------------------------------------------- download
def download(artifact: dict, budget: Budget) -> dict:
    budget.require_network()
    dest_dir = paths.downloads()
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / artifact["filename"]

    if dest.exists():
        local = hashlib.sha256(dest.read_bytes()).hexdigest()
        if local == artifact["sha256_pypi"]:
            return {"path": str(dest), "bytes": dest.stat().st_size,
                    "sha256_local": local, "digest_matches_pypi": True,
                    "transferred": False, "note": "already in cache, digest re-verified"}
        dest.unlink()

    h = hashlib.sha256()
    n = 0
    req = urllib.request.Request(artifact["url"], headers=_UA)
    with urllib.request.urlopen(req, timeout=180) as r, open(dest, "wb") as fh:
        while True:
            budget.tick()
            chunk = r.read(1 << 16)
            if not chunk:
                break
            budget.count_download(len(chunk))
            h.update(chunk)
            fh.write(chunk)
            n += len(chunk)
    local = h.hexdigest()
    return {"path": str(dest), "bytes": n, "sha256_local": local,
            "digest_matches_pypi": local == artifact["sha256_pypi"], "transferred": True}


# --------------------------------------------------------------------------- license
_LICENSE_FILE_RE = re.compile(r"(^|/)(LICEN[CS]E|COPYING|NOTICE)([.\-_][A-Za-z0-9]+)?$", re.I)


def license_from_wheel(wheel_path: str) -> dict:
    """Read the license out of the distributed artifact. Three independent sources,
    all reported, none merged into a single guess:

        License-Expression   PEP 639 SPDX expression (authoritative when present)
        License              free text (often the full license body)
        Classifier           trove classifiers
        license files        the actual notice files shipped in the wheel

    If all four are empty the result is UNRESOLVED, and that is a finding, not a gap to
    fill from the repository's API classifier.
    """
    out = {"license_expression": None, "license_field": None, "classifiers": [],
           "license_files": [], "source": "wheel METADATA", "status": "UNRESOLVED"}
    if not wheel_path.endswith(".whl"):
        out["source"] = f"NOT A WHEEL: {pathlib.Path(wheel_path).name}"
        return out
    with zipfile.ZipFile(wheel_path) as z:
        names = z.namelist()
        meta_name = next((n for n in names if re.match(r"[^/]+\.dist-info/METADATA$", n)), None)
        if meta_name:
            text = z.read(meta_name).decode("utf-8", "replace")
            for line in text.splitlines():
                if line.startswith("License-Expression:"):
                    out["license_expression"] = line.split(":", 1)[1].strip()
                elif line.startswith("License:") and out["license_field"] is None:
                    out["license_field"] = line.split(":", 1)[1].strip()[:300]
                elif line.startswith("Classifier:") and "License" in line:
                    out["classifiers"].append(line.split(":", 1)[1].strip())
                elif line.startswith("License-File:"):
                    out["license_files"].append(
                        {"name": line.split(":", 1)[1].strip(), "declared": True})
                elif line == "":
                    break
        for n in names:
            if _LICENSE_FILE_RE.search(n):
                data = z.read(n)
                out["license_files"].append({
                    "name": n, "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "first_line": data.decode("utf-8", "replace").strip().splitlines()[0][:160]
                    if data.strip() else "",
                })
    if out["license_expression"]:
        out["status"] = "RESOLVED_SPDX_EXPRESSION"
    elif out["classifiers"]:
        out["status"] = "RESOLVED_CLASSIFIER_ONLY"
    elif out["license_field"]:
        out["status"] = "RESOLVED_FREE_TEXT_ONLY"
    elif out["license_files"]:
        out["status"] = "NOTICE_SHIPPED_BUT_NO_DECLARED_LICENSE"
    return out


def requires_dist_from_wheel(wheel_path: str) -> list[str]:
    if not wheel_path.endswith(".whl"):
        return []
    with zipfile.ZipFile(wheel_path) as z:
        meta_name = next((n for n in z.namelist()
                          if re.match(r"[^/]+\.dist-info/METADATA$", n)), None)
        if not meta_name:
            return []
        text = z.read(meta_name).decode("utf-8", "replace")
    return [ln.split(":", 1)[1].strip() for ln in text.splitlines()
            if ln.startswith("Requires-Dist:")]


# --------------------------------------------------------------------------- isolated env
def env_python(env_name: str) -> pathlib.Path:
    root = paths.env_root(env_name)
    return root / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")


def ensure_env(env_name: str, budget: Budget) -> dict:
    """Create the isolated venv if absent. Never the live interpreter.

    --without-pip is NOT used: the lock install needs pip inside the env. pip itself is
    bootstrapped by ensurepip from the base interpreter's bundled wheel, which means the
    env's pip version is inherited rather than pinned. That is recorded, not hidden.
    """
    root = paths.env_root(env_name)
    py = env_python(env_name)
    created = False
    if not py.exists():
        root.parent.mkdir(parents=True, exist_ok=True)
        r = budget.run([sys.executable, "-m", "venv", str(root)])
        created = True
        if r["returncode"] != 0:
            raise RuntimeError(f"venv creation failed: {r['stderr'][:2000]}")
    ver = budget.run([str(py), "-c",
                      "import sys,json;print(json.dumps({'v':sys.version.split()[0],'exe':sys.executable}))"])
    pipver = budget.run([str(py), "-m", "pip", "--version"])
    info = json.loads(ver["stdout"].strip()) if ver["returncode"] == 0 else {}
    return {
        "env_name": env_name,
        "root": str(root),
        "python": str(py),
        "created_now": created,
        "python_version": info.get("v"),
        "is_live_interpreter": str(py) == sys.executable,
        "pip_version": (pipver["stdout"] or pipver["stderr"]).strip(),
        "pip_pinned": False,
        "pip_note": "pip bootstrapped by ensurepip from the base interpreter's bundled wheel; "
                    "its version is inherited, not pinned by this lock",
    }


def resolve_lock(env_name: str, spec: str, budget: Budget) -> dict:
    """Resolve the full transitive closure WITH hashes, without installing anything.

    pip's --report gives the resolved set and each artifact's declared sha256. That is
    what a --require-hashes lock needs, and it is produced by the resolver that will do
    the install, so the lock cannot disagree with the resolution that produced it.
    """
    budget.require_network()
    py = env_python(env_name)
    report = paths.tool_cache() / "reports" / f"{env_name}-{re.sub(r'[^A-Za-z0-9._-]', '_', spec)}.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    r = budget.run([str(py), "-m", "pip", "install", "--dry-run", "--ignore-installed",
                    "--quiet", "--report", str(report), spec])
    if r["returncode"] != 0:
        return {"ok": False, "command": r, "resolved": []}
    data = json.loads(report.read_text(encoding="utf-8"))
    resolved = []
    for item in data.get("install", []):
        md = item.get("metadata", {})
        di = item.get("download_info", {})
        sha = (di.get("archive_info", {}).get("hashes", {}) or {}).get("sha256")
        resolved.append({
            "name": md.get("name"), "version": md.get("version"),
            "url": di.get("url"), "sha256": sha,
            "requested": bool(item.get("requested")),
        })
    return {"ok": True, "command": {k: v for k, v in r.items() if k != "stdout"},
            "pip_report": str(report), "resolved": resolved,
            "unhashed": [x["name"] for x in resolved if not x["sha256"]]}


def write_lock(entry_id: str, env_name: str, resolved: list[dict], extra_header: str = "") -> pathlib.Path:
    import sysconfig
    host = f"cp{sys.version_info.major}{sys.version_info.minor}-{sysconfig.get_platform()}"
    out = paths.locks() / f"{entry_id}-{host}.lock.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# techne.acquisition lock -- entry {entry_id!r}, isolated env {env_name!r}",
        f"# host interpreter: Python {sys.version.split()[0]} / {sys.platform}",
        "#",
        "# Install ONLY into the isolated env, and ONLY with hashes required:",
        f"#     <tool_cache>/envs/{env_name}/Scripts/python -m pip install "
        f"--require-hashes --no-deps -r {out.name}",
        "#",
        "# --no-deps is deliberate: the closure below IS the dependency set, resolved once",
        "# and pinned. Letting pip re-resolve would let a transitive floor move silently.",
        "#",
        "# This lock is valid for THIS interpreter and platform only. A different Python",
        "# minor version or platform needs its own lock; a lock is not portable evidence.",
    ]
    if extra_header:
        lines += ["#"] + [f"# {ln}" for ln in extra_header.splitlines()]
    lines.append("")
    for item in sorted(resolved, key=lambda x: (x["name"] or "").lower()):
        if not item.get("sha256"):
            lines.append(f"# UNHASHED, REFUSED: {item['name']}=={item['version']} "
                         f"(pip reported no sha256; cannot appear in a --require-hashes lock)")
            continue
        lines.append(f"{item['name']}=={item['version']} \\")
        lines.append(f"    --hash=sha256:{item['sha256']}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def install_locked(env_name: str, lock: pathlib.Path, budget: Budget) -> dict:
    budget.require_network()
    py = env_python(env_name)
    r = budget.run([str(py), "-m", "pip", "install", "--require-hashes", "--no-deps",
                    "-r", str(lock)])
    return {"lock": str(lock), "returncode": r["returncode"], "timed_out": r["timed_out"],
            "wall_seconds": r["wall_seconds"],
            "stdout_tail": r["stdout"][-4000:], "stderr_tail": r["stderr"][-4000:]}


def verify_import(env_name: str, import_name: str, distribution: str, budget: Budget) -> dict:
    py = env_python(env_name)
    code = (
        "import json,importlib,importlib.metadata as md\n"
        f"out={{}}\n"
        f"try:\n"
        f"    m=importlib.import_module({import_name!r})\n"
        f"    out['imported']=True\n"
        f"    out['module_file']=getattr(m,'__file__',None)\n"
        f"except Exception as e:\n"
        f"    out['imported']=False; out['error']=f'{{type(e).__name__}}: {{e}}'\n"
        f"try:\n"
        f"    out['dist_version']=md.version({distribution!r})\n"
        f"except Exception as e:\n"
        f"    out['dist_version']=None; out['dist_error']=str(e)\n"
        "print(json.dumps(out))\n"
    )
    r = budget.run([str(py), "-c", code])
    try:
        return json.loads(r["stdout"].strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {"imported": False, "error": "probe produced no JSON",
                "stdout": r["stdout"][-2000:], "stderr": r["stderr"][-2000:]}
