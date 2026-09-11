/-!
Nyx, 2026-09-11. Cheap ablations and controls for the lean_simp specimen, CUT-3.
Run with the PINNED toolchain only (the elan default on this machine is a 2023 nightly):
  ~/.elan/toolchains/leanprover--lean4---v4.30.0/bin/lean cut3_ablations.lean
Core Lean only; no mathlib import. Every block whose outcome is a message is wrapped in
#guard_msgs with the message OBSERVED on 2026-09-11 (Lean 4.30.0, d024af099); a deviation
is a compile error, so a clean exit is the receipt. Blocks without #guard_msgs are positive
controls that must simply elaborate.
-/

-- Inert definitions and rules over them, so the store is under our control.
def f (n : Nat) : Nat := n
def g (n : Nat) : Nat := n
def h (n : Nat) : Nat := n
def k : Nat := 2
theorem fg (x : Nat) : f x = g x := rfl
theorem gf (x : Nat) : g x = f x := rfl
theorem gh (x : Nat) : g x = h x := rfl

/-! ## c06 ordered rewriting guard -- POSITIVE control
A store containing only a commutativity rule terminates AND rewrites one direction. -/
example (a b : Nat) : b + a = a + b := by simp only [Nat.add_comm]

/-! ## c08 -- CHEAT CONTROL D3: a planted two-rule loop must hit the budget, not report
"no progress". OBSERVED: the step-limit error. FIRED. -/
/--
error: `simp` failed: maximum number of steps exceeded
-/
#guard_msgs in
example : f 1 = 1 := by simp (config := { maxSteps := 200 }) only [fg, gf]

/-! ## c08 fixpoint -- POSITIVE: a rule enabled by another rule's result fires. -/
example : f 1 = h 1 := by simp only [fg, gh]

/-! ## A3 singlePass -- ABLATION: with the re-loop off, the chained rewrite fails to close.
OBSERVED as predicted. -/
/--
error: unsolved goals
⊢ g 1 = h 1
-/
#guard_msgs in
example : f 1 = h 1 := by simp (config := { singlePass := true }) only [fg]

/-! ## A2 memoize -- ABLATION: same result with the memo off. OBSERVED as predicted. -/
example : f 1 = h 1 := by simp (config := { memoize := false }) only [fg, gh]

/-! ## A1 index -- ABLATION (c02): root-symbol-only retrieval gives the same result.
OBSERVED as predicted. -/
example : f 1 = h 1 := by simp (config := { index := false }) only [fg, gh]

/-! ## c23 decide route -- POSITIVE: closes with decide on. -/
example : (2 : Nat) + 2 = 4 := by simp (config := { decide := true }) only []

/-! ## c23 -- NEGATIVE CONTROL THAT DID NOT FIRE (the CUT-3 finding)
Prediction at CUT-2: with decide off and the Nat literal folders erased, 2 + 2 = 4 does not
close. OBSERVED: it closes. Trace (probe_route.lean): `eq_self:1000: 2 + 2 = 4 ==> True`.
Route: the hidden `simp only` builtins (Elab/Tactic/Simp.lean 410: eq_self, iff_self) plus
UNIFICATION deciding `2 + 2 =?= 4` by definitional Nat-literal evaluation inside Meta.isDefEq.
Neither is a simp route Nyx enumerated. The block below records the observed behaviour. -/
example : (2 : Nat) + 2 = 4 := by simp (config := { decide := false }) only [-Nat.reduceAdd, -Nat.reduceEqDiff]

/-! Erase the hidden builtin too: NOW the negative control fires. -/
/--
error: `simp` made no progress
-/
#guard_msgs in
example : (2 : Nat) + 2 = 4 := by simp (config := { decide := false }) only [-Nat.reduceAdd, -Nat.reduceEqDiff, -eq_self]

/-! Block the literal defeq with a non-reducible definition: eq_self no longer matches. -/
/--
error: `simp` made no progress
-/
#guard_msgs in
example : k + k = 4 := by simp (config := { decide := false }) only []

/-! ## c01 canonicalization -- POSITIVE: a bare Prop-shaped fact and an iff both act as rules. -/
theorem p_true : f 0 = 0 := rfl
theorem iff_rule (x : Nat) : (f x = x) ↔ True := by simp [f]
example : f 0 = 0 := by simp only [p_true]
example : f 5 = 5 := by simp only [iff_rule]

/-! ## c07 recursive discharge -- POSITIVE and A6 ABLATION
A conditional rule whose guard is provable by the (hidden-builtin) store fires at depth >= 1
and does not fire at maxDischargeDepth := 0. -/
theorem fcond (x : Nat) (_h : x = x) : f x = x := rfl
example : f 3 = 3 := by simp only [fcond]
/--
error: `simp` made no progress
-/
#guard_msgs in
example : f 3 = 3 := by simp (config := { maxDischargeDepth := 0 }) only [fcond]
