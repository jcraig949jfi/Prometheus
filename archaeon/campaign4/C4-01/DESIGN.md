+=====================================================================+
|  C4-01 -- DAMAGE-BOUNDARY CENSUS: PREREGISTRATION DRAFT              |
|  Archaeon[m2-49ee5a4d]   2026-09-18   Status: DRAFT, NO ROW RUN      |
|  Sealed by the harness (PREREG.json, prereg_digest) at run time      |
|  with THIS content; any change after sealing is an annotation.       |
+=====================================================================+

Written while the launch gate is RED (G1 Daedalus, G5 Proteus). Nothing
executes until `python -m archaeon.campaign4.launch_gate` prints
campaign_may_start True. Vocabulary: program variant / edit / variant
set; the directive's labels are quoted once as defined labels.

-----------------------------------------------------------------------
QUESTION
-----------------------------------------------------------------------
Where does the frozen substrate (runtime 73f110e2..., grammar v0.4
5043f5e1..., affordance table f1607ee8..., profile pfp1:625bc70456ebfa20)
destroy variation? For each of the 12 grammar operators applied once to
each of the 57 starting program variants, what is the distribution over
the directive's outcome classes D0..D7, and what is the distribution of
behavioral displacement conditional on the variant executing?

-----------------------------------------------------------------------
PARENTS (fixed, manifest-backed)
-----------------------------------------------------------------------
All 57 entries of archaeon/campaign4/STARTING_POPULATION.json (canonical
digest sha256:7f03cc82...), strata by `class`:
  gen0_random 12 | w0_solver 15 | shelf 19 | delay_general 11
No variant of unknown ancestry enters (gate G5). Parent environment per
stratum: D4-004. Every parent is evaluated on its own environment and on
the three OTHER environments before any edit is scored, so parent
baselines are measured, not inherited.

-----------------------------------------------------------------------
EDITS (preregistered set; no selection)
-----------------------------------------------------------------------
For each parent p, each operator o in the frozen grammar's 12 names
(insertion, deletion, duplication, movement, replacement,
operand_perturbation, reference_redirection, region_swap, splice,
zeroing, randomization, config_perturbation; unreachable_removal is the
grammar's removed operator and is NOT applied), and each draw r in 1..8:
  rng = SplitMix64(seed_from("c4.01.edit", 20260921, organism_id, o, r))
  child, op_record = grammar.mutate(parent_manifest, rng, mate=None, name=o)
Splice with no mate splices from self (the grammar's own rule). 57 x 12
x 8 = 5,472 edits. An operator that returns its "noop" record (at_max,
at_min, too_short, bounds) is an ELIGIBILITY fact: counted under
"could not apply", reported beside every rate, never folded into D5.
Operator args carry the touched position (`pos`, `word`, `a`/`b`,
`src`); the STRUCTURAL REGION of an edit is the affordance category of
the instruction at that position in the PARENT (halt_yield, read_write,
indirection, arithmetic, logical, comparison, control, opaque_io,
randomness), or MANIFEST for config_perturbation, or UNKNOWN when the
operator records no position.

-----------------------------------------------------------------------
EVALUATION (deterministic, common random numbers)
-----------------------------------------------------------------------
archaeon.wse.evolve.evaluate(manifest, episodes, rng_seed=0,
reward_mode="per_ask") with episodes = worlds.episodes_for(spec,
20260921, "train", index=1, n=16) for the parent environment, and the
same call on each OTHER environment (D4-004). Parent and every child see
the SAME 16 episodes per environment (CRN): displacement is then a
property of the edit, not of the draw.

-----------------------------------------------------------------------
CLASSIFICATION (D4-003; the label is not the evidence)
-----------------------------------------------------------------------
  D0 UNDECODABLE        mutate raised ManifestError (validation failed)
  D1 EXECUTION_FAULT    CANNOT FIRE: total interpreter (D4-002);
                        reported with eligible count 0 and the reason
  D2 DEGENERATE         answered_share == 0, or one constant answer on
                        every ask of the parent environment
  D7 IMPROVED_OR_NOVEL  reward > parent + 1/16 on the parent environment
  D6 EXAPTIVE           not D7; on >= 1 OTHER environment reward >=
                        parent(there) + 1/16 AND >= 3/16
  D5 NEUTRAL            |reward - parent| <= 1/16 on the parent environment
  D4 VIABLE_WORSE       reward >= 3/16 and reward < parent - 1/16
  D3 DISTINCT_NONVIABLE reward < 3/16 and displacement > 0
Precedence as listed (D0, D2, D7, D6, D5, D4, D3). A child with
displacement 0 and reward equal to the parent is D5 with displacement 0
(recorded; a "silent" edit). Every child row keeps the raw evaluate()
dict for every environment, the op_record, the parent id, the region,
len_before/len_after, statuses, ops_per_episode, and
structural_descriptor(child) beside structural_descriptor(parent)
(proteus.eval.population_manifest.structural_descriptor).

-----------------------------------------------------------------------
PRIMARY OUTPUT
-----------------------------------------------------------------------
The flow table P(Dk | operator) and P(Dk | operator, stratum) and
P(Dk | region) with counts and eligible counts (applied vs could-not-
apply), Wilson 95% bands on every rate, and the displacement
distribution (histogram over 0, (0,0.25], (0.25,0.5], (0.5,0.75],
(0.75,1]) conditional on executed (= all applied edits, D4-002) by
operator. The DAMAGE GEOMETRY MAP's first column (edit magnitude 1) is
filled from this table.

-----------------------------------------------------------------------
CONTROLS (run first; a failing control closes the slot INSTRUMENT_INVALID)
-----------------------------------------------------------------------
  negative  identity edit (child = parent): 57/57 D5 with displacement 0
  positive  whole-genome randomization (randomization with k = every
            instruction, applied by the census code, NOT a grammar
            operator): expected >= 45/57 in D2 or D3 (a destroyed
            program should read as destroyed)
  cheat     the D7 detector on a child whose reward is set to 1.0 by
            hand in a copy of the row (no execution): must read D7;
            confirms the classifier reads the field it claims to
  self      re-running the census for one parent with the same seeds
            reproduces its 96 rows byte-for-byte (determinism)

-----------------------------------------------------------------------
FALSIFYING OUTCOME (the directive's, made testable)
-----------------------------------------------------------------------
"Nearly all mutation classes show the same result distribution": for
every pair of operators the total variation distance between their
D-distributions (over applied edits, pooled strata) is < 0.05. Or "the
instrumentation cannot distinguish where loss occurs": region is
UNKNOWN for > 20% of applied edits, or D0 absorbs > 50% of edits.
Either is RECORDED as the census's result; nothing is fixed inside C4-01.

-----------------------------------------------------------------------
CLAIM CEILING / TYPED DISPOSITIONS
-----------------------------------------------------------------------
A measured map at 8 draws per (parent, operator) on one frozen substrate;
no mechanism, no claim about evolvability. Dispositions: SUPPORTED (map
produced, controls pass, at least one operator pair with TVD >= 0.05),
NEGATIVE (map produced, controls pass, all pairs < 0.05: the falsifying
outcome), INSTRUMENT_INVALID (a control fails), SKIPPED_RESOURCE_BOUND
(not expected: 5,472 x 4 evaluations, minutes).

-----------------------------------------------------------------------
BUDGET / IDENTITY / RECORDS
-----------------------------------------------------------------------
parents 57; operators 12; draws 8; environments 4; E 16; campaign seed
20260921; client cmp4-archaeon; engine eng_906356f7 (9.0.1, 699ca0f9,
schema 9); one engine world for the slot, one experiment per (parent,
operator) group carrying its 8 child outcomes as one observation each
(684 observations) plus 57 parent-baseline observations; rows.json keeps
every child row; PEW ingest by the campaign-4 reader at the S6 commit.
Execution path: D4-001.
