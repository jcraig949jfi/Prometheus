# ENSORAIN WTP-01 "WILD TENSOR PHYSICS" -- campaign preregistration

Currency: 2026-09-24. Seat Ensorain[m2-14baf7d5]. Authority: operator
foundry directive, roles/Ensorain/prompts/2026-09-24_foundry_directive/
(verbatim). Committed BEFORE the engine runs a single world. WTP-01 is
exploratory; what is fixed here is how an observation is PROMOTED and how
the campaign VERDICT (directive s58) is reached, so neither can drift
toward whatever turns up.

## 1. Engine (directive s55; built next, in ensorain/wtp/)

WorldGenome (serialisable, hashable, mutable, replayable) with laws:
substrate (mode sizes, field generator + an atom chain), geometry,
observation, transition (drift, basis change, rewiring, catastrophes),
irreversibility (one-way edges, closing doors, memory-hazard edges),
resource (energy, metabolism, harvest, query payoffs, prices for compute,
memory reads/writes, moves, probes, rollouts), memory (substrate,
capacity, precision, forgetting geometry), learning (rule), credit
(delay, radius, noise, sign), search (policy incl. counterfactual depth
and active probes), boundary (sealed / external marks shared by a small
population), time (lifetime, change timescales). Operator registry with
the directive's metadata; legality preflight; mutation engine with
several generators (random, grammar-structured, local mutation, large
mutation, recombination, novelty, anomaly-directed). Every run keeps:
genome + hash, seed, code commit, hardware fingerprint, library versions,
initial/final state digests, event-stream digest (full events for
anomalies), metrics, ancestry, mutation provenance, event markers.
Replay = deterministic re-execution from (genome, seed, commit) with a
digest check; step inspection by re-execution with hooks.

## 2. Observables (vector; no single fitness -- s44)

U net energy; survival; CG = competence gain on a fixed probe battery
(NLMSE of the organism's predictions of the field at 128 battery cells,
end of life minus birth: "how much easier are future problems"); E2C =
CG / log10(1 + steps x compute x memory) (s30); compression = CG per
persistent float; reach = harvest rate second half / first half;
option preservation = reachable-node fraction at end (irreversible
worlds); rank dynamics (factorised memories); external-mark use; probe
and rollout use; transfer (Wave D only).

## 3. Anomaly detectors (Wave A; flags, not findings)

  A1 COMPETENCE OUTLIER  CG robust z > 4 within its memory-substrate class
  A2 JUMP                battery NLMSE rises in one checkpoint by > 5x the
                         life's median |increment| and > 0.3 absolute
  A3 MEMORYLESS PREDICTION  CG > 0.3 with <= 16 internal persistent floats
  A4 ANTI-LEARNING       CG < -1 (the organism ends much worse than birth)
  A5 REACH EXPANSION     reach > 3 with CG > 0
  A6 METRIC DISAGREEMENT top-5% U with CG <= 0, or top-5% CG with
                         bottom-20% U

## 4. Promotion states (directive s50) -- rules fixed now

  ANOMALY       flagged by a detector in Wave A
  REPLICATED    Wave B: the flagged property recurs in >= 3 of 5 fresh
                seeds (same genome) by the same detector threshold
  FALSIFIED     recurs in <= 1 of 5
  WEAK SIGNAL   recurs in 2 of 5
  ARTIFACT      a competence-type anomaly (A1/A2/A3/A5) whose
                SHUFFLED-LATENT control (field values permuted over cells,
                everything else identical) reproduces the property in
                >= 3 of 5 seeds
  CAUSAL SUPPORT Wave C: in the anomaly's world family (single-dial
                neighbours: memory x0.5 and x2, no credit delay, shuffled
                topology, shuffled latents, reversible, noisier, no
                external marks, no rollouts, frozen world) at least one
                neighbour removes the property and at least one keeps it
                (3 seeds each; majority rule)
  TRANSFERRED   Wave D: memory transplanted into a reskinned world (mode
                labels permuted) keeps >= 50% of CG over a fresh organism
  PHASE BOUNDARY a single-dial sweep (7 levels x 4 seeds) around a
                REPLICATED anomaly where the property jumps between two
                adjacent levels by > 3x the pooled within-level sd, in
                both seed halves

## 5. Verdict (directive s58), fixed now

FOUND RICH SEARCH PHYSICS -- CONTINUE iff ALL of:
  (a) >= 3 REPLICATED anomalies not ARTIFACT, spanning >= 2 distinct
      mechanism classes (differing in memory substrate, geometry family
      or learning law);
  (b) >= 1 PHASE BOUNDARY;
  (c) >= 5% of valid Wave-A worlds have CG above the 95th percentile of
      the shuffled-latent control CG distribution, and those worlds
      occupy >= 20 behavioural niches (cells of CG bin x U bin x memory-
      size bin x reach bin).
NO USEFUL SIGNAL -- PARK iff no REPLICATED non-ARTIFACT anomaly exists.
SEARCH SPACE MOSTLY DEGENERATE -- REDESIGN otherwise (signal exists but
  narrow: one mechanism class, < 5% competent worlds, or no boundary).

## 6. Budget and generator mix (s43, s56, s57)

Wave A: >= 3,000 worlds in generations of 500, one seed each, lifetime
<= 600 steps, <= 4,096 cells. Generator mix per generation after the
first: 30% pure random, 20% grammar-structured toward the s57 special
targets, 20% novelty (farthest from the archive in descriptor space),
20% local/large mutation of anomalies and niche elites, 10%
recombination. Wave B: up to 40 anomalies x 5 seeds + shuffled-latent
control. Wave C: up to 8 REPLICATED anomalies x world family + up to 3
sweeps. Wave D: up to 5 autopsies. Wave E: up to 200 recombinants of
surviving mechanisms. Seeds: A 100000+, B 200000+, C 300000+,
D 400000+, E 500000+. CPU reference implementation first; no GPU on the
critical path (s34: "after CPU/reference correctness exists").

## 7. Seat prediction (losable)

REDESIGN (p .45): a handful of replicated competence anomalies, mostly
one mechanism class (a factorised memory matched to a factorised field),
external marks as the second class; boundaries possible along capacity.
CONTINUE (p .35). PARK (p .2).
