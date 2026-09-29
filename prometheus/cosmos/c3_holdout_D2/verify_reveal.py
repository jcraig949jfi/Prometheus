"""Verify a REVEAL of holdout D2 (for anyone, after Nestor publishes plaintext + salt + key).

  python -m prometheus.cosmos.c3_holdout_D2.verify_reveal --plaintext hidden_D2.plain.json \
      --salt hidden_D2.salt.hex --key hidden_D2.key.hex [--manifest MANIFEST_D2.json] [--ciphertext hidden_D2.enc]

Checks (booleans printed; exit 0 iff all true):
  manifest_spec_id_ok        spec_id == sha256(canonical manifest without spec_id)
  ciphertext_sha256_ok       sha256(ciphertext file) == manifest.ciphertext_sha256
  commitment_ok              sha256(salt || plaintext_bytes) == manifest.commitment
  decrypts_to_plaintext      AES-256-GCM decrypt(key, manifest IV, ciphertext, AAD) == plaintext bytes (auth tag ok)
  plaintext_canonical        plaintext bytes are the canonical JSON encoding of themselves
  plaintext_matches_manifest family / family_src_sha256 / n_worlds agree with the manifest
  redraw_from_nonce_ok       (only with COSMOS_BROKER=1) the worlds + run seeds re-derive from the nonce
Needs no family import unless the redraw check is requested.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from cryptography.exceptions import InvalidTag

from prometheus.cosmos.c3_holdout_D2 import sealbox

HERE = Path(__file__).resolve().parent


def verify(plaintext: bytes, salt: bytes, key: bytes, manifest: dict, ciphertext: bytes,
           redraw: bool = False) -> dict:
    out = {"manifest_spec_id_ok": sealbox.manifest_spec_id(manifest) == manifest.get("spec_id"),
           "ciphertext_sha256_ok": sealbox.sha256_hex(ciphertext) == manifest.get("ciphertext_sha256")}
    try:
        out["commitment_ok"] = sealbox.commitment(salt, plaintext) == manifest.get("commitment")
    except ValueError:
        out["commitment_ok"] = False
    try:
        dec = sealbox.decrypt(key, bytes.fromhex(manifest["iv_hex"]), ciphertext, manifest["family_src_sha256"])
        out["decrypts_to_plaintext"] = dec == plaintext
    except (InvalidTag, ValueError):
        out["decrypts_to_plaintext"] = False
    try:
        obj = json.loads(plaintext.decode("utf-8"))
        out["plaintext_canonical"] = sealbox.canon_bytes(obj) == plaintext
        out["plaintext_matches_manifest"] = (obj.get("family") == manifest.get("family")
                                             and obj.get("family_src_sha256") == manifest.get("family_src_sha256")
                                             and obj.get("n_worlds") == manifest.get("n_worlds")
                                             and len(obj.get("worlds", [])) == manifest.get("n_worlds"))
    except ValueError:
        obj = None
        out["plaintext_canonical"] = out["plaintext_matches_manifest"] = False
    if redraw and obj is not None:
        from prometheus.cosmos.c3_holdout_D2 import draw          # needs COSMOS_BROKER=1
        # v4 (Odysseus v3 claim 6 gap): the redraw is evidence only if it runs the AT-DRAW code
        at = manifest.get("d2_src_sha256_at_draw") or {}
        out["redraw_code_matches_manifest"] = bool(at) and all(
            sealbox.src_sha_lf(HERE / name) == h for name, h in at.items()) and \
            sealbox.src_sha_lf(draw.D_DIR / "medium.py") == manifest.get("family_src_sha256")
        worlds, seeds, rej = draw.draw_hidden(obj["nonce"], obj["n_worlds"], draw.exposed_d_worlds())
        out["redraw_from_nonce_ok"] = (worlds == obj["worlds"] and seeds == obj["run_seeds"]
                                       and rej == obj["rejected_equal_to_exposed_D"])
    out["all_ok"] = all(out.values())
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plaintext", required=True)
    ap.add_argument("--salt", required=True, help="file holding the salt as hex")
    ap.add_argument("--key", required=True, help="file holding the key as hex")
    ap.add_argument("--manifest", default=str(HERE / "MANIFEST_D2.json"))
    ap.add_argument("--ciphertext", default=str(HERE / "hidden_D2.enc"))
    a = ap.parse_args(argv)
    res = verify(Path(a.plaintext).read_bytes(), sealbox.read_hex_file(a.salt, sealbox.SALT_BYTES),
                 sealbox.read_hex_file(a.key, sealbox.KEY_BYTES),
                 json.loads(Path(a.manifest).read_text(encoding="utf-8")), Path(a.ciphertext).read_bytes(),
                 redraw=os.environ.get("COSMOS_BROKER") == "1")
    print(json.dumps(res, indent=1, sort_keys=True))
    return 0 if res["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
