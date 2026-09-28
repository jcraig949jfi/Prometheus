"""Draw holdout D2's FRESH hidden set ONCE and seal it opaquely.

  COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D2.draw

Same family and lattice as holdout D (prometheus/cosmos/c3_holdout_D/medium.py, UNCHANGED, imported).
A new 256-bit nonce from the OS CSPRNG (secrets) seeds the world rng exactly as holdout D's seal did
(numpy default_rng(int(nonce,16) mod 2^128)); worlds come from medium.draw_worlds' per-knob-uniform
lattice rule, and additionally any draw EQUAL to a world of the exposed original D set is rejected and
redrawn (so no D2 world was ever public). Then N_WORLDS run seeds are drawn from the same rng.

Writes SECRET material ONLY under SECRETS_DIR (outside every git repo, machine M1):
  hidden_D2.plain.json   canonical plaintext bytes (the committed object)
  hidden_D2.salt.hex     32-byte commitment salt (secret until reveal)
  hidden_D2.key.hex      32-byte AES-256-GCM key (never leaves M1 before reveal)
Writes PUBLIC material into this package directory:
  hidden_D2.enc          AES-256-GCM ciphertext (+tag) of the plaintext bytes
  MANIFEST_D2.json       public manifest (IV, sha256(ciphertext), salted commitment, versions, spec_id)
Prints hashes and counts only.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import platform
import secrets
import sys
from pathlib import Path

if os.environ.get("COSMOS_BROKER") != "1":
    raise ImportError("holdout D2 draw: set COSMOS_BROKER=1 (broker only)")

import cryptography
import numpy as np

from prometheus.cosmos.c3_holdout_D import medium
from prometheus.cosmos.c3_holdout_D2 import sealbox

HERE = Path(__file__).resolve().parent
D_DIR = HERE.parent / "c3_holdout_D"
SECRETS_DIR = Path("C:/Users/jcrai/nestor_secrets/holdout_D2")
N_WORLDS = 128
PLAIN_NAME, SALT_NAME, KEY_NAME = "hidden_D2.plain.json", "hidden_D2.salt.hex", "hidden_D2.key.hex"
ENC_NAME, MANIFEST_NAME = "hidden_D2.enc", "MANIFEST_D2.json"
PLAINTEXT_FORMAT = "c3-holdout-D2-hidden/1"
MANIFEST_FORMAT = "c3-holdout-D2-manifest/1"


def inside_git_repo(path: Path) -> bool:
    p = Path(path).resolve()
    for q in [p] + list(p.parents):
        if (q / ".git").exists():
            return True
    return False


def exposed_d_worlds() -> set:
    spec = json.loads((D_DIR / "sealed_spec_D.json").read_text(encoding="utf-8"))
    return {sealbox.canon_bytes(medium.world_from_dict(w).as_dict()) for w in spec["worlds"]}


def draw_hidden(nonce_hex: str, n: int, exclude: set) -> tuple:
    rng = np.random.default_rng(int(nonce_hex, 16) % (2 ** 128))
    worlds, rejected = [], 0
    while len(worlds) < n:
        w = medium.draw_worlds(1, rng)[0]
        if sealbox.canon_bytes(w.as_dict()) in exclude:
            rejected += 1
            continue
        worlds.append(w.as_dict())
    run_seeds = [int(x) for x in rng.integers(0, 2 ** 31 - 1, n)]
    return worlds, run_seeds, rejected


def build_plaintext(worlds, run_seeds, nonce_hex, draw_utc, rejected, family_sha) -> bytes:
    obj = {
        "format": PLAINTEXT_FORMAT, "family": medium.FAMILY_NAME, "family_version": medium.FAMILY_VERSION,
        "family_src_sha256": family_sha, "nonce": nonce_hex,
        "nonce_source": "secrets.token_hex(32); world rng = numpy default_rng(int(nonce,16) mod 2^128); "
                        "worlds via medium.draw_worlds(1, rng) repeated, rejecting any world equal to an exposed "
                        "holdout-D world; then run_seeds = rng.integers(0, 2^31-1, n)",
        "n_worlds": len(worlds), "worlds": worlds, "run_seeds": run_seeds,
        "rejected_equal_to_exposed_D": rejected, "draw_utc": draw_utc,
        "lattice": {k: list(v) for k, v in medium.LATTICE.items()},
    }
    for w in worlds:                                     # every world validates and lies in the lattice
        assert medium.in_lattice(medium.world_from_dict(w))
    return sealbox.canon_bytes(obj)


def _write_excl(path: Path, data: bytes) -> None:
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(data)


def seal(plaintext: bytes, secrets_dir: Path, public_dir: Path, draw_utc: str, n_worlds: int,
         family_sha: str, key: bytes = None, salt: bytes = None, iv: bytes = None) -> dict:
    """Encrypt + commit. Secret files -> secrets_dir (must be outside git); public files -> public_dir."""
    secrets_dir, public_dir = Path(secrets_dir), Path(public_dir)
    if inside_git_repo(secrets_dir):
        raise SystemExit("refusing: secrets_dir is inside a git repository")
    key = key or sealbox.new_key()
    salt = salt or sealbox.new_salt()
    iv = iv or sealbox.new_iv()
    ct = sealbox.encrypt(key, iv, plaintext, family_sha)
    assert sealbox.decrypt(key, iv, ct, family_sha) == plaintext
    secrets_dir.mkdir(parents=True, exist_ok=True)
    _write_excl(secrets_dir / PLAIN_NAME, plaintext)
    _write_excl(secrets_dir / SALT_NAME, salt.hex().encode("ascii"))
    _write_excl(secrets_dir / KEY_NAME, key.hex().encode("ascii"))
    _write_excl(public_dir / ENC_NAME, ct)
    manifest = {
        "format": MANIFEST_FORMAT,
        "family": medium.FAMILY_NAME, "family_version": medium.FAMILY_VERSION,
        "family_module": "prometheus/cosmos/c3_holdout_D/medium.py",
        "family_src_sha256": family_sha,
        "family_code_statement": "D2 reuses the UNCHANGED holdout-D family code (medium.py, same knobs, "
                                 "lattice, build/intervene); only the hidden evaluation set is new.",
        "predecessor_sealed_spec_sha256": sealbox.sha256_file(D_DIR / "sealed_spec_D.json"),
        "predecessor_status": "holdout D's original hidden set is EXPOSED (plaintext on main); never reuse it blind",
        "n_worlds": n_worlds, "n_run_seeds": n_worlds,
        "draw_rule": "lattice worlds, per-knob uniform with rejection on x_in+d_patch+w_patch<=L "
                     "(medium.draw_worlds), plus rejection of any world equal to an exposed holdout-D world; "
                     "fresh 256-bit secrets nonce",
        "cipher": sealbox.CIPHER_NAME,
        "iv_hex": iv.hex(),
        "aad": (sealbox.AAD_PREFIX.decode("ascii") + "<family_src_sha256>"),
        "ciphertext_file": ENC_NAME, "ciphertext_bytes": len(ct),
        "ciphertext_sha256": sealbox.sha256_hex(ct),
        "commitment_scheme": "sha256(salt || plaintext_bytes); salt = 32 random bytes (secret until reveal); "
                             "plaintext_bytes = canonical JSON (sort_keys, separators (',',':'), ascii)",
        "commitment": sealbox.commitment(salt, plaintext),
        "plaintext_format": PLAINTEXT_FORMAT,
        "d2_src_sha256_at_draw": {f: sealbox.src_sha_lf(HERE / f) for f in ("__init__.py", "sealbox.py", "draw.py")},
        "src_sha_convention": "sha256 of file bytes with CRLF normalised to LF",
        "secret_material": "plaintext, salt and key exist only on machine M1 (SKULLPORT), in a directory under "
                           "the operator user profile that is outside every git repository; held by Nestor",
        "author": "Nestor (delegate), machine M1 SKULLPORT",
        "python": sys.version, "numpy": np.__version__, "cryptography": cryptography.__version__,
        "platform": platform.platform(), "draw_utc": draw_utc,
    }
    manifest["spec_id"] = sealbox.manifest_spec_id(manifest)
    _write_excl(public_dir / MANIFEST_NAME,
                (json.dumps(manifest, indent=1, sort_keys=True) + "\n").encode("utf-8"))
    return manifest


def main() -> dict:
    for p in (SECRETS_DIR / PLAIN_NAME, SECRETS_DIR / KEY_NAME, HERE / ENC_NAME, HERE / MANIFEST_NAME):
        if p.exists():
            raise SystemExit("D2 already drawn (%s exists); drawing is once-only" % p.name)
    family_sha = sealbox.src_sha_lf(D_DIR / "medium.py")
    nonce = secrets.token_hex(32)
    draw_utc = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    worlds, seeds, rejected = draw_hidden(nonce, N_WORLDS, exposed_d_worlds())
    plaintext = build_plaintext(worlds, seeds, nonce, draw_utc, rejected, family_sha)
    del worlds, seeds, nonce
    m = seal(plaintext, SECRETS_DIR, HERE, draw_utc, N_WORLDS, family_sha)
    print(json.dumps({"n_worlds": m["n_worlds"], "commitment": m["commitment"],
                      "ciphertext_sha256": m["ciphertext_sha256"], "spec_id": m["spec_id"],
                      "manifest_sha256": sealbox.sha256_file(HERE / MANIFEST_NAME)}, indent=1))
    return m


if __name__ == "__main__":
    main()
