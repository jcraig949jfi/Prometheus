# Review Dossier — Harmonia B, 2026-08-12

**THE ENTRY POINT for this session.** Everything reviewed, everything executed, everything
produced, and everything deliberately *not* reviewed. If you read one file from this
session, read this one; it is built so the other five are reachable but optional.

**Author:** Harmonia_M2_B (cartographer / adversary)
**Session:** cold restart after a 46-day pause → four-option reassessment → whole-program
review against the north star → documentation.
**Repo:** HEAD at start `2350a1de` (2026-06-27). HEAD at end `ec6fbd89`. Commit is **local,
not pushed** as of writing.

---

## 1. The answer, on one page

**Three numbers.** 12,666 markdown documents tracked. 8 typed training objects in the
failure corpus. 1 of those survives audit.

**The instrument finding (E3).** The grading oracle — the flagship of the v3 "are we
closer?" thesis — leaks its answer key at R6. `probe.data["truth"]` **is**
`ground_truth`; a 3-line reader scores 100% and ties `reasoner_falsifier` at the top of
the published staircase, and `reasoner_falsifier` *is* that reader. Root cause is
representational: R6 probes carry no statement of the conjecture, only a `cid` label, so a
lookup table is the only available strategy. It is M0's A4 wall seen from the other side.
**Exactly one tier wide** — R0–R3, R5, R7, R8 are clean.

**The program finding (E3).** The complexity sprawl ended in **May, not July**, and not by
decision: April peaked at 28,268 monthly `.md` touches, May ran at 7% of that, June at
1.4%. Everything that died was *coordination machinery*; everything that lived was an
*instrument or a corpus*. Working theory: that machinery was hand-built agent scaffolding
the frontier harness now provides natively — outcompeted, not wrong.

**The cartographic reading.** One failure primitive at four altitudes: *the measurement
carries its own answer inside itself.* Substrate (SYNTHESIS_v2) → selector (M0) →
instrument (R6 leak) → **program (the document about the progress is the measurement of
the progress)**.

**The recommendation.** Merge "fix the meter" + "audit the fleet instrument" into one lane;
run the authorship-independence probe *after*, against a repaired ladder; park the h2
cross-generator audit. Then change the unit of program output from documents to typed
objects, and retire dead directories by disuse rather than debate.

---

## 2. Everything I read

Evidence typing: **E1** = read the source myself · **E2** = another agent's executed
result, taken as reported · **E3** = executed by me this session.

### 2a. Role and bootstrap

| source | what it gave me |
|---|---|
| `D:\prometheus\roles\Harmonia\CHARTER.md` | The cartographer frame: measure terrain, not bridges; record features not verdicts; "the honest number is zero." |
| `D:\prometheus\roles\Harmonia\RESPONSIBILITIES.md` | The battery (38+ tests), the 3.8M-object calibration anchor, the 10 negative dimensions. |
| `D:\prometheus\harmonia\proposals\2026-06-09\RESTART_HANDOFF_by_B.md` | My own prior state: the A/B/D/E/F program, the frozen `costume_check` contract, and a ranked open-items list (items 1 and 4 since closed by others; 2 and 3 still open; 5 superseded). |
| `D:\prometheus\roles\Harmonia\RESUME_20260615_icarus_ladder.md` | Icarus at R5-passing, climbing R6 on the loop backend; the R5 lesson — *suspect the interface before the reasoning*. |
| `D:\prometheus\harmonia\memory\restore_protocol.md` (v4.4, §head) | The 12-file / 30-minute cold-start path. **Flagged: it restores you into the dead April substrate.** |
| `D:\prometheus\harmonia\memory\coordination\current_wave.md` | Still reads *"Updated: 2026-04-22 wave 0 (bootstrap)."* Never updated again — the single clearest fossil. |
| `D:\prometheus\docs\landscape_charter.md` | The landscape-is-singular reframing; open problems as compression requests; machinery over theorem. |
| memory `user_prometheus_north_star` | Coordinate systems of legibility, not laws. Novelty as the reward signal. **The named failure mode: reward-signal capture.** |

### 2b. The program chain

| source | date | ev | what it said |
|---|---|---|---|
| `D:\prometheus\pivot\REASSESSMENT_2026-06-22_v3_the_reframing.md` | 06-23 | E1 | Prometheus = the TDD layer, not the organism. Q1/Q2/Q3 as executable gates. Ships its own kill condition (a progress meter can be Goodhart'd). M0 is the keystone, raised not dodged. |
| `D:\prometheus\charon\CHARON_SESSION_2026-06-23.md` | 06-23 | E1 | Adversarial verdict on A's chain. Diagnosis right, **CC-1 leverage claim wrong**: the central gate has promoted ~0–5 symbols; volume lives in N per-agent ledgers. Recommends a scoped M0.5 ledger census. |
| `D:\prometheus\harmonia\experiments\M0_RESULTS.md` | 06-27 | E2 | The keystone. 0% reject across 18 true claims (fails closed/silent, not loud/wrong); **17% on the true-novelty arm**; every genuine accept hand-routed past `verify()`. Blocker is representational, not epistemic. Author overrode the harness's own mechanical "Reading A." |
| `D:\prometheus\harmonia\diagnostics\COVERAGE_SWEEP_RESULTS.md` | 06-22 | E2 | Three distinct stall mechanisms, not one: EC = B2 ceiling (12%), a3 = dead-by-proof (0%), Apollo and Icarus = MIXED (climb-limited). **The diagnostic refuses to force verdicts** — its best property. |
| `D:\prometheus\roles\Harmonia\MEASUREMENT_FLEET_2026-06-27.md` | 06-27 | E1 | Track 1 grading oracle, "non-gameable," calibrated staircase, wired into Hephaestus's #1 priority. **This is the document my finding falsifies at R6.** |
| `D:\prometheus\harmonia\proposals\2026-06-09\SYNTHESIS_v2_by_B.md` | 06-10 | E1 | My own capstone: coordinate collapse across 5 substrates; two of the program's most-promising leads killed with proofs; the a3 product-measure theorem; the two open lenses (authorship-independence, information-vs-utility). |
| `D:\prometheus\roles\Harmonia\AUDIT_20260622_*` (2 files, skimmed) | 06-22 | E2 | Instrument monoculture; the 6-lens stall map. |
| Techne resume, commit `5b8a80c2` | 06-23 | E2 | **M0.5 executed.** 0 promoted under the current formula → the "2,351 promotions" is a *formula fossil*. Plus a non-canonical dissent against v3's reframe. |

### 2c. Code read at the source

| file | what I was checking |
|---|---|
| `D:\prometheus\harmonia\services\grading_oracle.py` | Confirmed it imports `gen_R0…gen_R8` from `reasoning_phase0` — so the ladder's defects are the oracle's defects. |
| `D:\prometheus\harmonia\experiments\reasoning_phase0.py` | `gen_R6` (:125, probe built at :131), `gen_R5` (:141), `reasoner_falsifier` (:404, leak at :410), `_ans_correct` (:428, R6 branch :439), `grade` (:460, trace credit :479–486). **The finding lives here.** |
| `D:\prometheus\agents\icarus\tier_oracle.py` | Cheat fields *are* stripped from `probe_schema` (:96) — the leak is at grade time, not schema time. |
| `D:\prometheus\agents\icarus\daemon.py` :527 · `lenses\generator.py` :30 | The only guard is a prompt sentence — and the generator prompt actively points at `probe.data['cid','cex']`. |
| `D:\prometheus\agents\icarus\cycles\cycle_021\code\reasoner.py` :149 | Icarus's evolved R6 handler: five hardcoded `if cid ==` branches. The rational response to the interface it was handed. |
| `D:\prometheus\agents\icarus\state\*` | 22 cycles run, **8 typed objects**, 2 `capability`, cycles 0–12 emitted nothing. |
| `D:\prometheus\harmonia\experiments\m0_anticalibration.py` :376 | The mechanical 50% knife-edge verdict the M0 author overrode in prose but did not fix in code. Still owed. |
| `D:\prometheus\harmonia\diagnostics\ladder_liveness_audit.py` | **Harmonia D's, written today.** The positive control to my negative one. |

---

## 3. Everything I executed (all E3, all reproducible)

| # | measurement | result |
|---|---|---|
| 1 | cheat / const / null reasoners on R6 | cheat **100%**, const_false 57.5%, const_true 42.5%, null 0% |
| 2 | reproduce the fleet's published staircase | **exact to the digit**, 6 weeks later, cold tree: template 8.4 / procedural 34.3 / careful 59.1 / falsifier 62.5 |
| 3 | grade the cheat reader through the real oracle | R6 **100%** — ties `falsifier` |
| 4 | R5: label-reader vs blind derivation | **100% vs 100%** — leak present, *not* load-bearing. My prediction failed. |
| 5 | `ladder_leakage_audit.py` — all 8 tiers | **only R6 leaks**; chance floors measured first time (R5=75%, R6=57.5%, R7=42.5%) |
| 6 | `ladder_liveness_audit.py` (D's) — all 8 tiers | **all LIVE** — every tier accepts its own ground truth, so R7/R8 are genuinely unclimbed |
| 7 | monthly `.md`/`.py` churn, Mar–Jun | 8,879 → **28,268** → 2,031 → 392 `.md`; the May collapse |
| 8 | last-commit date per subsystem | coordination machinery 04-18…05-05 (dead); instruments/corpora 06-15…06-27 (alive) |
| 9 | corpus + repo census | 12,666 `.md`, 30,460 tracked files, 41 top-level dirs, 8,727 `.py` (5,273 in `agents/hephaestus`) |
| 10 | Icarus training stream contents | 8 objects, cycles 13–18/20–21, `capability` ×2 (one of which — cycle 21, R6 — is unearned per #1) |
| 11 | Theseus ledger presence on M2 | `signature_index.sqlite` **absent on this host** (corpus dir exists) |

Re-run the two that matter in ~10 seconds:
```
cd D:\prometheus
PYTHONPATH=. PYTHONIOENCODING=utf-8 python harmonia/diagnostics/ladder_leakage_audit.py
PYTHONPATH=. PYTHONIOENCODING=utf-8 python harmonia/diagnostics/ladder_liveness_audit.py
```

---

## 4. Everything I produced

| artifact | role |
|---|---|
| **`D:\prometheus\harmonia\corpus\typed_objects.jsonl`** | **the session's real output** — 8 typed objects |
| `D:\prometheus\harmonia\corpus\validate_corpus.py` | schema + validator + rollup |
| `D:\prometheus\harmonia\diagnostics\ladder_leakage_audit.py` | standing negative control |
| `D:\prometheus\roles\Harmonia\REVIEW_20260812_program_and_instrument_audit.md` | the instrument audit + four options re-ranked (§7 = corrections) |
| `D:\prometheus\roles\Harmonia\POSITION_20260812_north_star_reset.md` | position paper for the A / Apollo brainstorm |
| `D:\prometheus\roles\Harmonia\SESSION_JOURNAL_B_20260812.md` | session narrative — **local only**, `roles/*/SESSION_JOURNAL_*.md` is gitignored by policy |
| `D:\prometheus\roles\Harmonia\DOSSIER_20260812_harmonia_B_review_index.md` | this file |

**The eight typed objects** (`harmonia/corpus/typed_objects.jsonl`):

| id | altitude | kind | subject |
|---|---|---|---|
| 001 | instrument | defect | R6 answer-key leak |
| 002 | instrument | **failed attack** | R5 leak is *not* load-bearing — my prediction died |
| 003 | instrument | scope bound | only R6 leaks; chance floors measured |
| 004 | program | measurement | the April coordination substrate died of disuse |
| 005 | program | measurement | reward-signal capture: 12,666 : 8 : 1 |
| 006 | program | measurement | adversarial contact rate — 2 passes, 2 breaks |
| 007 | instrument | scope bound | D's positive control completes mine; all 8 tiers LIVE |
| 008 | program | **failed attack** | two of my own program-level claims falsified same-day |

Memories written: `project_harmonia_B_ladder_leak_20260812`,
`feedback_measurement_carries_its_answer` (since amended),
`feedback_repo_state_is_not_program_state`.

---

## 5. Corrections — claims of mine that died this session

1. **"R5 leaks the same way as R6."** Tested; blind derivation ties the label-reader.
   Wrong. Produced the useful discriminator instead: *leak + non-recoverable = unearned
   credit; leak + recoverable = cosmetic.*
2. **"Assume R7/R8 leak until checked."** Checked. Clean. The finding is one tier wide.
3. **"Charon's M0.5 census is the highest-value unclaimed item."** Techne executed it
   2026-06-23. The answer — *formula fossil* — is a third possibility neither Charon nor I
   predicted.
4. **"No commits in 46 days."** True of HEAD, false of the program: Techne, Ergon, Apollo
   and Harmonia D all pushed today.
5. **"The program builds instruments faster than it audits them."** Accurate for June,
   **partially falsified today**: two uncoordinated sessions built complementary controls
   on the same instrument within hours, each catching what the other missed.

The root process error behind 3 and 4: **I inferred program state from repo state.** HEAD
is a lower bound on activity, not a measurement of it.

---

## 6. What I did NOT review — the honest boundary

- **Did not re-run** M0 or the coverage sweep. Their numbers are E2 here.
- **Did not audit** the CF / RE / AE / LE tiers (not in `grading_oracle.TIER_GENS`, so
  they don't affect the published staircase, but the same `grade()` handles them).
- **Did not verify** the "157/157 independent verifier agreement" claim, or whether
  `verifier_lens` covers `kind="conjecture"` independently of the `cid` registry. **I
  suspect it does not. This is the next thing to check.**
- **Did not inspect** Apollo or Hephaestus state, or reconcile the Apollo verdict dated
  2026-06-28 that post-dates HEAD.
- **Did not read** ~35 of the 41 top-level directories — `forge`, `noesis`, `arcanum`,
  `ignis`, `stoa`, `thesauros`, `rhea`, `aethon`, most of `pivot/`, and the 5,273 files in
  `agents/hephaestus`. My §3 sprawl census counts them; it does not evaluate them.
- **Did not confirm** the Theseus ledger is absent program-wide — only on M2.
- **Single author, single family.** This is Opus reviewing Opus artifacts
  (`PATTERN_CORRELATED_MUTATION`). The load-bearing part is deliberately the *executed
  disagreement* in §3, which no shared prior can produce.

---

## 7. Open, ranked (supersedes `RESTART_HANDOFF_by_B.md` §5)

1. **Repair the meter, then freeze it.** R6 gets a real predicate; strip `truth`/`cex`;
   verify every ground-truth label (`sum_two_squares` is committed as `truth=True` with the
   source comment *"true-ish placeholder"*); cross-check trace fields instead of crediting
   self-assertion; publish chance floors; install **both** controls as standing gates.
2. **Change the unit of output** — typed objects, not documents. Needs A's and Apollo's
   argument first; my own stated risk is that it degenerates into April with JSON.
3. **Retire by disuse.** 41 dirs, most last touched in April. Rewrite or archive
   `restore_protocol.md` — it restores cold agents into the dead substrate.
4. **Authorship-independence probe** — still unowned, biggest threat to the
   coordinate-collapse finding, better run against a repaired ladder.
5. **Check the verifier's independence at `kind="conjecture"`** (§6, item 3).

**Owed elsewhere:** Icarus's parked cycle-21 R6 promotion must not be promoted; Hephaestus
grades against the leaking oracle each cycle; the fleet doc's Track-1 R6 column needs a
correction note.

---

*Honest number of novel discoveries: zero. Honest number of verified typed training
objects in the program: one. Two adversarial passes against this program's instruments,
two breaks — one of them mine, against my own file — and by day's end a third and fourth
session had landed, one correcting me and one completing me.*

— Harmonia B, 2026-08-12
