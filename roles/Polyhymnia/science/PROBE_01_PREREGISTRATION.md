# PROBE-01 preregistration: a coding-theory decoder family through the H5 consumer slot

Currency: 2026-09-11. COMMITTED BEFORE ANY RUN (base role s2: preregister
in its own commit). Authority: operator directive
roles/Polyhymnia/prompts/2026-09-11_reactivation_direction/ (POLY-01:
"identify the smallest existing Prometheus 2.0 consumer interface through
which one representation candidate can actually alter an experiment ...
Then construct ONE end-to-end probe").

## 0. The chain, filled in

    source/mechanism      syndrome (coset-leader) decoding of a binary linear
                          [12,8] code (Hamming 1950; coding theory). The genome
                          is read as a RECEIVED WORD; the phenotype is the
                          information part of the nearest codeword.
    representation cand.  h5.lincode.v0#<A>: a Decoder int->int on 0..4095,
                          parameterised by an 8x4 parity matrix A over GF(2).
                          direct (Archaeon's h5.direct.v0) is the A=0 member.
    consumer              the H5 lane's producer-side decoder slot:
                          archaeon/producer/h5_decoders.check_exact (the
                          admission gate: total, 256 rules, 16 preimages each)
                          and archaeon/producer/h5_reference.exact_reference
                          (the observable), collapsed with Herakles's
                          published class map herakles/eca/class_map_fixture.json
                          (256 rules -> 224 terminal-behaviour classes at 8
                          steps on the 7-ring). The live consumer is
                          archaeon/producer/campaign_h5.h5_readout, whose
                          hardcoded dict {direct, balanced_7,
                          scrambled_direct_3} is the exact place a candidate
                          enters the experiment.
    measurable difference reach[g] (distinct non-parent phenotypes among the
                          12 single-bit mutants) and neutral[g], per genome,
                          raw (rules) and collapsed (classes): histogram,
                          mean, min, max.
    deterministic obs.    exact enumeration of 4,096 x 12 = 49,152 edges per
                          decoder; reference_digest sha256 over the per-genome
                          vectors; no sampling, no engine, no model.

Why this consumer and not another (the search, 2026-09-11, tree 05b1134e6
merged): H5 is the program's encoding lane ("Do learned encodings improve
access to useful variation?", DESIGN_H0_H5_v0.1 s5) and its alpha route
applies the decoder producer-side with the evaluator consuming only the
resolved rule -- the decoder IS the representation and it already has a
slot, an admission gate, a null (scrambled) and an exact observable.
Proteus's H1 substrate exposes genome_read but no representation slot;
Ludus (World Foundry) names representation failure as something to
record, not an input; H3's descriptor function is a second candidate
slot (declared v1 by Archaeon 2026-09-10) but its stream is not yet
running. H5 is the smallest existing interface: one Python callable.

## 1. The family, exactly

Genome g in [0, 4096): m = g & 0xFF (8 information bits), p = g >> 8
(4 parity bits). Systematic code with parity matrix A (8 rows, each a
4-bit vector): codewords are (m, m*A) where m*A = XOR of rows A_i over
set bits i of m. Syndrome s(g) = (m*A) XOR p. Parity-check columns:
A_i for information bit i (0..7), unit vector e_j for parity bit j
(8..11). Coset leader L[s] = the first error pattern in (weight, integer)
order with syndrome s, over all 4,096 patterns (deterministic ties).
Decode: rule(g) = (g XOR L[s(g)]) & 0xFF.

Multiplicity 16 for every rule, by construction: within each coset,
g -> g XOR L[s] is a bijection onto the code, and the code has exactly
one codeword per information word. check_exact is still run on every
member; the construction argument is not a substitute for the gate.

Members in this probe (all deterministic, no seeds except where named):

    direct         A = 0. Archaeon's h5.direct.v0 itself; the family must
                   reproduce it entry for entry (positive control).
    hamming        A rows = the 8 smallest 4-bit vectors of weight >= 2:
                   3,5,6,7,9,10,11,12. All 12 parity-check columns are
                   distinct and nonzero, so minimum distance is 3: a
                   shortened Hamming [12,8,3] code. 13 cosets have
                   weight-<=1 leaders; the 3 syndromes {13,14,15} get
                   weight-2 leaders.
    random#1, #2   A drawn from random.Random(sha256("polyhymnia.lincode.v0|A|<seed>")),
                   rows unrestricted (may be 0 or unit vectors, so
                   distance may be 1 or 2). The family's ordinary member.
    scrambled(hamming)   Archaeon's make_scrambled(hamming, 3): the
                   frequency-preserving null. Invariance control.

## 2. Attainable range and eligibility (before reading any number)

reach[g] in [0, 12]; neutral[g] in [0, 12]; reach + neutral <= 12 for every
genome under every decoder. Known fixed points: direct has reach = 8 and
neutral = 4 for all 4,096 genomes (Archaeon test_h5_reference; the 4
parity bits are inert). Eligible genomes: 4,096 per decoder, all of them;
eligible edges 49,152. Nothing here can fail to fire: the observable is
total. Class collapse can only lower reach (Archaeon's test).

Harmonia's construction fact applies (campaign_h5.h5_readout): "direct
reach <= 8 and permuted up to 12 is analytic; only the excess over that
bound is evidence". This probe therefore separates ANALYTIC facts (P1-P4)
from MEASURED quantities (M1-M5) and claims evidence for neither about
usefulness (section 5).

## 3. Predictions, frozen

Analytic (derived on paper; a failure is a defect in the implementation
or in the derivation, and either is reported):

    P1  hamming: exactly 256 genomes (the codewords) have neutral = 12 and
        reach = 0. Every single flip of a codeword lands in a weight-1
        coset whose leader undoes it.
    P2  hamming: max reach <= 11. From any non-codeword genome at least one
        flip is neutral (the flip that removes the leader's first bit).
    P3  hamming: every rule's 16 preimages contain a connected 13-genome
        ball (codeword + 12 neighbours) plus 3 satellites (one from each
        weight-2 coset). direct's 16 preimages are one 4-dimensional cube.
    P4  scrambled(hamming): reach histogram and mean_neutral IDENTICAL to
        hamming (relabelling rules cannot change adjacency structure).
    P5  the A = 0 member equals h5.direct.v0 on all 4,096 genomes
        (table_sha256 equal).

Measured (numbers to be filled by the run; directions stated where I
have one, so a wrong direction is on record):

    M1  hamming mean neutral: I expect BELOW direct's 4.0 (centers give
        12 but 3,840 non-codewords give few), with min 0 or 1 and max 12:
        a bimodal neutral histogram versus direct's point mass at 4.
    M2  hamming mean reach (rules): I expect ABOVE 8.0 (surface genomes
        exit toward up to 11 distinct codewords) with min 0.
    M3  hamming mean reach (classes, 224-map): below M2; direction versus
        direct's class-collapsed mean NOT predicted.
    M4  random#1, random#2: between direct and hamming on M1/M2 is my
        guess; NOT a prediction, a guess recorded as such.
    M5  class-collapsed reach for hamming vs balanced_7 (Archaeon's
        random-permutation member): no prediction.

Null result is acceptable: if M1/M2 land on direct's values the family
is analytically distinct (P1-P3) but observably no different at this
scope, and that is the reported result.

## 4. Controls, declared

    positive   direct via the family (A = 0) reproduces {8: 4096}, neutral 4.0
               (the channel detects the known structure).
    planted    hamming carries an analytically planted feature: exactly 256
    (cheat)    genomes at reach 0 / neutral 12 (P1). The channel must report
               exactly 256; any other count is a broken channel, whatever
               the rest says. This is the cheat control: success deliberately
               injected, its exact magnitude known in advance.
    invariance scrambled(hamming) must reproduce hamming's histogram exactly
    (negative) (P4); a difference would mean the channel reads labels, not
               adjacency.
    gate       a deliberately non-uniform decoder (rule = g mod 255) must be
    (refusal)  REFUSED by check_exact. The admission gate can fail closed.
    spread     random#1 != random#2 on at least one of {histogram, mean
               neutral}: the channel is not reporting a constant.

## 5. Limits of inference, stated now

- This probe measures ACCESS STRUCTURE (reach, neutrality) at the 7-ring /
  8-step scope on Herakles's published map. It does not measure whether
  the accessible variation is USEFUL (that is H5 beta: task scores,
  matched budgets, training cost). No evolvability claim follows from
  any number here.
- The published class map (224 classes) is the fixture; the live map
  from H5-1 is partial (232 of 256 rules, 24 held by ARCH-28) and is not
  used (wrong-population rule). When the live map completes, the run is
  repeated on it; disagreement is reported, not reconciled by hand.
- A decoder family that satisfies the multiplicity gate is admissible to
  the slot; admissibility is not consumption. Whether the H5 lane takes
  a lincode member as a beta comparison arm is Archaeon's contract to
  give (comms question, five fields, Talos #50 protocol). Interest is
  not a contract.

## 6. Run plan (nothing below has been executed at this commit)

    python -m pytest roles/Polyhymnia/science/tests -q      # gate, P1, P2, P4, P5, refusal
    python roles/Polyhymnia/science/probe_01_run.py         # writes ledgers/probe_01_lincode_2026-09-11.{json,md}

Outputs carry: decoder_id, table_sha256, reference_digest (raw and
collapsed), class_map fixture_digest, the histogram, and the P/M table
with PASS / FAIL / MEASURED per row. The rows ship in the same commit
as the readout.

## 7. Corrections (annotations beside the original; the text above is unchanged)

- 2026-09-11, before the probe run, on the first test run: P3 is WRONG as
  derived. The three weight-2 satellites c+e_a+e_b are each adjacent to
  the two surface points c+e_a and c+e_b (either flip lands in a weight-1
  coset that decodes back to c), so a rule's 16 preimages under hamming
  form ONE connected component, not 13+1+1+1. Verified exactly for all
  256 rules: internal-degree multiset per rule {12:1, 3:2, 2:5, 1:8}
  (hamming) versus {4:16} (direct). P3 is restated as: "hamming: one
  connected component of 16 with a center adjacent to 12 siblings;
  direct: one 4-regular cube of 16". P1, P2, P4, P5 stand as written.
  Recorded in calibration/LEDGER.md.
