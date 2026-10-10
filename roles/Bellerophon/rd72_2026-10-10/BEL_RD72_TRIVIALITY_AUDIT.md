# BEL-RD-72 TRIVIALITY AUDIT (Workstream B2)

Instrument tools/trivaudit.py (pin 6aad831fe; measurement only, no world run); receipt receipts/B2_trivaudit.json.
Competence = tasks.verify_exact (16-input panel, read gate ABR, budget 256); FUNC = belinst.Func (>= 0.9 L own-material
self-copy). Plus the adversarial K review (BEL_RD72_REVIEW_RECORD.md R1) for COND_MULTI.

## 1. Random success, constant outputs, accidental matches
| task | shortest known solver (bytes after IN) | uniform random tapes competent / 20,000 | sparse (16 random bytes) / 20,000 | competent AND FUNC (both pools) | constant outputs that pass |
|---|---|---|---|---|---|
| CONST (k=42) | 3 | 0 | 0 | 0 | k = 42 only (by definition) |
| ECHO | 2 | 88 (0.44%) | 13 | 0 | none |
| INC | 3 | 4 | 0 | 0 | none |
| COND_ONE | 7 | 0 | 0 | 0 | none |
| COND_MULTI | 11 | 0 (also 0/300,000, review R1) | 0 | 0 | none |
| SUM2 | 5 | 0 | 0 | 0 | none |
Reading: ECHO competence is CHEAP (1 in ~230 random tapes): any ECHO-level or LO-half result (COND_ONE / COND_MULTI low half
= echo) is not evidence of nontrivial computation by itself. No task is solved by a random REPLICATOR. No constant-output
exploit exists outside CONST.

## 2. Single-step solvability (one-step routes to competent + FUNC, from copier + task hybrids; SUB / MOVE<=16 / INS / DEL)
Nonzero entries only (all other source -> target pairs are 0 under all four operators):
| target | from | SUB | MOVE | INS | DEL |
|---|---|---|---|---|---|
| ECHO | CONST | 0 | 0 | 1 | 0 |
| ECHO | INC | 226 | 71 | 11 | 1 |
| ECHO | COND_ONE | 231 | 260 | 4 | 0 |
| ECHO | COND_MULTI | 5 | 332 | 2 | 0 |
| ECHO | SUM2 | 13,627 | 39,805 | 15,423 | 53 |
| INC | ECHO | 0 | 0 | 1 | 0 |
| INC | COND_ONE | 468 | 701 | 2,142 | 3 |
| INC | SUM2 | 1 | 0 | 3 | 0 |
From the bare copier: 0 routes to every task. COND_ONE, COND_MULTI and SUM2 have ZERO one-step routes from every other
rung and from the copier: they are deserts relative to every simpler mechanism in the family. Going DOWN the ladder is
easy (composite -> half: hundreds of routes); going UP is not. Single-mutation solutions are therefore impossible for
the composite tasks; any composite that appears was built in >= 2 steps (COND_MULTI: >= 4 substitutions from the nearest
half-solver, review R1).

## 3. Shortcut classes checked (directive B2 list)
constant outputs: none (s1). accidental matches / random success: s1 (0 for composites). reward leakage: R1 item 2 (0 random,
0 single mutants); a 256-input full check is now run on every K2 competent machine. copying without computation: FUNC
alone never passes the panel (copier 0 routes; random FUNC 0 competent). environmental completion: R1 item 3 (writers
over random targets 0/1.0M; one real one-step assembly route, Y-copy-length-12 over X, competent but NOT a replicator).
partial-program exploits: the LO half = ECHO is cheap (s1); half-capability is reported separately (LO / HI / BOTH) and
never counted as composite. resource exploits: v3 ledger balanced in every run (asserted). single-mutation solutions: s2
(none for composites). pre-existing mechanisms: founders are bare copiers (E1b) or fixtures whose competence is enumerated
(K2); composites must be ABSENT at tick 0 (checked per run).
