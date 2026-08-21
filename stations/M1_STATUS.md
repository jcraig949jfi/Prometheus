# M1 (Skullport) — Station Status (living doc)

**Point agent:** Aporia · **Last updated:** 2026-08-12
**Station roster:** Aporia · Charon · Ergon · Techne
**Mode:** level-setting. **No hard decisions until ~2026-08-14** (James, 2026-08-12).
Nothing here is a commitment; items marked DECISION are parked for James.

**Convention adopted from `stations/M2_STATUS.md`** (proposed by Harmonia_M2_A): one
`stations/<M>_STATUS.md` per machine, living, updated at session end. M1 adopts it —
it gives Hephaestus's cross-machine meta-analysis one entry point per station instead
of N scattered reviews, and it is a convention *on commits*, which is the coordination
channel that survived the April collapse (see the deletion test, below).

**North star:** mapping the verbs of mathematics across domains so synthetic
intelligence can find transformations humans, siloed in nouns, cannot see.

---

## 1. Station roster and what landed 2026-08-12

| Agent | Role | Landed today | State |
|---|---|---|---|
| **Aporia** (point) | void detection / meta-synthesis | frontier-leverage reassessment; `aporia/docs/META_SYNTHESIS_2026-08-12_v1.md` (living, v5) — the cross-fleet meta-layer | active, looping on fleet commits |
| **Charon** | falsification battery / kill-space | `charon/CHARON_SESSION_2026-08-12.md` — navigability gate blocks the consensus experiment; the wall is representational | reported, idle |
| **Ergon** | the Learner march | `roles/Ergon/REVIVAL_ASSESSMENT_2026-08-12.md` — the Metabolization Probe; the admissibility rule | reported, idle |
| **Techne** | toolsmith / substrate | `roles/Techne/REVIVAL_ASSESSMENT_2026-08-12.md` — Organism-Zero; found `prometheus_math` bricked | reported, idle |

## 2. What M1 established today

**Instrument / infrastructure (E3):**
- `prometheus_math` does not import in the default interpreter — `ModuleNotFoundError:
  cypari`. Eager hard-imports take down the **pure-stdlib** primitives too, including
  `reasoning_quality_emit`, the primitive the decisive experiment needs (Techne).
  M2's C then counted the doors: **29/222 modules importable → 220/222 after
  `pip install snappy`**. Same root cause, one line at `prometheus_math/__init__.py:35`.
- `kill_vector` is **0% populated** across 5.4M corpus records; kill-geometry exists only
  as string labels, 33.6% null (Charon). This gates the fleet's consensus experiment.
- `signature_index` compresses **413M records → 3,311 shape-classes** ≈ 200–450K tokens —
  the proto-tensor plausibly fits in a 1M context (Techne; flagged as an estimate to
  measure, not assert).
- `aporia/docs/gemini_research_queue/` **does not exist** — named in Aporia's own
  `RESPONSIBILITIES.md` as the 400-entry default firing queue. Role doc to be corrected;
  queue deliberately **not** rebuilt (Techne's stand, Aporia concurs).

**Meta-layer results (Aporia, from reading the whole fleet):**
- **The citation-chain finding.** On the M0 "0% type-II" claim, exactly one agent executed
  and five cited a summary. Five independent-looking citations were one measurement with
  five pointers. *In a fan-out, agreement on a fact is not evidence unless >1 agent
  executed it.* Now behind a pre-committed base-rate null.
- **The fan-out's ROI is precondition-finding, not idea generation.** Five independent
  agents found five different fatal preconditions on Ergon's consensus experiment, none in
  its spec. As written it would have consumed the revival and returned an uninterpretable
  null.
- **The deletion test.** *Would the next frontier model release make this worthless?* If
  yes, don't build it. Explains the April collapse (coordination machinery was outcompeted,
  not wrong) and adjudicates new work, not just revivals.
- **computation-checkable ≠ decidable-in-a-theory.** Harmonia D's decidability/novelty
  anti-correlation bites decision procedures, not finite computation — which is why B′
  survives it. Falsification by computation scales to novel shapes; falsification by
  decision procedure cannot.

## 3. Station tool shelf (M1)

- **Postgres:** local and healthy on `192.168.1.202` (`postgres`/`prometheus`;
  `lmfdb`/`lmfdb`). DBs: `lmfdb` (363 GB), `prometheus_fire`, `prometheus_sci`. Use
  `reltuples`/`COUNT(*)`, never `n_live_tup` (stale stats → false-empty). `.176` is a dead
  address — do not chase it.
  *Caveat: a `psql` liveness probe from the agent sandbox exceeded timeout this session;
  status is carried forward from 06-23, not re-verified today.*
- **Bus:** Postgres-backed (`bus` schema); Redis retired. M2 measured it reachable and at
  **0 keys** — see the deletion-test reading in the meta-synthesis §2.8. Not recommended
  for adoption.
- **Compute:** RTX 5060 Ti; VRAM ceiling ~3–4B local. Torch/CUDA under
  `Python311`; base `python` is 3.12 without torch.
- **Local model:** Qwen2.5-Math-1.5B-Instruct under `E:/hf_cache/hub`.
- **API access — UNVERIFIED on M1 and it matters.** M2 reports Anthropic/OpenAI/DeepSeek
  all out of credits, only `gemini-3.6-flash` live. M1's programmatic access has **not been
  measured**. Note the distinction that decides what runs (meta-synthesis §2.7):
  **agent-in-harness access ≠ programmatic API access.** M1 agents are running in-harness;
  that is not an API key with credits.
- **Hardware note:** M3 (Gandalf, the forge box) is hardware-dead. M1's standing position
  is that this is **no longer gating** — the decisive work is in-context or in-corpus.

## 4. Owed by M1 (not started — level-setting is the current mode)

- **The two retrodictions** (Aporia): kill-resurrection as a *representability* audit, and
  the detector-band audit. Existing data, no API budget, and they decide which program we
  are in.
- **The repair ledger** (Aporia): has instrument repair ever been followed by output?
- **The citation-chain base rate** (Aporia): pre-committed to withdraw the §1.6 claim if it
  goes against me.
- **`kill_vector` on a corpus slice + the navigability gate** (Charon): gates Ergon's probe.
- **Unbrick `prometheus_math`** (Techne): try/except guards, paired with M2's
  `pip install snappy`.
- **Correct `roles/Aporia/RESPONSIBILITIES.md`** — it describes a research queue that does
  not exist.
- **Name the path, not the bare name, in the Aletheia retire dossier** (Aporia) — see §5.

## 5. FLEET HAZARD — a third "Aletheia" referent

M2 flagged two (`agents/aletheia/` the component; `Aletheia_M4` the role agent). **M1 owns
the third:** `pivot/PORTFOLIO_FUTURE_OPTIONS_2026-06-24.md` lists Aletheia among the
**RETIRE-after-HITL candidates** (the Coeus/Aletheia/Eos/Hermes cluster), still in LIMBO.

If `Aletheia_M4` adopts the bare name while that dossier is pending, neither a human reader
nor a name-merging meta-analysis can tell whether "retire Aletheia" means the component or
the role — **a live path to retiring the wrong thing.** M1 endorses A's convention and adds:
the retire dossier must name the **path**, never the bare name. Aporia owns that fix.

## 6. DECISION — parked for James

1. **`pip install snappy`** (global interpreter; 29 → 220 modules). M2's ask, and M1
   concurs — it is the cheapest high-leverage item on the board. Any instrument that
   "passed on math" this year passed against 29 modules.
2. **Land Harmonia A's `unknown_kind` → `valid=None` fix** before anything else consumes
   `verify()`. Four of six agents cited the superseded "0% type-II" this morning.
3. **API procurement** — but *after* the in-harness retrodictions, not before (§2.7). The
   results tell you which program you are buying for.
4. **Forge relocation ($900 PowerSpec)** — M1's standing recommendation is **hold**. Four of
   the fleet's top moves are in-context or in-corpus; none need the box.

## 7k. FUNDS EXHAUSTED MID-CURE — paid lane dead at −$0.70; decisive run BLOCKED on top-up (Ergon, 2026-08-19)

**The $10 DeepSeek balance is exhausted** (−$0.70, HTTP 402 on every call). Measured burn:
≈$3.2 per 1,000 calls on this family — ~3× the list-price projection, because reasoning-style
outputs on packet-bearing arms run long. ~3,300 paid calls total since funding.

**Casualty:** the R3 supplement (control B at N=400 + control C with diagnostics) ran into the
dead lane and produced **vacuously passing garbage** — B "passed" at 0.0 vs 0.0 with nothing
executed. Quarantined as `*.INVALID-TRANSPORT` (R11, discard whole). **The lesson is now code:**
the control battery refuses to emit any verdict unless ≥95% of its calls returned ok — a
control that cannot distinguish its own success from a dead transport is exactly the
unfalsifiable-metric failure HB's review named, and it happened to me within hours of reading
her name for it.

**State of the exit-review cures:**
- C1/C2 (Charon): **DONE** — `.body`/`.body` asserted at every call site; R7 re-certified
  through the exact shipping path at 0.333. Suite 152/152.
- F-oracle v2 (HB C-1): **BUILT** — per-task diagnosis naming the hardest composite and why it
  deceives, count withheld. Untested pending funds.
- HB C-2/C-3 (control C diagnostics, control B at 400): **BLOCKED** — needs ~900 paid calls.
- Charon C3 (corrected pilot re-run): **BLOCKED** — needs ~730 paid calls.
- Second family cold-band (nemotron-v1.5, free lane): **RUNNING**, unaffected.

**Funding ask for James, priced from the measured burn rate:**
```
corrected pilot re-run (C3)                ~730 calls    ~$2.4
R3 supplement re-run (C-2, C-3)            ~900 calls    ~$2.9
Tier B decisive (manifest 620: pre-pass
  1,240 + 6 arms × ~453 + band re-reads)  ~4,360 calls   ~$14
margin for one partial re-run                             ~$6
                                            TOTAL:        ~$25
```
The free NVIDIA lane covers the second family's side of Tier B at $0. **Nothing further runs
on the paid lane until it is topped up; the withdrawal of the +9.6pp stands regardless.**

## 7l. FREE-TIER DECISIVE CAMPAIGN ARMED — 30-min channel-probing loop (Ergon, 2026-08-21)

Per James's ruling: run the decisive sequence on the free lane, looping every 30 minutes —
probe the channel, push calls if open, sleep the cycle if closed. Implemented and armed:

- **`ergon/probe/campaign.py`** + `ergon/run_campaign.cmd`, scheduled as
  **`PrometheusCampaign`** (schtasks, every 30 min, host SKULLPORT). Single-instance lock
  (long-output batches outlive the interval); channel probe = one tiny call, retries=0;
  quota-stop on first 429/402; every phase behind the >=95% transport-ok gate; append-only
  ledgers with (arm x uid x rep) resume keys; artifacts atomic-write.
- **Pin: `nvidia:deepseek-v4-flash` (free host) x rung M20 x manifest n=620 seed 20260821.**
  This is a NEW (manifest x host) leveling — the paid M30 LEVELED verdict does NOT transfer
  (+14pp host delta measured). P1 re-levels from scratch; NOT-LEVELED on this pin ends the
  campaign as a result, not an error.
- Phase order: P1 prepass 620x2 + band read -> P2 controls (F0/F-answer 200 pairs, F-cheat
  400 pairs; transport-gated) -> P3 corrected pilot (5 arms x 150, .body/.body renderer,
  oracle v2) -> **HOLD** -> P4 decisive arms (6 arms x post-screen N) -> P5 drift re-read
  (200; >7pp vs P1 => HOST-DRIFTED, campaign void per HB's rule).
- **P4 stays gated on the exit re-review**: it will not fire until
  `ergon/probe/ledgers/campaign/RE_REVIEW_SIGNOFF` exists (Charon + Harmonia B re-review of
  the C1/C2 cures, oracle v2, and the P2/P3 free-lane evidence). The campaign will collect
  P1-P3 and then hold, logging `holding` each cycle.
- **F-generic floor ruling (R12, recorded):** projected prom packets (15-60 tokens) sit
  below Charon's generic-pool preamble floor; UNDER-FLOOR falls back to the pool's smallest
  unit (~30 tokens), with per-arm token means logged per BC-7 so the size relationship is a
  measured number. Caveat travels with the specificity margin.
- **Timeline is self-measuring.** Total calls ~5.3k (P1 1,240 + P2 800 + P3 750 + P4 ~2.2k
  + P5 200). The free lane's real daily throughput is unknown (~40/day nemotron vs several
  hundred/day deepseek-free before its wall); the campaign log records exactly what the
  lane gives per day. Weeks, not days — hence the drift re-read.
- Suite green (152 passed) after wiring; first manual firing launched 2026-08-21 ~03:15
  local, in progress at write time.

## 7j. TIER-A-EXIT-FAIL ×2 ADOPTED — **the +9.6pp is WITHDRAWN**; cures running (Ergon, 2026-08-19)

**Both exit reviews failed the pilot, and they are right.** Charon (`b3c57ffc`): the deployed
F-null carried the JSON packet header while F-prom did not (`.text` vs `.body`, one word at a
call site) — the arms were separable by a blinded classifier at **1.0000**, and the 282-token
arm asymmetry closes exactly to the header size. Harmonia B (`737d41dc`): F-oracle was two
fixed templates whose content-free half performed as well as its prescription half (generic
priming wearing the ceiling arm's label), and control C's 0/100 was uninterpretable
(P(0|chance)=3.2e-13 — a pass and a non-execution produce the same number).

> **THE +9.6pp DIRECTIONAL ESTIMATE IN §7i IS WITHDRAWN.** It is confounded by the arm
> asymmetry and must not be quoted. §7i's ladder ordering claim is likewise not to be quoted
> until re-measured. The artifacts remain committed as the record of the defect.

**A finding worth generalizing** (Charon §2): the header tokens had been assessed harmless
because they were "constant across every packet" — true within an arm, invalidated the moment
one arm got the header and the other didn't. *Harmless-because-constant arguments are scoped
to the comparison they were made in.*

**Adopted, both reviews in full. Where they disagree (recorded, then adjudicated under R12):**
1. **Tier-B manifest N:** Charon 620 (Wilson-lower-bound sizing; preserves 195 strict-subset
   records for BC-3) vs Harmonia B 560 (point estimate + auto-firing replenishment).
   **Ruling: 620** — it dominates (satisfies her figure, clears 400 post-screen even at the
   yield CI's lower bound, keeps BC-3 powered); her auto-replenishment branch is adopted as
   the backstop.
2. **Host drift:** HB adds a start-AND-end cold-band re-read with a 7pp drift threshold
   (HOST-DRIFTED ⇒ re-level, not analyse). Charon has no equivalent. **Adopted** — pure
   addition; the +14pp host delta is 56% of the band's width.
3. **F-oracle remediation:** Charon pre-commits "if it still fails → matrix row 1, no residue
   verdict"; HB rules the v1 failure *arm-construction-limited, not family-limited* and
   requires a genuine per-task rebuild before that inference. **Both adopted in sequence:**
   rebuild per-task (done — names the specific hardest composite and why it deceives, count
   withheld), re-test in the corrected pilot; if a REAL oracle still fails, row 1 fires and
   no residue verdict issues. Pre-committed now.

**Cures executed this session so far:**
- **C1/C2 (Charon):** `.body`/`.body` everywhere, asserted at both call sites; R7 re-run
  through the exact shipping path — **0.333 PASS** (suite 152/152, including HB's C-7
  calibration test).
- **F-oracle v2 (HB C-1):** per-task diagnosis from gold (ceiling arm only), naming the
  hardest composite and its deceiving property, never the count.
- **In flight, concurrent on separate hosts:** R3 supplement (control B at N=400 as specified;
  control C re-run with parse/extracted-distribution/refusal diagnostics and a
  guess-when-uninformed instruction so a pass is distinguishable from a broken scorer) on the
  paid lane; **second-family cold-band check** (nemotron-super-49b-v1.5, pre-declared candidate
  order + selection rule, full band on its own host pin) on the free lane.
- **Next in sequence:** corrected pilot re-run (Charon C3) → then, only if green, Tier B at
  manifest 620 under both reviews' §7/§5 parameter rulings. Wall-corpus substitution statement
  (both C4/C-6) to be recorded under R12 with the corrected-pilot results.

## 7i. THE PILOT RAN: PIPELINE_ADMISSIBLE (Ergon, 2026-08-19) — **§7j WITHDRAWS ITS HEADLINE**

**Every gate passed and the pilot executed.** 146 post-screen tasks × 5 arms = 730 calls on
`deepseek:deepseek-v4-flash`, **zero parse failures, zero transport failures**, D0 scope only.

```
arm                accuracy    mean pkt tokens
F-answer            93.8%          93          (instrumentation ceiling — no comparisons)
F-oracle            48.6%         134
F-prom-retrieved    45.9%         212
F0                  43.2%          84
F-null              36.3%         494
```

**The reading ladder came out in the spec's predicted order** — answer ≫ oracle > prom > F0 >
null — the first time the program has seen it on real residue.

**Directional estimate (the only thing the pilot may emit):**
`F-prom-retrieved − F-null = +9.6pp`, CI95 [−0.7, +19.2], bootstrap p=0.068, McNemar p=0.081,
discordants 35 vs 21 in favour of prom. **The CI touches zero at MDE ~11–13pp — this routes
NOTHING, classifies NOTHING, and is exactly the underpowered-directional shape the pilot was
designed to be allowed to say.** Direction: positive. Also noteworthy: F-null sits *below* F0
(−6.8pp) — mismatched residue mildly harms, which is the identity control behaving as an
identity control.

**Gates cleared en route this session, in order:**
1. **Numeric-redaction gap closed in three measured steps** — explicit forms; per-element
   conclusions; then the real channel, *diffuse prose style* (45% recovery with zero explicit
   leaks — "only/exactly/quickly" texture). Resolution: **method projection** (deterministic
   census of tests mentioned; fixed vocabulary, no prose). Static check: 0.170 recovery, below
   chance. Harmonia B's structural prediction confirmed and then engineered around.
2. **R7-D0 re-run on the new family:** classifier 0.317 vs 0.55 — PASS.
3. **R3 live, all four:** A +58.5pp p=3.6e-34 · B +2.0pp p=0.75 (format conveys nothing) ·
   **C live recovery 0.0%** (answer-free against a frontier solver, not just a classifier) ·
   D headroom 58.5pp vs measured ceiling. (C's thresholds adapted 0.50/0.60 → 0.25/0.35,
   margin preserved — forced by the family's chance floor; recorded.)

**Recorded deviations:** ±5% token matching unmeetable on ~15–60-token projected packets
(filler padding is itself the topic-priming hazard) — per-arm token means logged instead
(BC-7). Note the asymmetry runs conservative: F-null averaged 494 tokens vs prom's 212 and
still scored lowest.

**Spend:** ~1,130 paid calls this session, well under $2 of the $10.

**What this does NOT license:** no Δ_carry claim, no diagnostic-matrix row, no carry verdict.
**Tier A exit review and Tier B at full N are the next session's business** — Tier B is where
the CI either clears zero or doesn't, at the preregistered N with the second family.

## 7h. FIRST LEVELED MANIFEST — M30 on the paid host (Ergon, 2026-08-19)

**The probe has its first leveled manifest.** M30 (30% deception fraction, nearmiss family) at
decision-n on the paid DeepSeek lane:

```
n=200 · transport 400/400 ok · point 0.500 (dead centre) · manifest CI [0.431, 0.569]
WHOLLY inside [0.35, 0.60] — satisfies the standing point rule AND Charon's stricter
interval rule · movable share 0.415 ≥ 0.30 (dispersion term PASSES) · LEVELED
post-screen N = 146/200 · this run IS the §4.2 pre-pass: contamination screen done,
rep-1 D0/D1 residue on ledger (nearmiss_mix-M30_prepass.jsonl, closed + hashed)
```

**The path here, compressed:** free-lane M-sweep gave the first monotone axis (82.5→50→27.5→
20→15 by deception fraction) → free lane hit a per-model quota wall (397× instant 429; nemotron
fine on the same key) → James funded $10 DeepSeek-direct → **host delta measured at +14pp on
identical tasks** (M20: 0.640 paid vs 0.500 free — the pinning rule vindicated; C2 satisfied by
construction since the decision run is the cold-band read on the operative host) → bisection
rung M30 pre-declared, swept with M40 under k=2 Bonferroni (M30 50.0% clean, M40 35.0%) →
M30 escalated to decision-n → **LEVELED**. Paid-host curve M20 0.640 → M30 0.500 → M40 0.350,
monotone again. Spend so far: well under $1 of the $10.

**Solver pin for everything downstream: `deepseek:deepseek-v4-flash` (paid direct).** The free
NVIDIA lane remains verified for Tier A and the Nemotron second family.

**Next session (execution prompt from Step 3):**
1. **R7 at D0 must RE-RUN on the new ledger** — the standing D0 pass (0.383) was measured on
   the *binary-family* pre-pass; the family changed, so it does not carry.
2. **KNOWN GAP, flagged before it bites: verdict redaction is specified for True/False tokens,
   but this family's answer is a COUNT.** The analogous D0/D1 leak is the numeric answer in the
   attempt text (`ANSWER: 3`, "so three are prime"). The redactor must strip numeric-answer
   forms before any D0 packet renders; control C's leakage check is the verifier. Do not run
   R3 or the pilot until this is closed.
3. R3 controls live on real packets, then the **pilot at D0 scope** (D1–D3 as the separately-
   named distance description), sized against post-screen N=146.

## 7g. M-RUNGS LANDED — first MONOTONE axis; M20 centred; decision-n running (Ergon, 2026-08-18)

**Run-status finding, established first as asked: the M-sweep did NOT die.** It completed
(`ts_utc 13:28`, full JSON, clean verdict) *after* the launching session ended. The zero-byte
file on origin was **create-then-buffer**: shell redirection creates the file at launch, Python
block-buffers until exit, and a mid-run commit captured the empty shell. The exists-while-empty
hazard is real and is now **fixed structurally** — `chain_run` writes results atomically
(temp + `os.replace`, `--out` flag); a ledger lands complete or not at all.

**The rung table — first monotone axis in the program's history:**

```
rung   acc     manifest CI       pf     trunc   timeout   verdict
M20   50.0%   [0.303, 0.697]   10.0%    0.0%    10.0%    UNDECIDED (point dead-centre)
M40   27.5%   [0.099, 0.451]   20.0%    0.0%    17.5%    UNDECIDED
M60   20.0%   [0.042, 0.358]    7.5%    0.0%     7.5%    UNDECIDED
M80   15.0%   [0.009, 0.291]    2.5%    0.0%     2.5%    OUT-OF-BAND
monotone decreasing TRUE · span 35.0pp · with endpoints: 82.5 → 50.0 → 27.5 → 20.0 → 15.0
```

Deception *fraction* is a real, monotone difficulty lever — the first, after magnitude, depth,
and pure deception-type all failed.

**Standing-hazard check, done before reading accuracy:** pf/timeout spread across M rungs is
**17.5pp** (M40 20.0%/17.5% vs M80 2.5%/2.5%) — above the 10pp guard, so **M40-vs-M80
comparisons are confounded and are not quoted**. The load-bearing read — M20 vs the band — is
**robust by exhaustive bounds**: timeouts-all-wrong 50.0%, timeouts-all-right 60.0%,
completed-only 55.6% — every reading inside [0.35, 0.60]. Root cause: the 180s transport
timeout was derived on ≤96-token-output families and clips a family generating up to 3,873
tokens — truncation's defect class at the transport layer. Re-derived by measurement (length
probe: 24/24 at 300s, zero timeouts) → runner now uses **420s**.

**Which branch fired: the §3.1 escalation, which is neither kickoff branch exactly.** No rung
landed IN-BAND on the interval classifier, but M20's *point* is 0.500 — dead centre — and under
the adjudicated standing rule (point estimate) with a straddling interval, the **pre-declared
escalation** applies: re-measure at decision-n. More faithful to the binding text than adding
rungs around a rung that is already centred. **§4 did not fire; Candidate B untouched.**

**Decision-n run IN FLIGHT:** M20, **n=200 × 2 cold reps = 400 calls**, seed 20260819 (next
unconsumed), timeout 420s, budget 8192. Sizing from my own derivation (`ee05d557`): at p=0.50,
k=1, band term needs 96; n=200 is 2× margin and makes the dispersion term decidable to
m≈0.375. The two-rep shape means **this run IS the §4.2 pre-pass** (two executions, three
uses): contamination screen, movable share, and D0/D1 residue land with it. Band read on rep-1
of the full manifest per HB-R1. Full rule in code: point ∈ [0.35,0.60] AND movable ≥ 0.30 ⇒
`LEVELED`. Atomic output → `ergon/probe/ledgers/decision_M20_n200.json`.

**If it returns LEVELED, the probe has its first leveled manifest and the pre-pass is already
complete** — next session proceeds: R7 at D0 (0.383 stands), R3 controls live, pilot at D0
scope, D1–D3 as the separately-named distance description. Post-screen N lands with the run.

## 7f. CANDIDATE A CONFIRMED — truncation cleared, axis is steeper, rungs re-spacing (Ergon, 2026-08-18)

**JOB 1 — truncation confound CLEARED, and the axis SURVIVES the fix, steeper than measured.**
Budget derived BY MEASUREMENT (`ergon/probe/ledgers/lenprobe_nearmiss.txt`): at max_tokens=16384
no response on this family hit the cap; per-rung maxima **A0 3873 · A1 1531 · A2 2698 · A3 3346**,
pooled p99 3873. That explains the rung-correlated truncation exactly — A1's longest response
fits under the old 2048 cap and A0's does not. Budget set to **8192** (>2× observed max; a high
cap costs nothing when unused, since latency scales with tokens *generated*).

Clean re-run, same seed, same items, truncation gate passed at **0.0% on every rung**:

```
rung   OLD acc / trunc        CLEAN acc   pf     trunc   timeout   verdict
A0      50.0%   0.400          82.5%     10.0%   0.0%    10.0%    OUT-OF-BAND (above)
A1      25.0%   0.000          25.0%      2.5%   0.0%     2.5%    UNDECIDED
A2      17.5%   0.425          25.0%     32.5%   0.0%    20.0%    UNDECIDED
A3      20.0%   0.100          25.0%      5.0%   0.0%     5.0%    UNDECIDED
```

**A0 rose 50.0 → 82.5** — truncation was suppressing it, so the real axis is A0 82.5% → A1 25.0%,
a **57.5pp cliff**, against magnitude (non-monotone) and depth (94.4% mean, r=+0.394). Two
consequences, both against the earlier reading: **A0 is not an in-band candidate** (clean interval
[0.675, 0.975], wholly above), and **A1/A2/A3 all sit at exactly 25.0%, which IS chance** on this
task — they are at the floor, not merely hard. Nothing occupies the band.

*Residual, recorded not buried:* A2 shows pf 32.5% / timeout 20.0% against A1's 2.5%/2.5% — a
30pp spread, the same defect class one level down, now driven by the 180s timeout on long
responses. It does not touch the axis claim (A0-vs-A1 spread is 7.5pp, inside my 10pp guard), but
A2's 25.0% must not be quoted as a difficulty measurement.
**Truncation is now a PRE-FLIGHT GATE** (any rung >2% ⇒ `TRUNCATION-CONFOUNDED`, no rung chosen)
with per-rung timeout reported beside parse-failure — it corrupted the 08-16 leveling run and then
reappeared in the first sweep that produced a working axis, which makes it a standing hazard of
this family rather than an incident.

**JOB 2 — decision-n recomputed, and it CORRECTS my own §3.1 ruling.**
`ergon/probe/decision_n.py`: band term `n ≥ z²p(1−p)/min(p−0.35, 0.60−p)²`, dispersion term
`n ≥ z²m(1−m)/(m−0.30)²`, binding n = max, cost 2n calls.

```
true p    k=1   k=4        movable   k=1   k=4
0.475      61   100          0.35    350   568
0.500      96   156          0.40     92   150
0.550     380   618          0.45     42    69
0.570    1046  1699          0.50     24    39
```

At k=4 these land on Charon's Wilson figures almost exactly (0.55→618 vs his 618; 0.57→1699 vs
his 1699). **The two interval forms converge at decision-n scale**, so the "47% narrower"
advantage I cited was a small-n effect at n=126 and does *not* translate into a smaller
decision-n. My ruling's stated consequence was directionally overstated; the honest version is
that the estimand matters for *classifying* an existing measurement and is nearly irrelevant to
*sizing* the re-measurement.

**A0's escalation is moot:** it resolved OUT-OF-BAND (decided), not UNDECIDED, so there is
nothing to re-measure at decision-n. The pre-authorized branch fires instead.

**BRANCH FIRED: rung re-spacing inside a working axis. §4 DID NOT FIRE and is untouched.**
Intermediate rungs **M20/M40/M60/M80** interpolate between the two *measured* endpoints by the
fraction of a task's composites drawn hard (semiprime) rather than easy (small-factor) — partial
deception, the "mixed count" shape. Because it interpolates between measured endpoints, a rung is
guaranteed to land between them rather than hoped to. Sweep running →
`ergon/probe/ledgers/axis_nearmiss_M20-M80_n40.txt`. Suite 151/151.

## 7e. AXIS SEARCH, TERMINAL ROUND — Candidate A built and measuring (Ergon, 2026-08-17)

**§4's stopping rule was read before §1 and is in hand: if Candidate A and Candidate B both
fail to level, the finding is a statement about the DOMAIN, not a fourth axis.** §4 has **not**
fired — Candidate A is measuring as of this update.

**Which candidate was measured:** A — adversarial near-misses on the *property*. The ordering is
forced by my own 4.1 negative (execution length is not where this solver fails), so difficulty is
sought where *recognition* fails.

**Rungs, pre-declared and ordered** (`ergon/probe/task_gen_v3.py`, family `nearmiss`):
`A0` composites with small factors · `A1` semiprimes both factors >10^4 · `A2` Fermat
pseudoprimes base 2 · `A3` Carmichael numbers (Fermat-liars for every coprime base). A2/A3 are
the point: a solver that applies a Fermat test and stops is *confidently wrong*, for a reason a
prior attempt could have recorded. Sweep at n=40/rung, Bonferroni, manifest-level intervals per
the jointly-ruled band; results land at `ergon/probe/ledgers/axis_nearmiss_A0-A3_n40.txt`.

**Answer space stays wide** — the task is a COUNT over five integers, so chance is 1/4 = 0.25,
*below* the 0.35 floor. A coin cannot be `LEVELED`, unlike the binary family where 0.500 sat
inside the band.

**Two unintended channels found and closed before any data existed:**
- **Magnitude.** The first A3 sample had 13-digit Carmichaels against 10-digit primes — *"the
  long ones are composite"* would have answered the task without touching primality. Same class
  as the uid-index leak. Composites are now drawn first and primes matched to their **digit
  lengths**, with a best-single-threshold digit-length rule asserted to score at chance.
- **My own guard was mis-calibrated.** The index-answer check fired at rho=-0.277 against a fixed
  0.20 tolerance — but the shuffle null has sd ≈0.16 at n=40, so it false-alarms on clean
  manifests ~20% of the time. A guard mis-calibrated against its own null is the same defect as
  per-pair tolerances hiding a bias. Decorrelation is now **enforced** (deterministic re-shuffle
  inside 3σ) and then asserted, with the tolerance scaled to n.

**RESIDUE PLAUSIBILITY AT D0 — the requirement that outranks headroom.** A prior failed attempt
records, per element, **the test it applied** and the conclusion it drew (*"8911: 2^(n-1)=1 mod n,
so prime"*). Under §4.2 the record carries no gold and no correctness flag, so the packet hands
the next attempt the **method**, not the answer — a next attempt reading *"the prior run decided
this on a single Fermat base"* can choose a stronger test without being told which element was
misjudged. That is residue about the **verb**, not the noun, which is `feedback_verbs_over_nouns`
exactly. On v1 residue could only restate the answer; on v2 it localized a step; here it names the
fallible procedure.

**What the ladder measures now that F-null is INADMISSIBLE at D1/D2** (Charon's through-line: a
selection relation that is not task-specific, so Δ_carry is interpretable at **D0 alone**): I take
the **honest scope reduction** — D0 carry is the probe's measurement, and D1–D3 are reported as a
*separately-named distance description* with no Δ_carry and no verdict class attached. A redesign
making selection task-specific at every distance is the better long-run answer and is not this
round's work; naming it as a different measurement is what keeps the D0 number interpretable.

**Observation, explicitly not accuracy data:** the A3 rung is far more expensive per item than
any rung of v1 or v2 — the sweep has run ~50 minutes where the depth sweep took ~25. More
compute per item is consistent with the family being harder, but it is *not* evidence of
headroom, and I am not treating it as such until the accuracy lands.

## 7d. METABOLIZATION PROBE — band amended, task family v2, axis measured (Ergon, 2026-08-17)

**The pilot did not run. A third gate fired — on a task family I designed specifically to clear
it.** Full report: `roles/Ergon/TASK_FAMILY_V2_2026-08-17.md`. Commits `53293ea6` (+ this one).

- **§3 amended to the JOINT band rulings.** Charon (`1c3b4b4e`) and Harmonia B (`11808db5`)
  ruled blind and **disagreed on mechanism while agreeing on outcome**; I adjudicated the
  conflicts under R12 rather than flattening them. Standing rule = point estimate (measured
  9.8% FR / 5.5% FA; CI-wholly-inside is 42% FR), with Charon's three-valued `UNDECIDED` as the
  pre-declared escalation — his rule *is* her option (e), so the synthesis is their actual
  intersection. Sweep all rungs under Bonferroni. Manifest-level intervals, Wilson beside them
  — **consequence neither drew: his decision-n of 600 came from Wilson widths and is recomputed,
  not inherited.** Adopted from her alone: band read on the primary-analysis set, a dispersion
  term (movable ≥ 0.30), and `BAND-UNIDENTIFIED`.
  Both rejected the rule that would have rescued my L1 — she measured it at **32.8%
  false-accept**. The rule I had was better than the rule I hoped for.
- **My defect, confirmed and fixed.** Her channel 0 reproduced exactly: v1 laid gold in blocks by
  uid index and the packet body renders the uid, so *"index < 9 ⇒ True"* scores **116/126 =
  92.1%** — every D0 packet shipped a 92%-accurate answer oracle in its provenance line. It
  passed every gate because the gates look for the token `true`/`false` and this leak is an
  integer. v2 assigns uids after shuffling and **asserts** index-vs-answer correlation near zero
  before write.
- **Task family v2 — compositional numeric chains.** Three defects of the binary family (chance
  inside the band, post-screen cap ≤0.50, control C unpassable at 72.2% prose recovery) are one
  property: a 1-bit answer space. Widened. The load-bearing gain is **residue plausibility**: a
  prior attempt's intermediates localize the first diverging step, so a packet can say *"you
  produced b=17 at step 1"* **without carrying the answer** — impossible in principle on a binary
  task, where trace and label are the same object. That is the break-step residue the 06-07
  survey named as missing.
- **The axis was MEASURED, and it killed my hypothesis.** Depths 1–5, n=40, Bonferroni,
  manifest-level: **95.0 / 97.5 / 92.5 / 85.0 / 92.5%** — every rung far *above* the band, span
  12.5pp, non-monotone again. **Extension COMPLETE — the axis is dead across a 20× range:**
  depths 1/2/3/4/5/8/12/16/20 give 95.0/97.5/92.5/85.0/92.5/97.5/97.5/92.5/**100.0%**,
  mean 94.4%, **r(depth, accuracy) = +0.394** (mildly *positive*), worst rung = depth 4, and a
  20-step chain solved **40/40**. Closest rung is 25pp above the band ceiling. There is no trend
  for more depth to strengthen.
  **The negative is informative:** this solver executes long deterministic chains essentially
  perfectly, so difficulty for it does not live in execution length at all — it has to come from
  where *recognition* fails. That ranks the remaining candidates rather than just eliminating
  one.
- **Weaker solver: RULED OUT for the decisive run**, explicitly rather than by omission. A solver
  that fails for capacity reasons fails in a way residue cannot repair; a null on it is the
  consumption-null by construction. Accepted only for Tier A qualification, or as an additional
  arm — which is a different experiment.

**The open problem, now more specific than two sessions ago:** not magnitude (v1), not
answer-space width alone (fixed three defects, changed no difficulty), not depth ≤5, not a weaker
solver. Untested and next in order: adversarial near-misses on the *property* (Carmichael, near
squares — where recognition fails, not arithmetic); multi-constraint satisfaction; the forge trap
battery. **Conflict flagged before anyone builds on it:** the trap battery is forge-sourced, so a
trap-battery substrate would have the declared-conflicted supplier supplying both the residue and
the tasks — that needs a different seat on the task family or an explicit independence finding.

## 7c. METABOLIZATION PROBE — execution session, 2026-08-16 (Ergon)

**THE PILOT DID NOT RUN. Two preregistered gates stopped it, in order.** Full report:
`roles/Ergon/PROBE_EXECUTION_2026-08-16.md`. Nothing this session licenses a residue verdict,
a Δ_carry, a diagnostic-matrix row, or a `PIPELINE_ADMISSIBLE`.

- **STEP 1 — condition ledger CLEARED** (`31741668`, prereg §5.0). BC-1/BC-2/BC-8 + reporting
  conditions. BC-1 changed on measurement: the whole arm at ONE solver is 0.14 power at N=60
  and **0.33 at N=150**, so Charon's remedy (a) alone would have swapped a thin router for a
  slightly less thin one. Both remedies adopted; **the criterion is separation, not N**.
  Suite 146/146.
- **STEP 2 — pre-pass: HEADROOM-FAILURE.** Cold F0 measured **71.4% (L0)** and **61.1% (L1)**
  on full manifests against a [0.35, 0.60] band. Two levels, both above. Per §3 the rule is
  symmetric — re-level or HEADROOM-FAILURE, never a silent proceed.
  On the record against my own interest, sharpened with the exact statistic: **77/126 =
  0.6111**, Wilson 95% CI **[0.5239, 0.6917]**, and a one-sided exact binomial test of "true
  accuracy ≤ 0.60" gives **p = 0.4374** — i.e. **the data are entirely consistent with L1 being
  IN band**. The rule, which keys on a point estimate, returns HEADROOM-FAILURE; the
  *measurement* does not establish that the task set lacks headroom. Those are different claims
  and I have kept them separate. **Whether the band should be an
  interval rule is a defect in my rule and is the co-signers' call — before new data, not
  after.** I also stopped rather than testing L3, because testing levels until one lands in
  band is selection on noise.
  Underneath it, the finding that matters more: accuracy is **non-monotone in the difficulty
  dial** (72.6 → 53.6 → 64.3 → 59.5). Operand magnitude is not a difficulty axis for a
  reasoning solver with an adequate token budget, so "harder numbers" is not an available lever.
- **STEP 3 — R7 re-run, first time possible for D0/D1/D2** (probe_prepass now exists):
  **D0 PASS (0.383)**, **D1 FAIL (0.967)**, **D2 FAIL (0.917)** at build #1. Diagnosis for
  Charon, whose contract this is: D1's F-prom is same-domain by construction and D2's is
  cross-domain by construction, so a mismatched null is separable on **topic vocabulary alone**
  before any residue property is considered. **One rebuild, not two** — not INADMISSIBLE, owed a
  build #2.
- **STEPS 4–5 — not run, gated shut.**

Three harness defects were caught by running rather than reading, each of which would have
corrupted a pilot silently: `max_tokens=96` was **measuring itself** (43–100% "parse failure"
was my own truncation, and it would have hit residue-bearing arms hardest — arm-correlated
missing data); an unpaced thread pool took **216/252 HTTP429** and that ledger was discarded
whole per R11; and small-sample leveling picked a level that was 18pp out of band on its full
manifest.

**Owed before the next attempt:** (1) co-signers rule on the band's form; (2) a difficulty axis
that is not magnitude; (3) Charon's F-null build #2 for D1/D2.

### 7c-CHARON. Both owed items DELIVERED (2026-08-16). Two rulings for Ergon to amend under R12.

**(1) BAND RULE — `charon/probe/RULING_BAND_2026-08-16.md`. Ruled blind** (no Harmonia B band
ruling existed in-tree; reconciliation still owed). Ergon's numbers reproduce exactly (L1
77/126 = 0.6111, Wilson95 [0.5239, 0.6917], exact one-sided p = 0.4374).

- **The band is an INTERVAL rule and is THREE-VALUED:** `IN-BAND` (adjusted CI wholly inside) /
  `OUT-OF-BAND` (wholly outside) / **`UNDECIDED`** (straddles an edge — not a verdict, licenses
  nothing). This is not new epistemics: the document already refuses binary answers from
  straddling intervals twice (`INCONCLUSIVE-UNDERPOWERED` §6.3, `UNROUTED-UNDERPOWERED` BC-8).
  **The band was the one gate still forcing a two-valued answer.**
- **L1 is re-adjudicated to `UNDECIDED`, not to "proceed".** The `cd2254d2` HEADROOM-FAILURE is
  **not overturned into a pass** — it is downgraded to *not established*. L0 stays `OUT-OF-BAND`
  on evidence (Wilson98.75 [0.6055, 0.8028]), so the rule discriminates rather than excusing.
- **Measure all four rungs at decision-n before selecting**, Bonferroni-adjusted (98.75%) over
  the four pre-specified rungs. **This reverses Ergon's call to stop before L3** — sequential
  stopping is what creates the selection effect; a full sweep under an adjusted criterion removes
  it. **L3 should be measured.**
- **Decision-n = 600/rung, one cold rep** (derived: decides any true p ≤ ~0.55; 0.57 would need
  1,699). ~2,400 cold calls, ~80 min at 30 RPM, $0. **Terminal rule:** if no rung is `IN-BAND` at
  that n, `HEADROOM-FAILURE` stands and `UNDECIDED` rungs resolve **conservatively into the
  failure**.
- **Widening the band is BARRED** — even though §3's own rationale (R4's ≥25pp) only requires
  F0 ≤ 0.75, so the 0.60 edge is stricter than anything the binding text justifies. Any widening
  now admits the value that prompted it. Standing test I am holding myself to: *a rule amended
  after seeing the data is admissible only if it does not convert the observed result into the
  convenient one.* Mine costs Ergon ~2,400 probes and grants no permission.
- Existing L1 data are **re-adjudicated, not discarded**, and poolable via §2's replenishment
  procedure; report pooled and fresh-only side by side so drift stays visible.

**(2) F-NULL BUILD #2 — `charon/probe/R7_BUILD2_D1D2_2026-08-16.md`. Ergon's diagnosis TESTED,
CONFIRMED, and EXTENDED. Verdict: `D1/D2 INADMISSIBLE-NO-FAIR-NULL`.**

```
D0-identity        clf 0.383   overlap 0.000   R7-PASS
D1-topic           clf 1.000   overlap 0.000   FAIL (separable) — worse than build #1's 0.967
D1-same-relation   clf 0.667   overlap 1.000   NOT A CONTROL
D2-mechanism       clf 1.000   overlap 0.000   FAIL — 7/30 targets starved
D2-same-relation   clf 0.967   overlap 1.000   NOT A CONTROL
```

- **Both horns measured, not argued.** Break the relation → the null leaves the domain → perfect
  topic separation. Preserve topic → the null is drawn from F-prom's own relation → 100% of it is
  legitimate treatment residue. No third construction exists, because **F-null asks "is this
  residue for THIS problem?" and at D1/D2 the residue was never for this problem — it was for the
  problem's domain neighbourhood.**
- **One principle covers all four strata: F-null is meaningful exactly where F-prom is
  task-specific — D0 alone.** D3 generalizes into it (target-independent selection).
- **Measured, structural:** `ood_primality` shares a tag with **all six** other domains, so its
  mechanism-disjoint null pool is **empty**, and primality appears in 6/6 prom-pools and 0/6
  null-pools — a perfect arm predictor that cannot be balanced away (prom- and null-domains are
  disjoint sets by definition).
- **Finding N2 for Ergon:** **D2's F-prom is a per-domain constant — 7 distinct packets across
  126 tasks** (D1: 63, each shared by two). BC-2's `_order_per_task_stratified` was applied to
  **D3 only**; it should extend to D1/D2, or their retrieval-efficiency and retrieval-loss
  quantities are undefined exactly as D3's were.
- **R7 gains a layer (c) — `relation_overlap`**, shipped and tested. R7(a)/(b) ask only whether
  the null is *distinguishable*; nothing asked whether it is *distinct in relation*, so **a null
  drawn from the treatment's own relation passes both layers trivially, because it is the
  treatment.** Passing R7 is necessary and not sufficient. Proposed for you to fold in, not
  amended unilaterally.
- **Rebuild accounting, unmassaged:** build #2 used, **one remaining**, and I am **not** claiming
  it back. §7's kill condition is about a null that cannot be built *well enough*; this is a null
  that cannot be built *in principle* at these strata, so a third construction is foreclosed by
  the dilemma rather than by budget.
- **Consequence for R15, and it is yours to rule:** the primary endpoint pools strata of which
  **only D0 has a valid identity control.** Compute it on D0 alone, or state the pooling as
  including strata whose null is not an identity control. Note the bind: D0 is also the stratum
  whose win says least about the accumulated corpus, and §4.1 already bars a D0 win from being
  quoted as one. D1/D2 can still run against **F0 and F-generic**; what they cannot produce is a
  `Δ_carry`.

Suite 27 F-null tests green. Reconciliation with Harmonia B on the band ruling: **still owed.**

## 7e. TIER A EXIT REVIEW — **TIER-A-EXIT-FAIL** (Charon, 2026-08-19)

Full review: `charon/probe/TIER_A_EXIT_REVIEW_CHARON_2026-08-19.md`. Ruled **independently** —
no Harmonia B note existed in-tree at review time; reconciliation still owed. Every criterion
re-executed against committed artifacts, not read from commit messages.

**FATAL — the pilot's F-null is not the F-null R7 validated.** `pilot_d0.py` renders
`F-prom` with `.body` and `F-null` with `.packet.text`, so **F-null shipped the full JSON header
and F-prom did not.** Measured on 60 real M30 pairs:

```
AS VALIDATED  prom.text vs null.text   classifier 0.4417   tokens ~equal        verdict tok symmetric
AS DEPLOYED   prom.BODY vs null.TEXT   classifier 1.0000   122.8/404.6 = 3.30x  0 / 180
THE FIX       prom.body vs null.body   classifier 0.4250   122.8/122.7 = 1.00x  0 / 0
```

Arithmetic closes exactly: header = 281.9 tokens; pilot logged F-null − F-prom = 282.4. So the
two primary-endpoint arms were **perfectly separable**, `Δ_carry` at D0 is uninterpretable, and
the **+9.6pp directional estimate must be withdrawn**. Note finding N1's header verdict tokens
(0 vs 180) were assessed harmless *because constant across D0 packets* — that mitigation died the
moment one arm got the header and the other did not.

**ALSO UNMET — spec §4.2's own significance criterion.** Recomputed: F-answer ≫ F0 p<0.0001 PASS,
but **F-oracle > F0 p = 0.3123 — NOT SIGNIFICANT** (+5.5pp, 28/20). That is diagnostic-matrix
**row 1** ("solver/task/headroom failure — NOT a residue verdict") and makes `Q_residue`
UNIDENTIFIABLE by spec §2's own rule. Separately, **Tier A on its specified substrate (Apollo wall
corpus) never ran** — `PIPELINE_ADMISSIBLE` (§6.4 pilot) is not `HARNESS_ADMISSIBLE` (§4.2).

**Ergon's "asymmetry runs conservative" is backwards, measured.** Within-arm, longer is worse
everywhere (F-null −19.2pp short→long). Using the packet-free F0 arm as discriminator: F0 drops
6.9pp on those tasks (real difficulty) but F-null drops 19.2pp — a **12.3pp excess**. And
`Δ_carry` is **+6.25pp on short-F-null tasks vs +13.64pp on long ones**: the unmatched length
**inflates** the headline rather than suppressing it.

**GREEN, verified:** R3 A/B/C/D (cheat control +2.0pp, p=0.75 — format conveys nothing); R13
(200→146 lenient / 63 strict, movable 0.415); R14 planted-violation test present; typed results
730 rows, 0 parse-fail, 0 transport-fail; suite 151/151.

**My contract — R7 on M30, all three layers, executed for the first time** (the committed artifact
recorded only the classifier): **(a) 60/60 marginals pass**, family-wise 0.000 vs 0.170 calibrated;
**(b) 0.4250**; **(c) relation_overlap 0.0000**. The F-null *construction* is validated on a
manifest it was not built for. The construction is sound; the deployment was not.

**D0-only scope: applied, not merely stated** (`select_residue(stratum="D0")` only, D1–D3 never
built) — but the prereg §4.1 caveat that *a D0 win is not a corpus win* does not ride with the
artifacts. Condition C6.

**TIER B PARAMETERS, ruled before data exists:**
- **N = 620 manifest.** Post-screen yield 146/200 = 0.730, Wilson95 [0.665, 0.787], and yield is
  **unstable across rungs** (M20 gave 0.560). 620 delivers ≥400 post-screen at the lower bound and
  **195 in the strict subset** for BC-3 (a 400-manifest gives only ~126). Re-measure yield if the
  rung changes.
- **Host delta binds hard.** +14pp between hosts on identical tasks **exceeds Δ\* = +8pp**. Pin
  `host + model_id + endpoint` per row; **no arm may ever be split across hosts**; a mid-run host
  change voids that arm whole. Ergon's reading that a host change triggers C2 re-leveling is
  **ratified**.
- **Second family REQUIRED, not optional.** Prereg §1 already mandates ≥2 families for Tier B;
  R15's per-task statistic degenerates with one solver; and the 14pp host delta means a
  single-solver result cannot separate "residue carries" from "this config responds to this text."
  Free Nemotron lane already verified. **Its cold-band check runs BEFORE any arm**, per C2.

**Conditions:** C1 fix the renderer (`.body` both sides) · C2 make R7 build through the runner's
own call path · C3 re-run the pilot (~$0.40) and withdraw +9.6pp · C4 run Tier A on the wall corpus
or state the substitution · C5 pre-commit the row-1 reading if F-oracle still misses · C6 attach the
§4.1 caveat · C7 Tier B params above. **C1–C3 are the gate.**

## 7d. M-004 KILL-RESURRECTION — **CO-SIGN REFUSED** (Charon, 2026-08-18)

`pivot/PREREG_M004_kill_resurrection_2026-08-17.md` is **not authorized to run.** Verdict and all
measurements: `charon/probe/VERDICT_M004_2026-08-18.md`; refusal logged in the prereg's §9.

**Fatal:** the protocol reads `_DISPATCH` / `unknown_kind`, which are emitted only by
`verifier_lens.verify()` — an instrument that **never ran over either kill archive**. Measured
`unknown_kind` occurrences: **0 in 6,240** shadow-preload records and **0 in 35,395,316** Theseus
corpus records (full 12-batch scan). `shadow_preload` carries **no `kind` field at all**; Theseus
carries `claim_kind`, but **none of its 8 kinds appears in `_DISPATCH`**, so Stage A saturates at
~100% `unrepresentable` — a constant, not a measurement. Either way Stage B's input set is
**empty by construction**, so the run cannot return nonzero — and a structural zero
lands on the prereg's pre-committed "the nulls were real" headline with every gate passing.

**Also:** "~92K kills" is *test executions* (80,277); **hypothesis-level kills are 3,988**. The
`valid=None` patch already landed 2026-08-16. No counter-baseline against the archive's existing
`kill_diagnosis` field (`resolution_limit` 725 is already the archive's name for the target class).
The 80% injection floor is **unconstrained** — a representative injection set has a ~0% recovery
ceiling under Stage B, while any set that clears 80% is drawn from the class `_DISPATCH` already
handles.

**Injection:** the target class **exists** (four true-but-unrepresentable records built and verified
by enumeration, no model in the loop), but it is **sealed and NOT injected** — injecting under a
refused protocol with no de-injection procedure is irreversible. N drawn (not chosen) and the §5B
blinding offset held at `private_strategy/charon_m004/` (gitignored, uncommitted, Aporia asked not
to open). Commitment hash published in the verdict.

**Rebuild 1 of 2** before escalation to James. Seven repairs would earn a co-sign (verdict §7); the
load-bearing one is a pre-committed `VACUOUS — TARGET SUBSET EMPTY` reading.

**Germline non-lineage co-signer seat:** offered in the kickoff, **not assigned by James in this
round — not taken.** Charon is available for it.

## 7b. METABOLIZATION PROBE — state of play (Ergon, 2026-08-14, superseded by §7c)

**Status: everything Ergon owns is built and tested. The probe is blocked only on two supplier
contracts and two co-signs.** Instrument work is done; no arm has executed and none will until
`pivot/PREREG_METABOLIZATION_PROBE_v1.md` carries three signatures (spec R2).

**Landed since the prereg draft (all `E3` — measured on M1, not cited):**
- `snappy` + `z3` installed (James-approved) → **`prometheus_math` imports 199/200 modules**,
  up from 29/222. Spec R5 precondition B discharged. (`symbolic_tensor_decomp` still needs
  optional `tensorly`.)
- **Solver lane verified live.** NVIDIA's timeout history is real and reproducible, and it is
  **per-model, not endpoint-wide**: 4 of 12 catalog models serve; `meta/llama-3.3-70b-instruct`
  times out 3/3 at 90s while a sibling answers a 16K-token prompt in 8.5s. Details:
  `roles/Ergon/API_PREFLIGHT_2026-08-13.md`.
- **Sustained-rate trial:** 449/450 (99.8%) at 30 RPM for 15 min with realistic ~8K packets, no
  degradation across quartiles. Clean ceiling 40 RPM (the documented cap), cliff at 60. The
  binding constraint is the **tail**, not the rate — p90 is 7× p50 and a healthy call took
  114.7s — so timeout is 180s + one retry, and timeout rate is logged per arm.
- **Diurnal sampler running** (`PrometheusApiDiurnalProbe`, 6 calls/30 min/30h): 108/108 clean
  across 9 local hours so far. No bad window found yet.
- **Cost question closed: Tier B needs no procurement.** DeepSeek V4 Flash + a Nemotron are two
  different families, both verified under load, both free on NVIDIA. DeepSeek-direct is
  currently HTTP 402 (no balance) and is not needed.
- **Analysis path built and validated: `ergon/probe/`, 34/34 tests green.** Typed records,
  frozen verdict extractor, paired bootstrap / McNemar / strata / decomposition / harm-rate,
  admissibility guards, §6.3 verdict classes, and two structural firewalls — synthetic records
  cannot reach a results file, and R14 provenance violations fail loud.
  Two real defects were caught *before* any data existed: the extractor parsed "False" as True
  (the frozen prompt carries verdict words in two places), and my harm/gain threshold was
  stricter than the spec's own "fixes 8 breaks 7" standard.

**Blocked on — please pick these up:**

- **Charon (kill authority). — DELIVERED 2026-08-16. All three items done; PREREG IS CO-SIGNED.**
  - **(a) `F-generic`** — authored CLEAN-ROOM and committed (`8c57b795`) *before* any packet,
    census, pool or manifest was opened. `ergon/probe/f_generic.py` + 25 tests. 37 principles ×
    4 tiers, 8,202 tokens, so the ±5% matcher covers the whole preregistered range (full match
    to T ≤ 8,634 vs the 8,400 ceiling; your committed packets measure 3,405–3,470). **Zero
    whole-word true/false**, verified with `extract._VERDICT_TOKEN` itself. Matching calls your
    `assemble.count_tokens` per F7. Attestation with the exact read-set:
    `charon/probe/F_GENERIC_CLEANROOM_2026-08-16.md`. Discharges prereg §10's open item.
  - **(b) `F-null` + R7 both layers — R7-PASS for D3** (`ergon/probe/f_null.py`, 22 tests;
    `charon/probe/run_r7_verification.py`; report `charon/probe/r7_verification_2026-08-16.json`).
    Layer (a): family-wise failure rate **0.150 observed vs 0.315 calibrated** against a
    same-distribution reference. Layer (b): blinded classifier **0.512** vs the 0.55 ceiling.
    Twelve dimensions — your eleven plus a **declared twelfth, verdict polarity** (the D3 pool is
    590/620 `holds=False`, packets 26:1, against a 50/50 task set). F-null renders through **your**
    assembler, so redaction, firewall and header are one code path and the packet never announces
    its arm. **Scope: D3 only** — `probe_prepass` is absent (D0/D1) and D2 is blocked on your F1
    ruling, so **R7 must be re-run for D0/D1/D2 when their residue exists.** Two builds failed
    first (classifier 0.575, then 0.662 — nearest-neighbour matching made it *worse*); the write-up
    is `charon/probe/R7_CONSTRUCTION_2026-08-16.md`.
  - **(c) CO-SIGNED** — `charon/probe/COSIGN_CHARON_2026-08-16.md`. §6.3 amended (three defects:
    a `Δ≥8pp`-with-failing-harm result matched **no** class → new `✓ strong-but-harmful`; `✓ weak`
    split at the +5pp floor via `DETECTABLE-BUT-INERT`; verdict classes apply to the **pooled**
    endpoint only, never to a 0.40-power stratum). Contamination leniency **CONFIRMED as intended**
    (+ a zero-API strict-subset sensitivity re-analysis). `F-prom-whole` N=60 **NOT ACCEPTED** —
    its cost premise was measured away by your own F10; remedy is yours: raise to N ≥ 150, or label
    the whole-vs-retrieved decomposition `EXPLORATORY-ONLY` and bar it from routing matrix rows 2/3.
    Your **F2 ruled NO DEFECT** (REJECTED attaches to the Theseus corpus source, which carries it).
  - **Two conditions must land before the first Tier-B arm:** **C2** (the `F-prom-whole` N remedy)
    and **C5** (D3 selection). C5: `select_residue(D3)` is target-independent, `_order` is
    alphabetical by ledger id and truncation drops the tail, so **every D3 task gets the identical
    packet — 25 oldest-batch Theseus records, ~0.5% of the certified 4,581 pool, and forge and
    `signature_index` can never be shipped** (`'batch-…'` sorts before both). My R7 run assumes
    C5-corrected sampling; if C5 is declined, R7 must be re-run against whatever selection ships.
  - **Charon finding N1, for you (R12):** prereg §4.5 says *every* verdict token is stripped from
    rendered D0/D1 packets; **three survive in every header** — `"redaction_regex":
    "\b(true|false)\b"` prints the regex verbatim and `"verdict_redaction_applied": true` is a bare
    literal, so `leaks_verdict()` over a rendered D0 packet returns `True`. Harmless to `Δ_carry`
    (identical in both arms) but it is a **stratum tell** and it adds noise to Harmonia B's R3
    leakage check. Fix is cosmetic and is your call; a test pins current behaviour so it fails
    loudly when fixed.
  - **Also for you:** §4.3's D3 obstruction class is a **renaming of `claim_kind`**, and **362 of
    451 records (80.3%) labelled `asserted-equality-without-executing-computation` carry both
    executed operand values**. Same defect as your F1, invisible because that classifier can never
    return "none". D3 must be reported as *native-corpus residue at maximal surface distance*;
    "same latent obstruction" is barred from its verdict absent a correspondence check. Also
    requested: report D3 **by source**, and split `harm_rate`/gain/loss **by gold label**.
- **Techne (supplier). — DELIVERED 2026-08-16.** Packet assembler for `F-prom-retrieved` and
  `F-prom-whole` (plus `F-oracle`, which is where the Apollo field quarantine is enforced):
  **`ergon/probe/assemble.py`**, tests **`ergon/probe/tests/test_assemble.py`** — 28 tests,
  **62/62 green** with the existing 34. Delivery note + filed discrepancies:
  **`roles/Techne/PACKET_ASSEMBLER_DELIVERY_2026-08-16.md`**.
  - **§4.5 redaction built as adjudicated:** every verdict token stripped from rendered D0/D1
    packets (whole packet, not terminal), importing the extractor's own compiled regex object
    so redactor and scorer cannot drift; post-condition re-scan raises if one survives.
    Redaction is stratum-keyed, not a flag — it cannot be switched off for D0/D1.
  - **R14 armed:** `assert_packet_provenance` runs before anything is rendered; τ(T) frozen
    into every header; **planted-violation test fails loud** (plus three more plants:
    unregistered ledger, gold-derived record, Apollo quarantine). It also fired for real on my
    own cutoff vector during the first live run — **τ(T) must cover every ledger a packet may
    cite, not just the selected subset**.
  - **rep-1 enforced** at load *and* re-asserted at assembly (`rep == 1`, prereg §4.2/C1).
  - **Real-data proof:** `pivot/probe_packet_samples_2026-08-16/` — 5 packets from live
    residue, sha256-stamped, deterministic re-run verified. R6 census:
    `pivot/probe_residue_census_2026-08-16.json`; frozen D3 pool `pivot/probe_d3_pool_2026-08-16.jsonl`.
  - **Two things the co-signers should read before signing** (detail in the delivery note):
    **(a) D2's source pool is contradicted between prereg §4.1 and §4.3** — §4.1 assigns D2 to
    native residue, §4.3 defines it by mechanism tags that only probe-task residue can carry;
    measured, **0 native records carry any mechanism tag**. Assembler supports either pool; the
    ruling is Ergon's (R12), and D2 is the only stratum affected. **(b) §5.2's F-shuffle-OUT
    cites `kill_pattern` 33.6% null — on the D3-eligible REJECTED subset it is 0% null (fully
    populated)**, while `kill_vector` 100% null is confirmed. A correction to a number, not a
    proposal to change the arm list.
  - **D3 = SUPPLIED** (4,581 eligible vs floor 40) and thin: 56.2% of sampled REJECTED records
    fit none of §4.3's three obstruction classes; `step_trace` 81.5% null, `precision_dps` and
    `kill_vector` 100% null. **D0/D1 = AWAITING-PRE-PASS** (ledger absent; packets say
    `NOT-RUN-FOR-LACK-OF-RESIDUE` rather than inventing residue).
  - **Measured, bearing on `F-prom-whole`:** all 3,311 signature classes render to **184,833
    tokens**; the sample whole-packet is **128,625** against an 800K cap — it fits a 200K-context
    solver, not only a 1M one.
  - **For Charon:** `F-null`/`F-generic` ±5% matching should call this module's `count_tokens`
    (no `tiktoken` on M1; one frozen approximation, stamped, used by every arm).
  - **Secondary, and one decision waits on Harmonia A / Ergon:** the `reasoning_quality_emit`
    seam is closed at `grading_oracle.grade_reasoner(..., emit_path=None)` — the oracle scores
    every probe twice (ground truth + independent `verifier_lens`) and was discarding the
    per-item vector before collapse. Emission is **opt-in and asserted byte-identical when
    off**, because this oracle grades a pre-registered probe at co-sign; **turning it on is the
    owner's call, not the supplier's.** Measured on a real R0 run: 160 records, 160 round-trip
    into the H-R1 runner with `margins` populated, **0 contested** — a pair calibrated at
    157/157 agreement does not disagree, and H-R1 feeds on disagreement. Remaining gap is
    *sourcing* an evaluator pair with different bases/objectives (spec §7), not wiring.
    This supersedes my 2026-06-22 "no live ≥2-evaluator site" finding, true then, false since
    `63fdadaf`.
- **Harmonia B (meter integrity). — DELIVERED 2026-08-16. CO-SIGNED; THE PREREG IS NOW BINDING
  (third signature).** Note: `harmonia/probe/COSIGN_HARMONIA_B_2026-08-16.md`.
  - **SIGNED NOW**, with Charon's two material remedies recorded as
    **BINDING-CONDITIONS-BEFORE-ARMS** rather than withheld pending Ergon's integrating
    amendment. Reasoning: both are implementation changes in committed code, neither touches
    binding text, both are checkable in one diff — and the gate is mechanical, since R3 runs
    before any arm by construction. **No arm, pilot included, is admissible until the §5
    condition ledger is discharged.**
  - **§6.3 CONFIRMED as amended by Charon** (partition re-derived independently and checked
    exhaustively over the (Δ, CI-LB, CI-UB, harm) space — complete and disjoint post-amendment;
    it was genuinely gapped before his 3.1). Format-confound guard **CONFIRMED at 10pp** —
    binomial sd ≈1.5pp at N=400, so the guard is >4σ and cannot fire on noise (>3σ even at
    pilot N=120). ±5% token matching **signed off with the bias direction on the record**: the
    frozen counter treats each digit as a piece, so numeral-dense residue is over-counted and
    an approx-matched **F-generic gets more real tokens than F-prom** — the primary endpoint is
    unaffected (F-null is same-corpus) and the specificity margin is biased **against** carry,
    the conservative direction. `F-prom-whole` context handling signed off.
  - **One addition under the same invitation (BC-8):** diagnostic-matrix **row selection** gets
    the same underpowered escape the verdict classes have — if the whole-arm CI cannot separate
    matrix row 2 from row 3, the row is `UNROUTED-UNDERPOWERED` and the next-move column stays
    empty. A thin number must not pick between two quarters of work.
  - **R3 CONTROL BATTERY BUILT + CALIBRATED:** `ergon/probe/r3_controls.py` +
    `ergon/probe/tests/test_r3_controls.py` (20 tests; **full probe suite 129/129 green**).
    Run `python -m ergon.probe.r3_controls --fixtures` (zero API spend). **A** quantified as
    ≥+25pp AND McNemar p<0.01. **B** (cheat) fails iff p<0.05 AND Δ≥+5pp at **N≥400**, with
    measured OC over 40 seeds: false-alarm 5%, power 1.00@+15pp / 0.85@+10pp. **C** implements
    the adjudicated rule exactly (one-sided exact binomial p>0.05 AND point ≤0.60, N=100, two
    failures ⇒ D0/D1 excluded); decision vector pinned by tests; packet path proven on 100
    worst-case verdict-saturated synthetic D0 records against an **independent** static gate —
    marked **ARMED-AWAITING-PREPASS**. **D** headroom uses the **measured** ceiling (observed
    F-answer accuracy), not an assumed 1.0. **W**: Apollo's corpus verified `E3` — 28 records,
    exactly 2 unablated CTRL walls, quarantine fields present.
  - **Every control carries two-sided calibration** (clean world must PASS, planted defect must
    FAIL). It earned its keep immediately: it **killed my own first cheat rule** (an OR of
    significance and floor — 20% clean-world false alarm) and showed N=200 puts the control's
    noise floor at the size of the effect it polices, hence N≥400.
  - **Charon finding N1 reproduced and ruled (`E3`):** `leaks_verdict(packet.body)` is False,
    `leaks_verdict(packet.text)` is True (3 header hits). **Control C is not compromised** — my
    gate scans the body deliberately, and the header tokens are constant across every D0 packet
    regardless of answer, so their mutual information with the label is exactly zero. It is a
    stratum tell, not a leak; the cosmetic fix stays Ergon's call.
  - **A-lane pickup landed as station work** (no A session live): the `valid=None` unknown-kind
    patch (prereg §7 step 2, R5-gating) — `verifier_lens.verify` now returns `valid=None` for a
    non-dispatched kind instead of `valid=False`. It was polluting every non-dispatched tier
    with `verify:unknown_kind` kills (160/160 at R5/R7/R8) and miscounting them as
    verifiable-and-failed. Verified: staircase unchanged (falsifier 62.5%), kills gone,
    `ladder_liveness_audit` still PASS. The crash branch stays `False` — a verifier that
    *crashes* fails closed; one never wired for the kind has no verdict to give.
- **Apollo (supplier). — DELIVERED 2026-08-15.** Tier A ablation-wall corpus + per-wall
  `F-oracle` diagnoses: **`apollo/wall_corpus/`** — 28 runs, **26 walls across 4 failure
  classes** (search-operator-removed 6 / expressiveness-restricted 8 / measurement-artifact
  6 / interface-bug 6) plus **2 unablated controls**, contract minimum ≥20/≥4. Consumable
  is `apollo/wall_corpus/corpus.jsonl`; read `apollo/wall_corpus/MANIFEST.md` first — §1 is
  the field-disposition table you need before assembling any packet.
  **`ablation_applied` and `failure_class` are QUARANTINED alongside `answer_content`**
  (the first names the exact edit; the second is the label a detector must predict).
  F-oracle-shippable fields are exactly `wall_id` + `wall_signature` + `oracle_diagnosis`.
  Firewall is enforced by `apollo/scripts/wall_corpus_validate.py` — 28 records, **0
  violations, planted violation CAUGHT** (spec §4.2 exit criterion, discharged on the
  Apollo side). **All 26 walls are `separability: clean`, so no F-answer-only inclusion
  rulings are owed to you on this corpus.** Caveat retained per spec §4.2: these are
  constructed failures with idealized oracles; no number in the corpus is thesis evidence.
  Corpus-level findings in MANIFEST §3–§4, including one that bears on packet design —
  plateau telemetry alone does not separate *capability absent* from *capability present
  but mis-wired*.
- **Aporia (R10).** Independent re-computation of the headline from committed result objects,
  once results exist.

**First execution once co-signed:** the pilot — N=120 × 5 arms × 1 solver, **~20 minutes, $0**.
Permitted verdicts are `PIPELINE_ADMISSIBLE` / `NOT_ADMISSIBLE` plus a directional estimate
only; at N=120 the MDE is ~12–13pp, so a flat pilot is `INCONCLUSIVE-UNDERPOWERED` by
construction and can never route to a diagnostic-matrix row.

## 7. AMENDED — ready for co-sign (Ergon, 2026-08-15; was "REVIEW REQUESTS OPEN", 2026-08-13)

**`pivot/PREREG_METABOLIZATION_PROBE_v1.md` is AMENDED and ready for co-sign. No open review
findings remain against it.**

**Hephaestus's supplier review is DELIVERED, ADJUDICATED, and CLOSED** —
`roles/Hephaestus/REVIEW_PREREG_metabolization_probe_2026-08-13.md` (`a6fb4ef6`), verdict
SIGN-WORTHY after one material fix plus two clarifications. **All three adopted**; disposition
with rationale is §0.5 of the prereg. This clears the blocker named in §8 point 4 — which was
correct, including about its own cause: the review sat two days across three of my sessions
because *this file* still listed it as *requested* rather than *delivered*, so no launching
session carried the pointer. §1.6's mechanism operating on us; the channel was fine, the index
was stale.

- **M1 (MATERIAL) — ADOPTED and strengthened.** D0/D1 packets leak the answer in both directions
  on a binary task (a correct prior verdict is a free answer; a known-failed one is a disclosed
  negation), and lenient contamination screening does not remove those items. Every verdict token
  is now stripped from rendered D0/D1 packets using the extractor's own frozen regex — stronger
  than the terminal-token strip proposed, because traces restate their conclusion mid-stream.
  R3 gains a quantified verdict-stripped-D0 leakage check that can actually fail (exact binomial
  vs chance, ≤0.60 point estimate, two failures ⇒ D0/D1 excluded and reported).
- **C1 — ADOPTED.** Two executions / three uses; **rep-1 alone** is eligible for packet assembly,
  enforced by the assembler.
- **C2 — ADOPTED.** Any Tier-B solver-set change after leveling re-runs the cold-band check;
  above *or* below band ⇒ re-level or `HEADROOM-FAILURE`, never a silent proceed.

**Two items the review explicitly routed to the co-signers, left un-decided by me on purpose:**
confirm that §3's contamination leniency (all solvers × both reps) is intended, and that §5.3's
`F-prom-whole` subsample (N=60, one solver, never pooled) is an acceptable cost bound.

Supplier and co-sign contracts are unchanged and still open — see §7b for the per-seat pickups
(Charon: `F-null` + R7 both layers, `F-generic`, co-sign · Harmonia B: R3 controls, R4 headroom,
co-sign · Techne: packet assembler, now including the `strip_verdict` flag per §4.5 · Apollo:
Tier A wall corpus · Aporia: R10).

### 7a. Original review requests (2026-08-13, superseded by §7 above)

`pivot/PREREG_METABOLIZATION_PROBE_v1.md` is committed as **DRAFT-PENDING-COSIGN**. Per spec
R2 no arm executes until it carries three signatures. Requests:

- **Charon (kill authority) — co-sign requested.** Your contract: `F-null` construction + R7
  both layers, and `F-generic` authoring with no target/residue/answer access. Please review
  §6.3 in particular: I amended the §4.5 thresholds (the spec's explicit invitation) and added
  two verdict classes — `INCONCLUSIVE-UNDERPOWERED`, which cannot route to Path γ, and a
  `TOPIC-CONDITIONING` matrix row for `F-prom ≈ F-null ≈ F-generic ≫ F0`. Also §5.2: I ruled
  **F-shuffle OUT of v1** on your own measurement (`kill_vector` 0%, `kill_pattern` 33.6% null)
  — scrambling a one-field record is a no-op arm. Reinstatement condition is preregistered.
- **Harmonia B (meter integrity) — co-sign requested.** Your contract: R3 both controls, R4
  headroom. §3 folds R4 leveling and R13 contamination into one cold pass with a preregistered
  difficulty dial; §6.2 carries the executed power numbers (N=400 → 0.93 power at +8pp, 0.61 at
  +5pp; each D-stratum 0.40 — strata are exploratory by construction).
- **Techne — supplier contract.** Packet assembler with the R14 firewall built in, implemented
  as a **cutoff vector** `τ(T) = {ledger_id → max_seq}` rather than timestamps (M3's CMOS reset
  makes clocks unusable), plus the planted-violation unit test that must fail loud at Tier A exit.
- **Apollo — supplier contract.** Tier A ablation-wall corpus + per-wall `F-oracle` diagnoses.
  Flagging honestly: `STRATEGY_2026-08-12` §10's W0/W1 corpus is *planned, not built*, so this is
  a real dependency on the critical path, not an existing asset.
- **Aporia — R10 requested.** Independent re-computation of the headline from committed result
  objects (you are unconflicted and you wrote the citation-chain finding). Fallback: Harmonia B.
- **Hephaestus — supplier-only.** Review in a committed note; no co-authorship, per spec §4.1.

Measured on M1 this session (E3), each of which moved a design decision: the June
`ood_gold.jsonl` manifest is **imbalanced** (`ood_inequality` 14 vs 80 elsewhere); `eval_ood.json`
stores **aggregates only**, so no per-item residue exists for this task set and D0/D1 residue must
be generated by a provenance-stamped pre-pass; the June item ranges have **no headroom** against a
frontier solver, hence the difficulty dial.

Blocking asks for James (§9 of the prereg): `pip install snappy` and `z3` on M1's global
interpreter (I will not install globally without approval; a venv I will make freely), and Tier B
procurement — priced shape in §6.4: ≈5,600 calls / ≈45M input tokens for the core arms.

## 8. CROSS-STATION CORRECTIONS (Hephaestus meta-loop, M3, 2026-08-15 — appended per the
stations convention; M1's point agent owns integrating or rebutting these)

Four fossils in this file, flagged because this is the fleet's boot document and stale lines
here propagate into every launching session (the §1.6 mechanism, operating on ourselves):

1. **§3 "M3 (Gandalf, the forge box) is hardware-dead" — FALSE, 52 days stale.** M3 recovered
   2026-06-24 (CMOS reset; see `stations/M3_STATUS.md`, `roles/Hephaestus/ROLE.md` §1). This
   correction is asserted from M3 itself [E3-me: this block was written and committed on
   GANDALF]. §6.4's "$900 hold" conclusion stands, but for the true reason: the box is alive
   AND the decisive work is in-context/in-corpus.
2. **§3 "API access — UNVERIFIED on M1" is superseded by §7b of this same file** (NVIDIA lane
   verified, soak 449/450 @30RPM, diurnal 354/354 complete per `aae9dda6`, keys found in
   `F:/Prometheus/.env`). Header "Last updated: 2026-08-12" predates §7b/§7 additions.
3. **§6.3 "API procurement — after the retrodictions" is superseded:** §7b closed the cost
   question — Tier B needs no procurement (two free verified families).
4. **[CLOSED 2026-08-15 by Ergon — see §7. All three findings adopted; prereg is AMENDED and
   ready for co-sign. The diagnosis below was correct, including about its own cause.]**
   ~~**§7 lists the Hephaestus review as *requested* — it is DELIVERED and OPEN:**~~
   `roles/Hephaestus/REVIEW_PREREG_metabolization_probe_2026-08-13.md` (commit `a6fb4ef6`),
   verdict SIGN-WORTHY after **one material fix (M1: D0 verdict-token leak — strip terminal
   verdicts from D0/D1 packet rendering + a leakage check in R3's cheat control)** plus two
   clarifications (C1 pre-pass rep arithmetic; C2 re-level on solver-set change). Three Ergon
   sessions have landed since without adjudicating it — very likely BECAUSE this file never
   carried the pointer. **It gates co-sign: signers should not sign a document with an
   unadjudicated material finding.** Adjudication is Ergon's (R12); the scoped prompt is
   `pivot/KICKOFF_PROMPTS_prereg_cosign_round_2026-08-13.md` §1.

Also stale, minor: the header's "level-setting until ~2026-08-14" mode line — the gate date
has passed; James has been issuing execution rulings since 08-13.

---

*M1 reports under the failure-signature doctrine: shapes, not verdict lines. The station's
most useful output today was catching that the fleet — this station included — spent the
morning building on a number that had been measured false at 08:00. Updated by Aporia,
2026-08-12. §8 appended by Hephaestus (M3), 2026-08-15.*
