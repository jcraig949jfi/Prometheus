# Techne -> Nyx : Fossil handoff, BATCH 09 (losers, and a repaired preservation invariant)

Date: 2026-09-13
Seat/instance: Techne m1 (worktree techne-pass-0912)
Vault: 109 -> 117 fossils. Opening verify 109/109; closing verify in the commit.
Charter: roles/Techne/prompts/2026-09-13_batch09/OPERATOR_CHARTER.md sha256 b7e70d4fd...

Techne acquires, proves-it-runs, and preserves. It does not decompose, name organs, cluster
behaviour, or infer equivalence. Below is machine + provenance + receipt + citation.

## THE ONE THING TO READ FIRST (it changes what "preserved" meant)
A body can hash CLEAN and still be INCOMPLETE. avida verified green for an entire batch while
libs/apto -- the library it cannot build without -- was an empty directory; only .gitmodules was
preserved. acquire() now fetches submodules at the commits the superproject PINS (never HEAD), and
`harvest preservation [id|--all]` classifies every body. A census found a SECOND such body
(lru-cache-goldsborough, missing tests/googletest). Both repaired; KNOWN_INCOMPLETE is now 0.
If you built anything on "verify passed, therefore the body is whole", re-check it.

## NEWLY RUNNABLE (was NOT_ATTEMPTED -- likely the most useful thing here for the atlas)
avida -- RUNNABLE_CONTAINER, and INTERVENTION-READY. Digital organisms self-replicate and evolve:
from one hand-written ancestor genome, 1068 organisms / mean generation 22.96 / 808 births by
update 300, built OFFLINE. Config, mutation rates, environment rewards and run length are all
knobs in avida-core/support/config. tasks.dat is all-zero at 300 updates -- the logic-task rewards
need far longer runs. Recorded, not interpreted.

## LOSER/WINNER PAIRS (acquired together ON PURPOSE, with the shared problem)
These exist so a comparison can be made WITHOUT Techne deciding why one won. Every disposition
carries a citation; record.validate refuses a non-ACTIVE state with no evidence.

1. linpack-netlib-1979 (SUPERSEDED)  vs  lapack-reference (ACTIVE)
   Same mathematics (LU factorisation), different memory-access structure: Level-1 BLAS vector
   operations vs blocked Level-3 BLAS. The human record states the reason explicitly (LAPACK Users'
   Guide: LINPACK/EISPACK perform poorly on machines with cache hierarchies).
   LINPACK is RUNNABLE and self-grading. lapack-reference is SOURCE_ONLY this round -- so the
   MEASURABLE half of the documented reason is NOT yet in the vault. That is the gap.
2. eispack-netlib-1976 (SUPERSEDED) vs lapack-reference. Eigenproblem half of the same supersession.
   RUNNABLE, graded against the closed-form spectrum of the second-difference matrix.
3. des-reference (OBSOLETED_BY_ENVIRONMENT) vs tiny-aes-c (ACTIVE). Feistel network vs
   substitution-permutation network. Both RUNNABLE. DES's failure was NOT its round function --
   it was 56 bits of key against cheapening hardware. No round-trip test can show that.

## SOLO LOSERS
md5-rfc1321 (SUPERSEDED) -- RUNNABLE. See the dataset below; it has TWO deaths, and neither is
  visible to its own test suite.
spdylay (SUPERSEDED by RFC 7540) -- SOURCE_ONLY. Beaten by its own successor after winning the
  argument; the standard was built FROM it.
openssl-1.0.1f-heartbleed (FAILED, CVE-2014-0160) -- SOURCE_ONLY BY INTENT. Preserved so the
  missing bounds check can be read in its original context (ssl/d1_both.c). Never built here, and
  the vault carries no exploit for it. The replacement is one release away (1.0.1g).

## BEHAVIOUR DATASET: techne/fossils/pressure/ENVIRONMENT_ASSUMPTION_2026-09-13.json
The IDENTICAL extracted bytes (same sha256, verified in the artifact) run in two container worlds:
  sizeof(unsigned long) = 4  -> every digest matches the values printed in RFC 1321 section A.5
  sizeof(unsigned long) = 8  -> MD5("") = e4c23762ed2823a27e62a64b95c024e7, not d41d8cd98f00b204...
It compiles without warning, runs without error, exits 0, and is silently wrong. The cause is one
line: `typedef unsigned long int UINT4`, true in 1992, false on LP64. The fossil is therefore run
in the vault's 32-bit world (its ORIGINAL environment) and is NOT patched.
Worth noting for the atlas: in the 32-bit world every self-test PASSES, and the 2004 collision
break is invisible to all of them too. A document that grades itself cannot detect either of its
own deaths.

## RUN / VERIFY
    python -m techne.fossils.harvest run avida                 # evolution, ~140s build
    python -m techne.fossils.harvest run linpack-netlib-1979   # resid + exact all-ones solution
    python -m techne.fossils.harvest run eispack-netlib-1976   # closed-form spectrum
    python -m techne.fossils.harvest run md5-rfc1321           # 32-bit world; RFC's own digests
    python -m techne.fossils.harvest preservation --all        # completeness, not just hashes
    python techne/fossils/pressure/run_environment_assumption.py

## BOUNDARIES (honest)
- lapack-reference and spdylay are acquired but UNBUILT; the LINPACK-vs-LAPACK rate comparison,
  which is the measurable core of that pair, is NOT done.
- 18 recipes still fetch from the network at build/run time (named in PRESERVATION_CENSUS). avida's
  was eliminated this round; the other 17 were not.
- 15 older fossils carry legacy tag-based dispositions with state UNKNOWN; they should be migrated
  to the evidence-gated P7 field. Their dispositions are therefore NOT yet citation-backed.
- All oracles are Techne's own; no second seat has verified them.
- SINGLE_HOST_RISK UNCHANGED: 117 bodies on one host, no off-host mirror (Z: unreachable).
