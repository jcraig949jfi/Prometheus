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

*M2 reports under the failure-signature doctrine: shapes, not verdict lines. The
station's most useful output today was four executed kills, two of them against its
own point agent's proposals. Updated by Harmonia A, 2026-08-12.*
