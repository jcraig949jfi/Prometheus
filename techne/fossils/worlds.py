"""World images on a second host: rebuild the preserved Dockerfiles and MEASURE how different
the rebuilt world is from the one the receipts ran in (batch 12 P8 done for real, 2026-09-16).

    python -m techne.fossils.worlds build [--only TAG ...] [--out F]
        every local world named in GHOST_WORLDS_<date>.json is rebuilt here from its preserved
        Dockerfile; one row per image: dockerfile sha256, FROM line, the base image's repo digest
        as resolved TODAY, the rebuilt image id beside the recorded one, the sorted dpkg manifest's
        sha256 and package count inside the image, seconds, BUILT / BUILD_FAILED (stderr tail).
    python -m techne.fossils.worlds probe-compare [--only SPECIMEN ...] [--out F]
        for every docker-runner specimen with a run receipt: its probe commands (the ones that
        print toolchain versions) are re-run in the rebuilt image, in a disposable copy of the body
        exactly as `harvest run` stages it, and compared
        to the latest receipt's probe stdout. PROBE_IDENTICAL / PROBE_DIFFERS (which commands, and
        the two outputs) / NO_PROBE_IN_RECEIPT / IMAGE_MISSING_HERE / BODY_MISSING_HERE.

The question both answer: "REBUILDABLE_NOT_BIT_EXACT" was a classification by inspection
(floating FROM tags, unpinned apt). This turns it into numbers: how many worlds rebuild at all
today, and, for the specimens, whether the toolchain the receipts saw is the toolchain a rebuild
gives. Censuses flush after every row.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import platform
import shlex
import subprocess
import time

from . import harvest, vault

GHOST = vault.REPO / "techne" / "fossils" / "GHOST_WORLDS_2026-09-13.json"
BUILD_SCHEMA = "techne.fossil.world_build_census/1"
PROBE_SCHEMA = "techne.fossil.world_probe_compare/1"


def _wsl(cmd: list[str], timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(["wsl.exe", "-e", "bash", "-lc", " ".join(shlex.quote(c) for c in cmd)],
                          capture_output=True, text=True, timeout=timeout, errors="replace")


def _docker(args: list[str], timeout: int = 600) -> subprocess.CompletedProcess:
    return _wsl(["docker", *args], timeout)


def docker_available() -> bool:
    try:
        return _docker(["info", "--format", "{{.ServerVersion}}"], 60).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def recorded_worlds() -> list[dict]:
    """The M1-side reference: every LOCAL_BUILD image, its Dockerfile and its image id then."""
    g = json.loads(GHOST.read_text(encoding="utf-8"))
    rows = g.get("images") or g.get("rows")
    rows = rows if isinstance(rows, list) else list(rows.values())
    return [r for r in rows if r.get("dockerfile")]


def _from_line(df: pathlib.Path) -> str:
    for line in df.read_text(encoding="utf-8").splitlines():
        if line.strip().upper().startswith("FROM "):
            return line.strip().split(None, 1)[1]
    return ""


def package_manifest(image: str) -> tuple[str | None, int]:
    """sha256 over the sorted `name=version` list of every dpkg package inside the image."""
    p = _docker(["run", "--rm", "--entrypoint", "sh", image, "-c",
                 "dpkg-query -W -f='${Package}=${Version}\\n' | sort"], 300)
    if p.returncode != 0:
        return None, 0
    lines = [ln for ln in p.stdout.splitlines() if ln.strip()]
    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest(), len(lines)


def build_world(row: dict, timeout: int = 3600) -> dict:
    tag = row["image"]
    df = vault.REPO / row["dockerfile"]
    ctx = df.parent
    out = {"image": tag, "dockerfile": row["dockerfile"], "dockerfile_sha256": vault.sha256_file(df) if df.exists() else None,
           "from": _from_line(df) if df.exists() else None, "base_repo_digest_today": None,
           "image_id_recorded": row.get("image_id"), "image_id_rebuilt": None, "same_image_id": None,
           "package_manifest_sha256": None, "n_packages": 0, "seconds": None, "status": None, "error_tail": None}
    t0 = time.time()
    if not df.exists():
        out["status"] = "DOCKERFILE_MISSING"
        return out
    try:
        p = _docker(["build", "--pull", "-t", tag, "-f", vault.to_wsl(df), vault.to_wsl(ctx)], timeout)
    except subprocess.TimeoutExpired:
        out.update(status="BUILD_TIMEOUT", seconds=round(time.time() - t0, 1), error_tail="TIMEOUT after %ss" % timeout)
        return out
    out["seconds"] = round(time.time() - t0, 1)
    if p.returncode != 0:
        out.update(status="BUILD_FAILED", error_tail=(p.stderr or p.stdout)[-1500:])
        return out
    ins = _docker(["image", "inspect", tag, "--format", "{{.Id}}"], 60)
    out["image_id_rebuilt"] = ins.stdout.strip() or None
    rec = out["image_id_recorded"] or ""
    out["same_image_id"] = bool(rec) and (out["image_id_rebuilt"] or "").startswith(rec)
    if out["from"]:
        base = out["from"].split()[0]
        bi = _docker(["image", "inspect", base, "--format", "{{join .RepoDigests \",\"}}"], 60)
        out["base_repo_digest_today"] = bi.stdout.strip() or None
    out["package_manifest_sha256"], out["n_packages"] = package_manifest(tag)
    out["status"] = "BUILT"
    return out


def build_census(only=None, out=None, timeout: int = 3600) -> dict:
    worlds = [w for w in recorded_worlds() if not only or w["image"] in only]
    census = {"schema": BUILD_SCHEMA, "written_utc": None, "host": platform.node(),
              "docker": _docker(["version", "--format", "{{.Server.Version}}"], 60).stdout.strip(),
              "reference": GHOST.name, "n": len(worlds), "complete": False, "counts": {}, "rows": []}

    def flush():
        census["written_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        c = {}
        for r in census["rows"]:
            c[r["status"]] = c.get(r["status"], 0) + 1
        census["counts"] = c
        census["same_image_id"] = sum(1 for r in census["rows"] if r.get("same_image_id"))
        if out:
            pathlib.Path(out).write_text(json.dumps(census, indent=1) + "\n", encoding="utf-8", newline="\n")

    for w in worlds:
        r = build_world(w, timeout=timeout)
        census["rows"].append(r)
        flush()
        print("%-36s %-14s %7ss  id %s (recorded %s)  pkgs %d" % (
            r["image"], r["status"], r["seconds"], (r["image_id_rebuilt"] or "-")[7:19], (r["image_id_recorded"] or "-")[7:19], r["n_packages"]), flush=True)
    census["complete"] = True
    flush()
    print("WORLD-BUILD", census["n"], json.dumps(census["counts"], sort_keys=True), "same_image_id", census["same_image_id"])
    return census


# --------------------------------------------------------------------------- probe compare
def _norm(s: str) -> str:
    return "\n".join(ln.rstrip() for ln in (s or "").strip().splitlines())


def _receipt_probe_text(entry: dict) -> str | None:
    so = entry.get("stdout") or {}
    if "text" in so:
        return so["text"]
    if "head" in so:
        return None  # truncated in the receipt: not comparable
    return ""


def latest_run_receipt(specimen_id: str) -> dict | None:
    rd = vault.specimen_dir(specimen_id) / "receipts"
    files = sorted(rd.glob("run-*.json")) if rd.exists() else []
    for rp in reversed(files):
        r = json.loads(rp.read_text(encoding="utf-8"))
        if r.get("runner") == "docker" and not r.get("world_override_image"):
            try:
                r["_path"] = str(rp.relative_to(vault.REPO)).replace("\\", "/")
            except ValueError:
                r["_path"] = str(rp).replace("\\", "/")
            return r
    return None


def probe_compare_one(specimen_id: str, timeout: int = 300) -> dict:
    sd = vault.specimen_dir(specimen_id)
    recipe = json.loads((sd / "recipe.json").read_text(encoding="utf-8"))
    row = {"specimen_id": specimen_id, "image": recipe.get("image") or "prometheus-fossil-c:bookworm",
           "receipt": None, "n_probes": 0, "identical": 0, "differs": [], "status": None}
    rcpt = latest_run_receipt(specimen_id)
    if not rcpt or not rcpt.get("probe"):
        row["status"] = "NO_PROBE_IN_RECEIPT"
        return row
    row["receipt"] = rcpt["_path"]
    body = vault.body_dir(specimen_id)
    if not (body / "upstream").exists():
        row["status"] = "BODY_MISSING_HERE"
        return row
    if _docker(["image", "inspect", row["image"], "--format", "{{.Id}}"], 60).returncode != 0:
        row["status"] = "IMAGE_MISSING_HERE"
        return row
    rel = recipe.get("workdir", "upstream/tree")
    # the receipts ran in a disposable copy (upstream/ + harness/ + an empty build/); a recipe
    # whose workdir is build/ cannot cd in the raw body, and `cd X && first; rest` then skips
    # exactly the first probe command (found on bsd-4.3's simh probe). Stage the same copy.
    exec_body = harvest._stage_work(body, sd)
    for entry in rcpt["probe"]:
        then = _receipt_probe_text(entry)
        if then is None:
            row["differs"].append({"cmd": entry["cmd"], "reason": "receipt output truncated; not comparable"})
            continue
        now = harvest._shell("docker", entry["cmd"], exec_body, rel, row["image"], timeout)
        row["n_probes"] += 1
        if _norm(now["stdout"]) == _norm(then):
            row["identical"] += 1
        else:
            row["differs"].append({"cmd": entry["cmd"], "then": _norm(then)[:400], "now": _norm(now["stdout"])[:400],
                                   "exit_then": entry.get("exit"), "exit_now": now["exit"]})
    row["status"] = "PROBE_IDENTICAL" if row["n_probes"] and not row["differs"] else "PROBE_DIFFERS"
    return row


def probe_compare(only=None, out=None, timeout: int = 300) -> dict:
    ids = sorted(p.parent.name for p in vault.SPECIMENS.glob("*/recipe.json")
                 if json.loads(p.read_text(encoding="utf-8")).get("runner") == "docker")
    if only:
        ids = [i for i in ids if i in only]
    census = {"schema": PROBE_SCHEMA, "written_utc": None, "host": platform.node(), "n": len(ids),
              "complete": False, "counts": {}, "rows": []}

    def flush():
        census["written_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        c = {}
        for r in census["rows"]:
            c[r["status"]] = c.get(r["status"], 0) + 1
        census["counts"] = c
        if out:
            pathlib.Path(out).write_text(json.dumps(census, indent=1) + "\n", encoding="utf-8", newline="\n")

    for sid in ids:
        r = probe_compare_one(sid, timeout=timeout)
        census["rows"].append(r)
        flush()
        print("%-36s %-20s %d/%d %s" % (sid, r["status"], r["identical"], r["n_probes"],
                                        "; ".join(d["cmd"][:30] for d in r["differs"])[:60]), flush=True)
    census["complete"] = True
    flush()
    print("PROBE-COMPARE", census["n"], json.dumps(census["counts"], sort_keys=True))
    return census


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("--only", action="append"); b.add_argument("--out"); b.add_argument("--timeout", type=int, default=3600)
    pc = sub.add_parser("probe-compare"); pc.add_argument("--only", action="append"); pc.add_argument("--out"); pc.add_argument("--timeout", type=int, default=300)
    a = ap.parse_args(argv)
    if not docker_available():
        print("docker is not available through WSL on this host")
        return 2
    if a.cmd == "build":
        c = build_census(a.only, a.out, a.timeout)
        return 0 if c["counts"].get("BUILT", 0) == c["n"] else 1
    c = probe_compare(a.only, a.out, a.timeout)
    return 0 if c["counts"].get("PROBE_IDENTICAL", 0) == c["n"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
