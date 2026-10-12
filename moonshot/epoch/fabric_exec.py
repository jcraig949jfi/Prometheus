"""Moonshot's approved Fabric executor (C-012-T003; contract moonshot/nf/INTERFACE_CONTRACT.md s3).

Fabric's script executor runs it on a node as `python -E -s -m moonshot.epoch.fabric_exec <args>` in the checkout
pinned at the task's base_sha, with an allow-listed environment and FABRIC_OUT_DIR. Everything it needs arrives in
argv; everything it produces leaves as the four canonical files in FABRIC_OUT_DIR, which the Fabric runtime uploads
as artifacts. It imports no database, network, subprocess or git code (tested), and it publishes nothing: the
trusted publisher on M2 classifies its output.

    --namespace NS --genesis-b64 G --epoch-index K --input-b64 X --input-sha256 H

Exit 0: the epoch's files were written. Exit 2: refused (bad input, non-canonical genesis, epoch outside the
genesis, no FABRIC_OUT_DIR, output already present); nothing written. One JSON line on stdout records the identity.

Node-local faults (contract s7) model a faulty host for the demonstration: a file <fault dir>/<namespace>.json
holding a list of {"chain_id", "epochs": [k, ...], "mode": "flip_checkpoint" | "corrupt_trace", "delay_s"?}. They are
read ONLY for test namespaces (test, test-*, qual, qual-*), so a production chain never consults one, and only
someone with a shell on the node can create one -- no task submitter can.
"""
import argparse
import base64
import binascii
import hashlib
import json
import os
import re
import sys
import time

from moonshot.epoch import canonical as C
from moonshot.epoch import model
from moonshot.epoch import runtime as R

FILES = (("manifest", "MANIFEST.json"), ("spec", "SPEC.json"), ("trace", "TRACE"), ("checkpoint", "CHECKPOINT"))
TEST_NAMESPACE = re.compile(r"^(test|qual)(-[a-z0-9-]+)?$")
DEFAULT_FAULT_DIR = "/var/tmp/moonshot-fault"


class Refused(Exception):
    pass


def _parse(argv):
    ap = argparse.ArgumentParser(prog="moonshot.epoch.fabric_exec")
    ap.add_argument("--namespace", required=True)
    ap.add_argument("--genesis-b64", required=True)
    ap.add_argument("--epoch-index", required=True, type=int)
    ap.add_argument("--input-b64", required=True)
    ap.add_argument("--input-sha256", required=True)
    return ap.parse_args(argv)


def _b64(text, what):
    try:
        return base64.b64decode(text.encode("ascii"), validate=True)
    except (binascii.Error, UnicodeEncodeError, ValueError):
        raise Refused("{} is not base64".format(what))


def _fault(namespace, chain_id, k):
    """The node-local fault for this (namespace, chain, epoch), or None. Production namespaces never look."""
    if not TEST_NAMESPACE.match(namespace):
        return None
    path = os.path.join(os.environ.get("MOONSHOT_FAULT_DIR", DEFAULT_FAULT_DIR), namespace + ".json")
    try:
        with open(path, encoding="utf-8") as f:
            specs = json.load(f)
    except (OSError, ValueError):
        return None
    for s in specs if isinstance(specs, list) else []:
        if isinstance(s, dict) and s.get("chain_id") == chain_id and k in (s.get("epochs") or []):
            return s
    return None


def _flip_runner(input_checkpoint, spec):
    """The honest runtime, then one checkpoint bit flipped: a faulty host that still claims synthetic.v1."""
    trace, ckpt = R.run_synthetic_v1(input_checkpoint, spec)
    b = bytearray(ckpt)
    if b:
        b[0] ^= 0x01
    return trace, bytes(b)


def run(a):
    out = os.environ.get("FABRIC_OUT_DIR")
    if not out or not os.path.isdir(out):
        raise Refused("FABRIC_OUT_DIR is not a directory")
    gbytes = _b64(a.genesis_b64, "genesis")
    try:
        gobj = C.parse_canonical(gbytes)
    except C.CanonicalError as e:
        raise Refused("genesis is not canonical: {}".format(e))
    if not isinstance(gobj, dict) or "chain_id" not in gobj or "epochs" not in gobj:
        raise Refused("genesis is not a genesis object")
    inp = _b64(a.input_b64, "input checkpoint")
    if hashlib.sha256(inp).hexdigest() != a.input_sha256:
        raise Refused("input checkpoint does not match --input-sha256")
    k = a.epoch_index
    fault = _fault(a.namespace, gobj["chain_id"], k)
    mode = fault.get("mode") if fault else None
    try:
        r = model.execute(gobj, k, inp, _flip_runner if mode == "flip_checkpoint" else None)
    except (ValueError, KeyError, LookupError, TypeError) as e:
        raise Refused("cannot execute epoch {}: {}".format(k, e))
    files = r.files()
    if mode == "corrupt_trace":
        files["trace"] = files["trace"] + b"corrupt\n"        # after the manifest was computed: bytes != claims
    if fault and fault.get("delay_s"):
        time.sleep(float(fault["delay_s"]))
    targets = [(os.path.join(out, name), files[key]) for key, name in FILES]
    if any(os.path.exists(p) for p, _ in targets):
        raise Refused("output already present in FABRIC_OUT_DIR")
    for p, data in targets:
        try:
            with open(p, "xb") as f:                          # exclusive: never overwrite, even in a race
                f.write(data)
        except FileExistsError:
            raise Refused("{} appeared while writing".format(os.path.basename(p)))
    return {"chain_id": r.chain_id, "epoch_index": k, "work_id": r.work_id, "epoch_digest": r.epoch_digest,
            "input_checkpoint_sha256": a.input_sha256, "namespace": a.namespace, "fault": mode}


def main(argv=None):
    try:
        a = _parse(sys.argv[1:] if argv is None else argv)
    except SystemExit:
        return 2
    try:
        line = run(a)
    except Refused as e:
        print(json.dumps({"refused": str(e)}), file=sys.stderr, flush=True)
        return 2
    print(json.dumps(line, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
