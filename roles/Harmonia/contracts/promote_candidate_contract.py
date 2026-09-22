"""Promote a pre-deploy candidate contract to the live contract path.

Harmonia[m2-54a6d694], 2026-09-14, for comms #215 (Daedalus candidate 8c53d04e6).

WHY THIS EXISTS. A contract generated for a build that is not yet live
(generate_sfe_contract.py --candidate-hash) describes routes the running engine
does not serve. conformance_check.py reads a contract route that live lacks as
REMOVED, which is DRIFT, the never-retry state. So the candidate cannot sit at
roles/Harmonia/contracts/sfe_contract.json before the restart without halting
every consumer that reads it, and after the restart it must get there without a
person remembering to copy a file. This is the copy, with the conditions that
make it safe checked rather than assumed.

REFUSES (exit 2, nothing written) unless ALL hold, read from the target engine:
  1  the candidate carries a pre_deploy block (it was generated as a candidate)
  2  live engine_source_hash == the candidate's hash (the deploy happened)
  3  live engine_instance_id == the candidate's (same ledger; never bends)
  4  live schema_version == the candidate's
  5  conformance_check.py on the candidate against that engine exits 0,
     with no consumer routes declared, so an INCOMPLETE cannot pass as 0

Then it writes the target with the pre_deploy block replaced by a `promoted`
record (when, against which base, the gate's exit). It does NOT commit; the
caller commits the target by explicit path.

    python roles/Harmonia/contracts/promote_candidate_contract.py \\
        --candidate roles/Harmonia/contracts/candidates/<hash12>/sfe_contract.json \\
        --cacert <m1.crt>

Exit codes: 0 promoted, 2 refused (nothing written), 1 the gate did not return 0
(nothing written; its output is printed).
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import ssl
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    from workspace_guard import assert_not_canonical, CanonicalCheckoutRefused
except ImportError:                                                # pragma: no cover
    assert_not_canonical = None


def version(root, cacert):
    ctx = ssl.create_default_context(cafile=cacert) if cacert else None
    kw = {"context": ctx} if ctx else {}
    with urllib.request.urlopen(root + "/v2/version", timeout=30, **kw) as z:
        return json.loads(z.read().decode())


def main(argv=None):
    if assert_not_canonical is not None:
        try:
            assert_not_canonical("promote a candidate contract (it WRITES the "
                                 "live contract path)")
        except CanonicalCheckoutRefused as e:
            print("REFUSING: %s" % e)
            return 2
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--cacert", default=None)
    ap.add_argument("--base", default=None,
                    help="override; defaults to the candidate's base_url")
    ap.add_argument("--target", default=os.path.join(HERE, "sfe_contract.json"))
    a = ap.parse_args(argv)

    C = json.load(open(a.candidate, encoding="utf-8"))
    E = C["engine"]
    pre = E.get("pre_deploy")
    if not pre:
        print("REFUSING: %s has no pre_deploy block; it is not a candidate "
              "contract." % a.candidate)
        return 2
    base = (a.base or E["base_url"]).rstrip("/")
    root = base[:-3] if base.endswith("/v2") else base
    try:
        live = version(root, a.cacert)
    except Exception as e:                                         # noqa: BLE001
        print("REFUSING: cannot read %s/v2/version -- %r. Nothing written."
              % (root, e))
        return 2

    rows = [
        ("candidate hash is live", live.get("engine_source_hash"),
         pre["candidate_engine_source_hash"]),
        ("same ledger", live.get("engine_instance_id"),
         E["engine_instance_id"]),
        ("same schema", live.get("schema_version"), E["schema_version"]),
    ]
    ok = True
    for name, got, want in rows:
        passed = got == want
        ok = ok and passed
        print("  [%s] %s: live %s, candidate %s"
              % ("PASS" if passed else "FAIL", name, got, want))
    if not ok:
        print("REFUSING: the candidate is not the build this engine runs. "
              "Nothing written.")
        return 2

    cmd = [sys.executable, os.path.join(HERE, "conformance_check.py"),
           "--contract", a.candidate, "--base", base]
    if a.cacert:
        cmd += ["--cacert", a.cacert]
    # no --consumer-routes: an INCOMPLETE must not be able to read as exit 0
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout)
    if r.returncode != 0:
        print("NOT PROMOTED: the gate returned %d on the candidate against %s."
              % (r.returncode, base))
        return 1

    out = dict(C)
    out["engine"] = dict(E)
    out["engine"].pop("pre_deploy", None)
    try:
        src = os.path.relpath(a.candidate, HERE).replace(os.sep, "/")
    except ValueError:          # different drive (Windows): keep it as given
        src = a.candidate.replace(os.sep, "/")
    out["engine"]["promoted"] = {
        "from_candidate": src,
        "at": datetime.datetime.now(datetime.timezone.utc).isoformat(
            timespec="seconds"),
        "against_base": base,
        "live_engine_source_hash": live.get("engine_source_hash"),
        "gate_exit": r.returncode,
        "generated_while_live_was":
            pre.get("live_engine_source_hash_at_generation"),
    }
    with open(a.target, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=False)
    print("PROMOTED -> %s" % a.target)
    print("  commit it by explicit path; it is not committed here.")
    return 0


if __name__ == "__main__":
    # An uncaught exception exits 1 in Python, which is this tool's "the gate
    # did not return 0". Run 1 of the verification (2026-09-14, row P3) read a
    # relpath crash as a gate refusal for exactly that reason. A crash is 4.
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException:                                          # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("INTERNAL ERROR in promote_candidate_contract.py -- nothing "
              "about the gate or the engine is established. Exit 4.")
        sys.exit(4)
