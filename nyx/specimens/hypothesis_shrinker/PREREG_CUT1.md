# hypothesis SHRINKER -- N1 preregistration (the first transfer test of the knife)

Written 2026-09-11 (~23:00 UTC) BEFORE any body under
hypothesis/internal/conjecture/ was read. Ruling:
roles/Nyx/prompts/2026-09-11_ruling_proceed_n1/ (PROCEED N1, CAP=1).
Knife in force: nyx/KNIFE.md K1-K10 (K9, K10 added on Vivarium #182
before N1 opened; revision boundary recorded there). Rules carried
forward EXACTLY as written; none improved in anticipation. This file is
not edited after the cut begins; corrections are annotations in CUTS.md.

## 0. The question this specimen exists to answer

    Did Lean teach Nyx how to chop machinery,
    or did Nyx merely learn how to chop Lean?

Scored, at the stopping point, by: the K-rule status table (cuts.json
knife_application, statuses APPLICABLE / NOT_APPLICABLE / FIRED /
DID_NOT_FIRE / AMBIGUOUS with evidence), the four boundary categories
(inherited; independently supported; inherited-and-supported;
inherited-and-falsified -- cutledger boundary_categories_over_live), and
the eleven transfer questions of the ruling answered one by one in
nyx/CHOP_SHOP_TRANSFER_lean_vs_shrinker_<date>.md. No scalar score.

## 1. Specimen boundary (exact)

Pin: hypothesis==6.165.10, Techne lock
techne/acquisition/locks/hypothesis-cp312-win-amd64.lock.txt (wheel
sha256 3376f2594763aef14faa519b0fb27cae7ce9eeaab4c69efa07777499110306c9),
installed in Techne's isolated env F:\Prometheus\vault\techne_tools\envs\
h0h5_tools (receipt installation-hypothesis-20260909T214450Z,
INSTALLED_PINNED_AND_HASHED). The host site-packages copy is byte-
identical on shrinker.py (sha256 f364cbff15bdd1e9afe68e97eb4a895db6f8166a
d5fc83de8b4da8144e8d28e2 in both); execution uses the isolated env's
python. Techne-MANAGED: the lean_simp gap does not recur.

  IN   hypothesis/internal/conjecture/shrinker.py            (1953 lines)
       hypothesis/internal/conjecture/shrinking/*.py          ( 792 lines:
         common, integer, ordering, collection, floats, bytes, string,
         choicetree)
       hypothesis/internal/conjecture/choice.py               ( 637) -- the
         representation the shrinker operates on and, Nyx predicts, where
         "simpler" is DEFINED (P2 below); IN because a shrinker without its
         order is not a shrinker
  INTERFACE (read where the shrinker calls them, not cut)
       engine.py (1803): the entry that invokes shrinking and the function
         the shrinker calls to evaluate a candidate choice sequence
       data.py (1471): the ConjectureData object the shrinker receives
  OUT  generation (providers.py, strategies), the example database, the
       DataTree (datatree.py) EXCEPT as a K5 foreign-callee candidate,
       targeting/pareto/optimiser, the pytest plugin, settings machinery
       except the switches named in s3.
  CONSUMER CONTRACT (read as the consumer's interface; not modified, not
       cut): proteus/eval/shrink.py (174) and hypothesis_strategy.py (82);
       Techne receipt adapter_qualification-hypothesis-20260911T065703Z:
       predicate still_solves, declared order (node_count, depth,
       canonical_string), QUALIFIED_SOUND_NOT_MINIMAL, 24/45 not minimal,
       worst case target 7: '(not (not (or (and x0 x1) (and x0 x2))))'
       size 9 vs ground truth '(and (or x1 x2) x0)' size 5.
  Boundary finding at prereg: the prompt says "SHRINKER". The word in the
  source is a class (shrinker.py) AND a package (shrinking/) AND a phase
  (Phase.shrink). Which of the three the operator's word denotes is a
  CUT-1 question. Nyx will not assume the class.

## 2. Procedure (K1 skeleton-blind; K8 stamp at drawing)

1. NO grep of def/class names before candidates are drawn. Read
   shrinker.py sequentially, top to bottom, in ~250-line windows,
   recording per window what FLOWS (data in, out, state read, state
   written, callees outside the file) in CUTS.md "Flow log". Then
   shrinking/common.py, integer.py, ordering.py, collection.py; then
   choice.py; then only the call sites in engine.py and data.py that the
   flow log names. shrinking/floats.py, bytes.py, string.py, choicetree.py
   are read only if the flow log points at them.
2. Draw candidates from the flow log. Stamp origin at drawing (K8), with
   the source boundary each coincides with. boundary_support UNTESTED for
   all at CUT-1.
3. Records: ORGAN with K2 prefixes ("unknown -- ...") wherever unmeasured;
   PRESSURE organ-blind; forbidden_terms = famous names + mechanism words.
4. cutledger snapshot = CUT-1. Read the numbers only then.

## 3. Switches and negative controls BEFORE CUT-2 (K3, K4, K6)

Run in the isolated env, receipt committed. Order: negatives first.
  N-a  ALWAYS-FALSE predicate on a fixed failing example: the shrinker
       must return the ORIGINAL unchanged (no shrink is possible). Fires
       if anything else comes back.
  N-b  LOCAL-MINIMUM PLANT: a predicate whose true minimum is not
       reachable by any single choice-level change from the start (two
       coordinated changes needed). Prediction P3: the shrinker STOPS at
       the local minimum; if it reaches the global one, a route Nyx did
       not enumerate exists (the c23 pattern).
  N-c  NULL CONFIGURATION (K6): settings(phases=[explicit, reuse,
       generate]) -- i.e. Phase.shrink EXCLUDED. Is the reported example
       really unshrunk? Compare against the raw first failure. Prediction:
       something still reduces it (the DataTree or the generation order);
       if nothing does, K6 DID_NOT_FIRE and that is recorded.
  N-d  NON-MONOTONE predicate (fails on a set with holes): does the
       shrinker's answer depend on the seed? Two seeds; same start.
  P-a  standalone shrinking/*.py classes called WITHOUT the engine
       (Integer.shrink, Ordering.shrink, Collection.shrink on plain Python
       values with a lambda predicate). This is the first INDEPENDENT-OF-
       ANCESTOR behaviour test in the Chop Shop's history if it runs; if
       the classes need the engine, that is the finding.
  P-b  the Proteus worst case (target 7) re-run through the consumer's own
       predicate to see WHICH pass leaves the double negation standing --
       only if the flow log makes the pass structure legible; otherwise
       recorded as not run.
  S-a  derandomize=True vs a fixed seed: does the shrunk result change?
  S-b  Phase.shrink on vs off on N-a..N-d.

## 4. Bookkeeping (deterministic; defined before the cut)

nyx/chop/cutledger.py over nyx/specimens/hypothesis_shrinker/cuts.json,
now with boundary_support per candidate and knife_application per rule
(added 2026-09-11 by the ruling; test nyx/tests/test_cutledger.py).
The Phase V metrics map as for lean_simp (PREREG there, s3). The
composite "did iteration improve it" is carried over UNCHANGED
(materially_revised > 0 AND VERBOSITY_FAILURE false AND
unknown_became_known > 0 per transition) so that the two specimens are
comparable; its known weakness (it needs literal unknowns at CUT-1,
which K2 now guarantees) is what makes it attainable this time.

## 5. Predictions

P1  CUT-1 inherited-boundary rate under K1 will be BELOW 0.87 and ABOVE
    0.30. (A rate near 0 would itself be suspicious -- the ruling's
    anti-pattern; a rate near 0.87 means K1 DID_NOT_FIRE.)
P2  "simpler" (the shrink ORDER) is defined OUTSIDE shrinker.py, in
    choice.py's indexing of choices, and is POLICY/DATA, not mechanism:
    the shrinker minimises an index the representation supplies.
P3  N-b: the shrinker stops at the planted local minimum (the pass set
    is a human prior about which moves are worth trying).
P4  P-a runs: at least Integer and Ordering shrink correctly outside the
    engine. First independent behaviour reproduced.
P5  A K5 foreign callee will matter: the DataTree (datatree.py, OUT of
    boundary) answers "already tried" for the shrinker and so shapes what
    the shrinker can explore; predicted to show up in N-c.
P6  Techne's not-minimal cases are explained by the cut: shrinking acts
    on the CHOICE SEQUENCE the strategy consumed, not on the program
    tree, so a structural simplification (double negation) that the
    strategy's encoding does not make adjacent is unreachable. If the
    flow log shows a tree-level pass exists, P6 is falsified.
P7  At most 2 ORGANs survive to the stopping point; at least one CUT-1
    ORGAN becomes POLICY.

## 6. Stopping rule

CUT-1 dies (DEAD CUT recorded, no CUT-2) if every candidate is
INHERITED and the switches in s3 leave none of them with an independent
behaviour. CUT-2 proceeds after the s3 runs, on paper, only for what the
runs left standing. CUT-3 only on a consumer return (Proteus is
addressable and named in #189) or a finding that the s3 runs contradict a
CUT-2 disposition. A natural stopping point is reached when the s3 list
is exhausted and CUT-2 is written; then the transfer assessment, then
HOLD per the metabolic gate (one substantive return exists: #182; N2 is
to be ASSESSED, not begun).

## 7. K-rule table to be filled (statuses and evidence in cuts.json)

    K1 skeleton-blind        K2 unknown prefix        K3 switches before paper
    K4 negatives first       K5 foreign callee        K6 null config not null
    K7 consumer-first        K8 origin at drawing     K9 route to owner
    K10 one-sided null
All start APPLICABLE except K7/K9/K10, which are consumer-flow rules and
apply only if a pressure is delivered (K9: the owner is Proteus for any
pressure this specimen yields, since the consumer is Proteus's H1
minimiser).
