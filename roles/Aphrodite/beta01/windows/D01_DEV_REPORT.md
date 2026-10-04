# D01 -- DEV WINDOW 1 (BOOTSTRAP) REPORT: repair/design packet

C-006 (C-P2B-APH-BETA-01), cycle 1, DEV. Opened 2026-10-04 by operator directive. Active thread: TH-021 (instrument
validity). Evidence tier 2 (apparatus).

## 1. Information bottleneck
The previous programme's information was limited by INSTRUMENTS, not by the improver:
- asserted (constant) gates;
- a positive control equal to the treatment;
- a tribunal query-window mismatch;
- a ruler without re-expression closure;
- a capability endpoint dominated by the escrow/walk cliff;
- supply/design failures (3 of 4 ARC3 assays).
The DEV rule says to fix the earliest failed rung first, and every rung above R0 was being read through these
instruments.

## 2. Evidence motivating the changes
- **Forensic triage**, C-006 tasks A+B: ops/campaigns/C-006/TRIAGE_AB.md. It covers about 70 findings from the
  Tantalus dossier and audit, the failure-to-gate map, TH-018..021, the ARC3 merge packet and the harvest defect
  catalog.
- **Historical constant-gate record**: beta01/HISTORICAL_CONSTANT_GATES.json. It holds 7 genuine or asserted constants.
  Three of them are NEW since TH-021: `R5_clean_transplant` inside the BOUNDED_RSI conjunction at a16:547, a17:639 and
  run_g2:395. **No historical label flips:**
  - S4 YES survives on 2 unseen + 2 related families once the 3 PC-admitted families are removed (correction-only);
  - A16/A17/G2 have no YES resting on R5.
- **Probe TB-T4b** (engine/v2b/receipts/PROBE_TB_T4B_A23.json): T4 v1a changes admission for **0 of 330** A23-used
  families (2 of 504 unused rows flip). A23's family admission stands on T4 v1. Re-scoring transfer hits under v1a is
  left to the T47 bridge.

## 3. Changes (all NEW files under engine/v2b/; no historical file modified)

| Module | What it is |
|---|---|
| tribunal_t4_v1a.py, ruler_v21.py | W7's drafts, frozen byte-identical as versioned instruments (source blob and sha256 in their headers). T4 v1 and ruler v2 untouched |
| instruments.py | one switch for the tribunal (v1, v1a) and ruler (v2, v2.1); ARTIFACT and DIRECT tribunal paths, with mandatory agreement; extensional schema equality |
| gates.py | evidence-computed Gate (bool-typed, evidence digest); Gate.qualify (must be True on a pass fixture and False on a fail fixture, else GateUnreachable); require_qualified at seal; Control.check_distinct (a positive control equal to the treatment raises); static constant-gate lint |
| walk.py | resumable exact walker yielding every dev-consistent hit in fast_cost's order, and first_qualified, which walks past spurious hits |
| capability.py | D-stratified endpoint (T53): D = log10 charge to the first TRIBUNAL-QUALIFIED program; strata COVERED / WINDOW / CENSORED by D_PRISTINE; SOLVES_WHERE_REF_CENSORED; generic-cliff excess over shams |
| supply.py | supply screen as a precondition (SupplyReceipt; SupplyLimited) |
| apparatus.py | APPARATUS_ID = hash of all imported engine and v2b module contents plus the instrument selection |
| conformance_v2b.py | C1-C5 battery |
| probe_tb_t4b.py | the A23 admission probe |
| t1_known_answer.py | the TEST-1 runner |

## 4. Qualification tests
- `pytest engine/v2b/tests`: 12 passed. They cover gate liveness, constant-gate unreachability, the
  control-distinctness refusal, lint reproduction of all 7 historical sites, lint-clean v2b, supply fail-closed,
  stratum logic, cliff excess, and the walker vs fast_cost.
- **Conformance GREEN:** walker == fast_cost (40/40, plus 60/60 in an earlier run); fast_cost == reference Cell.cost
  (40/40); artifact == direct tribunal (16/16 under v1 and v1a); ruler v2.1 reproduces W7's 47 adversarial verdicts;
  classing fixtures hold. A full-size conformance run (200/200/40) is part of TEST-1's receipts.
- **Smoke** (beta01/runs/T01_SMOKE, DEV only, never a result): the pipeline executes end to end. One audit: a
  tribunal-qualified program that is not syntactically equal to the witness agreed with it on 500/500 random inputs,
  so it is a genuine extensional equivalent and not a leak.

## 5. Compatibility / version implications
- v2b-1 is a NEW apparatus version. Every v2b result carries APPARATUS_ID and is never pooled with v1-instrument
  results.
- Historical experiments are untouched. Bridges (T47) re-score preserved data under both instrument versions and are
  correction-only.
- The historical 250k escrow is never a sole endpoint again. The D endpoint is budget-free up to its cap and reports
  censoring.
- Known residuals:
  - T4 v1a certifies nothing about queries 1-2;
  - ruler v2.1 still has 8/47 adversarial errors (distributed re-expressions; acc >= 0 grid; inert wraps COMPOSES;
    efficiency-only NEW) and a W5 chance-novelty floor of 24.5%;
  - condition-8-style "no donor state" still has no receipt check (TRIAGE R2). It is scheduled for a later DEV,
    before the S4 replication.

## 6. Next frozen experiment
TEST-1 = T01 known-answer assay: beta01/windows/T01_KNOWN_ANSWER_SPEC.md (runner and plan sha256 frozen there).

## 7. Decisions recorded
- T4 v1a = fix (a) (W7). Fix (b) is rejected: it re-draws every dev set and still fails qbda.
- Positive controls must be ruler-DISTINCT from the treatment. A re-expression "sham" is classified NOT_A_SHAM.
- A23 admission is unaffected by v1a (probe). A23's label stays as recorded. The interpretation questions (T52, T53)
  remain queued as early-Beta probes.
- `azure.env` (tracked) was checked: it contains configuration and price assumptions only, no credentials.
