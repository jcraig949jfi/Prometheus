# Ergon Kickoff Prompt — Metabolization Probe Preregistration

**Purpose of this file:** the exact prompt James pastes into a fresh Ergon session on M1 to
start the probe work. Committed so the kickoff is reproducible and auditable. All paths are
repo-relative (Ergon's checkout root on M1 differs from other stations'). Everything
referenced below is verified present on `origin/main` as of 2026-08-13.

---

## THE PROMPT (copy everything between the rules)

---

You're Ergon @roles/Ergon — running on M1. First `git pull origin main`, then resume from
`roles/Ergon/resume_ergon.md` and `roles/Ergon/REVIVAL_ASSESSMENT_2026-08-12.md`, then take
this mission.

CONTEXT: The 2026-08-12 fleet reassessment concluded. James ruled the Metabolization Probe
Priority #1 and green-lit it after his peer review. The binding spec is
`pivot/SPEC_METABOLIZATION_PROBE_2026-08-12.md` — v2.0-FINAL, FROZEN. It is your Move-1
design, evolved: canonical arm names (F0 / F-null / F-generic / F-prom-retrieved /
F-prom-whole / F-oracle / F-answer — your old C1/C2/C3 labels are retired; §2 has the
mapping), a D0–D3 transfer-distance ladder, a causal/provenance firewall (R14), a
contamination probe with power floor (R13), a single-primary-endpoint statistical plan
(R15), and a 6-row diagnostic matrix. Read it end to end before anything else. Then read
`aporia/docs/META_SYNTHESIS_2026-08-12_v1.md` §2.5, §2.7, §7.5 (the preconditions and the
audit chain that hardened the spec) and `stations/M1_STATUS.md`. Background if wanted:
`pivot/PROMETHEUS_DOSSIER_2026-08-12_where_we_go_from_here.md` (the program-level frame) and
`roles/Hephaestus/META_ASSESSMENT_2026-08-12_fable_seat.md` §7.5 (James's phase ruling).

YOU ARE THE SINGLE OWNER (spec R12). This session's one deliverable:

DRAFT `pivot/PREREG_METABOLIZATION_PROBE_v1.md` per spec R2 — the binding instrument. It
must resolve every spec-§9 open item:
- task-set sizes and D0–D3 quotas (your `ergon/learner/greedy/ood_judgement.py` set is the
  seed corpus; `prometheus_math` op instances post-unbrick; optional Lean-checkable claims);
- solver list (Tier A: local Qwen2.5-Math + gemini-3.6-flash free tier; Tier B pending
  James's procurement — record a requested-by date; spec §5E's 7-day escalation applies);
- F-shuffle feasibility (in or out, with one line of reasoning);
- whether M0-unrepresentables join Tier A;
- packet token ceiling;
- exact statistical test + minimum practical effect size (R15);
- the R13 power calculation and the hashed replenishment source pool;
- the R14 firewall procedure — provenance IDs + ledger append-order, NOT wall-clock
  timestamps (M3's clock reset makes clock-derived times untrustworthy for affected
  windows); the assembler's executable assertion and its fail-loud behavior;
- the D0–D3 tagging procedure (how each task's distance from its residue's originating
  failures is determined and recorded);
- the §4.5 decision thresholds — which you are explicitly invited to AMEND, not just
  confirm: the spec's author (Hephaestus) is the declared-conflicted residue supplier, and
  the thresholds belong to you, Charon, and Harmonia B.

Then: commit the draft marked DRAFT-PENDING-COSIGN and push. Request co-signs from Charon
(kill authority; owns F-null + F-generic construction and R7's two-layer verification) and
Harmonia B (meter integrity; owns R3's two controls and the R4 headroom check) by adding a
short review-request note to `stations/M1_STATUS.md` and, if their sessions are not live,
listing the requests in your commit message — commits are the fleet's working channel.
Coordinate the two supplier contracts the same way: Techne (packet assembler with the R14
assertion built in) and Apollo (Tier A ablation-wall corpus + per-wall F-oracle diagnoses,
per `pivot/STRATEGY_2026-08-12_resumption_and_roadmap.md` §10's W0/W1 corpus).

HARD CONSTRAINTS:
- No arm executes before the prereg is committed AND co-signed.
- No new architecture (the heredity rule: no new architecture until one failure produces
  one verified improvement).
- No edits to the spec — it is frozen. Discrepancies you find go IN the prereg or in a
  committed review note.
- Tier A must need zero API budget. Tier A's only verdict is HARNESS_ADMISSIBLE /
  HARNESS_NOT_ADMISSIBLE — its numbers are never quoted as thesis evidence.
- Hephaestus is supplier-only: it will review your draft in a committed note and will not
  co-author.
- Pit-stop dependencies (z3, snappy/cypari for `prometheus_math`) that touch M1's global
  interpreter are James-approval items: list them as asks in your first commit rather than
  installing silently. A venv is fine without asking.

DISCIPLINE: every load-bearing claim E-tagged with executor identity (E1 read / E3 ran) —
on a factual claim, agreement without independent execution is one measurement with N
pointers. Typed objects over prose. A session that produces no committed artifact produced
nothing. Update `stations/M1_STATUS.md` at session end.

---

## Verification note (Hephaestus, M3, 2026-08-13)

Every path referenced above confirmed present on `origin/main` via
`git cat-file -e origin/main:<path>`: the spec, both Ergon docs, the Aporia meta-synthesis,
both station files, the dossier, the meta-assessment, the Techne assessment, the Apollo
strategy, `ood_judgement.py`, and `routing_eval.py`. Ergon needs only `git pull` on M1.
