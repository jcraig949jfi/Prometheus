"""Firewall check for holdout D2 (run by the key holder on M1; prints booleans and counts ONLY).

  python -m prometheus.cosmos.c3_holdout_D2.firewall_check [--secrets DIR] [--scan ROOT ...] [--git-ref REF ...]

Loads the secret material from the secrets directory and searches every scan root (working-tree files,
.git directories skipped) and every given git ref's tree (git grep, patterns passed via a file inside
the secrets directory, never on the command line) for:
  key hex, salt hex, nonce hex, the canonical JSON of any hidden world, a file whose sha256 equals the
  plaintext's, and files holding >= 4 of the hidden run seeds as decimal tokens.
Also: secrets dir outside every git repo, running host name, and that the only files in the secrets dir
are the expected three (+ this check's pattern file while it runs).
Nothing secret is printed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
from pathlib import Path

DEFAULT_SECRETS = Path("C:/Users/jcrai/nestor_secrets/holdout_D2")
EXPECTED = {"hidden_D2.plain.json", "hidden_D2.salt.hex", "hidden_D2.key.hex"}
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
MAX_BYTES = 64 << 20
NUM = re.compile(rb"(?<![0-9])[0-9]{5,10}(?![0-9])")


def inside_git_repo(path: Path) -> bool:
    p = Path(path).resolve()
    return any((q / ".git").exists() for q in [p] + list(p.parents))


def load(secrets_dir: Path) -> dict:
    plain = (secrets_dir / "hidden_D2.plain.json").read_bytes()
    obj = json.loads(plain)
    worlds = [json.dumps(w, sort_keys=True, separators=(",", ":")).encode() for w in obj["worlds"]]
    return {"plain_sha": hashlib.sha256(plain).hexdigest(),
            "strings": {"key": (secrets_dir / "hidden_D2.key.hex").read_bytes().strip(),
                        "salt": (secrets_dir / "hidden_D2.salt.hex").read_bytes().strip(),
                        "nonce": obj["nonce"].encode()},
            "worlds": worlds, "seeds": {str(s).encode() for s in obj["run_seeds"]}}


def scan_tree(root: Path, sec: dict) -> dict:
    hits = {k: 0 for k in ("key", "salt", "nonce", "world_json", "plaintext_file", "seed_cluster")}
    n_files = 0
    lowered = {k: v.lower() for k, v in sec["strings"].items()}
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            p = Path(dp) / fn
            try:
                if p.stat().st_size > MAX_BYTES:
                    continue
                b = p.read_bytes()
            except OSError:
                continue
            n_files += 1
            bl = b.lower()
            for k, v in lowered.items():
                if v in bl:
                    hits[k] += 1
            if any(w in b for w in sec["worlds"]):
                hits["world_json"] += 1
            if hashlib.sha256(b).hexdigest() == sec["plain_sha"]:
                hits["plaintext_file"] += 1
            if len(set(NUM.findall(b)) & sec["seeds"]) >= 4:
                hits["seed_cluster"] += 1
    return {"files_scanned": n_files, "hits": hits, "clean": not any(hits.values())}


def git_grep(repo: Path, ref: str, pattern_file: Path) -> dict:
    r = subprocess.run(["git", "-C", str(repo), "grep", "-l", "-F", "-i", "-f", str(pattern_file), ref],
                       capture_output=True)
    n = len([l for l in r.stdout.splitlines() if l.strip()])
    return {"ref": ref, "git_rc": r.returncode, "files_matching": n, "clean": r.returncode == 1 and n == 0}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--secrets", default=str(DEFAULT_SECRETS))
    ap.add_argument("--scan", nargs="*", default=[str(Path(__file__).resolve().parents[3])])
    ap.add_argument("--git-ref", nargs="*", default=["HEAD", "origin/main"])
    a = ap.parse_args(argv)
    sd = Path(a.secrets)
    sec = load(sd)
    out = {"host": socket.gethostname(), "secrets_dir_outside_git": not inside_git_repo(sd),
           "secrets_dir_files_expected": set(os.listdir(sd)) == EXPECTED, "scans": {}, "git": []}
    for root in a.scan:
        out["scans"][root] = scan_tree(Path(root), sec)
    pf = sd / "_grep_patterns.tmp"
    pats = [v.decode() for v in sec["strings"].values()] + [w.decode() for w in sec["worlds"]]
    pf.write_text("\n".join(pats) + "\n", encoding="ascii")
    try:
        for ref in a.git_ref:
            out["git"].append(git_grep(Path(a.scan[0]), ref, pf))
    finally:
        pf.unlink()
    out["all_clean"] = bool(out["secrets_dir_outside_git"] and out["secrets_dir_files_expected"]
                            and all(s["clean"] for s in out["scans"].values())
                            and all(g["clean"] for g in out["git"]))
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0 if out["all_clean"] else 1


if __name__ == "__main__":
    sys.exit(main())
