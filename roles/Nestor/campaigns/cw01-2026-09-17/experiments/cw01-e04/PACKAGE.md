# cw01-e04 — ENGINEERING LEDGER (XIII)

Experiment 4 of 10. Disposition **INCONCLUSIVE** (downgraded from the driver's COMPLETE).
RECONCILE 18:13 → disposition settled ~18:32, ≈19 min of a 24 h timebox. Science cost: 54.7 s for
4 replicates × 3 arms × 60 generations × 64 organisms.

---

## THE SCIENCE

**What holds.** Selective, worth-conditional carrying evolved and beats both controls in every
replicate:

| | treatment | non-conditional | always-recompute |
|---|---|---|---|
| score | 1.7215–1.7834 | 1.5742–1.5977 | 0.8691–0.9000 |

selectivity 0.595, ancestor-relative **+49.1%**, triage MI significant against its shuffled null in
**4/4** (0.280 bits, excess +0.276).

**What does not.** The decisive intervention — scrambling which properties predict worth, at identical
cost — clears its own noise floor in only **3/4** replicates. r02's −3.27% sits inside its null band
[−6.69, +7.17]; the others clear theirs (−10.63 vs −4.47; −12.66 vs −7.64; −8.14 vs −3.65).

So the **existence** of triage is solid; the **causal dependence** on the hidden value structure does
not replicate. Those are different claims, and the pre-registration reserves COMPLETE for an effect
replicated across independent seeds. INCONCLUSIVE is the category it fixed in advance for exactly this.

**Generality (separate verdict, never upgrades the primary):** ttl_half **−14.83%**, drop_shock
**−8.51%**, ttl_double **+5.24%**. The evolved policy is tuned to having *enough time* — it degrades
when the channel forgets faster and improves when it forgets slower. That is fitting to one damage
schedule, which the campaign order explicitly asks to detect.

---

## STARTUP

**Reused unchanged: six components** — `seeds`, `localrun`, `residue`, `lineage`, `infometrics`,
`learnability`. (e01 reused 0, e02 3, e03 4, e04 6.)

**Failed qualification — four defects, all caught before budget:**

| Defect | What |
|---|---|
| **D032** | The scarce resource was never scarce. Capacity 12 against unconstrained demand 6.28 meant **zero** placement failures; carrying was free and blind placement *beat* triage (2.45680 vs 1.98291). Capacity re-derived from measured occupancy by a contention rule declared **before** the outcome was known. |
| **D033** | The learnability comparison conflated selectivity with worth-alignment. The verdict swung with capacity (+9.30% / +3.42% / −14.43%) because blind placement wins on raw hits, not targeting. Restated as best-conditional vs best-non-conditional, plus an anti-aligned control at matched selectivity. |
| **D034** | Q10 passed **vacuously** on `info=0.0` — two arms agreeing the world was empty. Re-earned on live genomes. |
| **D035** | The decisive intervention was tested by **sign alone**. Reported 4/4; the noise floor says 3/4. |

---

## EXECUTION

**726 rows.** IX discharged by measurement *before* the run — an independent reimplementation of the
channel (explicit list bookkeeping vs the dict-based primary) agreed exactly across 135 comparisons,
worst divergence **0.000e+00**. Testing it standalone cost seconds; discovering a divergence inside a
4-replicate run would have cost the run.

Structural fixes that held: arms as up-front transformations, deterministic decisions, and **pre-drawn
drop outcomes** so an organism placing fewer items cannot desynchronise the arms' RNG. That last one
was anticipated in PREFLIGHT rather than discovered — the first time this campaign has pre-empted the
D019 class instead of catching it.

---

## TEARDOWN & PORTABILITY

Clean: in-process, 0 owned runtime resources, `pm:cw01:*` empty, 0 live consumers, 0 matched
processes. Unchanged requirements: **git worktree + `PM_TAG`**, no GPU, no Redis, no container.

---

## COMPRESSION

**Landed:** `learnability.assert_live` / `require_live` (an identity check is refused unless the named
metrics are non-zero) and `infometrics.sham_null` / `effect_clears_null` (an effect must clear the
sham-vs-sham floor).

**Why both exist.** Three defects across the campaign share one shape — **conditions satisfiable in the
absence of the phenomenon**:

- **D022** a gain detector with no noise floor fired on pure noise
- **D034** a matched-arms check passed when nothing happened
- **D035** an intervention verdict tested direction but not magnitude

Each was caught late, by inspection rather than by machinery. Both are now executable gates that fail
closed.

---

## THE HONEST HEADLINE

**The cost curve stalled: 8 → 12 → 3 → 4.** But the composition changed completely, and that is the
real finding. e01 and e02's defects were in the **world** — mechanisms that never fired, arms that were
never matched, latent facts redrawn every episode. **Every one of e04's four defects is in the
measurement layer.** The world was sound on the first build; my *verdicts* were too weak to support
what they claimed.

That is progress of a kind the defect count cannot show, and it points at where the remaining risk
lives. The worlds are getting reliable. The judgements about them are now the weak link — and the
specific weakness is a recurring willingness to accept a criterion that the absence of the phenomenon
would also satisfy.
