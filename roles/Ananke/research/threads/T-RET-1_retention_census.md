# T-RET-1  Does PTE contain a nontrivial retention regime? (SI01 successor, step 1)

QUESTION
After a trial's query has passed, does any PTE champion keep information
about that trial's cue in its endogenous state, and for how long? Is that
information recoverable (decodable) and/or still causally effective?
"Nontrivial" excludes (a) nothing retained and (b) retention that is
only chaotic divergence with no recoverable cue.

WHY
The operator's SI01 successor: only if PTE has a nontrivial retention
regime is an irreversibility experiment around the ACTUAL mechanism
worth designing. If PTE retains nothing past the query, PTE is the wrong
lens for Selective Irreversibility.

EVIDENCE POINTERS
- Exactness: PTE is all-integer and deterministic, and its exogenous
  randomness is keyed by (world seed, tick, site). Single-cue twins
  therefore differ ONLY by the cue's causal consequences:
  lens.cue_arrival_profile shows the construction (roles/Ananke/research/
  instruments/INSTRUMENT_TEMPORAL_REACH.md).
- Carrier classes: spikes/out/s_ct.json (12 cells), T-CT-1 census when
  done; M2 fresh genomes spikes/out/champions_m2.json.
- Prior steward-era framing (historical, advisory only):
  roles/Ananke/prompts/2026-09-25_pte_si01_directive/ and the recovery
  tiers MERGED / PRESENT / RECOVERABLE / ACCESSIBLE discussed there.
- Prior art on fading memory and memory capacity:
  PRIOR_ART_temporal_distributed_computation.md s3.

STEPS
1 PLAN.md (before running): the definitions.
  - MERGE TIME: the first tick after trial k's query at which the
    twins' full endogenous state (S, E, r, Kp, w, inbox, in-flight ring)
    is bitwise equal. Once merged, the cue is provably gone.
  - PRESENT DURATION: time until merge, or censored at the episode end.
  - RECOVERABLE at lag j: a held-out decoder of cue k from state at the
    end of trial k+j beats a permutation null. Keep the decoder small:
    sign of per-carrier sums, fitted on half the pairs.
  - EFFECTIVE at lag j: a carrier swap of the full state at trial k+j's
    onset changes trial k+j's answer. It should not, since targets are
    iid, so any effect = interference.
2 Run on the 12 D-wave cells + 4 M2 champions, trial k = 3, lags
  j = 0..6 (CPU, 2 threads, or a GPU lease).
3 Classify each champion as FORGETS (merge within trial k+1),
  DIVERGES-UNRECOVERABLE (never merges; decoders at chance),
  RETAINS-RECOVERABLE (decodable at j >= 2), or INTERFERES (effective at
  j >= 1).
DECISION
"PTE has a nontrivial retention regime" iff >= 1 champion is
RETAINS-RECOVERABLE at j >= 2 with permutation p < 0.01 after
multiple-comparison correction over champions and lags. Then write the
SI successor question around that champion's actual carrier.
STOP. 3 h. Report which carrier classes retain and which forget.
