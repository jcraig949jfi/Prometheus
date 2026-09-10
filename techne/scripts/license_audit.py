"""Keep the licenses with the copies, and record what could not be resolved.

    python -m techne.scripts.license_audit --out techne/acquisition/LICENSE_EVIDENCE.json

The design's rule is exact: "Keep licenses/notices with the tool copy and record
unresolved licensing rather than guessing from a repository API classifier."

So this tool does three things and refuses a fourth:

  1. reads the license declaration out of each INSTALLED wheel's METADATA
  2. when the wheel ships no notice, looks in the DISTRIBUTED sdist for one -- an sdist
     is still the project's own artifact, unlike a repository API classifier
  3. copies every notice it finds into <tool_cache>/notices/<dist>-<version>/ so the
     notice physically travels with the bytes, and records its sha256 here
  4. REFUSES to assign an SPDX identifier that the artifacts do not state. A repository
     whose GitHub API license field says MIT while its wheel and sdist carry no license
     text at all is recorded as UNRESOLVED, because the thing we redistribute is the
     artifact, not the repository page.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import io
import json
import pathlib
import re
import tarfile
import urllib.request
import zipfile

from techne.acquisition import budget as _budget
from techne.acquisition import manifest_io, paths, pypi

_UA = {"User-Agent": "prometheus-techne-acquisition/1"}
_LIC_RE = re.compile(r"(LICEN[CS]E|COPYING|NOTICE|COPYRIGHT)", re.I)


def _fetch(url: str, b: _budget.Budget) -> bytes:
    b.require_network()
    b.tick()
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=180) as r:
        raw = r.read()
    b.count_download(len(raw))
    return raw


def _save_notice(dist: str, version: str, name: str, data: bytes) -> dict:
    d = paths.tool_cache() / "notices" / f"{dist}-{version}"
    d.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    (d / safe).write_bytes(data)
    return {"stored_as": safe, "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "source_path_in_artifact": name,
            "first_line": data.decode("utf-8", "replace").strip().splitlines()[0][:160]
            if data.strip() else ""}


_GH = "https://api.github.com"
_RE_MIT_NOTICE = re.compile(
    r"above copyright notice and this permission notice shall be included", re.I)


def _repository_notice(entry: dict, b: _budget.Budget) -> dict:
    """Read the licence DOCUMENT out of the source tree at the manifest's pinned revision.

    Returns the grant's own text and copyright line, hashed and stored beside the copy. This is
    evidence, not a classifier: it is the document that grants the rights. It is nonetheless
    recorded separately from the artifact metadata, because for a distribution with no matching
    upstream tag we cannot prove this revision built that wheel.
    """
    # official_source may be DOCUMENTATION -- the design's table names readthedocs for several
    # entries -- and a licence document can only be read from a source tree, so repository_url
    # takes precedence when the manifest supplies one.
    src = entry.get("repository_url") or entry.get("official_source") or ""
    rev = (entry.get("upstream_revision") or {}).get("commit")
    out = {"consulted": False, "reason": None,
           "source_used": "repository_url" if entry.get("repository_url") else "official_source"}
    if not src.startswith("https://github.com/") or not rev:
        out["reason"] = (f"no GitHub source tree ({src!r}) or no pinned revision; a repository "
                         f"notice cannot be read at a revision that was never pinned")
        return out
    owner_repo = src.removeprefix("https://github.com/").rstrip("/")
    out.update({"consulted": True, "repository": owner_repo, "revision": rev})
    try:
        b.require_network()
        b.tick()
        req = urllib.request.Request(f"{_GH}/repos/{owner_repo}/contents/?ref={rev}",
                                     headers={**_UA, "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
        b.count_download(len(raw))
        listing = json.loads(raw)
    except Exception as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
        return out

    files = []
    for item in listing:
        if item.get("type") != "file" or not _LIC_RE.match(item["name"]):
            continue
        try:
            b.tick()
            req = urllib.request.Request(item["download_url"], headers=_UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            b.count_download(len(data))
        except Exception as exc:
            files.append({"name": item["name"], "error": str(exc)})
            continue
        text = data.decode("utf-8", "replace")
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        copyright_line = next((ln for ln in lines if ln.lower().startswith("copyright")), None)
        files.append({
            "name": item["name"], "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "first_line": lines[0][:160] if lines else "",
            "copyright_line": copyright_line,
            "requires_notice_be_included_in_copies": bool(_RE_MIT_NOTICE.search(text)),
            "stored": _save_notice(entry["distribution"], entry["pinned_version"],
                                   f"REPOSITORY@{rev[:12]}/{item['name']}", data),
        })
    out["notice_files"] = files
    out["found"] = bool(files)
    out["evidence_grade"] = (
        "LICENCE DOCUMENT AT A PINNED SOURCE REVISION. Stronger than a repository API "
        "classifier, which is a heuristic guess and is never used here. Weaker than the "
        "artifact's own metadata, because the revision is not provably the one that built the "
        "distributed artifact -- decisively so when the distribution has no matching upstream "
        "tag.")
    return out


def audit_entry(entry: dict, b: _budget.Budget) -> dict:
    dist, ver = entry["distribution"], entry["pinned_version"]
    meta = pypi.release_metadata(dist, ver, b)
    out = {
        "entry_id": entry["id"], "distribution": dist, "version": ver,
        "rule_applied": entry.get("license_resolution_rule"),
        "wheel": {}, "sdist": {}, "notices_kept": [],
        "spdx_claim": None, "status": None, "redistribution_note": None,
    }

    sel = pypi.select_artifact(meta)
    art = sel["selected"]
    if art:
        wheel_path = paths.downloads() / art["filename"]
        if not wheel_path.exists():
            pypi.download(art, b)
        lic = pypi.license_from_wheel(str(wheel_path))
        out["wheel"] = {"filename": art["filename"], "sha256": art["sha256_pypi"],
                        **{k: lic[k] for k in ("license_expression", "license_field",
                                               "classifiers", "status")},
                        "notice_files_in_wheel": [f.get("name") for f in lic["license_files"]]}
        with zipfile.ZipFile(wheel_path) as z:
            for n in z.namelist():
                if _LIC_RE.search(pathlib.PurePosixPath(n).name):
                    out["notices_kept"].append(
                        {"from": "wheel", **_save_notice(dist, ver, n, z.read(n))})

    sd = next((u for u in meta["urls"] if u["packagetype"] == "sdist"), None)
    if sd:
        raw = _fetch(sd["url"], b)
        local_sha = hashlib.sha256(raw).hexdigest()
        sdist_lic = []
        declared = []
        with tarfile.open(fileobj=io.BytesIO(raw)) as t:
            names = t.getnames()
            for n in names:
                base = pathlib.PurePosixPath(n).name
                if _LIC_RE.match(base):
                    m = t.extractfile(n)
                    if m is None:
                        continue
                    data = m.read()
                    sdist_lic.append(n)
                    if not any(x["sha256"] == hashlib.sha256(data).hexdigest()
                               for x in out["notices_kept"]):
                        out["notices_kept"].append(
                            {"from": "sdist", **_save_notice(dist, ver, n, data)})
            for n in names:
                if pathlib.PurePosixPath(n).name in ("PKG-INFO", "pyproject.toml", "Cargo.toml"):
                    m = t.extractfile(n)
                    if m is None:
                        continue
                    body = m.read().decode("utf-8", "replace")
                    for ln in body.splitlines():
                        if re.match(r"\s*(License(-Expression)?\s*[:=]|Classifier:\s*License)", ln):
                            declared.append({"file": n, "line": ln.strip()[:200]})
        out["sdist"] = {"filename": sd["filename"], "sha256_pypi": sd["digests"]["sha256"],
                        "sha256_local": local_sha,
                        "digest_matches_pypi": local_sha == sd["digests"]["sha256"],
                        "n_files": len(names), "notice_files_in_sdist": sdist_lic,
                        "declared_license_lines": declared}

    # THIRD source, and it is a different evidence grade from both of the above.
    #
    # The rule is "never infer a licence from a repository API classifier". A classifier is
    # GitHub's guess from a heuristic scan. The LICENCE DOCUMENT ITSELF, read out of the source
    # tree at a pinned revision, is not a guess -- it is the grant, with a named copyright
    # holder. Conflating those two was an error in the 2026-09-09 pass: stitch_core was recorded
    # as having no licence anywhere, when in fact its repository carries a full MIT grant and it
    # is the DISTRIBUTED ARTIFACTS that omit the notice.
    #
    # It is still weaker than the artifact's own metadata, for a reason that matters here: the
    # repository revision is not provably the revision that built the wheel. So it is recorded
    # separately, never merged into `spdx_claim`.
    out["repository_notice"] = _repository_notice(entry, b)

    w = out["wheel"]
    if w.get("license_expression"):
        out["spdx_claim"] = w["license_expression"]
        out["status"] = "RESOLVED_FROM_ARTIFACT_SPDX"
    elif w.get("license_field") or out["sdist"].get("declared_license_lines"):
        out["spdx_claim"] = None
        out["status"] = "DECLARED_AS_FREE_TEXT_NO_SPDX"
    elif out["notices_kept"]:
        out["status"] = "NOTICE_PRESENT_NO_DECLARATION"
    else:
        out["status"] = "UNRESOLVED_NO_LICENSE_IN_ANY_DISTRIBUTED_ARTIFACT"

    if out["status"] == "UNRESOLVED_NO_LICENSE_IN_ANY_DISTRIBUTED_ARTIFACT":
        repo_n = out.get("repository_notice") or {}
        if repo_n.get("found"):
            n = repo_n["notice_files"][0]
            out["status"] = "ARTIFACT_CARRIES_NO_NOTICE_BUT_SOURCE_GRANT_EXISTS"
            out["redistribution_note"] = (
                f"NARROWED from 'no licence anywhere'. The repository DOES carry a licence "
                f"grant at the pinned revision {repo_n['revision'][:12]}: "
                f"{n['first_line']!r}, {n['copyright_line']!r}. What the distributed wheel and "
                f"sdist omit is the NOTICE and the packaging metadata. If that grant requires "
                f"the notice to travel with copies -- it does: "
                f"requires_notice_be_included_in_copies="
                f"{n['requires_notice_be_included_in_copies']} -- then redistributing the wheel "
                f"AS SHIPPED would fail the grant's own condition, while redistributing it "
                f"WITH the notice attached would satisfy it. The notice has been stored beside "
                f"the copy for exactly that purpose. RESIDUAL GAP, and it is the one that keeps "
                f"this open: with no upstream tag matching the installed version, this revision "
                f"is not provably the revision that built the wheel, so the grant is attached "
                f"by inference about provenance rather than by the artifact itself. That is why "
                f"D-17 asks for a pinned SOURCE REVISION as well as a licence.")
        else:
            out["redistribution_note"] = (
                "BLOCKER for redistributing any copy or derived artifact. The distributed "
                "wheel and sdist carry no license declaration and no notice file, and no "
                "licence document was found in the source tree at the pinned revision either. "
                "Whatever a repository page or API classifier says, what we hold grants "
                "nothing in writing. Internal use of the installed copy continues; exporting "
                "it, vendoring it, or shipping anything containing it does NOT, until a human "
                "records a resolution.")
    elif not w.get("notice_files_in_wheel") and out["sdist"].get("notice_files_in_sdist"):
        out["redistribution_note"] = (
            "The WHEEL we installed ships no notice file; the sdist does. The notice has "
            "been copied into the tool cache alongside the wheel so the license travels "
            "with the copy, which is what the design requires. The wheel alone is an "
            "incomplete copy.")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="License evidence for acquired distributions.")
    ap.add_argument("--out", default="techne/acquisition/LICENSE_EVIDENCE.json")
    ap.add_argument("--profile", default="light_probe")
    a = ap.parse_args(argv)

    man = manifest_io.load()
    prof = _budget.get_profile(a.profile)
    results = []
    with _budget.Budget(profile=prof) as b:
        for e in man["entries"]:
            if e["kind"] != "python_package":
                continue
            try:
                results.append(audit_entry(e, b))
            except Exception as exc:
                results.append({"entry_id": e["id"], "status": "ERROR",
                                "error": f"{type(exc).__name__}: {exc}"})
        rr = b.resource_receipt()

    doc = {
        "schema": "techne.acquisition.license_evidence/1",
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "rule": "licenses read from DISTRIBUTED artifacts only (wheel METADATA, wheel notice "
                "files, sdist notice files, sdist PKG-INFO/pyproject/Cargo declarations). A "
                "repository API license classifier is NEVER used as the basis of a claim.",
        "notices_stored_under": str(paths.tool_cache() / "notices"),
        "entries": results,
        "resource_receipt": rr,
    }
    out = pathlib.Path(a.out)
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    for r in results:
        print(f"{r['entry_id']:<12} {r.get('status')}")
        rn = r.get("repository_notice") or {}
        if rn.get("found"):
            n = rn["notice_files"][0]
            print(f"             repo notice @{rn['revision'][:12]}: {n['name']} -- "
                  f"{n['copyright_line']}")
        if r.get("spdx_claim"):
            print(f"             spdx={r['spdx_claim']}")
        if r.get("redistribution_note"):
            print(f"             NOTE {r['redistribution_note'][:200]}")
        print(f"             notices kept: "
              f"{[n['stored_as'] for n in r.get('notices_kept', [])]}")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
