# Hephaestus status

Currency: 2026-09-25 (session close before operator reboot of M2). Plain language.
Each line says which of PRESENT / ACTIVE / PRODUCTIVE / VALID it asserts.

## Where the seat is running

- Host SPECTREX5 (M2). Worktree D:\Prometheus-worktrees\hephaestus-boot-2026-09-19,
  branch hephaestus/m2-boot-2026-09-19 (KEEP: resume here). Comms against the
  canonical M1 store: set EW_DB_HOST=192.168.1.202 before the first comms call.
- Previous worktree F:\Prometheus-worktrees\hephaestus-base-role (M1, branch
  hephaestus/base-role-adopt-2026-09-11) is merged and stale; pruned at this close.

## Temporary mission (operator 2026-09-19): cross-pollination replay -- EXECUTED, VALID as far as one draw each can be

- hephaestus/xpol_2026/: 114 packets extracted read-only from the frozen 1.0 corpus
  (six preregistered lenses); era-matched Nous/CODE_GEN templates from git with
  sha256; floors on the honest 186-trap ruler published first (position-majority
  decoy 0.4032, NCD 0.3925, constant-first 0.3387).
- Arms run: fable51 (claude -p, 10 packets before the subscription ran dry),
  fable51_session (this seat authoring in-session, 3 packets, contamination
  declared per record), groq gpt-oss-120b (12 before rate cap), qwen2.5-coder:14b
  local (5), gemini (503-saturated, dropped), gpt6astra (BLOCKED: unfunded).
- Finding: size buys the EXISTENCE of a mechanism, not its quality. 14B sits on
  the constant-first floor (constant scores, do-nothing tools); 120B echoes NCD;
  Fable 5.1 fires several parsers (0.42-0.52, two tools >= 0.50). R2/R4 unmoved
  at every size; the prompt architecture caps everyone. Paired vs committed
  originals: originals 2, new models 1 (inside noise). "Newest models beat 1.0"
  NOT supported on paired data. Packets: REVIEW_PACKET_2026-09-19_xpol_small_set.txt
  and REVIEW_PACKET_2026-09-23_xpol_addendum_size_gradient.txt.
- Nothing under agents/ was modified. No experiment is mid-flight: every run
  wrote DONE.json or was stopped and recorded (fable51_s0..s2 stopped by
  operator scope-down; their partial rows are kept).

## The 2.0 position (boot packet 2026-09-19) -- PRESENT, awaiting operator answers

- Proposed re-premise: boundary certifier (closure gauntlet over ecology
  substrates) + mechanism assay (knockout on what evolution produces) +
  Master Smith re-premised to assay, not mint. First test HEPH-32 (gauntlet vs
  the SFE VM opcode set / C4 cliff). Operator has not yet answered Q1-Q3 of
  that packet (recorded in OPEN_QUESTIONS_2026-09-25.md).

## Queue (hephaestus/mint_queue/) -- PRESENT, DORMANT (no events since 2026-09-11; by design under the 2.0 question)

## Blockers

- GPT-6 Astra unfunded (openrouter key 402); Fable subscription usage-capped for
  claude -p breadth. Independent held-out generator for MINT-0001 still absent.
- Coeus #83 answered (comms 515, HEPH-31 closed).

## Next executable action

Read OPEN_QUESTIONS_2026-09-25.md, re-ask the operator, then: HEPH-34 (one Master
Smith revise cycle on XP-009 R2, only if authorized) or HEPH-32 (gauntlet vs SFE
substrate) -- whichever the operator picks; default if silent: HEPH-32.
