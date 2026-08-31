# PREREG-PREFLIGHT — Primary Substrate + Accessibility Preflight (Phase 0)

Status: FROZEN 2026-08-27 (thresholds fixed before any evidence-seed run).
Engineering seeds (1000–1999) were used to size budgets and validate the
instrument; every post-calibration change is logged in ledgers/BUILD_LOG.md.

## 1. Primary substrate: RM-D5 (bounded register machine)

Chosen for: exact deterministic execution, cheap exhaustive verification over
finite input domains, machine-native observations (no natural language), rich
compositional structure, and a genotype space where mutation physics defines a
real transformation graph.

### 1.1 Machine
- Words: 16-bit unsigned, all arithmetic mod 2^16.
- Registers: r0..r7. Inputs load into r0..r(k-1); all other registers start 0.
- Output: value of r0 at halt.
- Program: list of 1..24 instructions (MAX_LEN = 24).
- Step budget: 512 executed instructions; exceeding it halts execution where it
  stands (output = current r0). Execution is therefore total and deterministic.

### 1.2 Instruction set (14 opcodes)
Instruction = (op, a, b); a is always a register index 0..7.
- MOV a b : ra := rb
- SET a c : ra := PALETTE[c]; PALETTE = [0,1,2,3,5,7,11,13,16,255] (c in 0..9)
- ADD a b : ra := (ra + rb) mod 2^16
- SUB a b : ra := (ra - rb) mod 2^16
- MUL a b : ra := (ra * rb) mod 2^16
- AND/OR/XOR a b : bitwise
- SHL a b : ra := (ra << (rb mod 16)) mod 2^16
- SHR a b : ra := ra >> (rb mod 16)
- MOD a b : ra := ra mod rb if rb != 0 else 0
- SKZ a _ : if ra == 0 skip next instruction
- SKG a b : if ra > rb skip next instruction
- JNZ a k : if ra != 0 jump back k instructions (k in 1..8); bounded by the
  global step budget, so loops are possible but always terminate.

### 1.3 Phenotype / behavior
For a probe input set P (frozen per assay/family), the behavior of program g is
the output vector [run(g, x) for x in P]. Behavior class = SHA-256 of that
vector. Behavior distance between g and a target vector = Hamming mismatch
count over P (bookkeeping/navigation metric ONLY — task correctness in later
phases uses the exact oracle over the task's FULL domain, never a fingerprint).

### 1.4 Starting repertoire (frozen)
16 literal trivial programs (identity, the 10 palette constants, ADD/XOR/MUL/
SHR/self-input combinators) listed exactly in mutation/physics.py:SEED_REPERTOIRE.
No other starting material for navigators or (later) the learner.

## 2. Frozen mutation physics
Six mutation classes, drawn uniformly at random among applicable classes:
- OP_REPLACE: replace one instruction's opcode (operands resampled compatibly)
- ARG_TWEAK: resample one operand of one instruction
- INSERT: insert a random instruction at a random position (if len < 24)
- DELETE: delete a random instruction (if len > 1)
- SWAP: swap two adjacent instructions
- DUP_BLOCK: copy a block of 1–3 instructions to another position (if it fits)
Recombination: one-point crossover, cut points independent in each parent,
child truncated to MAX_LEN. Physics is frozen for the entire generation.

## 3. Preflight assays (all history-free; per §11)
All budgets are counted in VERIFIER EVALUATIONS (one evaluation = execute the
candidate on the full probe set). Probe set for preflight: single-input tasks,
P = {0..63} (k=1, 64 inputs).

- PF1 VIABLE DIVERSITY. W random walks of L mutation steps from the seed
  repertoire (round-robin over seeds). Count distinct behavior classes visited.
- PF2 REPRODUCIBLE ACCESSIBILITY. Emit T target behaviors from walk stream A;
  from an INDEPENDENT seed stream B, run the reference hill-climber toward each
  target with budget B_pf evaluations. Fraction reached exactly (distance 0).
- PF3 MULTIPLE COMPETITIVE NAVIGATORS. Three history-free navigators (NAV-HC
  (1+λ) hill-climber; NAV-POP population+immigrants; NAV-RX population with
  crossover) on the same T targets, same budget. No single navigator may be the
  only working corridor.
- PF4 NO PRIVILEGED MUTATION CORRIDOR. Ablate each mutation class singly
  (physics minus one class); best navigator on the same targets. No single
  class may be indispensable.
- PF5 START-REPERTOIRE SENSITIVITY. Re-run the PF2 navigation toward the same
  targets starting from a MINIMAL repertoire (identity program only) instead of
  the 16-seed menu. Accessibility must not depend on a privileged starting
  menu. (Replaces the original register-permutation assay, which is vacuous by
  construction: the physics samples registers uniformly and non-input registers
  initialize to zero, so register-permutation equivariance holds provably and
  that assay could never fail. Changed pre-run, in DRAFT; see BUILD_LOG.)

## 4. Preflight budgets (FINAL, sized on engineering seeds 2026-08-27)
Engineering calibration measured: budget 2000 starves navigation (NAV-POP 35%
at 2000 vs 55% at 8000 with solves arriving as late as eval 7152); NAV-POP
dominates NAV-HC. Final sizing, frozen before the evidence run:
- Reference navigator: NAV-POP (population-32, tournament-3, 10% immigrants).
- PF1: W=200 walks × L=150 steps.
- PF2: T=30 targets, B_pf=8000 evaluations each, NAV-POP.
- PF3: 3 navigators (NAV-POP, NAV-HC, NAV-RX) × 30 targets × 8000.
- PF4: 6 single-class ablations × 30 targets × 8000 (best PF3 navigator).
- PF5: 30 targets × 8000, minimal start repertoire, NAV-POP.
- Solve-eval is recorded per row, so reach at 500/2000/8000 is derivable
  (reporting-only findability ladder). Gates evaluate at 8000 only.

## 5. Preflight gates (G0 components) — FROZEN 2026-08-27, before evidence run
Thresholds sit ~2 SE (n=30 targets, SE ~9pp) below engineering-calibrated
anchors (PF1=201 classes; NAV-POP 55% @8000, n=20) so the evidence run measures
the substrate rather than seed noise, while staying far above a dead-substrate
floor.
- G0a (PF1): ≥ 120 distinct behavior classes.
- G0b (PF2): NAV-POP exact-reach ≥ 30% at budget 8000.
- G0c (PF3): ≥ 2 of 3 navigators reach ≥ 25% of targets; among navigators with
  ≥ 5% reach, max/min reach ratio ≤ 3.
- G0d (PF4): no single mutation-class ablation reduces the best navigator's
  reach rate by more than 80% relative to its unablated rate.
- G0e (PF5): minimal-repertoire reach rate within 25 percentage points of the
  full-repertoire PF2 rate.
G0 = all of G0a–G0e. FAIL → substrate invalid for this generation.

## 6. Fallback and stop rule
If RM-D5 fails G0: one preregistered fallback substrate may be attempted — a
composition substrate over elementary cellular-automaton rule sequences (same
preflight, fresh thresholds frozen before its evidence run). If the fallback
also fails G0: STOP; verdict SUBSTRATE_INVALID. Hard-task learning is not built
on an invalid substrate (§11).

## 7. What preflight does NOT establish
Passing G0 is instrument calibration for geometry, not evidence of learning,
findability, or anything on the claim ladder above P0-adjacent bookkeeping.
