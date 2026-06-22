# Harmonia D — Resume State (2026-06-15: T1b/T0 tiers + EC rich diagonal)

**Worked:** 2026-06-15 (Harmonia_M2_D). Follows `SESSION_STATE_20260610_proposal_B_done.md`.
**Status: all deliverables complete + validated; NOT yet committed** (on `main`;
held per harness "commit only when asked" — ready to commit on request).

---

## One-paragraph state

Picked up the post-Proposal-B open queue. (1) **Postgres recount stays parked**
— 192.168.1.176:5432 UNREACHABLE for a 3rd straight session; coverage claim
parked indefinitely, everything else stands. (2) **Engine taxonomy upgrade
shipped** (owed by B_RESULTS §4): added `T0_TAUTOLOGY` (guards self-test
generators like b1) and `T1b_THEOREM_PIGEONHOLE` (domain-restricted, population-
true pigeonhole) to `lattice_void_miner.py`, plus a `D_THEOREM` refinement to the
diagonal path — all backward-compatible (gated on injected `domain_theorems` /
`tautology_check`, empty by default). (3) **a3 reclassified** with Mazur injected:
split `24/173/53 → 24/6/172/48` (6 cells to T1b; reconciled the 5-vs-6 vs
closure-stress — `mod_3` neutralises `trace_field_class`'s unknown semantics, a
refinement not a contradiction). (4) **Cross-instance loop closed:** re-running
the sweep revealed Harmonia B shipped (commit `cbcf8abb`) the degeneracy guard +
`register()` hook D filed — `costume_gate` migrated off the `CATALOG[name]=`
monkey-patch; generic control now `DISTINCT` not the spurious
`COSTUME_OF:marginal_majority`. (5) **EC rich diagonal mined** (panel #1 target):
9 invariants, Mazur injected → **0 novel within-object laws**; 176 D_JOINT fully
partitioned (41 definitional conductor/radical family + 9 known torsion|∏c_p +
126 cm/signD/sha_an degeneracy), perm-null cleanly isolates the 50 real laws from
the 126 degenerate. D_THEOREM=98 (Mazur tier earning its keep on a new lattice).

---

## Deliverables (all on disk, validated, UNCOMMITTED)

- `D:\Prometheus\harmonia\primitives\lattice_void_miner.py` — +T0/T1b nulls, classifier `T4→T0→T1→T1b→T2→T3`, `domain_theorems`/`tautology_check` spec fields, diagonal `D_THEOREM`, `costume_gate` on `register()`
- `D:\Prometheus\harmonia\experiments\test_lattice_void_miner.py` — **34/34** (16 orig + 18 new tier tests + negative controls)
- `D:\Prometheus\harmonia\experiments\a3_lattice_void_sweep.py` — injects `DOMAIN_THEOREMS={torsion: Mazur}`; regenerated `a3_lattice_sweep_results.json` + `a3_candidate_identities.jsonl`
- `D:\Prometheus\harmonia\experiments\validate_b_results.py` — **29/29** (split updated to 24/6/172/48; degeneracy-guard-closed check)
- `D:\Prometheus\harmonia\experiments\ec_rich_diagonal_sweep.py` — NEW driver → `ec_rich_diagonal_results.json`
- `D:\Prometheus\harmonia\experiments\validate_ec_rich_diagonal.py` — **16/16**
- `D:\Prometheus\harmonia\proposals\2026-06-09\B_RESULTS_2026-06-10.md` — §3/§4/§5 + header updated with the T1b upgrade + loop-closed note
- `D:\Prometheus\harmonia\proposals\2026-06-09\EC_RICH_DIAGONAL_2026-06-15.md` — NEW results doc

**Sanity on resume:** `test_lattice_void_miner.py` 34/34, `validate_b_results.py`
29/29, `validate_ec_rich_diagonal.py` 16/16, `test_baseline_costume_parity.py`
(B's, run with `PYTHONPATH=/d/Prometheus`) all-pass.

---

## What's still open (priority order)

1. **COMMIT** this session's work (held for the user; suggested message:
   "Harmonia D: T0/T1b/D_THEOREM tiers + a3 Mazur reclassification; costume_gate
   on register() (B loop closed); EC rich diagonal — 0 novel laws").
2. **Postgres recount** — still blocking the a3 coverage claim ONLY; unreachable
   3 sessions; treat as parked indefinitely unless the host returns.
3. **Next mining target** (panel #2): **g1 Galois-twist pairs** — non-product so
   nulls informative, but THIN (23 pairs); needs catalog enrichment first. EC
   diagonal cheap-integer invariants are now mined out for pairwise laws.
4. **FP nomination for Harmonia E:** *sign-variant fan-out* — one relation
   re-counted N× under parity-preserving / sign-invariant operators (conductor/
   radical fact = 41 cells; torsion|∏c_p = 9). Detector: canonicalise to
   (invariant-pair, relation, parity-class) before counting. (Filed in
   EC_RICH_DIAGONAL §2.)
5. **`sha_an` needs a unary-property miner** (perfect-square structure is a
   single-invariant fact, invisible to a 2-invariant diagonal). Not a void-miner job.

## Doctrine reinforced this session

- **Re-running after a context gap can surface cross-instance fixes.** B closing
  D's filed loop only became visible on re-execution; an artifact-only check would
  have missed it. (executing lens > reading lens, again.)
- **Sign/operator fan-out inflates candidate counts ~10×.** Always canonicalise
  to the law's symmetry class before declaring "N untagged survivors."
- **A taxonomy refinement that moves cells DOWN the triviality ladder cannot
  create a discovery** — T3→T1b removes false marginal-facts, it doesn't add laws.
