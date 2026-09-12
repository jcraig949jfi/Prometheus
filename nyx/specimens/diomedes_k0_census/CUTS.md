# diomedes K0 census -- the cut (a NEGATIVE chop; one cut, stopped early by design)

Currency: 2026-09-12. Ledger: cuts.json. Receipt: ablations/RECEIPT_N2_2026-09-12.json.

## Flow log (K1; lines 41-388 read in two windows after the docstring)

W1 41-220: constants (HEADROOM_FLOOR 0.05; VERDICTS); auc (exact, tie-aware,
   O(pos x neg)); conditional_headroom: count per-action success rates
   globally and per context; per state compute AUC of (rate, label),
   AUC of (context-rate, label), oracle AUC (label as its own score),
   chance AUC; ceiling = mean of cond (if context) else marg; headroom =
   oracle - ceiling; qualifies iff >= floor; entropy of the action
   alphabet; gate_reachable (range test); gate_exceeds_error (distance
   >= 2 err); cluster_bootstrap (resample whole clusters n times via an
   LCG, sort, 2.5/97.5 percentiles); _Lcg (a*s+c mod 2^31; below(n) =
   s % n).
W2 221-388: identifiability_ceiling (group causes by signature; sum of
   P(sig)/|causes|); car (assemble a record; verdict by entropy ~ 0 ->
   VACUOUS, qualifies -> ADEQUATE, else INADEQUATE; assert in enum;
   warn on empty decision); _planted_controls (cheat / negative /
   vacuous fixtures with exact expected values); _selftest (reads sibling
   cycle005_operator_tables.json; recomputes b3 b4; asserts committed
   constants; exercises the gates on the seat's own past failures; demo
   identifiability and bootstrap; CAR demo); __main__ prints.

## Candidates (12), all INHERITED (each is one def or one constant)

    id  disp         reason (one line; full text in cuts.json notes)
    c01 RECURRENCE   Mann-Whitney AUC (textbook), hand-recomputed to 1e-4
    c02 RECURRENCE   TEMPTED: headroom statistic; behaves on foreign inputs; equals a textbook baseline-vs-oracle AUC gap; refused on the duplicate control
    c03 RECURRENCE   Shannon entropy
    c04 POLICY       range check = doctrine 'gate must be shown reachable' (Nyx holds it as feedback memory)
    c05 POLICY       2x-error rule = doctrine 'gate must exceed measurement error' (same)
    c06 RECURRENCE   textbook cluster bootstrap -- with a DEFECT found by running it (F1)
    c07 RECURRENCE   TEMPTED: identifiability ceiling; equals Bayes-optimal accuracy under signature ambiguity; refused on the duplicate control
    c08 SCAFFOLDING  CAR assembly + enum enforcement (schema); the verdict rule is POLICY
    c09 DATA         planted-control fixtures (base-role rule 3 as data)
    c10 SCAFFOLDING  differential self-test; historical constants
    c11 DATA         the 0.05 floor
    c12 DATA         the states schema (an interface)

## Result

    ORGANs 0   PRESSUREs 0   useful cuts 0   SPECIMEN BOUNDARY VALID
    The null is SUPPORTED: every computation in the file is a textbook
    statistic or a threshold rule; the Diomedes-specific content is which
    baseline is compared, which constants are asserted, and which doctrine
    is enforced -- POLICY, DATA and historical residue. Transferable
    content: the DOCTRINE, which the program already holds elsewhere.

## Tempted and refused (P3 held)

c02 and c07 both passed the ORGAN contract clauses (a)-(c) and had their
independent behaviour RUN on non-Diomedes inputs -- which is exactly why
they tempt. Both failed clause (iii): their input -> output equals a
textbook quantity recomputed by hand in the receipt. Under the ruling,
"found in another program" is not a new ORGAN. Had the duplicate control
not been preregistered, Nyx would have written two organ records.

## Fishing log: five impulses, zero opened (cuts.json fishing_log)

## Numbers

    inherited 12/12 = 1.00 (reported, not optimised); independently
    supported boundaries 7 (all textbook recurrences and policies exercised
    once each); inherited-and-supported 7; inherited-and-falsified 0;
    K statuses: K3 K4 K8 FIRED; K1 K5 DID_NOT_FIRE; K2 K6 K7 K9 K10 N/A.
    Predictions: P1 CONFIRMED (0/0); P2 CONFIRMED except headroom, which
    Nyx read as a statistic rather than a 'known primitive' -- same
    disposition, different reason; P3 CONFIRMED (two tempted); P4
    CONFIRMED; P5 CONFIRMED (c04 c05 c10); P6 CONFIRMED (five impulses,
    none opened).
