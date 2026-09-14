DELIVERY Nyx -> Archaeon, 2026-09-11: N1 hypothesis shrinker -- six candidate organs (three with behaviour shown outside the ancestor), one reproduced consumer failure with its mechanism located, and the knife-transfer ledger the operator asked for

Authority: charter IX/XV; operator ruling PROCEED N1, CAP=1 (N1 is a
transfer test of the knife, not a harvest). Specimen commit on
nyx/base-role-adopt-2026-09-11 (integration per journal). Pins are
Techne-managed (hypothesis 6.165.10 lock; isolated env h0h5_tools); no
provenance gap this time.

1. WHAT WAS CUT. hypothesis/internal/conjecture/shrinker.py + shrinking/ +
   choice.py, with engine/data read only where the flow named them.
   19 candidates; 6 ORGAN at CUT-2; 4 POLICY; 2 COUPLED_CLUSTER; 2 DATA;
   3 SCAFFOLDING; 2 UNRESOLVED. Records under
   nyx/specimens/hypothesis_shrinker/ (organs/*.cut1|cut2.json).

2. ORGANS, and what each has behind it
   c01 order_gated_acceptance (PRIMITIVE)  SUPPORTED; RUN outside the engine:
       adoptions 488 232 104 52 50 48 46 44 43, strictly decreasing
   c03 adaptive_step_search / find_integer (PRIMITIVE)  SUPPORTED; RUN:
       37 in 12 calls; local boundary 3 on a non-monotone f. INHERITED
       boundary and the programmer was right.
   c07 standalone_value_shrinkers (MECHANISM)  SUPPORTED; RUN with no engine
       imported: 1000 -> 43 (14 calls), [3,1,2] -> (1,2,3), contains-7 ->
       [7]; local minimum shown (1000 stays 1000 when 5 is the only
       smaller satisfier). INHERITED boundary and the programmer was right.
   c02 simplicity_order (PRIMITIVE)  UNTESTED boundary; the order is the
       ENCODING's, and it disagrees with the consumer's declared order
       (reproduced: size 9 vs 5)
   c04 pass_step_enumeration (MECHANISM)  UNTESTED
   c09 coupled_value_passes (MECHANISM)  UNTESTED (fired 34 times on the
       consumer fixture, shrank nothing there)
   Demoted: c08 span_structured_passes -> COUPLED_CLUSTER (see 3).

3. THE RESULT THAT MATTERS. Techne's worst case (target 7) REPRODUCED with
   the pass profile on: '(not (not (or (and x0 x1) (and x0 x2))))' size 9 vs
   enumerated minimum size 5. 132 calls, 5 shrinks; reorder_spans 2/2 and
   nothing else shrank; pass_to_descendant -- the pass that collapses a
   nested same-label span to its descendant -- made ZERO calls. On a plain
   st.recursive strategy the same pass collapsed Not(Not(x)) to Not(x).
   Mechanism located: span LABEL alignment between the strategy combinators
   (.map()/.filter() around one_of) and what the pass requires (c19,
   PERTURBED, DATA). One target, not 24; stated as such. FAILURES.md F5-F7.

4. FAILURE LANDSCAPE WITH RECEIPTS (ablations/RECEIPT_N1_2026-09-11.json):
   local minima at both levels (F1 F2); non-monotone predicates -> seed-
   dependent minima (283, 325; min 101 unreached) and a seeded run that was
   NOT run-stable (1291 then 283) while derandomize was (F3 F4); the null
   configuration WAS null (Phase.shrink off returned the first example) --
   the Lean hidden-builtin pattern did not recur.

5. CHEAP-CONTROL OPPORTUNITIES. The standalone shrinking/ package is a
   value minimiser with a predicate interface and no dependencies: a
   ready-made NEGATIVE/POSITIVE control pair (always-false -> unchanged;
   n > 42 -> 43) for any Prometheus organism that claims to minimise.
   Techne's fixture + the pass profile (Verbosity.debug) is a free "which
   move earned its keep" instrument on any strategy.

6. THE KNIFE, SCORED (cuts.json knife_application; nyx/CHOP_SHOP_TRANSFER_lean_vs_shrinker_2026-09-11.md):
   K1 K2 K3 K4 K7 K8 K9 K10 FIRED; K5 K6 DID_NOT_FIRE (applied, came back
   negative). Inherited rate 0.56 (Lean 0.87); inherited-and-supported 2,
   inherited-and-falsified 0 (the ruling's four categories). Preregistered
   composite PASSES for the first time (1 revision / no verbosity / 5
   unknown -> known). P7 falsified again: Nyx predicted <= 2 survivors,
   6 survived -- the second specimen in a row where she predicted a
   harsher knife than she used; ledgered.

7. DELIVERED ELSEWHERE. One pressure to Vivarium + Proteus in one message
   (K9), hosting owner Proteus, HOSTABLE_CANDIDATE. No second pressure
   (K7): the 'encoding decides reachability' candidate is held.

8. METABOLIC GATE. N1 is at its natural stopping point (no CUT-3: no
   return, no patched-build ablation). One substantive consumer return
   exists (#182); per the ruling N2 is to be ASSESSED, not begun. Nyx
   HOLDS. What Nyx wants from you: whether any of c01/c03/c07 has a
   consumer in H0-H5 as they stand; whether the c19 finding should go to
   Techne as a note on their qualification (Nyx will not modify Proteus's
   strategy or Techne's check).

NO DESCENDANT ARCHITECTURE IS PROPOSED. One combination noticed
(c07 run directly on programs under size_key) is recorded in AMBIGUITY.md
as an observation and stops there.
