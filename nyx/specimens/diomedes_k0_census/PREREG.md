# diomedes K0 coordinate census -- N2 preregistration (a NEGATIVE chop)

Written 2026-09-12 ~00:20 UTC BEFORE any body of the specimen was read.
Ruling: roles/Nyx/prompts/2026-09-12_ruling_n2_negative_chop/ (licensed as an
anti-harvest control; the general loop and N3 remain CLOSED). What HAS been
read for boundary-setting only: the module docstring (lines 1-40), the
import block, `wc -l`, `git log` of the file, and the list of files that
mention it. No def, class or body below line 40. No adjacent module.

## 0. The question

    CAN NYX LOOK HARD AT MACHINERY AND HONESTLY RETURN ZERO ORGANs AND
    ZERO PRESSUREs WHEN NOTHING TRANSFERABLE IS THERE?

Expected result (the null): ORGANs 0, PRESSUREs 0, useful cuts 0, with a
supported explanation. The null must be allowed to win.

## 1. Specimen boundary (FIXED; anti-fishing law)

    IN   roles/Diomedes/coordinate_census.py at f08c81c66 (388 lines,
         sha256 a7fe167ba2a1a35e...), including its self-test.
    NAMED AS DEPENDENCY, NOT ENTERED: anything it imports; aporia/lot/
         census.py (the docstring names it as the thing this is NOT);
         ROLE.md S4/S5 doctrine it says it implements; the CAR-004..006
         reports it says drifted; cycle 005 Arm A it says motivated it.
    If the file turns out to be a thin wrapper over machinery elsewhere,
    the report is SPECIMEN BOUNDARY INVALID, not a wider boundary.
    Fishing watch: every impulse to open a file outside the boundary is
    logged in CUTS.md "Fishing log" with what was NOT opened.

## 2. What counts as what (stated before inspection; not weakened for a
##    small, internal, ugly or trivial specimen)

ZERO RESULT   no candidate satisfies the ORGAN contract below and no
              candidate satisfies the PRESSURE contract; every candidate
              lands in DATA / POLICY / SCAFFOLDING / RECURRENCE /
              bookkeeping / historical residue with a stated reason.
ORGAN         a mechanism that (a) transforms an input to an output by
              steps that are not a lookup, a format change or a threshold
              comparison alone; (b) has a contract statable without
              Diomedes, cycle 005 or the K0 doctrine; (c) can be exercised
              on inputs that are not this program's (an independent
              behaviour is at least SPECIFIED); (d) is NOT an instance of a
              mechanism already in the inventory (s3) unless it has
              materially new mechanistic behaviour; (e) all fifteen
              charter questions answerable, "unknown --" legal.
PRESSURE      an environmental condition, statable without the specimen,
              under which some capability gains fitness, with world
              requirements a seat can own, a vacuity condition, closed
              shortcuts and a cheat control -- AND whose world
              requirements + fitness condition do not match an existing
              pressure (s3). "This code exists because X matters" is NOT a
              pressure.
mere bookkeeping   counters, logging, receipts, verdict formatting,
              self-test scaffolding, argument parsing, printing.
DATA          tables, thresholds' VALUES, known-answer fixtures, enums.
POLICY        a threshold or rule that decides when something counts
              (e.g. "below 0.05 disqualifies"), with no independent
              behaviour beyond the comparison.
SCAFFOLDING   code that arranges calls to other things (orchestration,
              wrappers, routing) without transforming anything itself.
duplicate / RECURRENCE   a mechanism whose input->output behaviour matches
              an inventory organ or a textbook statistical primitive (a
              bootstrap, a mean, an entropy) -- classified as RECURRENCE
              with the ancestor named, or as "known primitive, not Chop
              Shop inventory" if the ancestor is a textbook, not an organ.
interface boundary mistaken for mechanism   a function whose only
              content is its signature and a call-through.
historical residue   code whose behaviour is fully explained by an event
              in Diomedes's history (a lesson encoded) and which would not
              be written by anyone without that history; transferable only
              as a doctrine, not as machinery.

## 3. Inventory to compare against (duplicate control, names ignored)

Organs in the Chop Shop at this date (mechanism, one line each):
  map_elites (3): cell replacement by fitness in a behaviour-keyed archive;
    descriptor-keyed niching; hidden-axis retention (held)
  dreamcoder (3): library compression by repeated-subexpression search;
    wake/sleep alternation; recognition-guided enumeration
  lean_simp (4): rule canonicalization; key-path flattening w/ wildcards;
    ordered-rewriting guard for permutations; recursive side-condition
    discharge
  hypothesis_shrinker (6): order-gated greedy acceptance; simplicity
    order with inverse; adaptive step search (find_integer); pass-step
    enumeration by choice tree; standalone value shrinkers; coupled-value
    passes
Pressures (7): niche persistence under regime shift; recurring structure
  under budget; growing store must terminate; retrieval at store scale;
  conditional facts must be paid for; orientation is a choice; smallest
  witness not first. Held: mutual normalisation; encoding decides
  reachability.
Textbook primitives that would be RECURRENCE-of-textbook, not organs:
  entropy of a distribution; a bootstrap (cluster or plain); a rank /
  AUC-style score; a range check; a standard error.

## 4. Evidence required to OVERTURN the expected zero

An ORGAN is admitted only if ALL of: (i) the ORGAN contract in s2 holds;
(ii) an independent behaviour is specified as a runnable check on inputs
not from this program AND that check is RUN (this specimen is small enough
that "specified only" is not an excuse); (iii) the duplicate control
finds no inventory organ or textbook primitive with the same input ->
output behaviour, or names the materially new behaviour.
A PRESSURE is admitted only if its world requirements and fitness
condition differ from every existing pressure in s3 in a way a consumer
would have to build differently, AND a seat that could own its substrate
is named (K9).

## 5. Predictions (so the null can lose honestly)

P1  ORGANs admitted: 0. PRESSUREs admitted: 0.
P2  The five checks named in the docstring will disposition as: headroom
    -> known primitive (a score difference); gate reachable -> POLICY over
    a range computation (DATA); gate vs SE -> POLICY; cluster bootstrap ->
    RECURRENCE-of-textbook; identifiability ceiling -> a formula over an
    enumerable world (DATA/PRIMITIVE, decided at reading).
P3  At least one candidate will TEMPT an ORGAN reading (Nyx's bias to
    survive candidates, ledgered twice); it will be recorded as tempted-
    and-refused with the reason, or admitted with s4 evidence.
P4  The verdict enum and its enforcement are SCHEMA (bookkeeping).
P5  At least two of the five checks are "historical residue": encodings
    of program doctrine (gate reachability, gate vs measurement error --
    both already in Nyx's own feedback memory as rules) whose transferable
    content is the DOCTRINE, which the program already holds.
P6  Nyx will feel the pull to open aporia/lot/census.py or ROLE.md; the
    fishing log will show whether she did (prediction: she will not open
    them).

## 6. Procedure and stopping rule

K1: read the body sequentially (lines 41-388) in two windows; flow log
per window; candidates stamped at drawing (K8). K2 prefixes. K3/K4: the
self-test is the specimen's own switch -- run it (it needs nothing outside
the file per its docstring) and, if cheap, run each check on a non-
Diomedes input to test the "independent behaviour" clause. K5: name the
callees; do not enter them. K6: not applicable unless a "null" mode
exists. K7/K9/K10: apply only if a pressure is admitted.
STOP as soon as every candidate has a disposition and the s4 evidence
question is answered for each tempted ORGAN. No CUT-2 unless a candidate
is admitted; no CUT-3.
