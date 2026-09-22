"""The FOSSIL PACKET (Mechanism Archaeology Pipeline, Amendment 2 R16-R22, R25, R30; 2026-09-16).

One JSON per specimen, `techne/fossils/specimens/<id>/FOSSIL_PACKET.json`, carrying from birth
every R30 identity -- the Techne-owned ones filled, the downstream ones present and null with
their owner named, so no descendant ever retrofits a key.

    python -m techne.fossils.packet validate <id>       exit 1 on any defect, printed
    python -m techne.fossils.packet validate --all

Techne-owned fields (must be filled; the validator refuses a packet without them):
  FOSSIL_RAW_ID          tree sha256 over the preserved body + the archive/commit pins
  PAYLOAD_MANIFEST_ID    sha256 of UPSTREAM_HASHES.txt as committed
  PROVENANCE_GRADE       R19 vocabulary, per artifact
  FOSSIL_WORLD_ID        R21: measurement-based -- sha256 over (dockerfile sha256, package
                         manifest sha256, toolchain probe strings); an image digest is a witness
  RUNTIME_WITNESS        the image/emulator identity that actually ran, per receipt
  HOST_CAPS_ID           host, CPUs, kernel, container runtime at the witnessed run
  CAPABILITY_MATRIX      R22 verbs the FOSSIL_WORLD supports
  SCAFFOLDING_LEDGER     R18: applied and MEASURED_AND_REJECTED transformations
  INSTRUMENT_CONTROLS    C11: what showed the modern instrument is not the thing failing
  TECHNE_STATE           R17 lattice; never rounded up
  TECHNE_RUN_RECEIPTS    paths
  PRESERVATION           R25: independent copies with verification time/result
  REQUIRED_STATE_FOR_HANDOFF  R17: the state the next stage's experiment actually needs
  HANDOFF_REQUESTED      true once Techne offers the packet downstream; only then is a state below
                         the requirement a defect (a packet parked below its requirement is valid)
Downstream-owned (present, null until the owner fills them): CUT_ID, NYX_PREDICTION_PACKET (Nyx);
ORACLE_SOURCES, ORACLE_PROVENANCE_GRADES, HARMONIA_SURROGATE_ID, EQUIVALENCE_RESULT,
DIVERGENCE_LEDGER (Harmonia); TEST_WORLD_ID, PRESSURE_ID, INTERVENTION_ID, TENSOR_ADMISSION_RESULT,
PAYLOAD_READING_NULL (Theophrastus); FINAL_DISPOSITION (operator).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys

from . import vault

SCHEMA = "techne.fossil.packet/1"

LATTICE = ["BODY_RECOVERED", "BODY_RECOVERED_WORLD_NAMED", "WORLD_RECONSTRUCTED", "WORLD_EXECUTABLE",
           "BODY_EXECUTABLE", "BEHAVIOR_PARTIALLY_REPRODUCED", "BEHAVIOR_REPRODUCED"]
BLOCKED = ["WORLD_PARTIALLY_RECONSTRUCTED", "BLOCKED_BY_MISSING_TOOLCHAIN", "BLOCKED_BY_MISSING_MEDIA",
           "BLOCKED_BY_UNKNOWN_BEHAVIOR"]
GRADES = ["ORIGINAL_ARTIFACT", "CONTEMPORARY_COPY", "AUTHENTIC_TRANSCRIPTION", "LATER_TRANSCRIPTION",
          "RECONSTRUCTION", "DERIVED_RECOVERY_ARTIFACT", "AUTHOR_STATED", "UNKNOWN"]
VERBS = ["INSTANTIATE", "EXECUTE", "OBSERVE", "SNAPSHOT", "RESTORE", "STEP", "TRACE", "EXAMINE", "WATCH",
         "INTERVENE", "SCREENSHOT", "INJECT_INPUT", "EXTRACT_OUTPUT"]
TECHNE_FIELDS = ["FOSSIL_RAW_ID", "PAYLOAD_MANIFEST_ID", "PROVENANCE_GRADE", "FOSSIL_WORLD_ID", "RUNTIME_WITNESS",
                 "HOST_CAPS_ID", "CAPABILITY_MATRIX", "SCAFFOLDING_LEDGER", "INSTRUMENT_CONTROLS", "TECHNE_STATE",
                 "TECHNE_RUN_RECEIPTS", "PRESERVATION", "REQUIRED_STATE_FOR_HANDOFF"]
DOWNSTREAM = {"CUT_ID": "Nyx", "NYX_PREDICTION_PACKET": "Nyx", "ORACLE_SOURCES": "Harmonia",
              "ORACLE_PROVENANCE_GRADES": "Harmonia", "HARMONIA_SURROGATE_ID": "Harmonia",
              "EQUIVALENCE_RESULT": "Harmonia", "DIVERGENCE_LEDGER": "Harmonia", "TEST_WORLD_ID": "Theophrastus",
              "PRESSURE_ID": "Theophrastus", "INTERVENTION_ID": "Theophrastus", "TENSOR_ADMISSION_RESULT": "Theophrastus",
              "PAYLOAD_READING_NULL": "Theophrastus", "FINAL_DISPOSITION": "operator"}
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def fossil_world_id(dockerfile_sha256: str, package_manifest_sha256: str, probes: list[str]) -> str:
    """R21: identity by measurement. Same manifest + same toolchain strings => same world, whatever
    image digest a rebuild produced."""
    h = hashlib.sha256()
    h.update((dockerfile_sha256 + "\n" + package_manifest_sha256 + "\n" + "\n".join(sorted(probes)) + "\n").encode("utf-8"))
    return "fw-" + h.hexdigest()[:24]


def worlds_registry() -> dict:
    return json.loads((vault.REPO / "techne" / "fossils" / "WORLDS.json").read_text(encoding="utf-8"))


def packet_path(specimen_id: str) -> pathlib.Path:
    return vault.specimen_dir(specimen_id) / "FOSSIL_PACKET.json"


def validate(p: dict) -> list[str]:
    why = []
    if p.get("schema") != SCHEMA:
        return ["schema is %r, expected %r" % (p.get("schema"), SCHEMA)]
    for k in TECHNE_FIELDS:
        if k not in p or p[k] in (None, "", [], {}):
            why.append("Techne-owned field missing or empty: %s" % k)
    for k, owner in DOWNSTREAM.items():
        if k not in p:
            why.append("downstream field absent (must be present, null, owner %s): %s" % (owner, k))
    if why:
        return why
    raw = p["FOSSIL_RAW_ID"]
    if not _HEX64.match(str(raw.get("tree_sha256", ""))):
        why.append("FOSSIL_RAW_ID.tree_sha256 is not sha256")
    if not _HEX64.match(str(p["PAYLOAD_MANIFEST_ID"])):
        why.append("PAYLOAD_MANIFEST_ID is not sha256")
    for a in p["PROVENANCE_GRADE"]:
        if a.get("grade") not in GRADES:
            why.append("PROVENANCE_GRADE %r not in R19 vocabulary" % a.get("grade"))
    st = p["TECHNE_STATE"]
    if st not in LATTICE + BLOCKED:
        why.append("TECHNE_STATE %r not in the R17 lattice / R27 blocked states" % st)
    req = p["REQUIRED_STATE_FOR_HANDOFF"]
    if req not in LATTICE:
        why.append("REQUIRED_STATE_FOR_HANDOFF %r not in the R17 lattice" % req)
    if p.get("HANDOFF_REQUESTED") and st in LATTICE and req in LATTICE and LATTICE.index(st) < LATTICE.index(req):
        why.append("TECHNE_STATE %s is below REQUIRED_STATE_FOR_HANDOFF %s: not ready for handoff" % (st, req))
    if p.get("HANDOFF_REQUESTED") and st in BLOCKED:
        why.append("HANDOFF_REQUESTED while TECHNE_STATE is a blocked state %s" % st)
    if st.startswith("BEHAVIOR") and not p.get("BEHAVIOR_EVIDENCE"):
        why.append("a BEHAVIOR_* state needs BEHAVIOR_EVIDENCE (what published/contemporary behaviour was matched, by which oracle)")
    if not str(p["FOSSIL_WORLD_ID"]).startswith("fw-"):
        why.append("FOSSIL_WORLD_ID must be measurement-based (fw-...), not an image digest")
    cm = p["CAPABILITY_MATRIX"]
    for v in VERBS:
        if v not in cm:
            why.append("CAPABILITY_MATRIX lacks verb %s" % v)
        elif cm[v] not in ("yes", "no", "partial"):
            why.append("CAPABILITY_MATRIX[%s] must be yes/no/partial" % v)
    # R22 as data: the packet's matrix must equal the registry's for its world (WORLDS.json owns it)
    wname = (p.get("FOSSIL_WORLD") or {}).get("name")
    reg = worlds_registry().get("worlds", {}).get(wname)
    if reg is None:
        why.append("FOSSIL_WORLD.name %r is not in techne/fossils/WORLDS.json" % wname)
    else:
        diff = [v for v in VERBS if cm.get(v) != reg["capabilities"].get(v)]
        if diff:
            why.append("CAPABILITY_MATRIX differs from WORLDS.json for %s on %s" % (wname, diff))
    led = p["SCAFFOLDING_LEDGER"]
    for key in ("applied", "measured_and_rejected"):
        if key not in led or not isinstance(led[key], list):
            why.append("SCAFFOLDING_LEDGER.%s must be a list (empty is a statement, absence is not)" % key)
    for t in led.get("applied", []):
        for f in ("transformation_id", "reason", "sites_affected", "exact_operation", "tool", "reversible", "effect_on_execution"):
            if f not in t:
                why.append("scaffolding %s lacks %s" % (t.get("transformation_id", "?"), f))
    pres = p["PRESERVATION"]
    copies = pres.get("copies", [])
    hosts = {c.get("failure_domain") for c in copies if c.get("verification_result") == "VERIFIED"}
    if len(hosts) < 2:
        why.append("PRESERVATION: fewer than 2 VERIFIED copies in distinct failure domains (R25)")
    for c in copies:
        for f in ("object", "location_class", "failure_domain", "verification_time", "verification_result"):
            if f not in c:
                why.append("preservation copy lacks %s" % f)
    if not p["TECHNE_RUN_RECEIPTS"]:
        why.append("no run receipts")
    for r in p["TECHNE_RUN_RECEIPTS"]:
        if not (vault.REPO / r).exists():
            why.append("receipt path does not exist: %s" % r)
    if not p["INSTRUMENT_CONTROLS"]:
        why.append("INSTRUMENT_CONTROLS empty (C11)")
    return why


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate"); v.add_argument("specimen_id", nargs="?"); v.add_argument("--all", action="store_true")
    a = ap.parse_args(argv)
    ids = [a.specimen_id] if a.specimen_id and not a.all else sorted(p.parent.name for p in vault.SPECIMENS.glob("*/FOSSIL_PACKET.json"))
    bad = 0
    for sid in ids:
        pp = packet_path(sid)
        if not pp.exists():
            print(sid, "NO_PACKET"); bad += 1; continue
        why = validate(json.loads(pp.read_text(encoding="utf-8")))
        print(sid, "VALID" if not why else "INVALID: " + "; ".join(why))
        bad += bool(why)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
