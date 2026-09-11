set_option trace.Meta.Tactic.simp.rewrite true in
example : (2 : Nat) + 2 = 4 := by simp (config := { decide := false }) only [-Nat.reduceAdd, -Nat.reduceEqDiff]

set_option trace.Meta.Tactic.simp.rewrite true in
example : (2 : Nat) + 2 = 4 := by simp (config := { decide := false, ground := false }) only [-Nat.reduceAdd, -Nat.reduceEqDiff]

-- all simprocs off
example : (2 : Nat) + 2 = 4 := by simp (config := { decide := false }) -simprocs only []
