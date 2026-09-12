"""Fossil harvest CLI: acquire a body into the vault, run its recipe, write the receipt.

    python -m techne.fossils.harvest acquire <specimen_id>        fetch per record.source_origin, hash, extract
    python -m techne.fossils.harvest run <specimen_id>            execute recipe.json (build, run, tests) -> receipt
    python -m techne.fossils.harvest verify <specimen_id>         re-hash the body against UPSTREAM_HASHES.txt
    python -m techne.fossils.harvest status                       one line per specimen
    python -m techne.fossils.harvest summary                      the directive's success measures, computed

A RECIPE (techne/fossils/specimens/<id>/recipe.json) is the executable statement of "how to
run it": {"runner": "wsl"|"native"|"docker", "image": ..., "workdir": <relative to the body>,
"probe": [cmds that print toolchain versions], "build": [cmds], "runs": [{"name", "cmd",
"expect": {"exit": 0, "stdout_contains": [...], "stdout_regex": ...}}], "tests": [same shape],
"classification_if_ok": "RUNNABLE_NATIVE", "test_classification_if_ok": ...}. Commands run
in the body's workdir; a receipt records every command, exit status, timing, stdout/stderr
(head and tail; full text under <vault>/<id>/run/), the toolchain probe, and the sha256 of
every file the build produced. Nothing here alters upstream source: a recipe that needs a
patch names it under patches/ and the receipt lists the patch's own hash.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import platform
import re
import shlex
import subprocess
import sys
import time

from . import record, vault

MAX_CAPTURE = 4000


# --------------------------------------------------------------------------- runners
def _shell(runner: str, cmd: str, body: pathlib.Path, rel: str, image: str | None, timeout: int) -> dict:
    """Run `cmd` in <body>/<rel>. $HARNESS is the body's harness/ copy (Techne's smoke inputs),
    $BODY the body root, whatever the runner; the command text in the receipt is what ran."""
    t0 = time.time()
    if runner == "wsl":
        b = vault.to_wsl(body)
        pre = "export BODY=%s HARNESS=%s; cd %s && " % (shlex.quote(b), shlex.quote(b + "/harness"), shlex.quote(b + "/" + rel))
        full = ["wsl.exe", "-e", "bash", "-lc", pre + cmd]
    elif runner == "docker":
        pre = "export BODY=/w HARNESS=/w/harness; cd %s && " % shlex.quote("/w/" + rel)
        full = ["wsl.exe", "-e", "bash", "-lc",
                "docker run --rm -v %s:/w -w /w %s bash -lc %s" % (
                    shlex.quote(vault.to_wsl(body)), shlex.quote(image or "prometheus-fossil-c:bookworm"), shlex.quote(pre + cmd))]
    elif runner == "native":
        b = str(body).replace("\\", "/")
        pre = "export BODY=%s HARNESS=%s; cd %s && " % (shlex.quote(b), shlex.quote(b + "/harness"), shlex.quote(b + "/" + rel))
        full = ["bash", "-lc", pre + cmd]
    else:
        raise ValueError("unknown runner " + runner)
    try:
        p = subprocess.run(full, capture_output=True, text=True, timeout=timeout, errors="replace")
        rc, out, err = p.returncode, p.stdout or "", p.stderr or ""
    except subprocess.TimeoutExpired as e:
        so = e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        rc, out, err = -1, so, "TIMEOUT after %ss" % timeout
    return {"cmd": cmd, "runner": runner, "exit": rc, "seconds": round(time.time() - t0, 2),
            "stdout": out, "stderr": err}


def _clip(s: str) -> dict:
    if len(s) <= MAX_CAPTURE:
        return {"text": s}
    return {"head": s[:MAX_CAPTURE // 2], "tail": s[-MAX_CAPTURE // 2:], "bytes": len(s), "truncated": True}


def _expect_ok(res: dict, expect: dict | None) -> tuple[bool, list[str]]:
    expect = expect or {"exit": 0}
    why = []
    if "exit" in expect and res["exit"] != expect["exit"]:
        why.append("exit %s != expected %s" % (res["exit"], expect["exit"]))
    for s in expect.get("stdout_contains", []):
        if s not in res["stdout"]:
            why.append("stdout lacks %r" % s)
    for s in expect.get("stderr_contains", []):
        if s not in res["stderr"]:
            why.append("stderr lacks %r" % s)
    if expect.get("stdout_regex") and not re.search(expect["stdout_regex"], res["stdout"], re.S):
        why.append("stdout does not match /%s/" % expect["stdout_regex"])
    if expect.get("stdout_not_contains"):
        for s in expect["stdout_not_contains"]:
            if s in res["stdout"]:
                why.append("stdout unexpectedly contains %r" % s)
    return (not why), why


# --------------------------------------------------------------------------- acquire
def acquire(specimen_id: str) -> dict:
    rec = record.load(specimen_id)
    origin = rec["source_origin"]
    body = vault.body_dir(specimen_id)
    up = body / "upstream"
    up.mkdir(parents=True, exist_ok=True)
    out = {"specimen_id": specimen_id, "fetched": [], "body": str(body)}
    for art in origin.get("artifacts", []):
        kind = art["kind"]
        if kind == "url":
            dest = up / art["filename"]
            if dest.exists() and art.get("sha256") and vault.sha256_file(dest) == art["sha256"]:
                f = {"url": art["url"], "path": str(dest), "sha256": art["sha256"], "cached": True}
            else:
                f = vault.fetch_url(art["url"], dest)
                if art.get("sha256") and f["sha256"] != art["sha256"]:
                    raise RuntimeError("sha256 mismatch for %s: got %s expected %s" % (art["url"], f["sha256"], art["sha256"]))
            art["sha256"] = f["sha256"]
            art["bytes"] = dest.stat().st_size
            if art.get("extract", True) and dest.name.lower().endswith((".gz", ".tgz", ".zip", ".bz2", ".xz", ".tar")):
                root = vault.extract(dest, up / "tree")
                art["extracted_to"] = str(root.relative_to(body)).replace("\\", "/")
            out["fetched"].append(f)
        elif kind == "git":
            dest = up / "tree"
            g = vault.git_pin(art["url"], art["commit"], dest)
            art.update({"commit_resolved": g["commit"], "commit_date": g["commit_date"]})
            if art["commit"] == "HEAD":
                art["commit"] = g["commit"]          # the pin is exact from now on
            out["fetched"].append(g)
        else:
            raise ValueError("unknown artifact kind " + kind)
    # hash EVERYTHING under upstream/: the immutable archive(s) as fetched plus the extracted
    # tree plus any loose files, so one tree hash covers the whole body
    rows = vault.hash_tree(up)
    vault.write_hashes(specimen_id, rows)
    rec["hashes"] = {"tree_sha256": vault.tree_hash_of(rows), "n_files": len(rows),
                     "bytes": sum(r[2] for r in rows),
                     "artifacts": [{"filename": a.get("filename") or a.get("url"), "sha256": a.get("sha256"),
                                    "commit": a.get("commit_resolved")} for a in origin.get("artifacts", [])],
                     "body_location": str(body), "hash_list": "techne/fossils/specimens/%s/UPSTREAM_HASHES.txt" % specimen_id}
    rec["acquisition_date"] = time.strftime("%Y-%m-%d", time.gmtime())
    record.save(rec)
    out["tree_sha256"] = rec["hashes"]["tree_sha256"]
    out["n_files"] = len(rows)
    print(json.dumps({k: v for k, v in out.items() if k != "fetched"}, indent=1))
    return out


def verify(specimen_id: str) -> bool:
    body = vault.body_dir(specimen_id)
    rows = vault.hash_tree(body / "upstream")
    want = record.load(specimen_id)["hashes"].get("tree_sha256")
    got = vault.tree_hash_of(rows)
    print(specimen_id, "tree", got, "matches" if got == want else "DIFFERS FROM RECORD %s" % want)
    return got == want


# --------------------------------------------------------------------------- run
def run(specimen_id: str, timeout: int = 1800) -> dict:
    rec = record.load(specimen_id)
    sd = vault.specimen_dir(specimen_id)
    recipe = json.loads((sd / "recipe.json").read_text(encoding="utf-8"))
    body = vault.body_dir(specimen_id)
    rel = recipe.get("workdir", "upstream/tree")
    workdir = body / rel
    runner = recipe["runner"]
    # Techne's smoke inputs travel with the specimen (tracked) and are copied beside the body
    # so every runner sees them at $HARNESS; upstream/ is never written.
    if (sd / "harness").exists():
        import shutil
        if (body / "harness").exists():
            shutil.rmtree(body / "harness")
        shutil.copytree(sd / "harness", body / "harness")
    image = recipe.get("image")
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    rundir = body / "run" / ts
    rundir.mkdir(parents=True, exist_ok=True)
    receipt = {"schema": "techne.fossil.run_receipt/1", "specimen_id": specimen_id, "receipt_id": "run-%s-%s" % (specimen_id, ts),
               "written_utc": ts, "runner": runner, "image": image, "workdir": rel,
               "harness_sha256": {p.name: vault.sha256_file(p) for p in sorted((sd / "harness").glob("*")) if p.is_file()} if (sd / "harness").exists() else {},
               "host": {"platform": platform.platform(), "python": sys.version.split()[0]},
               "tree_sha256_before": rec["hashes"].get("tree_sha256"),
               "recipe_sha256": vault.sha256_file(sd / "recipe.json"),
               "patches": [], "probe": [], "build": [], "runs": [], "tests": [],
               "produced": [], "classification": None, "test_classification": None, "ok": None}
    for pth in sorted((sd / "patches").glob("*")) if (sd / "patches").exists() else []:
        if pth.is_file():
            receipt["patches"].append({"file": pth.name, "sha256": vault.sha256_file(pth)})

    def do(section, items):
        all_ok = True
        for it in items:
            cmd = it["cmd"] if isinstance(it, dict) else it
            res = _shell(runner, cmd, body, rel, image, it.get("timeout", timeout) if isinstance(it, dict) else timeout)
            ok, why = _expect_ok(res, it.get("expect") if isinstance(it, dict) else None)
            name = it.get("name", cmd[:40]) if isinstance(it, dict) else cmd[:40]
            (rundir / ("%s-%s.stdout.txt" % (section, re.sub(r"[^A-Za-z0-9_.-]+", "_", name)[:60]))).write_text(res["stdout"], encoding="utf-8", errors="replace")
            (rundir / ("%s-%s.stderr.txt" % (section, re.sub(r"[^A-Za-z0-9_.-]+", "_", name)[:60]))).write_text(res["stderr"], encoding="utf-8", errors="replace")
            receipt[section].append({"name": name, "cmd": cmd, "exit": res["exit"], "seconds": res["seconds"],
                                     "ok": ok, "why_not": why, "stdout": _clip(res["stdout"]), "stderr": _clip(res["stderr"])})
            print("%-6s %-40s exit=%-3s %6.1fs %s %s" % (section, name[:40], res["exit"], res["seconds"], "OK " if ok else "FAIL", "; ".join(why)), flush=True)
            all_ok = all_ok and ok
            if section == "build" and not ok and it.get("stop_on_fail", True) if isinstance(it, dict) else (section == "build" and not ok):
                return False
        return all_ok

    before = {r[0]: r[1] for r in vault.hash_tree(workdir)} if recipe.get("track_products", True) else {}
    do("probe", recipe.get("probe", []))
    built = do("build", recipe.get("build", []))
    ran = do("runs", recipe.get("runs", [])) if built else False
    tested = do("tests", recipe.get("tests", [])) if built and recipe.get("tests") else None
    if recipe.get("track_products", True):
        after = vault.hash_tree(workdir)
        receipt["produced"] = [{"path": rel, "sha256": h, "bytes": n} for rel, h, n in after
                               if before.get(rel) != h][:200]
    if built and ran:
        receipt["classification"] = recipe.get("classification_if_ok", "RUNNABLE_NATIVE")
    elif built:
        receipt["classification"] = recipe.get("classification_if_built_only", "BUILDS_BUT_NOT_RUN")
    else:
        receipt["classification"] = recipe.get("classification_if_build_fails", "BROKEN_UPSTREAM")
    if tested is None:
        receipt["test_classification"] = recipe.get("test_classification_if_none", "NO_TESTS")
    elif tested and recipe.get("test_classification_override"):
        receipt["test_classification"] = recipe["test_classification_override"]
    else:
        kind = recipe.get("test_kind", "UPSTREAM")
        receipt["test_classification"] = ("%s_PASS" if tested else "%s_FAIL") % ("UPSTREAM_TESTS" if kind == "UPSTREAM" else "TECHNE_SMOKE_HARNESS")
    receipt["ok"] = bool(built and ran and (tested is None or tested))
    rp = sd / "receipts" / (receipt["receipt_id"] + ".json")
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    rec["run_classification"] = receipt["classification"]
    rec["test_classification"] = receipt["test_classification"]
    rec["receipts"].append({"receipt": str(rp.relative_to(vault.REPO)).replace("\\", "/"), "ok": receipt["ok"],
                            "classification": receipt["classification"], "test_classification": receipt["test_classification"]})
    record.save(rec)
    print("RECEIPT", rp, receipt["classification"], receipt["test_classification"], "ok=%s" % receipt["ok"])
    return receipt


# --------------------------------------------------------------------------- status / summary
def _all_records():
    for p in sorted(vault.SPECIMENS.glob("*/record.json")):
        yield json.loads(p.read_text(encoding="utf-8"))


def status():
    for r in _all_records():
        print("%-28s %-6s %-22s %-24s %-26s %s" % (r["specimen_id"], r["era"][:6], r["run_classification"],
                                                   r["test_classification"], (r.get("language") or [""])[0][:26] if isinstance(r.get("language"), list) else r["language"], r["canonical_name"]))


def summary() -> dict:
    recs = list(_all_records())
    n = len(recs)
    def frac(pred):
        k = sum(1 for r in recs if pred(r))
        return "%d/%d" % (k, n)
    langs, eras, domains, lineages = set(), set(), set(), set()
    for r in recs:
        langs.update(r.get("language") or [])
        eras.add((r.get("era") or "")[:4])
        domains.update(r.get("domain") or [])
        lineages.add(r.get("lineage"))
    out = {
        "specimens": n,
        "unique_lineages": len(lineages),
        "era_coverage_decades": sorted({e[:3] + "0s" for e in eras if e}),
        "language_coverage": sorted(langs),
        "problem_pressure_domains": sorted(domains),
        "runnable": frac(lambda r: r["run_classification"].startswith("RUNNABLE")),
        "testable": frac(lambda r: r["test_classification"] in ("UPSTREAM_TESTS_PASS", "TECHNE_SMOKE_HARNESS_PASS")),
        "source_available": frac(lambda r: r["source_type"] in record.SOURCE_TYPES[:5]),
        "exact_version_pinned": frac(lambda r: bool(r.get("hashes", {}).get("tree_sha256"))),
        "historical_versions_preserved": sum(len(r.get("versions_preserved") or []) for r in recs),
        "executable_receipts": sum(1 for r in recs for x in r.get("receipts", []) if x.get("ok")),
        "provenance_complete": frac(lambda r: not record.validate(r)),
        "nyx_ready": frac(lambda r: r["run_classification"].startswith("RUNNABLE") and not record.validate(r)
                          and any(x.get("ok") for x in r.get("receipts", []))),
    }
    print(json.dumps(out, indent=2))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("acquire"); a.add_argument("specimen_id")
    r = sub.add_parser("run"); r.add_argument("specimen_id"); r.add_argument("--timeout", type=int, default=1800)
    v = sub.add_parser("verify"); v.add_argument("specimen_id")
    sub.add_parser("status"); sub.add_parser("summary")
    args = ap.parse_args(argv)
    if args.cmd == "acquire":
        acquire(args.specimen_id)
    elif args.cmd == "run":
        rc = run(args.specimen_id, args.timeout)
        return 0 if rc["ok"] else 1
    elif args.cmd == "verify":
        return 0 if verify(args.specimen_id) else 1
    elif args.cmd == "status":
        status()
    elif args.cmd == "summary":
        summary()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
