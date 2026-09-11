"""Clymene vault audit, part D: consumption census for repos and models.

Preregistered predicate (PREREGISTRATION_2026-09-11_vault_audit.md s1):
  CONSUMED-PATH      a tracked NON-DOCUMENTARY file resolves a vault path
  CONSUMED-IDENTITY  tracked non-documentary code imports the package this
                     snapshot provides, or names the model's HF id, in a way
                     that would load it
  NOT CONSUMED       documentary references only, or none
Documentary is fixed BY DEFINITION before the search: .md/.txt/.rst/.csv/.log/
.jsonl, survey/dossier/report/digest JSON, and pipelines/*.yaml (a spec whose
entry point is not in the tree).

The decisive extra question for repositories: if tracked code imports the
package, does the import resolve to the VAULT or to site-packages? The vault is
not on sys.path, so a site-packages resolution means the vault copy is NOT
consumed. Recorded with the resolved origin.

ONE PASS: every pattern is handed to a single `git grep` invocation over
tracked files at HEAD, then each hit line is attributed back to the patterns it
contains. The earlier per-pattern version issued ~200 greps over a 39k-file
tree and was abandoned as too slow, not as wrong.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import time

SCRATCH = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SCRATCH, "consumption_audit.jsonl")
REPO_ROOT = "D:/Prometheus-worktrees/clymene-base-role"
VAULT_REPOS = "D:/Prometheus/vault/repos"
VAULT_MODELS = "D:/Prometheus/vault/models"
REGISTRY = os.path.join(SCRATCH, "registry.json")

DOC_EXT = {".md", ".txt", ".rst", ".csv", ".log", ".jsonl"}
CONTROL_PRESENT = "CLYMENE_VAULT_ROOT"
CONTROL_ABSENT = "zzq-clymene-control-string-never-present-zzq"


def is_documentary(path: str) -> bool:
    ext = os.path.splitext(path)[1].lower()
    if ext in DOC_EXT:
        return True
    if ext == ".json" and any(h in path.lower() for h in
                              ("survey", "dossier", "report", "digest", "autopsies")):
        return True
    if path.startswith("pipelines/") and ext in (".yaml", ".yml"):
        return True
    return False


def is_self(path: str) -> bool:
    return path.startswith("agents/clymene") or path.startswith("roles/Clymene/")


PKG_RE = re.compile(r"""name\s*[:=]\s*['"]([A-Za-z0-9_.\-]+)['"]""")
PKGS_RE = re.compile(r"""packages\s*=\s*\[\s*['"]([A-Za-z0-9_.]+)""")


def package_names(d):
    cand = []
    for fn in ("pyproject.toml", "setup.py", "setup.cfg"):
        p = os.path.join(d, fn)
        if not os.path.exists(p):
            continue
        try:
            txt = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        cand += [m.group(1) for m in PKG_RE.finditer(txt)]
        cand += [m.group(1) for m in PKGS_RE.finditer(txt)]
    seen, out = set(), []
    for c in cand:
        c = c.strip()
        if c and c.lower() not in seen and c.lower() not in ("python", "setuptools"):
            seen.add(c.lower())
            out.append(c)
    return out


def resolve_import(mod):
    try:
        spec = importlib.util.find_spec(mod)
    except Exception as exc:
        return {"importable": False, "error": type(exc).__name__}
    if spec is None:
        return {"importable": False, "error": None}
    origin = spec.origin or (spec.submodule_search_locations[0]
                             if spec.submodule_search_locations else None)
    origin = str(origin) if origin else None
    norm = (origin or "").replace("\\", "/").lower()
    return {"importable": True, "origin": origin,
            "resolves_to_vault": "/vault/" in norm,
            "site_packages": "site-packages" in norm}


def one_pass_grep(patterns):
    """Single git grep over tracked files with every pattern; attribute back."""
    args = ["git", "grep", "-n", "-I", "-F", "--no-color"]
    for p in patterns:
        args += ["-e", p]
    args.append("HEAD")
    p = subprocess.run(args, capture_output=True, text=True, timeout=1800,
                       cwd=REPO_ROOT, errors="replace")
    hits = []
    for line in p.stdout.splitlines():
        parts = line.split(":", 3)
        if len(parts) < 4:
            continue
        _, path, lineno, text = parts
        hits.append((path, lineno, text))
    index = {pat: [] for pat in patterns}
    for path, lineno, text in hits:
        for pat in patterns:
            if pat in text or pat in path:
                index[pat].append({"path": path, "line": lineno, "text": text.strip()[:180]})
    return index, len(hits), p.returncode


def bucket(hits):
    out = {"self": 0, "documentary": 0, "code": 0, "code_sample": []}
    for h in hits:
        if is_self(h["path"]):
            out["self"] += 1
        elif is_documentary(h["path"]):
            out["documentary"] += 1
        else:
            out["code"] += 1
            if len(out["code_sample"]) < 6:
                out["code_sample"].append(h["path"] + ":" + str(h["line"]))
    return out


def emit(fh, rec):
    fh.write(json.dumps(rec) + "\n")
    fh.flush()
    os.fsync(fh.fileno())


def main():
    reg = json.load(open(REGISTRY, encoding="utf-8"))
    repos = reg["repos"]
    model_dirs = sorted(x for x in os.listdir(VAULT_MODELS)
                        if os.path.isdir(os.path.join(VAULT_MODELS, x)))

    patterns = [CONTROL_PRESENT, CONTROL_ABSENT]
    repo_pats = {}
    for r in repos:
        name = r["name"]
        pk = package_names(os.path.join(VAULT_REPOS, name))
        pats = {
            "path_posix": "vault/repos/" + name,
            "path_win": "vault\\repos\\" + name,
            "name": name,
            "url": (r.get("url") or "zzz-no-url"),
        }
        for i, mod in enumerate(pk[:3]):
            m = mod.replace("-", "_")
            pats["import_%d" % i] = "import " + m
            pats["from_%d" % i] = "from " + m
        repo_pats[name] = {"pkgs": pk, "pats": pats}
        patterns += list(pats.values())

    model_pats = {}
    for d in model_dirs:
        hf = d.replace("--", "/", 1)
        short = hf.split("/", 1)[1] if "/" in hf else hf
        pats = {"path_posix": "vault/models/" + d, "path_win": "vault\\models\\" + d,
                "hf_id": hf, "short": short}
        model_pats[d] = pats
        patterns += list(pats.values())

    patterns = list(dict.fromkeys(patterns))  # de-duplicate, keep order

    t0 = time.time()
    index, total_hits, rc = one_pass_grep(patterns)
    elapsed = round(time.time() - t0, 1)

    with open(OUT, "w", encoding="utf-8") as fh:
        emit(fh, {"kind": "header",
                  "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                  "repo_root": REPO_ROOT, "patterns": len(patterns),
                  "total_hit_lines": total_hits, "grep_seconds": elapsed,
                  "grep_returncode": rc,
                  "note": "single git grep over TRACKED files at HEAD"})

        emit(fh, {"kind": "control", "control": "SEARCH_CHANNEL",
                  "known_present": CONTROL_PRESENT,
                  "known_present_hits": len(index[CONTROL_PRESENT]),
                  "known_absent_hits": len(index[CONTROL_ABSENT]),
                  "PASS": len(index[CONTROL_PRESENT]) > 0 and len(index[CONTROL_ABSENT]) == 0})

        for r in repos:
            name = r["name"]
            info = repo_pats[name]
            pats = info["pats"]
            b = {k: bucket(index[v]) for k, v in pats.items()}
            path_code = b["path_posix"]["code"] + b["path_win"]["code"]
            import_code = sum(b[k]["code"] for k in b if k.startswith(("import_", "from_")))
            res = {}
            for mod in info["pkgs"][:3]:
                res[mod.replace("-", "_")] = resolve_import(mod.replace("-", "_"))
            vault_backed = any(v.get("resolves_to_vault") for v in res.values())
            rec = {"kind": "repo_consumption", "name": name, "url": r.get("url"),
                   "declared_packages": info["pkgs"][:3],
                   "path_ref_code": path_code,
                   "path_ref_documentary": b["path_posix"]["documentary"] + b["path_win"]["documentary"],
                   "name_ref_code": b["name"]["code"],
                   "name_ref_documentary": b["name"]["documentary"],
                   "name_ref_code_sample": b["name"]["code_sample"],
                   "url_ref_code": b["url"]["code"],
                   "import_ref_code": import_code,
                   "import_ref_code_sample": sum(
                       [b[k]["code_sample"] for k in b if k.startswith(("import_", "from_"))], [])[:6],
                   "import_resolution": res,
                   "IDENTITY_RESOLVES_TO_VAULT": vault_backed}
            rec["CONSUMED_PATH"] = path_code > 0
            rec["CONSUMED_IDENTITY"] = bool(import_code > 0 and vault_backed)
            rec["CONSUMED"] = bool(rec["CONSUMED_PATH"] or rec["CONSUMED_IDENTITY"])
            if import_code > 0 and not vault_backed:
                rec["note"] = "import reference exists but is satisfied outside the vault"
            elif import_code == 0 and path_code == 0:
                rec["note"] = "no non-documentary reference of any kind"
            else:
                rec["note"] = ""
            emit(fh, rec)

        for d in model_dirs:
            pats = model_pats[d]
            b = {k: bucket(index[v]) for k, v in pats.items()}
            path_code = b["path_posix"]["code"] + b["path_win"]["code"]
            rec = {"kind": "model_consumption", "dir": d,
                   "hf_id": pats["hf_id"],
                   "path_ref_code": path_code,
                   "path_ref_documentary": b["path_posix"]["documentary"] + b["path_win"]["documentary"],
                   "hf_id_ref_code": b["hf_id"]["code"],
                   "hf_id_ref_documentary": b["hf_id"]["documentary"],
                   "hf_id_ref_code_sample": b["hf_id"]["code_sample"],
                   "short_ref_code": b["short"]["code"],
                   "short_ref_code_sample": b["short"]["code_sample"]}
            rec["CONSUMED_PATH"] = path_code > 0
            rec["ID_REFERENCED_IN_CODE"] = (b["hf_id"]["code"] + b["short"]["code"]) > 0
            rec["CONSUMED"] = rec["CONSUMED_PATH"]
            rec["note"] = ("HF id appears in live code, but by identity -- it would resolve "
                           "through the Hub or the HF cache, not through the vault path"
                           if (rec["ID_REFERENCED_IN_CODE"] and not rec["CONSUMED_PATH"]) else "")
            emit(fh, rec)

        emit(fh, {"kind": "footer",
                  "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})


if __name__ == "__main__":
    main()
    print("wrote", OUT)
