# D-8 EXTERNAL REVIEW PACKET — Blind Serendipity Incubator

Generation: agent_d8, frozen 2026-08-28, binding complete same day.
Raw machine-readable ledgers accompany this packet: `ledgers/*.jsonl`,
`ledgers/validation_*.json`, `results/*.json`, `frozen/MANIFEST.json`,
`frozen/machinery.json`, `frozen/machinery_hrnd.json`. Code: `svm.py`,
`tasks.py`, `engine.py`, `experiment.py`. Protocol: `PREREG.md`.
Engineering history: `LOG.md`.

## VERDICT (frozen mapping, no post-hoc adjustment)

**S0 — NO_EFFECT.**

Accumulated executable history, as constructed by this generation's
machinery, did not produce a statistically distinguishable improvement in
exact task acquisition over the strongest history-free baseline under equal
metered resources. No candidate reusable object was admitted. The
instrument was validated sensitive before freeze (a planted genuinely
useful object produces gain 1.00 / ablation loss 1.00), so this null is an
informative property of the ecology + learner, not of a blind instrument.

---

## 1. Exact question

Can accumulated executable experience cause a machine-native system to
construct or preserve a reusable computational object z that materially
changes what it can subsequently find under fixed resources, when z's
form, human category, relevance coordinates, and mechanism of benefit are
not specified in advance?

## 2. Claim / verdict ladder

S0 no effect; S1 history-content effect; S2 relational-organization
effect; S3 new reusable machine object (behavioral admission criteria
A–I); S4 endogenous machine coordination; S5 unanticipated mechanism.
Full frozen operationalization: PREREG.md §8–§10. Preregistered design
ceiling: S3 realistically attainable; S4/S5 declared unlikely because the
constructor's physics biases z toward contiguous code fragments and
proposal-statistics objects (PREREG §11).

## 3. Substrate

SVM-8: deterministic, total, straight-line stack VM; 8-bit wraparound
values; stack cap 12 with lossy bottom-discard on overflow;
pop-on-empty-yields-0; scratch register; 26 opcodes + literal tokens; max
12 tokens; cost = tokens executed. Wraparound, dead code, destructive
moves, pathological arithmetic are legal physics, never sanitized.
Everything is exactly replayable from (arm, uid)-derived sha256 seeds.

## 4. Task generation

Six families; generators quarantined oracle-side (tasks.py header).
F1/F3 op-soups (len 7–12, arithmetic-biased / bit-logic-biased);
F2 motif-composed from a secret pool of 12 shared motifs (planted
reusable structure, hidden from the learner); F4 held-out compiled
affine/xor templates (eval only, materially different mechanism);
F5 structureless SHA outputs (no generator exists); F6 F2-shaped from a
disjoint motif pool (misleading history control, eval only).
Filters: >= 4 distinct hidden outputs; a 250-candidate uid-seeded random
probe must NOT reproduce the revealed outputs (triviality screen).
Batteries: DEV 60 (F1/F2/F3 x20), EV 96 (F1/F2/F3 x20 + F4 x16 + F5 x8 +
F6 x12); CAL/VAL prefixes are disjoint seed blocks used only pre-freeze.

## 5. Machine-visible task interface

uid + six (x0,x1,x2)->y byte pairs. Nothing else. Verifier: boolean only
(24 hidden pairs), 50 submissions/task/arm cap, metered.

## 6. History representation

Hoard of executable records: (program bytes, weight, behavior on 8 fixed
probe inputs). Frozen admission: verified solution (w=6), >=5/6 revealed
byte matches (w=5), bit-fitness >= 40/48 (w=1); dedup by probe behavior;
cap 3000 FIFO. From the hoard, deterministically rebuilt organization:
bigram token-class statistics, length/literal distributions, weighted
segment table (len 2–5, top 300), and a promoted-object registry
(contiguous segments len 3–6 occurring in verified dev solutions of >=2
distinct tasks; top 8). Promoted segments become macro tokens; expansion
still obeys the 12-token cap (search restructuring, not expressiveness).

## 7. M0 suite

M0a uniform random search; M0b restart hill-climber; M0c generational GA
— identical budget (10000 candidate evaluations/task), fitness (bit
agreement 0..48; solve stays fully exact), verifier access, and mutation
operators (incl. literal-local ±1..8). Frozen comparator rule: highest
pooled F1–F3 solve rate on calibration under the frozen config
(CAL5+CAL6, n=60): M0a 0.20, M0b 0.40, M0c 0.30 → **primary = M0b**.
Conservative note: M1 is GA-based, so the primary comparison runs against
a different, stronger baseline; M1F vs M0c is reported as decomposition.

## 8. M1 mechanism

Same GA physics; only the proposal distribution differs: donor retrieval
(200 stored programs executed on the new task's revealed inputs AT BUDGET
COST, top 10 seed the population), bigram-sampled fresh candidates,
weighted segment splice (30% of mutations), macro-token insertion (15%).
Dev phase: 60 DEV tasks sequentially, hoard live; promotion at dev end;
machinery frozen to frozen/machinery.json. Primary eval arm M1F uses the
frozen machinery (H-FROZEN built in); M1L (live) is secondary.

## 9. Controls and counterfactuals

H-BAG (same records, organization destroyed), H-SHUFFLE (same mass and
marginals, stored wiring permuted), H-RANDOM (full machinery from a
generation-count-matched random hoard), ABLMAC/ABLRET/ABLBIG (component
ablations), ABLZ0..7 (per-object ablations, EV F1–F4), M0a/b/c.

## 10. Instrument validation history (failures preserved)

- Gen 1 (validation_1787897167.json, budget 2000): 7/8 — V8 sensitivity
  FAILED (gain 0.08). Preserved.
- Gen 2 (validation_1787897224.json, binding budget): 6/8 — V8 FAILED
  harder (gain 0.00; ceiling: M0c solved 0.92 of the planted battery, and
  the hand-picked motif was mostly dead code); V3 tripped a float boundary
  with NEGATIVE d (not the guarded failure mode). Preserved.
- Fixes (pre-freeze, logged): planted battery gets the triviality screen +
  a load-bearing check (motif deletion changes >=12/24 hidden outputs) +
  motif selection into the detectable regime; V2/V3 made one-sided.
- Gen 3 (validation_1787897332.json): 8/8 — but ran before a final
  hoard-admission widening, so it does not certify the frozen code.
- Gen 4 (validation_1787897401.json): **8/8 under the exact frozen code**:
  V1 artifact reuse d=0.60 with bag retention 1.00 (attributed to
  possession); V2 −0.10; V3 −0.15; V4 memorization flagged; V5 useless
  object rejected; V6 budget cheat flagged; V7 structureless zero;
  V8 m0c=0.00, gain=1.00, ablation loss=1.00.

## 11. Freeze timeline and hashes

Calibration and validation used only CAL*/VAL* uid blocks. Freeze
2026-08-28 (frozen/MANIFEST.json), sha256:
- svm.py 7b345a347aebf5937782cb0d4eed46832eadba0a77282ae253c4da1f6f570afe
- tasks.py 405efc8666b8c5d45a03d501180c3ed7468ebcb2263cfb615ab425fd786d9a36
- engine.py 5298d70480939a098695bcdc919702b86be1f96e3751d201b2ceb087d89a1a74
- experiment.py c25a5b1069fbe6e1d924dadc49c4107b335452ab3bc6243edf8de56d22308003
- PREREG.md efcbffcc47915862b98977b4f0f32bca65c76af5ce981798ac2ce3745b261c0c
Binding order after freeze: dev → hrnd → eval arms → ablz → stats.
Nothing was modified after freeze.

## 12. Resource ledger (results/resource_ledger.json)

Development (binding, one-off): 382,613 candidate evals (19.8M VM steps),
127 verifier calls, history construction 31,488 probe evals (2.26M VM
steps), organization construction 217,118 ops. H-RANDOM hoard build:
3,000 probe evals, 2,080 build ops (records after dedup: 298 vs M1's
1,034 — disclosed weakness, see §20). Eval phase per arm ≈ 0.67–0.76M
candidate evals; retrieval executions (~19k/arm) were paid from the same
per-task budgets. No arm exceeded the declared budget (checked row-wise).

## 13. Binding results

Solve rates (EV battery; "primary" = 60 F1–F3 tasks):

| arm    | F1  | F2  | F3  | F4  | F5  | F6  | primary |
|--------|-----|-----|-----|-----|-----|-----|---------|
| M0a    | .30 | .15 | .30 | .00 | .00 | .25 | .250 |
| M0b(P) | .40 | .35 | .40 | .00 | .00 | .33 | .383 |
| M0c    | .45 | .25 | .45 | .00 | .00 | .33 | .383 |
| M1F    | .45 | .40 | .60 | .00 | .00 | .42 | .483 |
| M1L    | .55 | .50 | .55 | .00 | .00 | .50 | .533 |
| HBAG   | .50 | .35 | .50 | .00 | .00 | .33 | .450 |
| HSHUF  | .50 | .35 | .50 | .00 | .00 | .42 | .450 |
| HRND   | .35 | .50 | .55 | .00 | .00 | .42 | .467 |
| ABLMAC | .35 | .45 | .50 | .00 | .00 | .50 | .433 |
| ABLRET | .35 | .35 | .55 | .00 | .00 | .33 | .417 |
| ABLBIG | .40 | .40 | .65 | .00 | .00 | .42 | .483 |

## 14. Gates and margins

- PRIMARY G1: Δ = +0.100 (M1F .483 vs M0b .383), bootstrap 95% CI
  [−0.033, +0.233], exact McNemar discordant 11/5, p = 0.210 → **FAIL**
  (needs p < 0.05 and Δ > 0). Verdict fixed at S0 here.
- Retention points (CIs are extremely wide; all flagged inside-noise):
  H-BAG 0.67 [−1.0, 3.0]; H-SHUFFLE 0.67 [−1.0, 2.5]; H-RANDOM 0.83
  [−0.67, 3.67]; ABLBIG 1.00; ABLRET 0.33; ABLMAC 0.50; M1L 1.50.
  Had G1 passed, H-RANDOM retention 0.83 ≥ 0.7 would still have capped
  the verdict at S1 (content/generic effect, not organization).
- G2, G3: fail (dependent on G1; also no z admitted).
- Budget violations: none.

## 15. z objects (original frozen bytes; results/dev_summary.json)

8 promoted, 8 tested, **0 admitted** (Holm-corrected ablation p = 1.0 or
0.55–0.73 raw; max ablation delta +0.05):

| z | tokens (disasm) | dev tasks | abl Δ | p_holm | used in novel EV solutions |
|---|-----------------|-----------|-------|--------|----------------------------|
| z0 | OVER NOT LD1 INC | 3 | +.000 | 1.0 | 1 |
| z1 | NOT LD1 INC | 3 | +.033 | 1.0 | 2 |
| z2 | OVER NOT LD1 | 3 | +.000 | 1.0 | **8** |
| z3 | LD0 #127 INC NEG MULHI NOT | 2 | +.000 | 1.0 | 0 |
| z4 | LD1 LD1 ADD OVER NOT LD1 | 2 | −.017 | 1.0 | 3 |
| z5 | LD1 ADD OVER NOT LD1 INC | 2 | +.017 | 1.0 | 1 |
| z6 | LD1 INC ADD LD0 LD1 ADD | 2 | +.000 | 1.0 | 1 |
| z7 | LD1 DUP SHL LT LD0 #127 | 2 | +.050 | 1.0 | 3 |

Original bytes preserved uncleaned in frozen/machinery.json +
results/dev_summary.json.

## 16. Ablations

Component ablations of M1F cost nothing distinguishable (ABLBIG retention
1.0 — the learned bigram statistics carried no measurable load; ABLRET
0.33 point estimate hints retrieval-seeding carried the most, p = 0.29,
not significant). Per-z ablations: table above.

## 17. Transfer

- BYTE TRANSFER: not applicable (no z admitted). For completeness, per-z
  ablation on F4: all zero except ABLZ1 showing +1 F4 solve WITHOUT z1 —
  noise-level and direction-inverted.
- MECHANISM TRANSFER: F4 held-out solve rate 0.00 in every arm (M0 and
  M1); vacuous — the weak-baseline caveat declared in PREREG §3 applies.
- Verdict: NO TRANSFER DEMONSTRATED, and no transfer claim is made.

## 18. Hard negatives

- F5 structureless: 0.00 in all 20 arms (as required).
- F6 misleading pool: M1F .42 vs M0b .33 (discordant 2/1, p = 1.0) — no
  detectable harm OR benefit from misleading history; the anticipated
  negative-transfer signature did not materialize (preserved as-is).
- Fossils preserved: z3 (never used, zero effect), the entire unadmitted
  registry, and the 1787897167/1787897224 failed validation generations.

## 19. Post-hoc interpretation (NOT admission evidence)

Performed only after the verdict froze:
- z3 = `LD0 #127 INC NEG MULHI NOT` computes exactly NOT(x0 >> 1) by a
  wraparound pathology: INC(#127)=128, NEG(128)=128 (the two's-complement
  fixed point), MULHI(x,128)=x>>1. Development did construct a
  machine-native, noncanonical encoding that exploits 8-bit overflow —
  and it was behaviorally inert in evaluation. A genuine fossil.
- z2 = `OVER NOT LD1` appears inside 8 novel eval solutions across F1, F2,
  F3, F6 — yet ablating it costs nothing: the searcher routes around it.
  Usage is not consequence; the admission criteria correctly refused it.
- 3 eval solutions were byte-identical to dev solutions (EV-F1-09,
  EV-F3-12, EV-F6-03 — the last shows F2's pool-A and F6's pool-B tasks
  can collide behaviorally). The novelty checker caught all three; they
  were excluded from reuse evidence.
- Median first-solve cost on the 18 jointly solved primary tasks:
  M1F 344 evals vs M0b 661. Descriptive only: conditioned on joint
  solving, no preregistered gate, selection-biased.
- Why the null, mechanically? The strongest hint is H-RANDOM ≈ M1F: most
  of M1F's small numeric edge is reproduced by the same machinery filled
  with random programs. The proposal-diversity scaffolding (seeding +
  splicing anything at all) does the work; the developmental CONTENT adds
  nothing detectable at this scale. OTHER_UNKNOWN remains possible.

## 20. Known weaknesses

1. Power: with n=60 primary tasks and a true Δ near 0.10, the primary
   test was underpowered (post-hoc: detecting 0.10 at 80% power needs
   roughly 3–4x more discordance). Retention CIs are so wide that S1 vs
   S2 could not have been distinguished either — flagged inside-noise.
2. H-RANDOM record count (298 after dedup) is not matched to M1's 1,034;
   generation count was matched instead. Frozen before this was noticed;
   reported, not repaired.
3. F4 held-out family vacuous (0 everywhere) — transfer untestable.
4. Single search replicate per (arm, task); between-stream variance is
   folded into the paired test rather than averaged out.
5. The triviality screen correlates the battery with random-search
   failure modes (declared pre-freeze).
6. The M1 constructor is fragment-biased (PREREG §11): forms of z outside
   contiguous-fragment/statistics space were reachable only implicitly.
7. M0 primary was itself selected on a noisy n=60 calibration.
8. F2/F6 behavioral collision (EV-F6-03) means the misleading control is
   less adversarial than designed.

## 21. Strongest statement actually earned

Under this frozen ecology — a validated-sensitive instrument, equal
metered budgets, and a strong history-free comparator — sixty tasks of
accumulated executable experience produced NO statistically
distinguishable improvement in exact acquisition (Δ = +0.10, p = 0.21),
and the small numeric edge that did appear is largely reproduced by
identical machinery filled with random programs. Development did
construct machine-native objects (including a wraparound-exploiting
shift encoding), and the admission instrument correctly refused all of
them on behavioral grounds, including one reused in 8 novel solutions.

## 22. Tempting stronger statements NOT earned

- "M1 helps but the experiment was underpowered" — not earned; the CI
  includes zero and negative effects.
- "M1L (live history) is better than frozen history" — numerically 0.533
  vs 0.483; not significant; not earned.
- "History halves the cost of solving" — the 344-vs-661 median is
  selection-biased descriptive data; not earned.
- "z2 is a reusable building block" — it was reused, but ablation shows
  zero consequence; explicitly refused.
- "The ecology contains no discoverable reusable structure" — not earned
  either: V8 proved a useful object is detectable when present; the null
  is about what THIS learner constructed from THIS history.
- Any S1+ claim of any kind.

## 23. Reproduction

Windows, CPython 3.x, stdlib only. All randomness flows through
sha256-keyed named RNGs; no wall-clock, no filesystem order, no global
random state. From `agent_d8/`:
```
python experiment.py validate     # instrument suite (VAL seeds)
python experiment.py freeze M0b   # writes frozen/MANIFEST.json
python experiment.py dev          # binding dev phase (DEV seeds)
python experiment.py hrnd
python experiment.py evalrun M0a,M0b,M0c
python experiment.py evalrun M1F,HBAG,HSHUF
python experiment.py evalrun HRND,ABLMAC,ABLRET,ABLBIG
python experiment.py evalrun M1L
python experiment.py ablz
python experiment.py stats        # -> results/RESULTS.json, verdict
```
Verify file hashes against §11 first; any byte drift invalidates the
generation. Every number in this packet is recomputable from the ledgers
without re-running search.
