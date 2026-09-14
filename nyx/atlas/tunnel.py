"""The behavioural wind tunnel: run a fossil fragment (or the fossil) under an intervention and keep the receipt.

Bodies stay Techne's and are never edited. An experiment copies what it needs from the body into a host-local work
area (F:/Prometheus/vault/nyx_atlas/<fossil>/<experiment>/, gitignored like the vault), applies the intervention
THERE (a patch, an env var, an input permutation), runs in the same docker image Techne's recipe names (via WSL, as
techne.fossils.harvest does), and writes a tracked receipt to nyx/atlas/fingerprints/<fossil>/<experiment>.json
with the exact commands, exit codes, clipped stdout/stderr and the hashes of every file the intervention touched.

A receipt is evidence of what ran; the fingerprint values are computed by the experiment script from the receipts
and written beside them. Nothing here interprets.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import shlex
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional

from nyx.atlas.schema import ROOT, SCHEMA

VAULT = Path("F:/Prometheus/vault/fossils")
WORK = Path("F:/Prometheus/vault/nyx_atlas")
MAX = 6000


def to_wsl(p: Path) -> str:
    p = Path(p).resolve()
    return "/mnt/%s/%s" % (p.drive.rstrip(":").lower(), "/".join(p.parts[1:]))


def _clip(s: str) -> dict:
    return {"text": s} if len(s) <= MAX else {"head": s[:MAX // 2], "tail": s[-MAX // 2:], "bytes": len(s), "truncated": True}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class Experiment:
    def __init__(self, fossil_id: str, name: str, image: Optional[str] = None, runner: str = "docker", note: str = ""):
        self.fossil_id, self.name, self.image, self.runner = fossil_id, name, image, runner
        self.work = WORK / fossil_id / name
        self.work.mkdir(parents=True, exist_ok=True)
        self.receipt = {"schema": SCHEMA + "/receipt", "fossil": fossil_id, "experiment": name, "runner": runner, "image": image,
                        "started_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "note": note,
                        "copied": [], "interventions": [], "runs": []}

    # ---- staging
    def copy_from_body(self, rel: str, dest: str = "") -> Path:
        src = VAULT / self.fossil_id / rel
        dst = self.work / (dest or Path(rel).name)
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            self.receipt["copied"].append({"from": str(src), "to": str(dst), "kind": "dir"})
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            self.receipt["copied"].append({"from": str(src), "to": str(dst), "sha256": sha(dst)})
        return dst

    def write(self, rel: str, text: str, intervention: str = "") -> Path:
        p = self.work / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        before = sha(p) if p.exists() else None
        p.write_text(text, encoding="utf-8", newline="\n")
        self.receipt["interventions"].append({"file": rel, "sha256_before": before, "sha256_after": sha(p), "what": intervention})
        return p

    def patch(self, rel: str, old: str, new: str, intervention: str) -> None:
        p = self.work / rel
        t = p.read_text(encoding="utf-8")
        if t.count(old) != 1:
            raise ValueError(f"patch anchor occurs {t.count(old)} times in {rel}")
        self.write(rel, t.replace(old, new), intervention=f"{intervention} [replace {old!r} -> {new!r}]")

    # ---- running
    def run(self, name: str, cmd: str, cwd: str = "", timeout: int = 600, env: Optional[Dict[str, str]] = None) -> dict:
        t0 = time.time()
        envs = " ".join(f"export {k}={shlex.quote(v)};" for k, v in (env or {}).items())
        if self.runner == "docker":
            inner = f"{envs} cd {shlex.quote('/w/' + cwd) if cwd else '/w'} && {cmd}"
            full = ["wsl.exe", "-d", "Ubuntu", "-e", "bash", "-lc",
                    "docker run --rm -v %s:/w -w /w %s bash -lc %s" % (shlex.quote(to_wsl(self.work)), shlex.quote(self.image or "prometheus-fossil-c:bookworm"), shlex.quote(inner))]
        elif self.runner == "wsl":
            w = to_wsl(self.work)
            full = ["wsl.exe", "-d", "Ubuntu", "-e", "bash", "-lc", f"{envs} cd {shlex.quote(w + '/' + cwd if cwd else w)} && {cmd}"]
        else:  # native windows shell (python fossils)
            full = ["bash", "-lc", f"{envs} cd {shlex.quote(str(self.work / cwd).replace(chr(92), '/'))} && {cmd}"]
        try:
            p = subprocess.run(full, capture_output=True, text=True, timeout=timeout, errors="replace")
            rc, out, err = p.returncode, p.stdout or "", p.stderr or ""
        except subprocess.TimeoutExpired as e:
            rc, out, err = -1, (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or ""), f"TIMEOUT after {timeout}s"
        rec = {"name": name, "cmd": cmd, "cwd": cwd, "exit": rc, "seconds": round(time.time() - t0, 2), "stdout": _clip(out), "stderr": _clip(err)}
        self.receipt["runs"].append(rec)
        print(f"[{self.fossil_id}/{self.name}] {name}: exit {rc} in {rec['seconds']}s")
        return {"exit": rc, "stdout": out, "stderr": err}

    # ---- receipts
    def save(self, fingerprint: Optional[dict] = None, controls: Optional[List[dict]] = None) -> Path:
        self.receipt["finished_utc"] = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if fingerprint is not None:
            self.receipt["fingerprint"] = fingerprint
        if controls is not None:
            self.receipt["controls"] = controls
        out = ROOT / "fingerprints" / self.fossil_id / f"{self.name}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(self.receipt, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("receipt", out)
        return out
