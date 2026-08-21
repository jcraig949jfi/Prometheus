# Techne Arsenal + Ladder Loop — Charter

**Authorized:** James, 2026-08-21 ("Let's do A, 90 minutes... Go. Start looping.")
**Cadence:** ~60-minute wakes (runtime clamps single delays to 3600 s; James asked 90 — noted
in HITL log; he can slow it by interrupting).
**Mode:** autonomous cycles; HITL questions are LOGGED, never blocking.

## Each cycle does BOTH tracks

**Track 1 — Arsenal (chip away at all 4, round-robin as items unblock):**
1. `prometheus_math.certified` — FLINT3/Arb ball arithmetic (install + wrap + TDD)
2. Tensor-train wrap with correct-null API over `signature_index` (tensor-first)
3. PySR 2.0 spike — install, smoke on a known law, then one real table with battery judging
4. Lean 4 + mathlib feasibility spike → `check_lean` verdict tool
Standing Order #1 holds: wrap, don't rewrite. TDD via math-tdd skill for every new op.

**Track 2 — Reasoning Ladder circuit study (one rung per cycle, incrementing):**
Canonical vocabulary: `aporia/doctrine/reasoning_ladder.md` (Canon v2.0). Sequence:
R0→R12, then Band H (H1, H2), then restart at R0 improving on the prior pass.
Per rung, answer and BUILD where cheap:
- What reasoning circuits could be built for this rung? (AST-based options explicitly)
- What TDD tests? What traps catch a system gaming the tests?
- Straw-man design: build + test the simplest falsifiable version. NO grand architectures.
- Later rungs (S/G/H bands): theory + research organization substitute for building.
Artifacts land in `techne/ladder_circuits/` (code+tests) and
`techne/loop/rung_notes/` (analysis). Apollo/Hephaestus charters may be mined for ideas;
this loop is an INDEPENDENT channel — cite, don't coordinate.

## Every cycle ends with
1. `techne/loop/cycle_NNN.md` — what was done, rung notes pointer, **TLDR ELI5 section**,
   and a **ChatGPT paste block** (self-contained prompt James can cut-paste; fold any
   ChatGPT replies he posts into the next cycle).
2. Append open questions to `techne/loop/HITL_LOG.md` (do not block on them).
3. Commit + push (document-as-you-go is doctrine).
4. `ScheduleWakeup(3600, prompt=continue per this charter, next rung = N+1)`.

## Guards
- Every claim about a circuit carries its kill test (falsification-first, Canon §1).
- Vocabulary law: no new tier numbers; rung semantics only from Canon v2.0 (§8).
- Don't optimize for deeper menus (`feedback_gen_30_wall`) — prefer menu-growth mechanisms.
- If a cycle's build fails, log the failure as the artifact; kills are output.
- Loop ends when James says stop, or on unrecoverable environment failure (log + stop).
