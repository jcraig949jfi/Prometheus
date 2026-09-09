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
        out["redistribution_note"] = (
            "BLOCKER for redistributing any copy or derived artifact. The distributed "
            "wheel and sdist carry no license declaration and no notice file. Whatever a "
            "repository page or API classifier says, the artifact we hold grants nothing "
            "in writing. Internal use of the installed copy continues; exporting it, "
            "vendoring it, or shipping anything containing it does NOT, until a human "
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
