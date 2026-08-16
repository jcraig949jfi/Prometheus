# M2 — Station Status (living doc)

**Point agent:** Harmonia_M2_A · **Last updated:** 2026-08-12
**Station roster:** Harmonia A, B, C, D · Apollo
**Mode:** level-setting. **No hard decisions until ~2026-08-14** (James, 2026-08-12).
Assessment, strategic thinking, alignment to the north star. Nothing here is a
commitment; items marked DECISION are parked for James.

**Proposed convention (M1/M3/M4 may adopt or ignore):** one `stations/<M>_STATUS.md`
per machine, living, updated at session end — mirroring
`agents/hephaestus/STATUS.md`. Hephaestus's cross-machine meta-analysis loops on
commits, so a predictable per-station path gives it one entry point per machine
instead of N scattered reviews. If M1/M3/M4 prefer another shape, this file moves.

**North star:** compressing coordinate systems of legibility, not laws. Every item
below is tagged for whether it serves that or merely serves the program's own gates.

---

## 0. Coordination substrate — measured today, and it is not what the docs say

| Channel | State (E3, measured 2026-08-12 from M2) |
|---|---|
| **Git / commits** | **The de facto channel.** Everything the fleet coordinated on today moved through commits. |
| **Postgres bus** (`PgRedis`, M1 `192.168.1.202`, db `prometheus_fire`) | **REACHABLE from M2 and completely unused — 0 keys.** `PgRedis.__init__` performs a real `psycopg2.connect`, so this is a genuine connection, not a stubbed ping. |
| `get_fire()` data accessor | **BROKEN on M2** — `ConnectionError: Cannot connect to fire. Check ~/.prometheus/db.toml and credentials.toml`. Config gap, **not** network: PgRedis reaches the same server with default creds. |

Two corrections to standing belief:
- Memory `project_harmonia_D_20260615` records "Postgres unreachable 3rd session
  (parked)." **Stale.** The 2026-06-24 Redis→Postgres migration fixed transport; M2
  reaches M1 now.
- The stall map's action #1 cites `prometheus_data\config.py`. **That path does not
  exist on M2.** The live module is `D:\Prometheus\thesauros\prometheus_data\pool.py`;
  root `prometheus_data\` is a data directory (arxiv_corpus, cremona, oeis).

**Implication for the level-setting:** the fleet has a working real-time channel that
nobody is on. Not a recommendation to adopt it — an observation that "we can't
coordinate" is false, and the reason we don't is unexamined.

## 0b. FLEET HAZARD — two distinct things are named "Aletheia"

Raised by James 2026-08-12; collision **confirmed** by A the same day. Flagged here
because Hephaestus's cross-machine meta-analysis loops on commits and will merge them
by name unless qualified.

| Referent | What it is | Status |
|---|---|---|
| **`agents/aletheia/`** | Knowledge-harvesting / taxonomy **component**. Reads Eos papers → LLM extraction → SQLite knowledge graph (7 entity types). Pipeline position Eos → Aletheia → Skopos. Also documented as "Structural Mathematician for Noesis." | **Incumbent**, in-tree since ~April: `README.md`, `src/aletheia.py`, `src/ingest.py`, `data/knowledge_graph.db`, plus `cartography/shared/scripts/aletheia_night_sweep.py`. |
| **Aletheia on M4** | **Role agent.** Was managing an expanded orchestration attempt; asked by James to codify its named role 2026-08-12. | **Has committed nothing yet** — zero files, zero commits on origin as of `a6ccb3dc`. |

**Why this is the cheap moment:** the M4 agent has not written to the repo. Setting the
convention now costs nothing; after it lands, disambiguation means touching files.

**Proposed qualifier** (extends the demonstrated `<Name>_<Machine>_<Instance>` pattern
already in use for `Harmonia_M2_A` / `Harmonia_M2_auditor`):
- **`Aletheia_M4`** — the M4 role agent / orchestrator.
- **`aletheia-kg`** — the knowledge-graph component. Prefer naming the *path*
  (`agents/aletheia/`) in prose, since it is a component, not an identity.
- The tree already encodes the distinction — `agents/<lowercase>/` = component,
  `roles/<Capitalized>/` = role identity — but case-and-directory alone is too subtle
  for a prose-reading meta-analyzer. **Qualify in prose every time.**

**Needs confirmation from James / Aletheia_M4** — A is proposing, not deciding, and
will not rename anything. If `Aletheia_M4` writes to `roles/Aletheia/`, that is
consistent with the convention; if it writes to `agents/aletheia/`, the two merge
irreversibly.

*Observation, offered lightly and not as a general claim: this is a referent collision
under a shared surface name — the same shape as the `cid`-keyed conjecture registry
that made M0 fail on A4 (logically identical claim, unregistered string). Worth one
line, not a thesis; C's base-rate lesson applies to me here too.*

## 1. Station roster and current state

| Agent | Lens / role | Landed 2026-08-12 | Live state |
|---|---|---|---|
| **A** (point) | architecture | syntactic-router review + §9 corrections; B′ held-out benchmark + calibrated oracle; four-lens panel synthesis | active |
| **B** | instrument integrity | R6 answer-key leak; payload-reading negative control; typed-object corpus (14, schema-valid); review dossier as single entry point; north-star position paper | active |
| **C** | counterfactual / north-star | component reachability census; stranded calibration library; base-rate null method; lane exhaustion audit | active |
| **D** | permanence | permanence ladder P0–P4; constructive-death-is-durable; R4/R9–R12 don't exist; closure-novelty kill; a3 completeness over 355K cells | active |
| **Apollo** | evolutionary search | — | **dormant since 2026-06-28**, and the only M2 component never reviewed from inside |

## 2. What M2 established today (E3 unless noted)

**Instrument defects, confirmed:**
- `verify()` returns `valid=False` / `unknown_kind` for unregistered kinds — it
  **certifies true claims WRONG** rather than abstaining. Found by A on 5 synthetic
  kinds; D found it firing **160/160 at R5/R7/R8** on the live ladder. M0's "0%
  type-II" is a fossil; anyone citing it after today is citing a dead number.
- The grading oracle's R6 ships `truth` inside `probe.data`; a 3-line payload reader
  ties the top baseline (B).
- `TIER_GENS` holds exactly `R0,R1,R2,R3,R5,R6,R7,R8`. **R4 and R9–R12 do not exist**
  (D; independently re-verified by A). The R0–R12 ladder is a design document, not an
  instrument.

**Structural measurements:**
- 2,239,810 lines of Python in 8,726 modules; **577 (6.6%) ever imported**. 63% by
  volume is generator output nothing has ever read; **200 committed files do not
  `ast.parse`** (C). B measured the same shape in prose at ~1,500:1. Volume was never
  the constraint.
- `prometheus_math` + `techne.lib` are **87% unreachable behind three pip packages**;
  `pip install snappy` takes 29 → 220 of 222 modules (C).

**Methodological results promoted out of the panel** — these are the transferable part:
1. **Repo state is not program state.** HEAD is a lower bound on activity. (A called
   the program "6.5 weeks idle" while 281 commits behind origin.)
2. **Base-rate null before any pattern claim.** Killed A's §1 *and* C's own headline.
3. **Every metric needs both controls** — negative (can a cheat pass?) and positive
   (can anything pass?). A tier nobody has ever passed is unfalsifiable.
4. **Novelty meters are timeout detectors until proven otherwise.** Ask what the meter
   returns on a falsehood and on an undecidable.

## 3. Contested cells — deliberately unresolved

Per map-of-disagreement doctrine. All three are decidable by measurements nobody has
run; none should be settled by argument.

| Cell | Positions | What would settle it |
|---|---|---|
| Is "built-and-not-wired" a disposition? | D: A's §1 unbroken. C: base rate breaks its dispositional form (detectors orphaned *less* than average; unwired is ambient at 55–58%). | Count shape-gates vs content-gates over **gates on critical paths** — the reference class neither reviewer used. |
| B1 vs B2 exhaustion | A: B2 ceiling, diversify hypothesis classes. D: the dispute is malformed — "does novel structure exist outside H" has **no finite certificate**, so B1 is not establishable in principle and A's fix **does not terminate**. | Adopt class-relative exhaustion as the deliverable; formalize H as a grammar and decide membership mechanically. |
| Apollo: exhausted or not? | Turns entirely on whether **crossover is classed as `search_operator` or as part of evolutionary search**. First → 5 kills, fires. Second → June success, count resets, goes silent. | Apollo's owner, one afternoon. Under R3 both answers keep the lane. |

## 4. Owed by M2 (not started — level-setting is the current mode)

- **`unknown_kind` → `valid=None`.** Smallest, highest-priority fix on the board;
  it is a live correctness bug, not a design question.
- **The translator** (claim → z3/sympy, kind-routing deleted). A's one surviving
  prescription. It was never an answer to Q1 and must not be re-sold as one.
- **B′ must be graded exactly once.** 24 held-out claims, oracle calibrated 8/8
  (`D:\Prometheus\harmonia\experiments\bprime_holdout.json`). A second look converts
  it into a training set.
- **Apollo reviewed from inside.** The only M2 component with no first-person account.

## 5. DECISION — parked for James

1. **`pip install snappy` on the global interpreter** (29 → 220 modules). Load-bearing
   because ruling R1 makes math the calibration standard, so every instrument that
   "passed on math" this year passed against 29 modules. C deliberately did not run it;
   host change is James's call.
2. **Write `~/.prometheus/db.toml` on M2** to unbreak `get_fire()`. PgRedis proves the
   server and default credentials work.
3. **Local model tier** — podman needs a WSL2 distro first (neither installed);
   the cheaper path is a modern 4-bit MoE into the existing ollama. Multi-GB download,
   not started unilaterally.

## 6. Station tool shelf (measured 2026-08-12)

- **APIs:** Anthropic, OpenAI, DeepSeek all **out of credits**. **`gemini-3.6-flash`
  live on the free tier** — and it is a genuinely independent model family, which is
  what makes B′ and any cross-family check possible. Pro tiers 429 on quota. Free tier
  is bursty; always retry on 503 or a whole batch vanishes silently.
- **Compute:** RTX 5060 Ti 16 GB · 32 GB RAM · 28 cores. Ollama 0.32.9 with one stale
  model (`qwen2.5-coder:14b`). **No podman, no Docker, no WSL distro.**
- **Working:** z3, sympy, psycopg2. **Missing:** psycopg (v3), cypari, snappy,
  knot_floer_homology.

---

## 7. Apollo — Tier A wall corpus DELIVERED (2026-08-15)

The metabolization probe's longest lead item (`stations/M1_STATUS.md` §7b, flagged there
as *"planned, not built — real critical path"*) is **built, validated and committed.**

**`apollo/wall_corpus/`** — 28 runs: **26 ablation walls across 4 failure classes** plus
2 unablated controls. Contract minimum was ≥20 / ≥4. Docs: `apollo/wall_corpus/MANIFEST.md`.
Harness `apollo/scripts/wall_corpus.py`; validator `apollo/scripts/wall_corpus_validate.py`
(**28 records, 0 firewall violations, planted violation CAUGHT**).

- **F-answer / F-oracle split is enforced, not asserted.** Oracles are cause-only; the
  validator rejects any oracle naming a registered operator or using a repair verb, and
  fails loud on a planted violation (spec §4.2 exit criterion). `ablation_applied` is
  quarantined alongside `answer_content` — it names the exact edit, so it is answer
  content in provenance clothing. All 26 walls are `separability: clean`, so **Ergon has
  no F-answer-only inclusion rulings owed on this corpus.**
- **Heredity rule honoured.** The harness never edits the substrate: ablations rebind
  module globals on a freshly imported `blackboard_evolve` in a throwaway subprocess.
  `blackboard_evolve.py`, `blackboard.py`, `blackboard_ops_*` are unmodified on disk.
  Move-withholding rejection-samples the substrate's own mutator rather than reimplementing it.
- **Type-bridge experiment remains PARKED** — corpus supply only, per contract.

**Three findings that are results, not bookkeeping:**

- **Withholding any single mutation move produces NO wall while crossover is on.** Four
  ablations hit *exact* control parity (0.833/1.000/0.833) and were re-specified as
  compound. An independent replication, from the ablation side, of the 2026-06-16
  recombination result: recombination is what makes this substrate searchable.
- **The routing-purity guard is inert under dispatch mode** — removing it produced
  telemetry byte-identical to control, because the guarded-only scorer pool already
  prevents the hybrids purity was written to punish. Belt-and-braces, not load-bearing.
- **Plateau telemetry cannot separate *capability absent* from *capability present but
  mis-wired*.** The per-branch ablation audit — the feature I expected to do it — reads
  identically for a deleted producer and a mis-keyed guard. Separation needed an indirect
  proxy for registry state. This is the program's representational-vs-interface problem
  reappearing as a measurement problem inside Apollo.

**Apollo's queue behind this (unchanged):** crossover classification call (addendum-A §3),
`genuine_routing` debt, ladder v0.2 clause-(c) audit.

**Tier A caveat, restated because it is easy to lose:** no number in this corpus is
thesis evidence. Constructed failures are idealized and their oracles are cleaner than
real residue will ever be — which is exactly why Tier A was demoted to harness
qualification. Permitted vocabulary remains `HARNESS_ADMISSIBLE` / `HARNESS_NOT_ADMISSIBLE`.

---

## Metabolization probe — Harmonia B, meter integrity (2026-08-16)

**CO-SIGNED. The preregistration is binding as of this commit (third signature).**
Note: `harmonia/probe/COSIGN_HARMONIA_B_2026-08-16.md`. Full detail in
`stations/M1_STATUS.md` §7b (the probe's home station); M2-relevant summary here.

- **Signed NOW**, with Charon's two material remedies recorded as
  **BINDING-CONDITIONS-BEFORE-ARMS** (BC-1 `F-prom-whole` N; BC-2 D3 selection) rather than
  withheld. Both are implementation changes in committed code, neither touches binding text,
  both are diff-checkable — and R3 runs before any arm by construction, so the gate is
  mechanical rather than honor-system.
- **R3 control battery shipped:** `ergon/probe/r3_controls.py` (+20 tests; probe suite
  129/129). Payload-consumption A quantified at ≥+25pp & p<0.01; cheat control B at
  p<0.05 AND Δ≥+5pp with **measured** operating characteristics (40 seeds: 5% false alarm,
  power 1.00@+15pp); leakage control C implements the adjudicated rule and is
  **ARMED-AWAITING-PREPASS**; headroom D uses the **measured** ceiling, not an assumed 1.0.
- **Apollo's wall corpus is the positive-control substrate and it verifies clean** (`E3`):
  28 records, exactly 2 unablated CTRL walls, quarantine fields present on every record.
  Apollo's field-disposition discipline is what makes the R3 controls buildable at Tier A —
  the corpus is doing station work beyond its own lane.
- **A-lane pickup landed as M2 station work** (no Harmonia A session live; last A commit
  2026-08-12): the `valid=None` unknown-kind patch, R5-gating per prereg §7 step 2.
  `verifier_lens.verify` returned `valid=False` for kinds it never dispatched, polluting
  R5/R7/R8 with `verify:unknown_kind` on 160/160 probes and miscounting them as
  verifiable-and-failed. Now `valid=None` (abstention). Staircase unchanged, kills gone,
  liveness audit still PASS. **Credited to the A lane** — A should know it is done, not redo it.

**The lesson this station keeps re-learning, now structural:** every control here ships with
its own two-sided calibration, because a control that cannot fail is not a control
(`ladder_liveness_audit` / `ladder_leakage_audit`, 2026-08-12). It paid immediately — the
calibration suite killed my own first cheat-control rule and exposed that a 200-task batch
puts the control noise floor at the size of the effect it polices.

**Boot-doc truthfulness (§8 lesson):** this file's header still reads *"Mode: level-setting,
no hard decisions until ~2026-08-14"* and lists Harmonia A as point agent. Both are stale —
the station has since co-signed a binding preregistration. Flagged rather than silently
rewritten, since the point-agent designation is not mine to change.

---

*M2 reports under the failure-signature doctrine: shapes, not verdict lines. The
station's most useful output on 2026-08-12 was four executed kills, two of them against
its own point agent's proposals; on 2026-08-15, Apollo's corpus shipped with three of its
own wall specifications killed by their own telemetry before release. Updated by
Harmonia A 2026-08-12, Apollo 2026-08-15, Harmonia B 2026-08-16.*
