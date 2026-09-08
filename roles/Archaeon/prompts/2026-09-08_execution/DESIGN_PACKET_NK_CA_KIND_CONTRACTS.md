================================================================================
DESIGN PROPOSAL FOR EXTERNAL REVIEW -- the two first-family kind contracts
Prepared by Archaeon for the operator, 2026-09-08
Baseline: archaeon/v0 at 5191c3383; engine be65b0efa; Vivarium 19e13e5b1
Reviewers: Harmonia (nulls, controls, stipulated outcomes), Daedalus (NK
           executor), Herakles (CA conventions), Vivarium (kind contracts)
Decision owner: operator. Nothing here is implemented; A1 waits on this.
================================================================================

WHY A PACKET. Two kinds are on the critical path (WP-A1, WP-C1). Each has
scientific parameters that its implementer must not choose alone: how the
landscape is built, what the witness means, what "solved" means, which
symmetries are exact, what outcomes are stipulated in advance. Deciding
them here, once, in writing, lets the owners implement without negotiation.

--------------------------------------------------------------------------------
PART 1. nk_landscape_v0 (Branch A, method evaluation)
--------------------------------------------------------------------------------
PURPOSE, NAMED. A method-evaluation instrument: authored difficulty with a
one-parameter interaction control. It may still yield an unplanned
regularity about search or landscape structure (BRANCHES.md s0), bounded to
its domain.

CONTRACT
  kind         nk_landscape_v0        stateless across executions
  payload      bits (str, binary, len == length)
               length (int, 8..64)
               k (int, 0..length-1)
  world        seed_root (int)        landscape identity = (seed_root, length, k)
  result       score (float in [0,1]), contribution (list[float], len ==
               length, each in [0,1]), solved (bool), executor,
               reproducibility = BIT_DETERMINISTIC
  measurements nk_landscape_v0.score (HIGHER_IS_BETTER, [0,1]);
               nk_landscape_v0.contribution (vector; per-locus)

CONSTRUCTION (decision D-A1-1)
  Option A  classic Kauffman NK: locus i depends on itself and k others;
            neighbours chosen uniformly without replacement from the other
            loci by a hash of (seed_root, length, k, i); contribution table
            for locus i has 2^(k+1) entries drawn uniform in [0,1] from a
            hash of (seed_root, length, k, i, pattern). score = mean of the
            length contributions.
  Option B  adjacent-neighbour NK (loci i+1..i+k mod length): simpler,
            structured, but its symmetry group is smaller and the
            permutation null is weaker.
  RECOMMEND A. Reason: the permutation null (below) is exact and strong only
  when neighbour choice is itself seed-derived per locus; B makes the
  landscape circulant and lets a method exploit the structure by accident.

k = 0 (decision D-A1-2)
  Under Option A with k = 0 the score is a sum of independent per-locus
  tables, i.e. additive with random per-locus weights. It is NOT onemax
  (onemax has all weights equal and a fixed target). RECOMMEND: keep the
  general construction at k = 0 and register a separate note that onemax is
  the special case with all contribution tables equal to {0,1}; do NOT
  special-case k = 0 to reproduce evaluate_bitstring. Reason: the mechanism
  control must differ from the treatment in ONE thing (k), not two.

WITNESS SEMANTICS (decision D-A1-3)
  contribution[i] is the realised table value for locus i under the
  candidate. It is a per-locus report, NOT a list of corrections: for k > 0
  raising one contribution can lower its neighbours'. The contract says so
  in the result docstring and the registry note.

SOLVED SEMANTICS (decision D-A1-4)
  Option A  solved = (score >= 1.0): attainable only if every table's max
            is 1.0 at a jointly consistent pattern -- generally FALSE for
            k > 0, so the gate cannot fire. Rejected.
  Option B  solved = (score >= global optimum of this landscape), where the
            optimum is computed by exhaustive enumeration at admission for
            length <= 20 and declared UNKNOWN above (solved = null).
  Option C  no solved field; score only.
  RECOMMEND B for length <= 20 and C above it. Reason: the attainable range
  rule; a gate that cannot fire is not a gate. The enumerated optimum is
  stored with the landscape identity, never recomputed silently.

EXCHANGEABILITY NULL (Harmonia to accept)
  Permute loci by a seed-derived permutation P, applied JOINTLY to: the
  candidate bits, the neighbour lists, the table indexing, and the
  contribution vector. score is invariant; contribution matches after P^-1.
  Known answer: zero effect. A candidate-only permutation must FAIL (A2-b).

MECHANISM CONTROL
  Same seed_root, same length, k = 0. Everything else identical.

KILL PRECONDITION (before A3-acq)
  One-flip hill climber from 20 random starts at the chosen (length, k):
  if it reaches the enumerated optimum in <= 2*length queries on >= 90% of
  starts, the landscape is not doing the work at this k. Trapped-start
  fraction enumerated first at length <= 16 (A1-e fixture).

STIPULATED OUTCOMES (written before A3 runs; Harmonia may extend)
  S1  at k = 0 a one-flip climber reaches the optimum in <= length queries
  S2  at k > 0 some fraction of starts are trapped; the fraction rises with k
  S3  D3 on a floor-sized NK corpus fires at the calibrated rate (~0.083 per
      region at 8/32) regardless of k, because the score's variance across
      random candidates is a property of the table distribution, not of k
  S4  the permutation null shows exactly zero effect
  Anything else that survives the null and the control is a candidate
  under BRANCHES.md s0, for Harmonia.

FIRST CORPUS (A3-acq; issued by Archaeon via the human path once admitted)
  length 24; k in {0, 2, 4}; 3 seed_roots per k; 20 random candidates per
  landscape (fixed-target series, C-0); 180 specs; minutes of compute.

ACCEPTANCE FOR THE CONTRACT
  Tests A1-a..e in WORK_PACKAGES.md; measurements registered on live M1;
  Vivarium parity fixture; Archaeon's A2 templates check runnable +
  drawable + buildable.

--------------------------------------------------------------------------------
PART 2. ca_density_v0 (Branch C, the more direct route to collective
        computation)
--------------------------------------------------------------------------------
PURPOSE, NAMED. A spatial, stateful world with local observation, action
that changes the neighbours' next observation, and the lattice as memory;
real recovered organisms; literature-known strategy classes as calibration
anchors, not findings.

CONTRACT
  kind         ca_density_v0          stateless across executions (the
                                      lattice lives inside one execution)
  payload      rule_hex (str, 32 hex chars = 128-bit table; leftmost
               neighbour = MSB -- Herakles pins the convention)
               radius (int; 3 only in v0; others refused)
               n_cells (int; 149 in v0; odd required)
               steps (int; 320 in v0)
               n_ic (int, 1..1000)
               ic_density_set (list[float] in (0,1); ICs drawn from these
               densities in equal shares; the density-0.5 unbiased
               distribution is the declared default)
  world        seed_root (int)        IC sample identity = (seed_root, n_ic,
                                      ic_density_set, n_cells)
  result       accuracy (float in [0,1]); misclassified_ic (list[int],
               indices into the IC sample, bounded to n_ic); spacetime_digest
               (str, sha256 of the normalised space-time array of the first
               IC); n_ic_evaluated (int); executor; reproducibility =
               BIT_DETERMINISTIC
  measurements ca_density_v0.accuracy (HIGHER_IS_BETTER, [0,1])

MAJORITY / TIE CONVENTION (decision D-C1-1)
  n_cells odd in v0, so density > 0.5 or < 0.5 is always defined; the
  target is all-1s if initial density > 0.5 else all-0s; correctness is
  "final lattice equals the target". Even n_cells is REFUSED in v0 (a tie
  rule would have to transform consistently under complement before any
  complement-invariance claim, C2-a).

EXACT SYMMETRIES (Herakles to pin; Harmonia to accept as nulls)
  Reflection: reflect the rule table's neighbourhood index AND the realised
  IC; the trajectory is the mirror image; the correctness mask is identical.
  Complement: complement the table's output bits and its input index, the
  IC, AND the majority target; correctness mask identical.
  Compared on NORMALISED trajectories (un-reflect / un-complement before
  comparing), never raw hashes. "Same seed" alone is not the symmetry.
  Known answer: identical masks; a rule-only same-IC transformation must be
  DETECTED as wrong (C2-b).

MECHANISM CONTROLS
  r = 0 control: an explicit centre-only rule family (2-entry table), the
  correct table size enforced; it reads only the centre cell.
  T = 1 control: one declared update; reported as a HORIZON change, not as
  removal of state or memory.

HISTORICAL ANCHOR (C1-e, separate qualification report)
  The six recovered genomes under the source's conventions and a declared
  IC sample; literature accuracies (~0.7-0.8, unfetched lead) are what
  C1-e measures, with a prespecified uncertainty rule. A mismatch is
  diagnosed across conventions, horizon, sampling, transcription,
  implementation -- never presumed a verifier defect.

KILL / HOLD (before C3-acq)
  Reflection null fails on the historical genomes -> HOLD the
  implementation and diagnose; says nothing about the direction.
  Historical genomes indistinguishable from 50 random rules at adequate
  sensitivity (SE ~0.05 at n_ic = 100, 0.016 at 1000; the literature gap
  is ~0.2-0.3) -> the task instance or conventions are wrong; fix first.

STIPULATED OUTCOMES (written before C3 runs; Harmonia may extend)
  S1  random rules score near the density prior (~0.5 at density-0.5 ICs)
  S2  the six historical genomes score in the literature band under the
      source conventions; if they do, that is a calibration anchor
  S3  block-expanding and particle strategies, if they appear in random or
      directed rules, are rediscoveries and are labelled so
  S4  reflection and complement nulls show exactly zero effect
  Anything else that survives the nulls and controls -- a strategy class
  not in the literature, or structure in the random-rule record on a
  declared rule-table descriptor that predicts accuracy -- is a candidate
  under BRANCHES.md s0, for Harmonia.

FIRST CORPUS (C3; issued by Archaeon via the human path once admitted)
  C3-hist: the six genomes x 4 ordered repeats (paired ICs).
  C3-acq: 50 random rule tables x 4 ordered repeats, same paired ICs,
  n_ic = 100, steps 320, n_cells 149. ~224 observations; ~2 minutes.

ACCEPTANCE FOR THE CONTRACT
  Tests C1-a..e; the six genomes' golden results on small fixed ICs;
  Vivarium parity fixture; Archaeon's C2 templates (reflection null, r0
  control, t1 control, uniform) check runnable + drawable + buildable.

--------------------------------------------------------------------------------
PART 3. what the reviewers are asked to decide
--------------------------------------------------------------------------------
  D-A1-1  NK construction: Option A (random neighbours) or B (adjacent)
  D-A1-2  k = 0 is the general construction, not a special case of onemax
  D-A1-3  contribution[] is a per-locus report, never a correction list
  D-A1-4  solved = enumerated optimum at length <= 20; absent above
  D-C1-1  odd n_cells only in v0; even refused
  Nulls   NK joint permutation; CA joint reflection AND complement
  Lists   the two stipulated-outcomes lists, to extend or strike
  Kills   the two preconditions, to accept or replace

Accept / amend / refuse each with the reason. On acceptance Daedalus starts
A1 and Herakles's C1 conventions are considered pinned as stated here
unless Herakles amends them in C1's report.
================================================================================
END OF PACKET
================================================================================
