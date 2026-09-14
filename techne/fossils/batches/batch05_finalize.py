"""Batch 05 finalize (2026-09-12): fill observability + nyx_handoff from the records+receipts and
set the SOURCE_ONLY specimens honestly. Run ONCE after batch05.py and after all runs; do NOT
re-run batch05.py afterward (its main() keeps observability/nyx_handoff, but the intent is the
same as batch04_finalize: receipts are the source of these flags).

    python -m techne.fossils.batches.batch05_finalize

ORACLE_BACKED is a per-specimen acquisition fact: did the receipt grade the machine against an
independent expectation? Activity-only receipts are marked no, honestly.
"""
from __future__ import annotations

from .. import record as R
from . import batch04_finalize as F4
from . import batch05

ORACLE = {
    "lmdb-0.9.31": True,             # recovery property: 1000 present, uncommitted absent
    "leveldb-1.23": True,            # log replay: 2500 present
    "concurrencykit-0.7.2": True,    # ck's validate programs assert their invariants
    "pybreaker-1.2.0": True,         # the CLOSED->OPEN->HALF-OPEN->CLOSED trace
    "backoff-2.2.1": True,           # 1 vs >=20 distinct waits
    "bsd-tcp-4.2-1983": False, "bsd-tcp-4.3-tahoe-1988": False, "bsd-tcp-4.3-reno-1990": False,
    "odepack-netlib": True,          # T=4e10 reached (MF=21); ISTATE=-1 (MF=10)
    "spin-pathfinder-priority-inversion-1997": True,   # invalid end state, errors: 1
    "particles-chopin-0.4": True,    # RMSE vs exact Kalman
    "emcee-3.1.6": True,             # moments vs analytic
    "tinyekf-levy": False,           # plausibility only (Earth radius, settled); no reference trajectory
    "umdhmm-kanungo-1.02": True,     # trained log-lik within 3% of generating model
    "padasip-1.2.2": True,           # recovered taps vs known plant
    "tinystm-marlier": True,         # bank invariant
    "radamsa-0.6": False,            # determinism + count; the generator has no truth to grade against
    "cjson-1.7.18": True,            # crashed=0 under ASan over 200 adversarial cases
    "libcorrect-quiet": True,        # upstream tests decode injected errors
    "paip-lisp-norvig-1991": True,   # the book's printed plan
    "whitakers-words-ada": True,     # dictionary entry for amo
    "basic-computer-games-1978": False,   # runs to an end state; no reference transcript
    "cobol-programming-course-omp": False,  # runs; SRCHBIN 'Not Found' (EBCDIC key) and S0C7 silently computed: recorded, not graded
    "verilog-arbiter-forencich": True,     # 4/4/4/4 vs 16/0/0/0 grant counts
    "biriscv-branch-predictor": True,      # gshare late mispredicts 0 < bimodal 10
    "erfa-2.0.1": True,              # t_erfa_c reference values
    "python-sgp4-2.23": True,        # tcppver.out
    "py-vollib-lets-be-rational": True,    # round trip 1e-9 on well-conditioned points
    "pyportfolioopt-1.5.5": True,    # feasibility + dominance (synthetic market)
    "compact-4.2bsd-1983": True,     # byte-exact round trip
    "gzip-1.2.4-1993": True,         # byte-exact round trip
    "zchaff-2007": True,             # SAT/UNSAT agreement with minisat/picosat
    "minisat-1.14-2006": True,
}
SOURCE_ONLY = {
    "bsd-tcp-4.2-1983": "SOURCE_ONLY: 4.2BSD kernel netinet/tcp_* -- links against the 1983 BSD kernel; preserved + tree-hashed for the congestion-collapse lineage; no in-vault runner (a 4.2BSD VM under SIMH is the way to run it, queued).",
    "bsd-tcp-4.3-tahoe-1988": "SOURCE_ONLY: 4.3BSD-Tahoe kernel netinet/tcp_* -- as above; the diff against BSD-4_2 is the redesign.",
    "bsd-tcp-4.3-reno-1990": "SOURCE_ONLY: 4.3BSD-Reno kernel netinet/tcp_* -- as above; the diff against Tahoe is fast retransmit/recovery.",
}


def main():
    # batch04_finalize.fill reads its module-level ORACLE / SOURCE_ONLY tables; point them at ours
    F4.ORACLE = ORACLE
    F4.SOURCE_ONLY = SOURCE_ONLY
    ids = [r["specimen_id"] for r in batch05.S] + ["do-mpc"]
    for sid in ids:
        probs = F4.fill(sid)
        rec = R.load(sid)
        print("%-40s %-28s obs=%s %s" % (sid, rec["run_classification"],
              "".join("1" if v == "yes" else ("0" if v == "no" else "?") for v in rec["observability"].values()),
              "ok" if not probs else probs))


if __name__ == "__main__":
    main()
