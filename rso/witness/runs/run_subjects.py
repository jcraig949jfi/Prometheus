"""C-010-T020 step 1 (PREREGISTRATION s2, s10): the two registered subject GA runs, each charged as ONE TOP_LEVEL
launch on rso/witness/LEDGER.jsonl under rso/witness/contract.json. Execution glue only: it calls the frozen
rso.witness.run_witness.run_subject unchanged (which writes genome.json + subject_record.json and prints/stores no
fitness). Usage (from the repo root): python -B -m rso.witness.runs.run_subjects"""
import json
import os
import sys
import time

from rso.slice001 import ledger as L
from rso.witness import run_witness as RW

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(ROOT, "..", "..", ".."))
LEDGER = os.path.join(REPO, "rso", "witness", "LEDGER.jsonl")
CONTRACT = os.path.join(REPO, "rso", "witness", "contract.json")
# PREREGISTRATION s2 (frozen): Config() defaults, P=128, G=120, eps=4
SUBJECTS = (("S4", "W4", 20261007), ("S15", "W15", 20261008))


def main():
    led = L.Ledger.from_contract(LEDGER, CONTRACT)
    out = {}
    for name, world, seed in SUBJECTS:
        d = os.path.join(ROOT, "subjects", name)
        run_id = "C010-SUBJECT-%s-%s" % (name, time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
        att = led.begin(run_id, "SUBJECT:%s" % name, L.TOP_LEVEL, supplied_by="rso.witness.runs.run_subjects")
        c0 = time.process_time()
        try:
            rec = RW.run_subject(world, "present", {}, 128, 120, 4, seed, d)
        except Exception:
            att.finish("FAILED", cpu_s=time.process_time() - c0)
            raise
        nbytes = sum(os.path.getsize(os.path.join(d, f)) for f in os.listdir(d))
        att.finish("COMPLETED", cpu_s=time.process_time() - c0, artifact_bytes=nbytes)
        out[name] = {"run_id": run_id, "world": world, "seed": seed, "genome_sha256": rec["genome_sha256"],
                     "episode_seeds": len(rec["episode_seeds"]), "cpu_s": round(time.process_time() - c0, 1)}
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
