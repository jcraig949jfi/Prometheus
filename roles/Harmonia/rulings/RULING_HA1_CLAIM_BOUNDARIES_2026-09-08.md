# HA-1: claim boundaries, with worked examples

2026-09-08. Lane: Harmonia. Adjudication only; no code outside my lane touched.
Numbers reproduce from `roles/Harmonia/science/ha1num.py`.

Six rulings. Five were asked for; the sixth is what attacking the other five
kept producing.

--------------------------------------------------------------------------
## HA-1.1 -- AN OBSERVABLE BEHAVIOURAL DIFFERENCE NEEDS NO PERFORMANCE
##           ADVANTAGE, AND SCORE EQUALITY IS NOT SAMENESS

RULING. Two organisms, rules or templates are behaviourally different if,
under matched seeds and after quotienting by the family's DECLARED symmetries,
any registered observable differs -- trajectory, output, halting status, step
count, witness. No performance ordering is required. A difference that is
exactly neutral on the family's registered measurement is still a difference.

The converse is also ruled: equality on a scalar measurement is NOT evidence of
sameness. A scalar is a projection, and projections lose things.

WORKED EXAMPLE 1 (from my own record, S4). Interventions A and B applied in
both orders: A-then-B recorded SYNERGY +0.078, B-then-A recorded ANTAGONISM
-0.043, a non-commutative gap of +0.121 -- and BOTH were filed under the
identical component label "A+B". Two behaviourally distinct processes. Neither
is better than the other; they have OPPOSITE SIGNS, and their mean is near
zero. Under a performance-advantage bar neither difference exists. Under this
ruling both are recorded, each with the intervention (order) that established
it.

WORKED EXAMPLE 2 (CA, C3-base). A constant-output rule and a random 128-bit
rule both score about 0.5 accuracy on a balanced sample. Under D-C1-1's odd
n_cells the constant rule's 0.5 is EXACT by symmetry, not approximate. They are
trivially distinct on the trajectory observable -- one reaches a fixed point at
step 1. Reading score equality as sameness would merge the family's own
baseline with its random control, which is the one comparison C3 exists to make.

BOUNDARY. A difference must survive the declared symmetries. Two NK candidates
differing only by a locus permutation the exchangeability null declares inert
are NOT different, and a report that they are is an invariant violation
(HA-1.5a), not a discovery.

AMENDS R4. R4.2 currently reads "changes the measured OUTCOME". Broaden to
"changes a registered OBSERVABLE", or R4 silently re-imposes the scalar bar
this ruling removes.

--------------------------------------------------------------------------
## HA-1.2 -- A CAUSAL CLAIM NEEDS ITS INTERVENTION; AN ASSOCIATION IS
##           REPORTED AS AN ASSOCIATION HOWEVER STRONG

RULING. "M causes the effect", "X predicts Y BECAUSE", "the structure produces
the accuracy" require an intervention on the named mechanism with everything
else matched -- the family's declared mechanism control -- and the contrast
measured at the level the intervention was applied. A relationship observed
across a corpus without an intervention is an ASSOCIATION. Strength does not
convert one into the other.

WORKED EXAMPLE (CA H2, live). H2 says the random-rule record, on a declared
rule-table descriptor, shows region structure that predicts accuracy. Suppose
D3 fires and an X1 analysis finds a strong relationship. That is an association
between a rule-table statistic and accuracy ACROSS RANDOMLY DRAWN RULES. It is
not "the region causes the accuracy", and it licenses no ablation prediction.

The intervention that WOULD license the causal reading is already in the
packet: C3-abl's `ca.region_ablation.v0`, ablating table entries in a declared
popcount region, WITH `ca.region_ablation_control.v0`, a size-matched random
region. Herakles's pilot is exactly why the control is not optional -- the
naive reading names the two 35-entry mid-popcount regions, and 35 entries is a
size, not a mechanism. So: H2 without C3-abl is an association; H2 with C3-abl
AND its size-matched control is a causal claim scoped to the drawn-rule
population.

WORKED EXAMPLE 2 (why the record cannot check this for you). In S2 an
undeclared co-intervention produced a record BYTE-IDENTICAL to the honest one.
A causal claim rests on the intervention ACTUALLY APPLIED, and the engine
cannot verify the declared intervention is the applied one. Vivarium's
CONFIG_DIVERGENCE attestation is what makes it checkable, and only when the
CONFIG is sent -- echoing the sealed spec_hash back passes with no findings and
proves nothing.

AMENDS R4. "changes the measured outcome by more than the exchangeability
null's spread" is not a test: a spread is a scale, not a reference
distribution, and no unit is named. Replace with a test at the DECLARED
independent unit against the null as reference, with the eligible count
computed first (HA-1.6).

--------------------------------------------------------------------------
## HA-1.3 -- TRANSFER OF A SOURCE-DERIVED ARTIFACT NEEDS A MAPPING AND
##           BASELINES, NOT RUNTIME MEMORY

RULING. A transfer claim asserts that information derived from a source world
changed behaviour in a target world. The carrier may be static -- a candidate,
genome, program, rule table or parameter vector. Persistent runtime memory is
NOT required and its absence is not a defect in the claim. Required instead:

    a declared carrier, named as an artifact or as declared runtime state
    a declared, versioned mapping between the two worlds' observation and
      action spaces; identity is allowed and must be DECLARED as identity
    baselines sharing the target worlds, seeds and budget, differing ONLY in
      the intended source information

THE BASELINES ARE NOT INTERCHANGEABLE, and R6's "matched fresh, shuffled, or
unrelated-source" reads as a menu. It is not one. Each rules out a different
alternative:

    matched fresh        rules out "the target world is simply easy"
    shuffled source      preserves the artifact's marginal statistics and
                         destroys its structure -> rules out "an artifact of
                         this shape helps"
    unrelated source     preserves structure and destroys relatedness ->
                         rules out "any prior artifact helps"

A claim that beats only FRESH has established that carrying something helps,
which is not transfer. The claim's strength is bounded by which arms are
present, and the report says which.

WORKED EXAMPLE (WP-A4). Source: an NK world at k=4. Target: a flipped-hash
relative. Carrier: the best candidate bitstring found in the source. Mapping:
identity on loci, declared as identity because both worlds share length and
locus indices. Arms: fresh random start; the source candidate bit-shuffled
(Hamming weight preserved, structure destroyed); a candidate from an unrelated
k=4 world at a different seed. All four arms share target worlds, seeds and
query budget; only the initial candidate differs. UNIT OF ANALYSIS: the
(source, target) PAIR. The 20 queries inside one target world are repeats and
add no independent units.

BOUNDARY THAT MATTERS HERE. The flipped-hash relatedness axis has its
construction curve pinned ANALYTICALLY at both ends. A known construction curve
is not an empirical exploitation result, and reporting "transfer works because
relatedness is high" when relatedness was authored reports the construction.
R6 says this; I am underlining it because it is the easiest sentence in the
program to write by accident.

--------------------------------------------------------------------------
## HA-1.4 -- PATH B IS SCOPED TO ITS POPULATION AND ITS CHANNEL

RULING. PATH B gates claims that RELY ON the 64 recovered specimens and the
wider observation channel. It does not gate:

    producer-proposed programs      no specimen population is involved
    source-artifact transfer        a static carrier plus a mapping (HA-1.3)
    the WP-B3 witness experiment    both arms are producer-proposed

WHY THE SCOPING IS THE WHOLE RULING. PATH B is a POPULATION boundary. Quoting
a limit derived on one population as a property of another is the error that
produced three load-bearing wrong numbers in this program in a single week.
Blocking B3 on B4 would be that error exactly: B4's limitation concerns what
the 64 specimens can be asked to do, and B3 asks nothing of them.

WORKED EXAMPLE. WP-B3 uses a seed-derived 4-input truth table, 20 proposed
programs per series, two arms (witness returned / withheld), selection in both
arms by the SAME deterministic rule over prior fossils, seeds per arm. No
specimen from the 64 appears anywhere in it. PATH B does not gate it.
Conversely "these 64 specimens respond to environmental observation" relies on
both the population and the channel, and is gated.

RE-ENTRY CONDITION. If a producer-proposed program is SEEDED from one of the
64, it re-enters PATH B's scope -- seeding IS carrying, the specimen is then
the source artifact, and HA-1.3's mapping and baselines apply to it.

--------------------------------------------------------------------------
## HA-1.5 -- CALIBRATED FALSE ALARM vs EXACT INVARIANT VIOLATION vs FINDING

Three different objects. R4 separates the first two; this makes the separation
operational and adds the branch R4 does not have.

(a) EXACT INVARIANT VIOLATION. A jointly transformed pair REQUIRED BY
    CONSTRUCTION to be identical is not identical. The comparison is exact
    (integer or byte equality after declared normalisation), the expected
    answer is known with probability 1, no distribution is involved. ONE
    violation is a DEFECT in the library, the template or the transform. It is
    never a scientific result and it halts the family.
    Example: NK locus permutation applied to both table and candidate, scores
    integer-identical; CA reflect/complement applied to both rule and IC,
    normalised trajectories identical. Packet v2 uses integer-exact comparison
    for NK precisely so that no tolerance can absorb a violation.

(b) CALIBRATED FALSE ALARM. A DETECTOR fires on a template declared to carry no
    effect. The detector has a known nonzero rate under the null. A firing at
    or below that rate is expected: not a defect, not a finding. Admissible
    only if the rate was calibrated AT THE GEOMETRY ACTUALLY RUN and the
    denominator -- eligible regions per corpus -- is reported. Without the
    denominator the rate is not a rate and the firing means nothing yet.
    Example: D3 on the CA exchangeability null at 12 rules per region, k=4,
    expected 0.032 per region. Two firings in 40 eligible regions is 0.05,
    inside noise. Calling that a leak is the error I made twice -- once writing
    "null as expected" when it HAD fired, once reading 14 coin flips as a leak.
    AND THE DIRECTION THAT NOW BITES HARDER: zero observed firings do not prove
    a zero rate, and F-2 explains why zero is easy to get -- for any true ratio
    inside D3's band the rate goes to 0.000 with corpus size by construction.
    Zero firings can mean "large corpus", not "clean null".

(c) FINDING. BRANCHES s0: not stipulated; survives the exchangeability null AND
    the mechanism control under matched seeds; not already known for that
    substrate; reproduces under replay and under a fresh seed of the same
    authored world class.

DECISION PROCEDURE.

    is the expected answer known with probability 1 (exact identity)?
      YES -> any difference is (a) VIOLATION. halt. not a result.
      NO  -> next

    did a detector fire on a template DECLARED to carry no effect?
      YES -> is the rate calibrated at THIS geometry, and is the
             eligible-region denominator reported?
               NO  -> VOID. the firing carries no information yet.
               YES -> is the observed rate above the calibrated rate by more
                      than its binomial SE?
                        NO  -> (b) CALIBRATED FALSE ALARM. record; do not act.
                        YES -> NOT A FINDING EITHER. it is evidence that the
                               null or the calibration is wrong. fix the
                               instrument before reading the science.
      NO  -> next

    candidate (c): apply BRANCHES s0 (1)-(4). Harmonia rules.

The third branch is the one R4 lacks and it is load-bearing: a null firing
ABOVE its calibrated rate is an instrument problem, not a discovery. A detector
that fails is a claim about the detector until resolved.

--------------------------------------------------------------------------
## HA-1.6 -- A DESIGN STATES ITS MINIMUM ATTAINABLE p BEFORE IT IS ISSUED
##           (standing rule; this is the third occurrence)

RULING. Before a corpus is issued, its analysis states the SMALLEST p its own
permutation lattice can produce. If that number exceeds the declared alpha, the
gate cannot fire on any data and the design is INELIGIBLE -- not underpowered,
incapable. Either resize, or reclassify the question as descriptive and run no
test.

    design                                        lattice     min p   0.05?
    -------------------------------------------   --------   -------  -----
    H1 NK trapped fraction, 3 landscapes/k (v1)    unpaired    0.1000   NO
    H1 NK trapped fraction, 6 landscapes/k (v2.1)  unpaired    0.0022   yes
    route (c) k-variance ratio, 6 per k            unpaired    0.0022   yes
    C3 analysed at the 4 IC SAMPLES                  paired    0.1250   NO
    C3 analysed at the IC, 400 paired                paired    ~0       yes
    B3 witness on/off, 3 seeds per arm             unpaired    0.1000   NO
    B3 witness on/off, 3 seeds PAIRED by seed        paired    0.2500   NO
    B3 witness on/off, 6 seeds per arm             unpaired    0.0022   yes
    B3 witness on/off, 6 seeds PAIRED by seed        paired    0.0312   yes

Unpaired: 2/C(2n,n). Paired sign-flip: 2/2^n. Note that PAIRING MAKES THIS
WORSE at small n -- 3 paired seeds give 0.25, worse than 3-vs-3 unpaired's
0.10 -- which is the opposite of the usual intuition that pairing helps.

Three separate designs in flight were sized below their own floor. That is a
pattern, so it becomes a standing rule rather than three amendments.

--------------------------------------------------------------------------
## ATTACK ON SELECTION_RULES.md R1-R8

R1, THE THIN THRESHOLD'S REASON IS NOW STALE. "24 rows" is justified as "one
D3-eligible region (8) in three worlds, or 6 worlds x 4 repeats". Post-fix,
D3 sees ONE ROW PER INDEPENDENT UNIT, so 6 worlds x 4 repeats is 6 units --
BELOW the floor of 8, not at it. The number may still be a fine threshold; its
stated reason no longer holds, and D-6 is precisely the decision where the
reasons are the point. Corrected reason: thin = 8 INDEPENDENT UNITS (one
eligible region), which is 32 rows at 4 repeats.

R1, THE M-SIGNAL NEUTRALITY ARGUMENT HAS A STATE DEPENDENCE. "the reserve
applies inside each arm identically, so it cannot favour a policy" holds only
if both arms see the same reserve-ELIGIBLE SET at every draw. Eligibility
depends on family age and row count, and row count is changed by the arm's own
draws. A directed arm that pushes a family past `thin` before the random arm
does makes the two arms' reserve sets diverge mid-run. FIX: freeze the
reserve-eligibility set at the start of the run from the frozen universe; do
not recompute it per draw.

R2, CAP 4 REPEATS THE UNIT PROBLEM ONE LAYER DOWN. "cap 4 matches the
M-ELIGIBLE repeats-per-world so a cell can hold one world's trajectory" means a
full cell holds 4 rows = ONE independent unit. If the archive is ever read as a
source of seeds or counted in the health report, a cell must report its
INDEPENDENT-UNIT count beside its entry count, or every count drawn from the
archive inherits the inflation the repeat fix just removed.

R2, "FIRST OCCUPANT OF ITS CELL" INFLATES INFORMATIVE FAILURES EXACTLY WHEN THE
ARCHIVE IS YOUNG. Clause (c) makes every cell founder an informative failure,
including successes, so the eviction protection covers arbitrary first-arrivals
and any health-report count of informative failures rises fastest when the
archive is newest -- a metric that goes up because the archive is new. Rename
(c) to CELL FOUNDER, give it its own protection level, and count it separately.

R3, DETECTOR-ELIGIBLE IS NOT A MONOTONE COVERAGE UNIT. A family becomes
"detector-eligible" by accumulating rows, but past the interior optimum (F-3)
more rows make D3 DISCRIMINATE LESS. Coverage may therefore rise while the
detector's actual discrimination falls. Report eligibility as coverage, and the
discrimination lift at the realised geometry BESIDE it, never instead of it.

R5, THE RANDOM CONTROL'S UNIVERSE MUST TRACK THE DIRECTED POLICY'S. A family
admitted early has a matched random control drawn over the universe as it then
was. If the universe later widens, that control is no longer matched. Carry the
M-SIGNAL rule explicitly into R5: a widened universe forces the random control
to be RE-DRAWN and SEPARATELY VERSIONED.

R6, THE BASELINE MENU IS NOT A MENU. See HA-1.3: "fresh, shuffled, or
unrelated" must not read as a choice among equivalents.

R8, POST-HOC EXPLANATIONS MUST BE STAMPED AS POST-HOC. LLM-generated candidate
explanations for a FIRED detector are conditioned on the outcome. If one later
becomes a stipulated-outcomes entry for a follow-up, that follow-up is not
prospective. Require each candidate explanation to carry the observation it was
generated from, and require any experiment testing one to declare it
POST-HOC-DERIVED.

R4, R7: no attack. R4 as amended is correct and R7's leads are correctly held.

--------------------------------------------------------------------------
## ATTACK ON BRANCHES.md s0 (as amended by the four-properties correction)

s0 IS INTERNALLY CONTRADICTORY, AND THIS IS THE MAIN CATCH. The four-properties
correction states plainly that predictability is NOT a bar: "The absence of an
analytical shortcut is therefore not a discovery requirement", and whether a
finding is predictable "is recorded as a property of the finding, not used as a
bar". But the refusals list at the end of s0 refuses "anything computable from
the seed" -- which is a predictability bar, reinstated three paragraphs later.
A regularity computable in principle from the seed, not stipulated and not
known, is by the operator's own correction still a candidate.
RESOLUTION: the refusal should be "anything STIPULATED on the family's
outcomes list", which is criterion (1) and does the intended work. Delete
"anything computable from the seed".

s0(3), "NOT ALREADY KNOWN", IS UNBOUNDED AND CAN ONLY EVER FAIL. It is a claim
about the literature, and in this program "nobody measured X" has twice turned
out to be a reporting claim rather than a fact. Require (3) to be evaluated
against a DECLARED, VERSIONED search -- the sources actually consulted, listed
-- and its verdict written as "not found in <named corpus> as of <date>", never
"not known". Otherwise the finding class silently depends on how hard someone
looked.

s0(2), "SURVIVES THE NULL", IS NOW GEOMETRY-DEPENDENT. Under F-2, at large n an
inside-band effect produces zero detector firings, so a candidate can survive a
null trivially by being run on a big corpus. Surviving must be defined against
the calibrated rate at the REALISED geometry (HA-1.5b), and the null must be
shown to have been ABLE to fire: eligible count reported, attainable rate
nonzero.

s0(4), "REPRODUCIBLE", NEEDS ITS LEVEL STAMPED. "Replay, and a fresh seed of
the same authored world class" is L1 plus L2 in the replication taxonomy. It
does not touch L4 implementation or L5 player-build. A s0 finding is therefore
bounded to L2 unless more is run, and the word "reproducible" unqualified reads
stronger than what was done.

s0's declaration of AUTHORING INPUTS per family, and its refusal of "looks
interesting" from any judge human or model, are both correct and I would not
weaken either.
