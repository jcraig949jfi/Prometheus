"""Loader for the FROZEN Lexis interface pair -- a QUARANTINED CANDIDATE, not admitted.

    compute : lexis_op_subtract               reads numbers        writes max_value
    readout : lexis_score_by_value_match__g   reads candidates,    writes selected_answer
                                              max_value

The implementations live, unchanged since 2026-08-25, in
`roles/Lexis/instruments/candidate_primitives.py`. This module does not copy them; it
imports them and REFUSES if the file's sha256 differs from the frozen hash recorded in
`interface_pair_manifest.json`, so a consumer cannot silently test a drifted object.

REQUIRED INPUT STATE. The compute primitive's precondition is `len(state.numbers) >= 2`.
`numbers` is written by Apollo's registry operator `parse_numbers`, which the production
0.833 organism (KNOWN_0833) does NOT carry. So relative to that organism the consumable
unit is a TRIPLE: parse_numbers (already in Apollo's registry) + compute + readout.
`augmented_program()` builds exactly that, in two placements, and nothing else.

Nothing here writes to apollo/. Nothing here registers the primitives anywhere.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INSTR = HERE.parent / "instruments"
PRIMS = INSTR / "candidate_primitives.py"
MANIFEST = HERE / "interface_pair_manifest.json"

sys.path.insert(0, str(INSTR))
sys.path.insert(0, str(ROOT / "apollo" / "src"))
sys.path.insert(0, str(ROOT / "apollo" / "scripts"))
sys.path.insert(0, str(ROOT / "agents" / "hephaestus" / "src"))

COMPUTE = "lexis_op_subtract"
READOUT = "lexis_score_by_value_match__g"
PLACEMENTS = ("readout_last", "readout_first", "compute_first")


def file_sha256(p: Path) -> str:
    """sha256 over LF-normalised bytes, so the pin is the same on a CRLF checkout."""
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load(verify: bool = True) -> dict:
    """-> {'compute': op, 'readout': op, 'sha256': str, 'verified': bool}"""
    sha = file_sha256(PRIMS)
    verified = False
    if verify:
        if not MANIFEST.exists():
            raise RuntimeError("manifest missing: %s" % MANIFEST)
        frozen = json.loads(MANIFEST.read_text(encoding="utf-8"))["source"]["sha256"]
        if sha != frozen:
            raise RuntimeError("candidate_primitives.py sha256 %s != frozen %s -- "
                               "the object under test is not the frozen pair" % (sha, frozen))
        verified = True
    from candidate_primitives import CANDIDATES   # noqa: E402  (deferred: after hash check)
    return {"compute": CANDIDATES[COMPUTE], "readout": CANDIDATES[READOUT],
            "sha256": sha, "verified": verified}


def augmented_program(placement: str = "readout_last", with_compute: bool = True,
                      with_readout: bool = True, verify: bool = True):
    """KNOWN_0833 with parse_numbers + the pair inserted. Returns (names, ops).

    readout_last : T... , parse_numbers, compute, S..., readout   (readout may overwrite)
    readout_first: T... , parse_numbers, compute, readout, S...   (home scorers may overwrite)
    compute_first: parse_numbers, compute, T..., S..., readout    (op_aggregate_quantities,
                   inside T, may overwrite compute's max_value -- the hazard runs the other way)
    """
    import blackboard_evolve as be                 # noqa: E402
    from o1_enumerate import KNOWN_0833            # noqa: E402
    if placement not in PLACEMENTS:
        raise ValueError(placement)
    pair = load(verify=verify)
    T = [n for n in KNOWN_0833 if be.role_of(n) == "transformer"]
    S = [n for n in KNOWN_0833 if be.role_of(n) != "transformer"]
    names, ops = [], []
    if placement == "compute_first":
        names.append("parse_numbers"); ops.append(be.REGISTRY["parse_numbers"][0])
        if with_compute:
            names.append(COMPUTE); ops.append(pair["compute"])
    for n in T:
        names.append(n); ops.append(be.REGISTRY[n][0])
    if placement != "compute_first":
        names.append("parse_numbers"); ops.append(be.REGISTRY["parse_numbers"][0])
        if with_compute:
            names.append(COMPUTE); ops.append(pair["compute"])
    if with_readout and placement == "readout_first":
        names.append(READOUT); ops.append(pair["readout"])
    for n in S:
        names.append(n); ops.append(be.REGISTRY[n][0])
    if with_readout and placement in ("readout_last", "compute_first"):
        names.append(READOUT); ops.append(pair["readout"])
    return names, ops


if __name__ == "__main__":
    p = load()
    print("frozen pair loaded; sha256 %s; verified=%s" % (p["sha256"], p["verified"]))
    for pl in PLACEMENTS:
        names, _ = augmented_program(pl)
        print("%-13s %s" % (pl, " -> ".join(names)))
