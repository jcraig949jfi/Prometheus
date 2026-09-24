"""Proposed (NOT final) hashes for the S4 candidate. Writes PROPOSED_HASHES.json.

C9-D08. The rev-B PROPOSED_HASHES.json carried a `proposed_protocol_hash` whose
derivation exists nowhere in the repository; it cannot be recomputed, so it certifies
nothing. Every value here is recomputable by running this file, and the protocol hash is
DEFINED as sha256 over the canonical JSON of everything else below:

  grammar_hash        grammar.grammar_hash()
  manifest_hash       manifest.build()["manifest_hash"]
  specimen_panel_hash specimens.manifest_p11()["panel_hash"]
  constants_sha256    constants.CONSTANTS_SHA256 (must equal its pin)
  documents           sha256 of PREREGISTRATION.md and P11_SPEC.md, LF-normalised
  modules             sha256 of every campaign .py (tests included), LF-normalised

Nothing here is written into PREREGISTRATION.md. Freeze is an operator instruction.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def lf_sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main():
    import constants
    import grammar as G
    import manifest as M
    import specimens
    assert constants.CONSTANTS_SHA256 == constants.PINNED_SHA256, "constants drifted from pin"
    m = M.build()
    bad = M.validate(m)
    panel = specimens.manifest_p11()
    mods = {p.relative_to(HERE).as_posix(): lf_sha(p)
            for p in sorted(HERE.rglob("*.py")) if "__pycache__" not in p.parts}
    body = {"status": "PROPOSED - NOT FROZEN",
            "protocol_version": M.PROTOCOL_VERSION,
            "grammar_hash": G.grammar_hash(),
            "manifest_hash": m["manifest_hash"],
            "specimen_panel_hash": panel["panel_hash"],
            "constants_sha256": constants.CONSTANTS_SHA256,
            "documents": {"PREREGISTRATION.md": lf_sha(HERE / "PREREGISTRATION.md"),
                          "P11_SPEC.md": lf_sha(HERE / "P11_SPEC.md")},
            "modules": mods}
    protocol = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"))
                              .encode("ascii")).hexdigest()
    old = json.loads((HERE / "PROPOSED_HASHES.json").read_text()) \
        if (HERE / "PROPOSED_HASHES.json").exists() else {}
    if old.get("status", "").startswith("PROPOSED"):
        old = old.get("supersedes", {})
    out = dict(body, proposed_protocol_hash=protocol,
               derivation="sha256 over canonical JSON of every other field above "
                          "(sort_keys, separators , :) - see proposed_hashes.py",
               n_bundles=m["n_bundles"], n_runs=m["n_runs"], by_hypothesis=m["by_hypothesis"],
               size=m["size"], validation_problems=len(bad), panel_size=panel["panel_size"],
               supersedes=old)
    (HERE / "PROPOSED_HASHES.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("proposed_protocol_hash", "manifest_hash",
                                          "specimen_panel_hash", "grammar_hash", "n_bundles",
                                          "n_runs", "by_hypothesis", "validation_problems",
                                          "panel_size")}, indent=1))


if __name__ == "__main__":
    main()
