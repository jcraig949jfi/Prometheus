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
