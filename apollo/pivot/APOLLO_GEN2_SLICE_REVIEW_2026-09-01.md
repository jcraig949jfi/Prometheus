+==============================================================================+
|                                                                              |
|   APOLLO GEN-2 -- VERTICAL SLICE REVIEW                                       |
|   First end-to-end run of the Serendipity substrate-miner loop against the    |
|   live Foundry, plus the legacy-cleanup work that preceded it.               |
|                                                                              |
|   Prepared by : Apollo (M2), 2026-09-01                                       |
|   For         : James (HITL) + external frontier reviewers                   |
|   Status      : results report + request for critique                        |
|   Self-contained: every number was measured on this machine against the      |
|                   live host; no repo access needed to review.               |
|                                                                              |
+==============================================================================+


0. WHAT THIS PACKET COVERS
--------------------------
Apollo was reassigned (Gen-2 charter, same day) from "prove evolution discovers
intelligence" to SUBSTRATE MINER inside an emerging "Serendipity Foundry" ecology.
This packet reports the first working slice of that role: a thin vertical loop that
round-trips against the live Foundry server, and the credential + legacy-cleanup work
that had to land first. It is a PLUMBING milestone. It is explicitly NOT a capability
result, and the one science number in it is a null, reported straight.


1. THE FOUNDRY, AS MEASURED (not as documented)
-----------------------------------------------
The Serendipity Foundry ("M1") is a release-pinned HTTPS server on machine one at
192.168.1.202:8799, driven by a std-lib client with a strict transport contract: a
release pin the client refuses to run against if mismatched, and a rule that the
network is NEVER a scientific result -- a timeout/5xx raises "indeterminate" and must
be reconciled against the host's authoritative ledger before anything is assumed.

Live facts captured this session:
  - release source_tree_hash = 50b5c232...  (git 71b29593, 211 files)
  - 40 REST routes; ledger length ~87,555 events; ~17,960 artifacts (shared by all
    research seats on the host)
  - 3 engines:  stackvm-v1 (DETERMINISTIC, bit-exact replay),
                push-pyshgp (seeded_stochastic), treegp-deap (seeded_stochastic)
  - 4 search drivers: random, objective, novelty, map_elites
                (a neighbouring seat, D-12/D-13, uses objective+random only, so
                 novelty+map_elites are Apollo's lane)
  - tasks are integer function-induction: inputs:[int] -> output:int


2. WHAT WAS BUILT (thin adapter boundary)
-----------------------------------------
The charter mandates a thin adapter so a fast-moving Foundry means editing an adapter,
not rewriting Apollo. Delivered under apollo/serendipity/:

  foundry_creds.py  Credential + client boundary. Loads the bearer token from the
                    operator kit AT RUNTIME and hands it straight to the client --
                    never logged, journaled, printed, or committed. Pins the TLS cert.
                    A .gitignore guards the dir against an accidentally-copied kit.
  remote.py         Vendored canonical Foundry client (std-lib only), sha256
                    bdd6f0771f5c -- byte-identical to the neighbouring seat's audited
                    copy.
  world_adapter.py  Apollo authors its OWN isolated task (client_id=apollo in
                    admin_metadata); never mutates/deletes another seat's world.
  eval_adapter.py   Wraps budget-consuming /v0/search and /v0/evaluate under the
                    reconcile-on-indeterminate doctrine (never blindly re-spends
                    budget).
  fossil.py         FossilEmitter + ProvenanceAdapter (content hash over the record).
  slice_pilot.py    The orchestrator that runs the whole loop and emits one fossil.
  FOUNDRY_API_NOTES.md  40-route surface + contract facts + operating envelope,
                    version-pinned to 50b5c232.

Preceding legacy cleanup (same session, separately committed):
  - Rebuilt the missing E9 scoring harness (apollo/scripts/e9_score.py). E9 is the
    2026-08-25 result that killed Apollo's headline 0.833 as a capability number; its
    RESULT.json was committed but the SCRIPT was not, so the falsification was not
    reproducible from source. The rebuilt scorer reproduces it EXACTLY: raw 0.0476 /
    mix-adjusted 0.0667 / home 0.6000, with the 40-abstained / 2-correct / 0-guessed
    failure shape. (Two reproduction discrepancies were found and resolved rather than
    papered over: the abstain sentinel is the empty string, not None; and the trivial
    floors are tie-aware expected scores read from the battery author's metadata.)


3. THE TEST: THE VERTICAL SLICE, STAGE BY STAGE
-----------------------------------------------
One command drives the full charter S19 loop on engine stackvm-v1, an Apollo-owned
task f(x)=3x+1 (10 train + 5 test cases), budget 300, seed 20260901. Result, verbatim:

  world      : Apollo-authored task created (content-addressed sha256:84133b8b...)
  burst      : random driver     -> solved=False best_fitness=0.10  evals=300  75.2s
  burst      : map_elites driver -> solved=False best_fitness=0.10  evals=300  58.1s
               map_elites archive: 11/64 cells, coverage 0.172, qd_score 0.40
  organism   : create_random artifact, 40 genotype bytes, creation_event_seq 93756
  evaluate   : event_seq 93757, result_hash sha256:abb9aaea...
  capture    : artifact + genotype (base64 bytecode) + lineage all retrieved
  replay     : event_seq 93757 -> MATCH=True, engine_version_mismatch=False
  fossil     : emitted, provenance sha256:d94a88cb5130...

Every stage returned real host data. The reproducibility check is the load-bearing
one: /v0/replay re-executed the recorded evaluation and returned
original_result_hash == replayed_result_hash (bit-exact), with no engine-version drift.


4. RESULT #1 (PLUMBING): PASS
-----------------------------
The loop round-trips end to end against the live host, and the deterministic engine
replays bit-exactly. Apollo can now: author an isolated world, run a bounded
evolutionary burst, evaluate a concrete organism, capture its genotype + lineage, and
prove the evaluation reproduces -- then preserve all of it as a provenance-hashed
fossil. This is the reusable unit the charter's periodic jobs are meant to be built
from.


5. RESULT #2 (SCIENCE): AN HONEST NULL
--------------------------------------
At budget 300, NEITHER map_elites NOR random solved f(x)=3x+1 -- both returned
best_fitness 0.10, solved=False. map_elites' ONLY differentiation from the random
baseline was that it populated a quality-diversity archive (11/64 cells, coverage
0.172); it showed NO solve advantage over random at this budget.

This is reported as a null, not spun. The charter's own doctrine (S18) is "do not
confuse evolutionary activity with evolutionary progress," and a QD archive filling up
is activity. Whether map_elites beats random on this world is a budget-dependent
question this slice did not answer and did not try to -- the slice's purpose was the
plumbing, and the science comparison at budget 300 is simply inconclusive-toward-null.


6. INCIDENTS AND WHAT THEY VALIDATED
------------------------------------
a) TRANSPORT CONTRACT, exercised for real. An early map_elites burst at budget 1500
   exceeded a 60s client read-timeout and raised "indeterminate." The orphaned trace
   was reconciled against the ledger: found=false, committed=false -- i.e. NO budget
   was spent; the timeout was purely client-side reception. The safety contract
   behaved exactly as designed: a lost connection produced no fabricated result and no
   silent double-spend.

b) TWO BUGS found and fixed mid-slice (a discrepancy is a finding, not a nuisance):
   - the driver report is nested under a `report` key; a first version read the
     top level and silently logged None for every science field, hiding real numbers.
   - the replayable event_seq comes directly off the /v0/evaluate response; an initial
     ledger-scan approach was unnecessary and fragile on an 87k-event shared ledger.
   The first (broken-parse) fossil was DISCARDED rather than kept -- its nulls were a
   bug, not a real null, and keeping it would have been a misleading artifact.


7. OPERATING ENVELOPE (for anyone sizing runs on this host)
-----------------------------------------------------------
  - /v0/search is SYNCHRONOUS and slow: ~60-75s per 300-evaluation burst on stackvm.
    Budget scales wall-clock roughly linearly; size modestly on a shared host.
  - Use a patient client timeout (>=300s) for budget-consuming calls, or the receive
    times out mid-run (a false indeterminate; the server is fine).
  - The host is shared. Apollo isolates by authoring its own tasks and tagging every
    call client_id=apollo; it never mutates another seat's worlds. Peers currently on
    the host: D-12/D-13 (a displacement/heritability study) and Harmonia A.


8. WHAT THIS DOES AND DOES NOT ESTABLISH
----------------------------------------
ESTABLISHES:
  - Apollo can operate as a Foundry client end to end, safely and reproducibly.
  - The adapter boundary is thin enough that a Foundry release (one is expected
    ~2026-09-02) should require editing adapters + the pinned notes, not Apollo.
  - The E9 falsification of Apollo's old headline is now reproducible from source.

DOES NOT ESTABLISH:
  - Anything about whether evolutionary search discovers useful reasoning structure
    in this ecology. Zero capability claims. The one science reading is a null.
  - That map_elites/novelty beat baselines here -- untested at meaningful budget.
  - That any Foundry world hosts structure worth mining -- not yet looked.


9. QUESTIONS FOR THE REVIEWER
-----------------------------
  Q1. The slice decouples "plumbing works" from "search solves" by injecting a
      create_random organism so evaluate/replay always have input. Is that a fair
      separation, or does it risk making the loop look healthier than the science
      warrants? (Apollo's view: fair -- the two are genuinely different claims -- but
      attack it.)
  Q2. f(x)=3x+1 was chosen as a simple, clearly Apollo-authored world. Is an affine
      integer task too trivial to be diagnostic, or is triviality correct for a
      plumbing slice (save the hard worlds for a real budget)?
  Q3. What is the RIGHT first science question on this substrate: map_elites-vs-random
      at a budget that can actually solve, novelty-driven QD coverage, or transfer
      across the three engines? (Charter lanes A/B/C all apply; which first?)
  Q4. Retire-check still stands from the prior packet: none of this bears on the
      central Gen-1 null (evolution exploited human-supplied capability, never widened
      it autonomously). Does a working Foundry loop change that calculus, or is it
      just a cleaner apparatus for re-confirming the same null at larger scale?


10. ARTIFACTS (for a reviewer with repo access)
-----------------------------------------------
  apollo/serendipity/                        adapter boundary (7 files) + API notes
  apollo/cycles/serendipity_slice/           the verified fossil + run log
  apollo/scripts/e9_score.py                 rebuilt E9 scorer (repro 0.0667)
  roles/Apollo/STATUS.txt                    machine-readable current state
  roles/Apollo/CHARTER_GEN2_serendipity_20260901.md   the active mission
  Commits (on origin/main): charter+E9 scorer, credential boundary, vertical slice.

+==============================================================================+
|  END -- reply with answers to section 9, and, as before, an explicit         |
|  willingness to say "this apparatus is not worth continuing." A working loop  |
|  is not the same as a loop worth running.                                     |
+==============================================================================+
