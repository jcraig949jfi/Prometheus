#!/usr/bin/env python
"""Execute HARMONIA_FIRST_ADVENTURER_BOUNDARY_PROBE_V2 EXACTLY as frozen
(sha256 84d7f198...). No reinterpretation, no repair, no retry. Frozen
parameters are used literally; if a frozen parameter is non-executable,
that is preserved as the terminal state, not worked around."""

import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, r"D:\Prometheus")
sys.path.insert(0, r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryClient")
sys.path.insert(0, str(Path(__file__).parent))

from sfclient.client import EngineClient                       # noqa: E402
from proteus.foundry.vm import Player                          # noqa: E402
from proteus.foundry.prng import SplitMix64                    # noqa: E402
from proteus.foundry.export import encounter_identity          # noqa: E402
import adapter                                                 # noqa: E402

BASE = "https://192.168.1.202:8811"
CA = (r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryClient"
      r"\config\m1.crt")
PIN = ("sha256:c358a53b9899fa16acb70c69747c8ec4ca494cdc62bd10fa9a550d5"
       "74eef8c39")
OUT = Path(__file__).parent
# --- FROZEN PARAMETERS, verbatim from the directive Part B ---
FROZEN_SEED = "20260904b"          # frozen exactly as written
STD_SEED_ROOT = 424242
STD_BUDGET = {"experiments": {"limit": 4, "enforcement": "enforceable"}}


def main():
    rec = dict(directive="HARMONIA_FIRST_ADVENTURER_BOUNDARY_PROBE_V2",
               frozen_sha256="84d7f198b32248f5965a90a334eabf34ee8d7a6f"
               "c44e7fe457dd24b819397e12", started=time.time())
    sp = adapter.load_specimen()          # first specimen, verified
    oid = sp["organism_id"]
    rec["organism_id"] = oid
    tok = open(r"C:\ZeusD-var\harmonia\sfe_token.txt").read().strip()
    c = EngineClient(BASE, token=tok, cafile=CA, timeout=60.0)
    v = c.version()
    if v["engine_source_hash"] != PIN:
        rec["terminal"] = "BLOCKED_ENGINE_HASH_CHANGED"
        rec["engine"] = v
        json.dump(rec, open(OUT / "v2_result.json", "w"), indent=1)
        raise SystemExit("engine hash != frozen pin")
    rec["engine"] = v
    sid = c.create_session("v2-boundary-probe")
    w = c.create_world(sid, "v2-standard-world", seed_root=STD_SEED_ROOT,
                       budget=STD_BUDGET)
    wid = w["world_id"]
    c.start(wid)
    rec["world"] = dict(world_id=wid, seed_root=STD_SEED_ROOT,
                        sharing_policy="ISOLATED")
    # setup: artifact placement (identity gate) -- SCAFFOLDING
    placement = adapter.place_in_world(c, wid, sp)
    rec["placement"] = placement
    # mint encounter_id with the FROZEN seed (string is legal in hash_obj)
    enc_id = encounter_identity([oid], wid, FROZEN_SEED, [])
    rec["encounter_id"] = enc_id
    # THE ONE ACTION, exactly as frozen: SplitMix64(seed 20260904b)
    try:
        rng = SplitMix64(FROZEN_SEED)              # frozen seed, literal
        player = Player(sp["manifest"])
        st = player.fresh_state()
        outputs, status = player.run_tick(st, [[0]], 1, rng)
        rec["action"] = dict(outputs=outputs, status=status)
        rec["terminal"] = "ACTION_EXECUTED"        # (not expected)
    except Exception as e:
        rec["action_exception"] = dict(type=type(e).__name__,
                                       msg=str(e)[:200])
        rec["terminal"] = ("BLOCKED_NON_EXECUTABLE_FROZEN_PARAMETER: "
                           "frozen RNG seed '20260904b' is not a valid "
                           "SplitMix64 integer seed; directive forbids "
                           "reinterpreting/repairing the frozen probe "
                           "during execution")
    rec["finished"] = time.time()
    json.dump(rec, open(OUT / "v2_result.json", "w"), indent=1,
              default=str)
    print("V2 terminal:", rec["terminal"])
    print("world (preserved):", wid)
    print("identity gate:", placement.get("readback_bytes_equal"))
    if "action_exception" in rec:
        print("action exception:", rec["action_exception"])


if __name__ == "__main__":
    main()
