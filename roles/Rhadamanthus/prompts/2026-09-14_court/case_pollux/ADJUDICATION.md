# ADJUDICATION -- case POLLUX

Court date: 2026-09-14.  Judge: Rhadamanthus (Keeper of Necropolis).
Grave: charon/agents/pollux (daemon.py, HEAD byte-identical to 43b094552).
Readers on record (all fresh contexts, all under case_pollux/COMMON_RULES.md):
  NECROMANCER_report.md      25 propositions, certificate DESIGN_ERROR / rival CONSUMER_ABSENT
  CLERIC_challenge.md        audit of P1-P25: CONFIRMED 23 / WEAKENED 2 / FALLS 0; own verdict
  SOLO_three_persona.md      control arm: one agent, three personas, 24 propositions
Prior verdicts read by the judge at zero weight: engine/necropolis/dossiers/pollux.dossier.json
(2026-09-11), pollux_evidence/ rescan, _keeper_evidence/pollux_replay_corrected_result.json,
coroner_plans/CR-001 + DISP-001.  None of the three readers could open these (firewall).

Vocabulary.  Ruling types: FACTUAL (what the record says), TAXONOMIC (which name),
CAUSAL (what produced what), EPISTEMIC (what the record can establish).  Outcomes:
RULED (the judge decides on evidence in hand), ADOPTED-UNEXECUTED (the judge accepts a
reader's re-implementation without re-running it; tagged so a later reader can re-run
it), UNRESOLVED (left open on purpose, with the observation that would close it).
Nothing below changes a status field anywhere (RHAD-15); nothing below is merged into
the 2026-09-11 dossier, FRANK-004 or CR-001 (charter: no merging of new conclusions
into old records).

## 0. What the judge did that the readers could not

J1  [READ pollux.dossier.json rescan block]  The 2026-09-11 rescan EXECUTED the daemon
    statistic on the loaded table (NT-048 lineage, before the firewall existed).  Its
    per-pair corr_norm: deg10_vs_deg12 -0.2235, deg14_vs_deg16 0.3992, salem_vs_pisot
    0.3985, smyth_extremal_vs_rest -0.0786, narrow_band -0.6922, deg18_vs_deg20 0.0400,
    even_vs_odd 0.0817, small_vs_large 0.4687, lehmer 0.0519.
J2  [READ CLERIC_challenge.md 2.2a]  The Cleric, forbidden the table, recomputed
    smyth_extremal_vs_rest from the 178 curated literals as read from _mahler_data.py
    source text: corr_norm -0.0786, REJECTED.  J1 and J2 agree to four decimals.  The
    Cleric's read-literal reconstruction of a pair is therefore CONFIRMED by an executed
    artifact it never saw.  (deg10_vs_deg12 -0.2235 was available to every reader from
    the daemon's own acceptance docstring; smyth was not.)
J3  [READ _keeper_evidence/pollux_replay_corrected_result.json]  The Keeper's 2026-09-11
    executed replay found that K = 47 v0.5 round-robin ticks followed by v0.6 daemon
    semantics reproduces the 86/39/161 census and the two per-pair artifact counts on
    record (deg18 x54, even_odd x56).  This is the compile that left
    charon/agents/pollux/__pycache__/daemon.cpython-314.pyc at 2026-09-11 13:26; the
    __init__ .pyc at 2026-09-13 20:54 is the NT-048 controls run (tests/run_controls.py).
    Both fresh readers and the solo arm flagged these mtimes as an unexplained trace
    (Necromancer C9, Solo P23).  The trace is Keeper-caused.  Recorded here so that no
    later reader spends a coroner proposal on it.
J4  [READ engine/necropolis/workshop/adapters/pollux_statistic_replay.py:33-55]  The
    verdict map in the adapter (written from daemon.py:427-434) sends
    pollux_no_correlation_observed to REJECTED.  This settles D14 below without opening
    the daemon again.
J5  No new instrument was executed by the judge for this adjudication.  Every
    re-implementation cited below (Cleric R2/R3/R5a/R7/R8b/R8c, S/smyth_pair_literals.py,
    S/salem_pisot_hybrid.py; Solo reimpl_rotation2.py) is ADOPTED-UNEXECUTED unless J1-J4
    independently confirm it.

## 1. Disputed propositions

### D1  Primary cause class -- DESIGN_ERROR as "empty instrument" vs "question-instrument mismatch"
Proposition.  Necromancer: the statistic carries no content (T1: every verdict reachable
from noise); primary DESIGN_ERROR.  Cleric 3b attack 1: the normalized leg measures a real
quantity (same-vs-opposite quantile-density trend of the two marginals; R2: two
independent draws from the same non-uniform density give mean corr_norm +0.22 at every n
from 20 to 1000; R3: opposite trends give REJECTED 200/200 at n = 300), so the design is a
MISMATCH between the question named in the docstring and the question the instrument
answers, not an empty instrument.  Solo: same class as Necromancer, no characterisation.
Evidence.  Necromancer P6 (synthetic Uniform: PROMOTED ~1 %, REJECTED ~53 %); Cleric R2/R3
(ADOPTED-UNEXECUTED); prior dossier N1/N2 (real marginals: PROMOTED recurs under
independence up to 0.94), which the readers could not see and which is consistent with
BOTH characterisations.
Type.  TAXONOMIC (same class, different description) with a CAUSAL consequence (D10
salvage; D11 null design).
Resolving observation.  None needed for the class.  For the characterisation: C-D
(shape-null per pair) would show whether corr_norm on the historical pairs exceeds what
each B's marginal shape alone produces.
Worth the cost.  The class ruling needs no observation.  C-D is cheap but is not
today's question.
Outcome.  RULED: primary cause class DESIGN_ERROR, characterised as QUESTION-INSTRUMENT
MISMATCH (Cleric's wording adopted).  The Necromancer's "no content" is downgraded from a
finding to a description of the raw leg only (P2: corr_raw = +1.0 identically for n >= 10,
confirmed by all three readers and by the prior dossier's T-series).

### D2  Is MEASUREMENT_ERROR a co-cause, and where does it rank?
Proposition.  Cleric 2.2 / 3b attack 2 / 4: the curated Mahler tier encodes one
mathematical value as many ulp-distinct floats (29 rows within 6.7e-15 of 1.0; 21 Lehmer
rows; 16 Smyth rows); the gap statistic reads these runs as near-zero-gap blocks and the
recorded PROMOTED / REJECTED on at least smyth_extremal_vs_rest (2.2a, computed) and
salem_vs_pisot (2.2b, PROMOTED 185/200 under uniform fill of the unread side, destroyed by
deduplicating one block) are functions of rounding residues and duplicate-block
placement, not of Mahler measures.  Ranked first among rivals because it retrodicts WHICH
verdicts the record shows.  Necromancer and Solo: MEASUREMENT_ERROR not offered.
Evidence.  Cleric S/smyth_pair_literals.py (J2: CONFIRMED against the executed rescan),
S/salem_pisot_hybrid.py (ADOPTED-UNEXECUTED; the Known180 side is synthetic fill, three
fills tried), _mahler_data.py textual census (READ).  Judge: J1 salem_vs_pisot executed
value 0.3985 lies inside the Cleric's uniform-fill distribution (mean 0.376), which is
consistent with but does not establish the mechanism.
Type.  CAUSAL (is the duplicate-block encoding what produced the labels) and TAXONOMIC
(does a defect in the input table's float encoding belong under MEASUREMENT_ERROR or
under DESIGN_ERROR as "no tie policy in _mean_spacing_normalize", which the Cleric's own
3e locates at daemon.py:238-250 `if mean_gap == 0: return gaps`).
Resolving observation.  Cleric C-C: run the three functions (not the daemon) on all 9
pairs from the loaded table, as-is and after deduplicating each subset at 1e-9; 9 x 2
(corr_norm, verdict).  If every PROMOTED in (i) is non-PROMOTED in (ii), the labels were
rounding artifacts.
Worth the cost.  Yes: seconds of compute, one loaded table, no daemon.  It is blocked by
execution authority (R-CR-1: a frozen plan and explicit approval) and by two missing
organs (section 4).  It is the single most valuable unexecuted observation in this case.
Outcome.  UNRESOLVED on ranking; RULED that MEASUREMENT_ERROR is ADMITTED as a named
co-cause candidate on the strength of J2 (one pair confirmed from literals against an
executed value) -- admitted, not ranked.  The taxonomic half is also left open: after
C-C, if dedup flips the verdicts, the court must still decide whether the defect is the
table's (MEASUREMENT_ERROR) or the normaliser's tie policy (DESIGN_ERROR); the
observation does not decide the name.

### D3  CONSUMER_ABSENT vs CONSUMER_INERT
Proposition.  Necromancer rival: CONSUMER_ABSENT.  Cleric 2.7 / 3b attack 3: Hecate and
Erebos read every row (docs/state.json Erebos block pollux_substantive_recent 286 at
05-30T15:59Z; Hecate ledger_found includes the Pollux ledger); what was absent was a
consumer that could turn a Pollux row into anything (Stygian short-circuit P19; ergon
inverts all labels P20; Hecate MI at noise P21).  Solo P16: Erebos g01/g04 read corr_raw
as data.  Solo judge D5: DESIGN_ERROR and CONSUMER_ABSENT are two independent sufficient
deaths, not rivals.
Evidence.  docs/state.json (READ by all three); P19-P21 (confirmed by all three).
Type.  FACTUAL (were there readers: yes) then TAXONOMIC (what to call a reader that
consumed every row to no effect).
Resolving observation.  Cleric C-E: count Erebos composed claims whose provenance cites a
pollux_record_id, with verdicts.  Zero = inert; non-zero with any PROMOTED = a Pollux
artifact propagated and a downstream case exists.
Worth the cost.  Yes if the Erebos ledger exists on M2 (a read, not a run); the answer
changes whether a second grave opens.
Outcome.  RULED: CONSUMER_INERT is the correct description of this record; the vocabulary
of the death-certificate field is NOT extended today (the certificate carries
CONSUMER_ABSENT with the qualifier "inert, not absent" -- see section 2).  RULED that the
Solo's D5 framing is adopted: the mismatch and the inert consumer are independent
sufficient deaths, not primary-vs-rival.  C-E remains open.

### D4  What stopped it
Proposition.  Necromancer: external halt of the shared 8-agent process, swarm-wide,
reason RECORD_INSUFFICIENT on files it may open.  Cleric 3a: more specific -- the eight
last ticks form one complete rotation ending on Nephele at 16:24:54Z with
Charon_Loop.last_run error null; the loop stopped in its sleep after the last agent;
stale PID lock (pid 24132 dead), Redis host .176 dark (COMPONENT_DOSSIERS 06-24:290-305);
never restarted.  Cleric asks that the certificate carry the halt mechanism separately
from the disease.  Solo: swarm-wide halt, same date.
Evidence.  docs/state.json Charon_Loop block (READ by Cleric); scripts/charon_loop.py
(READ by Cleric); prior dossier (judge) agrees on date and swarm-wide scope.
Type.  FACTUAL (mechanism) and TAXONOMIC (field structure).
Resolving observation.  None worth buying: the mechanism does not bear on the cause
class, and the Cleric's own C-list says so.
Outcome.  RULED: the certificate gets a separate halt_mechanism field; INFRASTRUCTURE is
recorded there and nowhere else.  The Cleric's mechanism detail is ADOPTED as READ (the
judge did not re-open state.json).

### D5  Hypothesis status
All three readers and the prior dossier: UNTESTED.  The Solo's Cleric phrasing is adopted
verbatim: "never tested did not fail".  No dispute.  RULED: HYPOTHESIS_FAILURE is not
available on this record; the hypothesis of record ("a correlation between
Mahler-measure subsets that survives mean-spacing normalization carries real shape
signal") has never been measured, because no measurement of a correlation BETWEEN two
subsets exists (P1: independent sort + truncate, no join).

### D6  FAIR / UNFAIR
Proposition.  All readers: UNFAIR on the question of record.  Cleric 3c: WEAKLY FAIR on
the rewritten question ("do the two marginals share a quantile-density trend") and on the
instrumentation question ("does a second operator class move Hecate's MI"); Cleric 3d
STANDS.  Solo B.3 FAIR FALLS / B.4 UNFAIR STANDS.
Type.  EPISTEMIC.
Outcome.  RULED: NO_FAIR_TEST_ON_RECORD on the question of record (this agrees with the
2026-09-11 dossier and was reached by three readers who could not see it).  The
rewritten question is not the case and receives no FAIR status; it is recorded as the
question the instrument can answer, for whoever raises a descendant.

### D7  The census retrodiction (two rival decompositions)
Proposition.  Solo P11-P13: a two-phase model (K = 47 v0.5 round-robin ticks, then v0.6
settle/replace semantics) reproduces the QUOTED census 86/39/161 EXACTLY and UNIQUELY,
with per-pair rows deg10 17 / deg14 17 / salem 17 / smyth 16 / even_odd 56 / small_large 5
/ narrow_band 53 / deg18 54 / lehmer 51, and predicts the 05-26 intermediate census
R47/U44/P39 and terminal settled_pairs length 54.  Cleric 2.4 (independently, not having
seen the Solo): a c1+c2 decomposition -- 22.6 h of c1 at a 28-min cycle = ~48 ticks over 4
TEST_PAIRS (24 PROMOTED + 24 REJECTED), then c2 with five settled pairs x 5 rows and four
unremovable pairs (deg18 54 / even_odd 56 / narrow_band 52 / lehmer 51) -- also
reproduces all four totals (39 / 86 / 161 / 286).  Necromancer: left as "confounded".
Evidence.  Both are RE-IMPLEMENTATION against the same QUOTED census and the same two
artifact counts (deg18 x54, even_odd x56).  J3: the Keeper's executed replay agrees with
the Solo's K = 47 on the daemon's own semantics.
Type.  FACTUAL, and decidable: the two decompositions differ on per-pair rows for
smyth_extremal_vs_rest (Solo 16 vs Cleric 17) and narrow_band (Solo 53 vs Cleric 52), and
on whether c1 had 4 TEST_PAIRS ticking or 9 pairs round-robin.
Resolving observation.  Cleric C-B: the historical ledger
(charon/agents/pollux/state/kill_ledger.jsonl on M2, 435 KB per the 06-24 dossier)
tabulated by (pair, verdict, corr_norm, batch date).  One read decides it.
Worth the cost.  Yes, if the file exists: it is a read of a dead ledger, no execution,
no LLM; it also retires the Solo's "UNIQUELY".
Outcome.  RULED: the Solo's UNIQUENESS claim FALLS as stated -- a second independent
reader produced a distinct decomposition that reproduces every quoted total; uniqueness
held only within the Solo's own model family.  The Solo's own Cleric persona graded the
retrodiction "WEAKENED-not-FALLS" and did not find the rival: this is the clearest
measured difference between the separated and solo arms in this case (see
SEPARATION_RECORD.md).  Which decomposition is right: UNRESOLVED, pending C-B.  Note for
the record: J3 favours the Solo's mechanism (the Keeper's replay used daemon semantics,
not the Cleric's 4-TEST_PAIRS assumption), but J3 is the judge's own prior work and is
not admitted as a tiebreak.

### D8  P5 -- what the anti-monotone case yields
Cleric R7: with A drawn from a rising density and B = 2.6 - A, the verdict is sign_flips
(REJECTED 173/200), not attenuates as the Necromancer's Uniform-A T4 gave; the specific
yield is a property of the marginal shapes, not of anti-monotonicity.  Type FACTUAL.
Outcome.  RULED WEAKENED as the Cleric says (ADOPTED-UNEXECUTED); the Necromancer's
conclusion (the statistic does not measure the A-B relation) stands and is strengthened:
the verdict is a function of the two marginal density shapes only.

### D9  P22 -- literal_verdict_lint 0 findings / 9 files
Cleric: true as a number, vacuous as evidence -- the lint matches a fixed verdict
vocabulary and cannot see a verdict chosen by a conditional over pollux_* kill-pattern
strings, nor a statistic that is a literal constant in effect (corr_raw).  Type FACTUAL
about the instrument.
Outcome.  RULED: accepted.  CONSEQUENCE FOR THE INSTRUMENT MAP: NT-056 is listed as a
DIRECT answerer of FQ-07 ("could the gate refuse?") with scope GENERAL.  This case
measures a scope limit: the lint sees literal-vocabulary returns only; a gate whose
refusal is an unreachable branch of a conditional (P3: no_correlation_observed is
unreachable because corr_raw is never < 0.30) is invisible to it.  FQ-07 is demoted
from ANSWERABLE to ANSWERABLE_RESTRICTED in build_forensic_map.py with this case as the
citation.  That is a move downward, made because the case measured it.

### D10  Salvage
Necromancer 13: _mean_spacing_normalize, _spearman, _load_subset + 7 selector kinds, the
pair taxonomy, the settle machine.  Cleric 3e: none worth lifting as-is
(_mean_spacing_normalize's `mean_gap == 0` path is the artifact; _spearman has no tie
correction; _load_subset's value is the pair taxonomy, which is where the duplicate
blocks live; the settle machine is inapplicable to a deterministic instrument).  Cleric
names three things not named: (i) the FINDING that the curated Mahler table's encoding is
a hazard for every gap/spacing statistic in the tree, including Stygian composition
loaders over Lehmer bands and Mahler cubes; (ii) "9 pairs, 9 constant outcomes, 286 rows"
as a calibration case for liveness auditors; (iii) the Erebos _filter_substantive_recent
seam (counts rows by verdict string, no per-(pair, instrument-version) novelty gate).
Type.  CAUSAL (what is worth lifting) with one FACTUAL open point (do the Stygian loaders
compute gaps over the same encoding).
Resolving observation.  For (i): a static read of the named Stygian loaders for gap /
spacing / difference operations over Mahler values -- a reader task, not a coroner run.
Worth the cost.  Yes; it is a grep-and-read and it decides whether a live component
carries the same defect.
Outcome.  RULED: no code component is recorded as salvageable as-is.  Items (i)-(iii)
are recorded as the salvage of this case.  (i) is UNRESOLVED as to the Stygian loaders and
is forwarded (section 5).  (ii) is forwarded to Pronoia's lane as a calibration case,
without a status.

### D11  Which null (Necromancer C5 vs Cleric C-D)
Necromancer C5: a shuffled-split null.  Cleric: mis-specified -- within-subset shuffles
are invisible to a sorted-multiset statistic (P4, confirmed by all three readers), and
split-half nulls are same-shape nulls that PROMOTE at the R2 rate; it would certify the
artifact.  Replace with C-D: hold the marginals fixed, draw B' from a smooth density
fitted to B, 1000 draws, z-score per pair.
Type.  CAUSAL (what counts as chance for this statistic).
Outcome.  RULED from P4 alone: C5 is withdrawn as specified.  C-D is recorded as the
proposal shape.  Whether C-D is itself well-posed (a "smooth density fitted to B" on a
table with 29 rows at 1.0 is not obviously smooth) is UNRESOLVED and is the reason C-C
(dedup) is ranked ahead of it.

### D12  The Solo's counterfactual F-B vs the Cleric's "looks like a repair, changes nothing"
Solo F-B: add a permutation null for corr_norm ("shuffle gap order within each series,
200 draws"), STANDS as the one mutation that changes the outcome's meaning ("a z-scored
corr_norm could REFUSE").  Cleric 3f second mutation: a permutation null while keeping the
sorted-truncated inputs and the duplicate runs changes nothing that matters (P4).  The
Solo's own attack on F-B noted the ~51 % PROMOTED same-family floor and still graded it
STANDS.
Type.  CAUSAL.  The two readers describe different operations under one name: the Solo
shuffles the GAP SERIES (which does change corr_norm, since corr_norm is a rank
correlation of index-aligned gap sequences), the Cleric's P4 objection is about shuffling
VALUES before sorting (which changes nothing).  Read literally, both are right about the
operation each names; the Cleric's remark does not reach the Solo's F-B.
Resolving observation.  None needed to see that the disagreement is definitional.  Whether
a gap-order permutation null is a MEANINGFUL null (what population does it represent?)
is the same open question as D11.
Outcome.  RULED: no conflict of fact; the counterfactual is UNRESOLVED in the same
sense as D11, and the case records that "permutation null" without an operand is not a
specification.  Requirement filed (section 5).

### D13  The Solo's F-C (swap daemon.py:331-332 below :336-339)
Solo: a shape-changer with zero content change (narrow_band would emit 5 rows, not 53;
the census would shrink).  Cleric: did not examine (P10/P11 confirmed as the bug; no
counterfactual on it).  Necromancer P10/P11 confirmed by all.
Outcome.  RULED: agreed as a fact about the code; recorded as the counterfactual that
would have made the record SMALLER and no truer.  It is the kind of "repair" the charter
warns about (looks like a repair; changes nothing about the question).

### D14  Necromancer body 2.6 vs P3 (verdict map)
Cleric 2.1: the report's section 2.6 sends no_correlation_observed to UNVERIFIED while P3
(correct) sends it to REJECTED.  J4 confirms P3 from the adapter's copy of the map.
Outcome.  RULED FACTUAL for the Cleric; the Necromancer's proposition list is right and
its prose is wrong; harmless to every conclusion because the branch is unreachable
(P3).  Recorded because the propositions, not the prose, are what a court reads.

## 2. Death certificate (final)

  grave                 charon/agents/pollux (daemon.py at 43b094552 == HEAD)
  born                  2026-05-24T07:10Z (8c619443a, v0.5); revised 2026-05-25T05:46Z
                        (43b094552, v0.6: settle + candidate pool + Stygian enqueue)
  last tick             2026-05-30T15:55:23.901164Z (docs/state.json agents[34])
  halt_mechanism        INFRASTRUCTURE: swarm-wide hard termination of the shared
                        8-agent loop process after one complete rotation; stale PID lock;
                        Redis host retired; never restarted.  Not Pollux-specific.  Not
                        the cause of the failure.
  cause, primary        DESIGN_ERROR -- question-instrument mismatch.  The raw arm is
                        constant (+1.0) by construction; the normalized arm measures the
                        same-vs-opposite quantile-density trend of two marginals, which
                        is not the correlation between subsets the docstring names; no
                        null, no chance floor, threshold 0.30 unexplained.
  cause, co-candidate   MEASUREMENT_ERROR -- duplicate-run float encoding in the curated
                        Mahler tier read as near-zero-gap blocks.  ADMITTED on one pair
                        (J2), UNRANKED pending C-C.
  independent death     CONSUMER_ABSENT (qualifier: inert, not absent).  Every row was
                        read by Hecate and Erebos; no reader could turn a row into
                        anything (Stygian short-circuit, ergon label inversion, Hecate MI
                        at noise).  Sufficient on its own.
  hypothesis            UNTESTED.  Never measured; not falsified; not supported.
  FAIR status           NO_FAIR_TEST_ON_RECORD (on the question of record).
  record sufficiency    Sufficient for the class ruling; INSUFFICIENT for ranking the
                        co-cause and for choosing between the two census decompositions
                        (ledger absent from every tree; possibly on M2).
  resurrect             NO.  Nothing here recommends revival; the CR-001 lineage and the
                        C-C proposal are questions about the record, not about Pollux.

Relation to the 2026-09-11 dossier (zero weight, compared after the fact): same primary
class, same FAIR status, same hypothesis status, reached by three readers who could not
open it.  New in this court and absent from the dossier: the mismatch characterisation
(D1), the duplicate-encoding co-cause (D2), CONSUMER_INERT (D3), the halt as a separate
field (D4), the rival census decomposition (D7), the lint scope limit (D9).

## 3. Left unresolved on purpose

  U1  D2 ranking: is MEASUREMENT_ERROR co-primary?           -> C-C (needs section 4 organs)
  U2  D2 taxonomy: table encoding vs normaliser tie policy    -> a ruling after C-C, not an observation
  U3  D7: which census decomposition is right                 -> C-B (M2 ledger read)
  U4  D3/C-E: did any Pollux row propagate through Erebos     -> C-E (M2 Erebos ledger read)
  U5  D10(i): do Stygian composition loaders read the same
      duplicate-encoded gaps                                  -> static reader task
  U6  D11/D12: what population a "permutation null" on this
      statistic represents                                    -> definition before any run
  U7  Necromancer C1-C3 (recover ledger/state from M2; per-pair
      n and corr_norm; replay)                                 -> subsumed by C-A/C-B; C-A is
                                                                 the only one needing the
                                                                 loaded table
  U8  Cleric C-A per-degree Known180 counts and distinct-M
      counts at 1e-9                                          -> loaded table; goes with C-C

Not left open: whether to run Pollux (no), whether the hypothesis failed (cannot be
said), whether the halt matters (it does not).

## 4. Descendants (items 11-12) and Zombies (item 13)

### 4.1 FRANKENSTEIN descendant -- SPEC, not raised
  ancestor A          FRANK-004 (Pollux repair: two-sample spacing-distribution test under a
                      random-subset null; PROPOSED, DESIGN ONLY)
  layer Y             input / loader (before any statistic)
  mutation M          deduplicate each subset by M rounded to 1e-9 before pairing;
                      statistic untouched (Cleric 3f first mutation)
  C -> C'             "spacing profile of subset A vs B" -> "spacing profile of the DISTINCT
                      values of A vs B"
  expected R          salem_vs_pisot PROMOTED (185/200 under fill) -> REJECTED/UNVERIFIED;
                      smyth REJECTED unchanged in label but no longer a rank correlation of
                      rounding residues; the "2 survivor signals" of the 05-27 memo lose
                      their support if C-C confirms
  kill-before-run     (k1) if the distinct-M count per subset at 1e-9 leaves n < 10 for a
                      pair, that pair is UNMEASURABLE and the descendant may not report it;
                      (k2) if C-C shows dedup changes NO verdict, the mutation is inert and
                      the descendant is DEAD_BEFORE_RUN against the proposer;
                      (k3) if FRANK-004's own organ 6 (KS over normalized gaps) reads the
                      zero-gap spike of a duplicate block as signal -- which the Cleric's
                      finding predicts -- then FRANK-004 has a pre-run kill of its own that
                      its cleric_gate does not list.  Recorded here; FRANK-004 is NOT
                      edited (charter).
  why not raised      raising a monster file requires an organ for the dedup step that is a
                      Keeper-controlled tool (no such row in TOOLS.jsonl; "do not invent
                      instruments" applies to the map, and "do not promote unvalidated
                      tools" applies to a monster's organ list).  The spec is complete
                      enough to become FRANK-005 the day the organ exists.

### 4.2 CORONER descendant -- NOT written; two reasons on record
  (a) A descendant of CR-001 must carry a planted-shift positive control (charter, CR-001
      ruling).  No admissible instrument plants a shift by claim class (FORENSIC_QUESTIONS
      FQ-02 PARTIAL; REQUIREMENTS RQ-1).  A descendant written today would be
      DEAD_BEFORE_RUN by construction on the same criterion that killed its parent; writing
      it would be theatre.  parent_plan would be {CR-001, 86e949f26f2f...} when it exists.
  (b) The decisive observation for THIS case is not CR-001's question at all; it is the
      Cleric's C-C (dedup rerun).  A well-formed plan for C-C needs: (i) a step-chaining
      driver -- coroner_run.py execute() passes literal kwargs to each function and carries
      no data between steps, so "load 9 pairs, then dedup, then call NT-048
      historical_statistic on each" cannot be expressed as actions today; (ii) a
      Keeper-controlled positive control that PLANTS a duplicate block into a
      non-duplicated synthetic subset and shows the verdict move.  Both are requirements
      (section 5, RQ-14 / RQ-15), neither is a plan.
  Contract defect found while checking (a)/(b), recorded, not fixed today: CR-001's action
  kwargs carry a `_note` key; execute() would have passed it to historical_statistic() and
  raised TypeError at step 0.  Fail-closed behaviour holds (the step is recorded ok=False),
  but the dry check does not bind kwargs to the function signature.  CR-001 is
  DEAD_BEFORE_RUN and immutable; the defect goes to the contract's next version with a
  negative test (BACKLOG RHAD-45).
  "Do not run Pollux yet" is obeyed: no plan, no run, no import of the daemon by the
  court.

### 4.3 Zombies
  ZERO.  Nothing was executed from the grave by any reader or by the judge during this
  court.  The only executions of Pollux code on this worktree remain the Keeper's
  2026-09-11 replay and the 2026-09-13 NT-048 controls (J3), both pre-court and both on
  record.

## 5. Forwarded (appended to REQUIREMENTS_to_Techne.md, "From case POLLUX")
  RQ-14  step-chaining driver for coroner plans (4.2b-i)
  RQ-15  planted-duplicate-block positive control as a Keeper-controlled tool (4.2b-ii)
  RQ-16  Stygian composition loaders: static read for gap/spacing operations over the
         curated Mahler tier (U5) -- addressed to the Stygian/Charon owner, not Techne
  RQ-17  AUTOPSY_TAXONOMY: distinguish absent / inert / inverting consumers (D3) --
         addressed to the taxonomy owner
  RQ-18  "permutation null" is not a specification without an operand (values / gap
         series / labels) and a population (D11/D12) -- a rule for any future plan
  RQ-19  liveness calibration case "9 pairs, 9 constant outcomes, 286 rows" (D10-ii) --
         offered to Pronoia, no status attached
