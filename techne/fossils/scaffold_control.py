"""The rejected-scaffolding control (Amendment 2 R18; TECHNE-89/90, 2026-09-16).

Every build accommodation in a recipe -- -std=..., -fcommon, -fpermissive, -w, -Wno-*, -include
X, CFLAGS=... -- is a scaffolding transformation whose NECESSITY is unmeasured until the build is
tried WITHOUT it. gzip's flags turned out unnecessary (TECHNE-90). This module measures that for
every docker-runner recipe:

    python -m techne.fossils.scaffold_control <id> [--dry-run]
    python -m techne.fossils.scaffold_control --all [--out F]

For each specimen: strip the ACCOMMODATION tokens from the recipe's build commands (the world,
-O levels, -I/-L paths, -l libs, harness paths and -m32 are NOT accommodations and stay), run the
stripped build in the world on a disposable copy, then the recipe's runs. Verdict per specimen:

    NO_ACCOMMODATIONS   nothing to strip
    NOT_REQUIRED        stripped build succeeds and every run passes -> the flags are decorative
    REQUIRED            stripped build fails, or builds but a run fails -> the flags are real scaffolding
    UNDECIDED           the recipe's own build fails too (world drift; nothing can be said)

Nothing tracked is written; the rows go to the census and to the packet author. The recipe is
NOT edited here -- removing a decorative accommodation is a separate, recorded act (C9).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import platform
import re
import time

from . import harvest, vault

SCHEMA = "techne.fossil.scaffold_control/1"
ACCOM = re.compile(r"""
    (?:^|(?<=\s))(?:
      -std=[\w+]+ | --std=[\w+]+ | -fcommon | -fpermissive | -fno-common | -w | -Wno-[\w=-]+ |
      -include\s+\S+ | -D_?(?:GNU_SOURCE|DEFAULT_SOURCE|BSD_SOURCE)\b | ADDONS=\S+
    )(?=\s|$|['"])""", re.X)
CFLAGS_VAR = re.compile(r"""(CFLAGS|CXXFLAGS|FFLAGS)=(?:'([^']*)'|"([^"]*)"|(\S+))""")


def strip_accommodations(cmd: str) -> tuple[str, list[str]]:
    removed = []

    def _var(m):
        var = m.group(1)
        inner = m.group(2) if m.group(2) is not None else (m.group(3) if m.group(3) is not None else m.group(4))
        kept = ACCOM.sub(lambda mm: removed.append(mm.group(0).strip()) or " ", inner)
        kept = re.sub(r"\s+", " ", kept).strip()
        return "%s='%s'" % (var, kept) if kept else ""

    out = CFLAGS_VAR.sub(_var, cmd)
    out = ACCOM.sub(lambda mm: removed.append(mm.group(0).strip()) or " ", out)
    out = re.sub(r"[ \t]+", " ", out)
    return out, [r for r in removed if r]


def control(specimen_id: str, timeout: int = 900, dry_run: bool = False) -> dict:
    sd = vault.specimen_dir(specimen_id)
    recipe = json.loads((sd / "recipe.json").read_text(encoding="utf-8"))
    row = {"specimen_id": specimen_id, "image": recipe.get("image"), "removed": [], "stripped_build": [],
           "verdict": None, "recipe_build_ok": None, "stripped_build_ok": None, "runs_ok": None, "runs_failed": [], "seconds": None}
    if recipe.get("runner") != "docker":
        row["verdict"] = "NOT_DOCKER"
        return row
    builds = [(b["cmd"] if isinstance(b, dict) else b) for b in recipe.get("build", [])]
    stripped, removed = [], []
    for c in builds:
        s, r = strip_accommodations(c)
        stripped.append(s); removed += r
    row["removed"], row["stripped_build"] = removed, stripped
    if not removed:
        row["verdict"] = "NO_ACCOMMODATIONS"
        return row
    if dry_run:
        row["verdict"] = "DRY_RUN"
        return row
    t0 = time.time()
    body = vault.body_dir(specimen_id)
    if not (body / "upstream").exists():
        row["verdict"] = "BODY_MISSING_HERE"
        return row
    rel = recipe.get("workdir", "upstream/tree")
    image = recipe.get("image")
    # 1. the recipe's own build, so a world that no longer builds anything is UNDECIDED not REQUIRED
    work = harvest._stage_work(body, sd)
    ok = True
    for c in builds:
        res = harvest._shell("docker", c, work, rel, image, timeout)
        ok = ok and res["exit"] == 0
    row["recipe_build_ok"] = ok
    if not ok:
        row["verdict"] = "UNDECIDED"
        row["seconds"] = round(time.time() - t0, 1)
        return row
    # 2. the stripped build on a fresh copy, then the runs
    work = harvest._stage_work(body, sd)
    ok = True
    for c in stripped:
        res = harvest._shell("docker", c, work, rel, image, timeout)
        ok = ok and res["exit"] == 0
        if not ok:
            row["stripped_build_error"] = (res["stderr"] or res["stdout"])[-600:]
            break
    row["stripped_build_ok"] = ok
    if ok:
        runs_ok = True
        for it in recipe.get("runs", []):
            cmd = it["cmd"] if isinstance(it, dict) else it
            res = harvest._shell("docker", cmd, work, rel, image, it.get("timeout", timeout) if isinstance(it, dict) else timeout)
            good, why = harvest._expect_ok(res, it.get("expect") if isinstance(it, dict) else None)
            if not good:
                runs_ok = False
                row["runs_failed"].append({"name": it.get("name", cmd[:40]) if isinstance(it, dict) else cmd[:40], "why": why})
        row["runs_ok"] = runs_ok
        row["verdict"] = "NOT_REQUIRED" if runs_ok else "REQUIRED"
    else:
        row["verdict"] = "REQUIRED"
    row["seconds"] = round(time.time() - t0, 1)
    return row


def census(out=None, only=None, timeout: int = 900, dry_run: bool = False) -> dict:
    ids = sorted(p.parent.name for p in vault.SPECIMENS.glob("*/recipe.json"))
    if only:
        ids = [i for i in ids if i in only]
    c = {"schema": SCHEMA, "written_utc": None, "host": platform.node(), "n": len(ids), "complete": False, "counts": {}, "rows": []}

    def flush():
        c["written_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        cc = {}
        for r in c["rows"]:
            cc[r["verdict"]] = cc.get(r["verdict"], 0) + 1
        c["counts"] = cc
        if out:
            pathlib.Path(out).write_text(json.dumps(c, indent=1) + "\n", encoding="utf-8", newline="\n")

    for sid in ids:
        r = control(sid, timeout=timeout, dry_run=dry_run)
        c["rows"].append(r)
        flush()
        if r["verdict"] not in ("NOT_DOCKER", "NO_ACCOMMODATIONS"):
            print("%-36s %-18s removed=%s %s" % (sid, r["verdict"], r["removed"], r.get("seconds", "")), flush=True)
    c["complete"] = True
    flush()
    print("SCAFFOLD-CONTROL", c["n"], json.dumps(c["counts"], sort_keys=True))
    return c


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("specimen_id", nargs="?"); ap.add_argument("--all", action="store_true")
    ap.add_argument("--out"); ap.add_argument("--timeout", type=int, default=900); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if a.all or not a.specimen_id:
        census(a.out, timeout=a.timeout, dry_run=a.dry_run)
        return 0
    print(json.dumps(control(a.specimen_id, timeout=a.timeout, dry_run=a.dry_run), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
