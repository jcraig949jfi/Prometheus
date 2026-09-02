# D-8 Session Chronicle — Blind Serendipity Incubator

- **Session date:** 2026-08-28 (single session, build through verdict)
- **Archived:** 2026-09-01 to `F:\Prometheus\SerendipityFoundry\D8\`
- **Working directory during the run:** `F:\SerendipityC\agent_d8\` (full tree
  copied here as `agent_d8/`)
- **Published review page:**
  https://claude.ai/code/artifact/2acd4d72-eb47-4a84-9c65-20226a1cd89d
- **Verdict:** **S0 — NO_EFFECT** (frozen mapping, computed once, untouched)

D-8 was launched as a fresh experimental agent with no knowledge of D-1..D-7:
no prior directories, substrates, or conclusions were read, and none exist in
this archive's provenance. Everything below was built from the D-8 charter
prompt alone.

---

## 1. What the session set out to do

Test whether accumulated executable experience can cause a machine-native
system to construct or preserve a reusable computational object **z** that
materially changes what it can subsequently find under fixed resources — with
z's form, human category, and mechanism unspecified in advance. The experiment
had to be preregistered, adversarial, deterministic, instrument-first, hostile
to assay breeding, and honest about failure. The deliverable was not a
specimen but a credible selection environment; a null was a legitimate result.

## 2. What was built (all in `agent_d8/`)

| Component | File | Summary |
|---|---|---|
| Substrate | `svm.py` | SVM-8: deterministic, total, straight-line stack VM; 8-bit wraparound; 26 opcodes + literals; max 12 tokens; lossy stack overflow, pop-empty-yields-0, scratch register. Unsanitized physics. sha256-keyed named RNGs everywhere. |
| Tasks | `tasks.py` | Six families behind a blind interface (learner sees uid + six I/O byte pairs only). F1/F3 op-soups, F2 secret shared-motif compositions, F4 held-out compiled affine/xor (eval only), F5 structureless SHA world, F6 misleading disjoint-pool world. Degeneracy filter + 250-probe triviality screen. Boolean-only verifier over 24 hidden pairs. |
| Learner side | `engine.py` | Metered Ctx (budget 10,000 evals/task/arm; bit-agreement fitness 0..48; exact solve unchanged); M0a random / M0b restart hill-climber / M0c GA; M1 = same GA physics + hoard-derived proposal distribution (bigram stats, weighted segment splice, donor retrieval paid from the same budget, promoted macro tokens); hoard with frozen admission predicates and behavior-dedup; H-BAG / H-SHUFFLE / H-RANDOM / component and per-z ablation variants. |
| Orchestrator | `experiment.py` | Subcommands: smoke, calibrate, validate (V1–V8, fail-closed), freeze (sha256 manifest), dev, hrnd, evalrun, ablz, stats (frozen statistics + verdict mapping). |
| Protocol | `PREREG.md` | Full preregistration: question, ladder S0–S5, admission criteria A–I operationalized, endpoints, McNemar/bootstrap/Holm statistics, retention thresholds (0.7), verdict mapping, anti-tautology audit with disclosed design biases, stop conditions. Hashed at freeze. |
| Engineering log | `LOG.md` | Every calibration round, every instrument failure, every pre-freeze fix, with rationale. |
| Packet | `REPORT.md` | The 23-item external review packet (markdown master). |

## 3. Session timeline (compressed from `LOG.md`)

1. **Build + smoke test.** Substrate, families, arms, orchestrator written;
   smoke run OK.
2. **CAL1** — battery too easy (M0 primary-rate 0.73 vs declared band
   [0.15, 0.60]); F4 unfindable. *Fixes:* generator lengths 7–12; oracle-side
   triviality screen; easier F4 templates.
3. **CAL2/CAL3** — in band, but an F4 probe showed byte-exact match-count
   fitness gives search almost no gradient (M0 weaker than the charter
   demands). *Fixes (all arms identically, declared pre-freeze):* bit-level
   partial-credit fitness; literal-local ±1..8 mutation.
4. **CAL4 + budget test** — F4 findable at 20k evals but not 3k. *Fix:*
   global budget 3,000 → 10,000.
5. **CAL5/CAL6 (frozen config)** — pooled F1–F3 rates: M0a 0.20, M0b 0.40,
   M0c 0.30 → **primary comparator M0b** by the preregistered rule.
6. **Instrument validation, four generations, failures preserved:**
   - Gen 1 (`validation_1787897167`): 7/8 — V8 sensitivity FAILED (budget
     mismatch).
   - Gen 2 (`validation_1787897224`): 6/8 — V8 failed harder (ceiling: M0c
     solved 0.92 of the planted battery; motif was dead code); V3 float-edge.
   - Fixes: planted battery gets screen + load-bearing check (motif deletion
     must change ≥12/24 hidden outputs) + regime-targeted motif selection;
     V2/V3 one-sided.
   - Gen 3 (`validation_1787897332`): 8/8 but pre-dated a final
     hoard-admission widening (richer hoard: bit-fitness ≥40/48 admitted at
     weight 1) — did not certify frozen code.
   - **Gen 4 (`validation_1787897401`): 8/8 under the exact frozen code.**
     V8: planted-object gain 1.00, ablation loss 1.00.
7. **FREEZE** (`frozen/MANIFEST.json`) — sha256 of svm.py, tasks.py,
   engine.py, experiment.py, PREREG.md; CFG dump; `m0_primary=M0b`.
8. **Binding, run once:** dev (27/60 solved; hoard 1,034 records; 8 macros
   promoted) → hrnd → 20 eval arms on the 96-task EV battery → per-z
   ablations → stats.
9. **Verdict: S0.** No post-freeze modification of anything.
10. **Post-hoc (after verdict freeze only):** z3 fossil analysis, z2
    usage-without-consequence, memorization-flag audit, cost descriptives.
11. **Packet assembled:** `REPORT.md`, published artifact page, ASCII packet
    (archived here as `REVIEW_PACKET.txt`).

## 4. Headline results

- **Primary:** M1F 0.483 vs M0b 0.383 on 60 paired F1–F3 eval tasks.
  Δ = +0.100, bootstrap 95% CI [−0.033, +0.233], discordant 11/5, exact
  McNemar p = 0.210 → gate G1 fails → **S0**.
- **Decisive tell:** H-RANDOM (identical machinery filled with *random*
  programs) retains ~83% of the small edge; ablating the learned bigram
  statistics costs nothing (ABLBIG retention 1.0). The proposal-diversity
  scaffolding does the work; developmental *content* added nothing detectable.
  Even had G1 passed, H-RANDOM ≥ 0.7 retention would have capped the verdict
  at S1.
- **z-candidates:** 8 promoted, 8 tested, **0 admitted** (max ablation effect
  +0.05; all Holm p = 1.0).
- **Controls behaved:** F5 structureless 0.00 in every arm; zero budget
  violations; memorization checker caught 3 byte-identical replays; F6 showed
  no detectable misleading-history harm or benefit; F4 held-out was vacuous
  (0.00 everywhere — weak-baseline caveat declared in PREREG before binding).

## 5. Findings worth keeping (post-hoc, not evidence)

- **z3 is a genuine machine-native fossil.** `LD0 #127 INC NEG MULHI NOT`
  computes exactly `NOT(x0 >> 1)` by exploiting the 8-bit two's-complement
  fixed point (INC(127)=128; NEG(128)=128; MULHI(x,128) = x>>1). Development
  really did construct a noncanonical, overflow-exploiting shift encoding —
  and it was behaviorally inert in evaluation. Preserved uncleaned in
  `agent_d8/frozen/machinery.json`.
- **z2 demonstrates usage-without-consequence.** `OVER NOT LD1` appears inside
  8 novel eval solutions across four families, yet its ablation changes
  nothing — the search routes around it. The behavioral admission criteria
  refused exactly the object a human reading the solutions would have
  celebrated. This is the instrument working as designed.

## 6. Strongest statement earned / not earned

**Earned:** under a validated-sensitive instrument, equal metered budgets, and
a strong history-free comparator, sixty tasks of accumulated executable
experience produced no statistically distinguishable improvement in exact
acquisition, and the small numeric edge is largely reproduced by identical
machinery filled with random programs.

**Not earned (explicitly refused):** "underpowered but real"; "live history
beats frozen" (0.533 vs 0.483, n.s.); "history halves solve cost"
(selection-biased); "z2 is a reusable building block"; "the ecology contains
no discoverable reusable structure" (V8 proves detectability when structure is
present); any S1+ claim.

## 7. Known weaknesses (disclosed in the packet, never repaired post-freeze)

Underpowered near Δ = 0.10 at n = 60 (retention CIs flagged inside-noise);
H-RANDOM record count (298 post-dedup) unmatched to M1's 1,034; F4 vacuous;
fragment-biased constructor (preregistered S4/S5 ceiling); single replicate
per arm-task; comparator chosen on noisy calibration; screen correlates the
battery with random-search failure; F2/F6 behavioral collision found post-hoc.

## 8. Archive inventory

```
D8/
  SESSION.md              this chronicle
  REVIEW_PACKET.txt       self-contained ASCII packet for external reviewers
  agent_d8/               full experiment tree (copied verbatim)
    svm.py tasks.py engine.py experiment.py     frozen code (hashes below)
    PREREG.md             preregistration (hashed at freeze)
    LOG.md                engineering log incl. all failures
    REPORT.md             23-item review packet (markdown master)
    frozen/MANIFEST.json  freeze record: hashes, CFG, m0_primary, timestamp
    frozen/machinery.json          M1 hoard + dev solutions + z bytes
    frozen/machinery_hrnd.json     H-RANDOM hoard
    ledgers/cal_*.jsonl            calibration runs (CAL1–CAL6)
    ledgers/validation_*.json      all 4 validation generations (2 failed)
    ledgers/dev.jsonl              binding dev phase, per-task rows
    ledgers/eval_*.jsonl           per-arm eval rows (solutions, meters)
    ledgers/meters_*.json          per-arm aggregate meters
    results/RESULTS.json           gates, margins, CIs, verdict
    results/dev_summary.json       z provenance
    results/resource_ledger.json   consolidated cost accounting
```

Frozen sha256 (authoritative copy in `agent_d8/frozen/MANIFEST.json`):

```
svm.py        7b345a347aebf5937782cb0d4eed46832eadba0a77282ae253c4da1f6f570afe
tasks.py      405efc8666b8c5d45a03d501180c3ed7468ebcb2263cfb615ab425fd786d9a36
engine.py     5298d70480939a098695bcdc919702b86be1f96e3751d201b2ceb087d89a1a74
experiment.py c25a5b1069fbe6e1d924dadc49c4107b335452ab3bc6243edf8de56d22308003
PREREG.md     efcbffcc47915862b98977b4f0f32bca65c76af5ce981798ac2ce3745b261c0c
```

## 9. Reproduction

Windows, CPython 3.x, stdlib only, fully deterministic. From `agent_d8/`:

```
python experiment.py validate
python experiment.py freeze M0b
python experiment.py dev
python experiment.py hrnd
python experiment.py evalrun M0a,M0b,M0c
python experiment.py evalrun M1F,HBAG,HSHUF
python experiment.py evalrun HRND,ABLMAC,ABLRET,ABLBIG
python experiment.py evalrun M1L
python experiment.py ablz
python experiment.py stats
```

Verify file hashes first; any byte drift invalidates the generation. Every
number in the packet is recomputable from the ledgers without re-running
search.
