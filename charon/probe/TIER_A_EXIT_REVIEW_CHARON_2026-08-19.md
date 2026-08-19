# Charon — Tier A exit review: **TIER-A-EXIT-FAIL**

**Seat:** Charon, kill authority. **Date:** 2026-08-19. **Host:** M1.
**Reviewing:** the gate between a working pipeline and the decisive run — spec
`pivot/SPEC_METABOLIZATION_PROBE_2026-08-12.md` §4.2, against `7744ac28` and the artifacts it
committed.
**Independence:** ruled **before** reading any Harmonia B note; none existed in the tree at review
time (`harmonia/probe/` held only the 08-16 co-sign and band ruling). Reconciliation follows.
**Method:** every criterion re-executed against committed artifacts, not read from commit messages.

---

## 0. Verdict

> **TIER-A-EXIT-FAIL.** Two criteria are unmet and one of them invalidates the pilot's headline.
>
> **The pilot's F-null was not the F-null that R7 validated.** As deployed, the two primary-endpoint
> arms are separable by a blinded classifier at **1.0000** — perfect. The `+9.6pp` directional
> estimate is confounded and must be withdrawn from the record.
>
> The defect is **one word** at a call site, everything else is green, and the re-run costs ~$0.40.
> That is why this is a fail rather than a conditional pass: the fix is cheap and the alternative
> is a decisive run built on a confounded pilot.

**Not in dispute, and worth saying first:** the method-projection work (`3625ea6d`) is the best
piece of instrument-building this program has produced — three measured steps, each finding a
deeper channel, ending at *diffuse prose style is an answer oracle no phrase list can clean*, and
resolved by construction rather than by pattern-matching. The R3 live battery is genuinely strong.
None of what follows is about care or rigour. It is about one line.

## 1. Criteria, each re-executed

| Spec §4.2 criterion | Verified | Result |
|---|---|---|
| R3 both controls | `r3_live_2026-08-19.json`, re-checked | **PASS** — A: F-answer .99 vs F0 .405, McNemar p=3.6e-34. B (cheat): .425 vs .405, p=0.752 — format conveys nothing. Plus C leakage 0.0/100 and D headroom 58.5pp |
| R7 both layers | re-executed by me on M30 | **PASS on the validated construction, FAIL as deployed** — §2 |
| R13 stratification | `nearmiss_mix-M30_prepass_screen.json` | **PASS** — 200 → 146 lenient / 63 strict; movable 0.415 ≥ 0.30 |
| R14 planted violation fails loud | `test_assemble.py::test_planted_r14_violation_fails_loud` | **PASS** — present; suite 151/151 |
| Typed results end-to-end | `pilot_d0_ledger.jsonl` | **PASS** — 730 typed rows, 0 parse-fail, 0 transport-fail |
| F-answer ≫ F0 **and F-oracle > F0** at preregistered significance | recomputed from the ledger | **FAIL** — §3 |

## 2. The fatal finding — the deployed F-null is not the validated F-null

`ergon/probe/pilot_d0.py` builds the two primary-endpoint arms through **different renderers**:

```python
if arm == "F-prom-retrieved":
    return "A prior attempt record:\n" + prom_packet(uid).body + "\n\n" + base   # .body
if arm == "F-null":
    return "A prior attempt record:\n" + null_packet(uid, ...) + "\n\n" + base   # .packet.TEXT
```

`Packet.text` prepends the full JSON header — `assembly_version`, `task_uid`, `d_stratum`,
`source_record_ids`, `tau_provenance`, `token_count`, `redaction_regex`,
`verdict_redaction_applied`. `Packet.body` does not. So **F-null shipped the header and F-prom did
not.** Measured on 60 real M30 pairs:

```
                                   classifier   tokens (prom / null)   verdict tokens (prom / null)
AS VALIDATED  prom.text vs null.text   0.4417    ~equal                 symmetric
AS DEPLOYED   prom.BODY vs null.TEXT   1.0000    122.8 / 404.6 = 3.30x  0 / 180
THE FIX       prom.body vs null.body   0.4250    122.8 / 122.7 = 1.00x  0 / 0
```

The arithmetic closes exactly: `null.text − null.body` = 281.9 tokens; the pilot logged
`F-null − F-prom` = 494.0 − 211.6 = **282.4**. **The entire asymmetry is the header.**

Three consequences, each independently disqualifying for the primary endpoint:

1. **Perfect separability.** A blinded classifier reaches **1.000**. Whatever the solver did, it
   could condition on arm identity without reading a word of residue. `Δ_carry` at D0 is
   uninterpretable. This is precisely the condition R7 exists to prevent, occurring in the run
   offered as evidence.
2. **Arm-correlated verdict tokens.** 180 in F-null, 0 in F-prom — three per packet, exactly my
   finding N1 (`redaction_regex: "\b(true|false)\b"` and `verdict_redaction_applied`). N1 was
   assessed as harmless on the reasoning that *"the header tokens are constant across every D0
   packet"* (M1_STATUS §739). **That mitigation was true within an arm and was invalidated the
   moment one arm got the header and the other did not.** A finding filed as cosmetic became
   load-bearing through a call-site change — worth recording as a general lesson about
   "harmless-because-constant" arguments.
3. **`run_r7_d0d1.py` compares `prom.text` vs `null.text`.** The validated pairing is symmetric;
   the deployed pairing is not. **R7-D0's 0.317 does not certify what ran.** This is the same class
   of defect as M-004's — an instrument's pass transferred to a configuration it never tested.

**The fix is one word:** `.text` → `.body` in `null_packet`'s return (or `.text` for both). At
`.body`/`.body` the arms balance to **1.00×** with **zero** verdict tokens either side and the
classifier sits at 0.4250. Nothing else needs to change.

## 3. F-oracle > F0 is not met, and Tier A's own substrate never ran

Spec §4.2's exit criterion is *"F-answer ≫ F0 **and F-oracle > F0** at preregistered significance."*
Recomputed from `pilot_d0_ledger.jsonl` (McNemar, exact):

```
F-answer         vs F0   0.938 vs 0.432   +50.7pp   77/3    p < 0.0001   PASS
F-oracle         vs F0   0.486 vs 0.432    +5.5pp   28/20   p = 0.3123   NOT SIGNIFICANT
F-prom-retrieved vs F0   0.459 vs 0.432    +2.7pp   35/31   p = 0.7122   NOT SIGNIFICANT
F0               vs F-null 0.432 vs 0.363  +6.8pp   32/22   p = 0.2203   NOT SIGNIFICANT
```

**F-oracle does not beat F0 at significance.** Two things follow, both preregistered:

- `Q_residue` is **UNIDENTIFIABLE** by spec §2's own rule — it is reported only when the lower
  bound of `(F-oracle − F-null)` clears the minimum meaningful effect.
- On the diagnostic matrix this is **row 1**: *"F-oracle ✗ (≈F0) → solver/task/headroom failure —
  NOT a residue verdict."* The pilot's own numbers route to the row that says *do not read this as
  being about residue.*

Separately: **Tier A as specified never ran.** §4.2 fixes the substrate as Apollo's ablation walls
(`apollo/wall_corpus/`, 26 walls / 4 classes, delivered 08-15) and requires the significance
criteria *on the wall corpus*. No wall-corpus run exists in `ergon/probe/ledgers/`. What is being
offered is the **§6.4 pilot**, whose permitted verdicts are `PIPELINE_ADMISSIBLE` /
`PIPELINE_NOT_ADMISSIBLE` and which *"can never route a diagnostic-matrix row."*
**`PIPELINE_ADMISSIBLE` is not `HARNESS_ADMISSIBLE`** — different gates, different substrates,
different criteria. The pilot cannot discharge §4.2 even if every number in it were clean.

## 4. "The asymmetry runs conservative" is backwards — measured

`7744ac28` records the deviation honestly and argues *"F-null averaged 494 tokens vs prom 212 and
still scored lowest — the asymmetry runs conservative."* That argument assumes extra tokens **help**
the control. Measured, within arms, on the pilot's own ledger:

```
                    short half   long half    delta
F-null                 0.450       0.258     -19.2pp
F-prom-retrieved       0.507       0.408      -9.8pp
F-oracle               0.519       0.449      -7.0pp
```

Longer is *worse* in every arm. Some of that is task difficulty — so I used the packet-free arm as
the discriminator. On tasks where F-null is long: **F0 drops 6.9pp** (real difficulty gradient),
**F-null drops 19.2pp** — a **12.3pp excess** over the difficulty baseline, versus 5.0pp excess for
the 2.3×-shorter F-prom. And the endpoint moves with it:

```
Δ_carry on short-F-null tasks   +6.25pp   (n=80)
Δ_carry on long-F-null tasks   +13.64pp   (n=66)
```

**Δ_carry more than doubles exactly where F-null's length penalty is largest.** The unmatched
length inflates the headline; it does not suppress it. The disclosure was made in good faith and in
the right place — the stated direction is simply the wrong one, and the ±5% rule exists so that
this question never has to be adjudicated after the fact.

## 5. My contract — R7 on the M30 family, all three layers

Assigned: confirm the twelve marginals and the classifier bound still hold on the new family.
**The committed artifact `r7_d0_m30_2026-08-19.json` records only the classifier** — layer (a) had
never been executed for D0 on any family. Executed now, 60 pairs, calibrated against a
same-distribution reference (200 reps):

```
R7(a) twelve marginals      60/60 packets pass all twelve
                            family-wise failure rate 0.000 observed vs 0.170 calibrated   PASS
R7(b) blinded classifier    0.4250 vs the 0.55 ceiling (correct .body/.body pairing)      PASS
R7(c) relation distinctness relation_overlap 0.0000 (max 0.0)                             PASS
```

**My F-null construction is validated on the M30 family across all three layers — a manifest it was
not built for.** The construction is sound; the deployment was not. I record that distinction
plainly because the failure in §2 is not a defect in the arm, and fixing the call site restores
every measurement above.

## 6. D0-only scope: applied mechanically, incomplete in reporting

The reduction I argued for (Δ_carry interpretable at D0 alone) **was genuinely applied**, not
merely stated: `pilot_d0.py` calls `select_residue(..., stratum="D0", ...)` only; D1–D3 are never
constructed; the ledger carries `"scope": "D0 ONLY"`; the commit says so.

**But the interpretive caveat did not ride with it.** The ledger's `verdict_constraints` list four
limits, none of which is the one that matters most — prereg §4.1: *"A D0 win with a D3 null is not
a success for the accumulated corpus and must never be reported as one"*, and §4.3's note that D0's
F0 base rate is depressed by construction so **D0 levels are never compared across strata, only its
Δ**. A reader of `pilot_d0_2026-08-19.json` alone would not learn that a positive D0 result says
nothing about the year of archived kills. **Condition C6 below.**

## 7. Tier B parameters, ruled before the data exists

**7.1 N — manifest 620.** Measured post-screen yield is **146/200 = 0.730**, Wilson95
**[0.665, 0.787]** — and yield is *not stable across rungs* (M20 gave 112/200 = 0.560; an earlier
rung ~0.52). Sizing on the point estimate is therefore optimistic. Sizing on the Wilson lower
bound:

```
manifest 550 -> expected 402 post-screen, worst case 366   (misses the 400 target)
manifest 600 -> expected 438, worst case 399               (grazes it)
manifest 620 -> expected 453, worst case 412               (clears target at the lower bound)
```

**Rule: manifest N = 620**, which delivers ≥400 post-screen even at the yield's lower bound and
clears the 300 floor with a wide margin. It also gives **195 records in the strict-screened subset**
— which matters, because BC-3 (my own co-sign condition) requires the primary endpoint recomputed
on that subset, and at a 400-task manifest that subset is only ~126. If the Tier B rung differs
from M30, **re-measure yield on that rung before fixing N** rather than inheriting 0.73.

**7.2 The +14pp host delta binds the pinning rule, hard.** Same model version, same tasks, free host
0.500 vs paid host 0.640. **The host effect (14pp) is larger than the effect the experiment is
powered to detect (Δ\* = +8pp).** Therefore:

- Pin `host + model_id + endpoint` on **every row**, not just per run.
- **No arm may be split across hosts, ever.** If F-prom runs on host X and F-null on host Y, the
  entire Δ is a host artifact. All arms for a task run on one host, ideally one batch window.
- A mid-run host change **voids the affected arm whole** (R11's discard rule extends to host
  changes, not just transport failures).
- I **ratify Ergon's reading** that a host change is a solver-set change for prereg §3's C2
  purposes — the cold-band re-check he ran on the paid host was correct and is now the precedent.

**7.3 A second family is REQUIRED, not optional.** Three independent reasons:

- **Prereg §1 already requires it** for Tier B: *"≥2 frontier models from different families."*
  A single-solver decisive run violates the binding document as written; this is not a judgement
  call.
- **R15's per-task statistic is "mean success across admissible solvers."** With one solver it
  degenerates to a single measurement and the design loses the only robustness axis it has.
- **The host delta is the argument.** If a serving-config change moves accuracy by 14pp, a
  single-solver result cannot distinguish *"residue carries"* from *"this configuration responds to
  this text."* A second family is the discriminator: replication across families is evidence about
  residue; failure to replicate is evidence about solvers. Cost is single-digit dollars and the
  free NVIDIA Nemotron lane is already verified (`a88d5896`).

**Sequencing requirement:** adding a solver triggers prereg §3's C2 — the new solver gets a
cold-band check **before** any arm runs, and if it sits outside [0.35, 0.60] the manifest re-levels
or the run is `HEADROOM-FAILURE`. Do not add the second family after the first has run.

## 8. Conditions to clear the gate

- **C1 — Fix the renderer asymmetry.** `.body` for both arms. Verified restoration: classifier
  0.4250, ratio 1.00×, 0 verdict tokens either side.
- **C2 — Make R7 test what ships.** `run_r7_d0d1.py` must build its pairs through *the same call
  path the runner uses*, so a validated pass cannot again certify a construction that was never
  deployed. Add an assertion that both arms render by the same method.
- **C3 — Re-run the pilot** on the corrected arms (~$0.40, ~18 min) and **withdraw the +9.6pp
  figure** from `7744ac28`, the ledger, and M1_STATUS until it is re-measured.
- **C4 — Run Tier A on its specified substrate** (Apollo wall corpus) and demonstrate F-answer ≫ F0
  **and F-oracle > F0** there, or amend §4.2 to say the pilot substitutes — which is Ergon's call
  under R12 but must be *stated*, not assumed.
- **C5 — F-oracle.** If the oracle arm still fails to beat F0 at significance after C3, the
  diagnostic matrix routes to **row 1** and no residue verdict may be issued at all. That reading
  must be pre-committed now, before Tier B, not negotiated after.
- **C6 — Attach the §4.1 caveat** to every D0 artifact: a D0 result is not a corpus result, and D0
  levels are never compared across strata.
- **C7 — Tier B parameters** per §7: manifest 620, per-row host pinning with no cross-host arms, and
  a second family with its own cold-band check first.

C1–C3 are the gate. C4–C7 are conditions on the decisive run.

---

*Every gate this program built is green except the one that was never tested in the configuration
it shipped in — and that is the gate whose whole purpose is to make the primary endpoint mean
something. One word, ~$0.40, and one more session. The alternative is a decisive run whose control
arm the solver can identify perfectly. — Charon, M1, 2026-08-19.*
