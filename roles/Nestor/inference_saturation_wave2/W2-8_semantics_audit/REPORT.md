# W2-8: executable-semantics audit of the NPE world, runners and rulers

> Saved by Nestor from the worker's returned text, condensed; every defect, number and verdict is kept. The harness blocks
> report-file writes by subagents.
>
> **Folder contents:** `demos/` (7 demos, outputs in `demos/out/`), `patches/` (world_patch.py P1–P3, xtg_patch.py) and
> `tests/test_w2_8.py` (exits 0).
>
> **Boundaries:** read-only on campaign files; no git writes. Runners were only constructed and single methods called; the
> one exception is the 0-epoch `run()` that reset_axis.selftest uses. Every script ran under `python -B`.

**Paths.** All are relative to `roles/Nestor/campaigns/`:
- `W/` = z80atlas-verify-2026-09-22/
- `DS` = c9x-explore-2026-09-24/x_donor_swap/run_ds.py
- `W1/` = npe-w1-donor-discovery-2026-09-26/
- `A3/` = npe-arc3-2026-09-28/
- `FR/` = npe-frontier-2026-09-30/

## Summary
1. **15 new defects, D1–D15.** Four invalidate results, seven bias them, and the rest are cosmetic.
2. **D2 (INVALIDATES).** Cycle-9 H3 could not have come out positive.
   - In all 64 H3 bundles, arms A and B are the same simulation, with every trajectory field equal. They share a cell_id and a seed.
   - The "easy niche" exists only inside the scoring function.
   - Arm C is not a transport control, because pairing ignores niches.
3. **D1 (INVALIDATES).** `val_cache` is keyed on genome bytes only.
   - An organism gets whatever score its genome first received, possibly on another niche's task.
   - Demonstrated: a recorded held of 1.0 against a true 0.25.
4. **X-TASK-GATE must not run as frozen.**
   - D1: ffa6 is COEVO_ENV with 4 niches, so cached scores cross niches.
   - D6: the reader filter uses the base cue index, so an ANSWER_BEFORE_READ-niche reader can never count.
   - D7: the post-run "fresh" revalidation is 100% cache hits.
   - D15: a program that ignores the regime counts as competent (held 0.74).
   - D14: the Stage-0 positive control never exercises the pair path or the CD ruler.
5. **D3.** On the pair tape, 7 of the 12 pressure levels give a byte-identical arena.
   - So the "native QD pressure" in W1, ARC3 and C-A3 is no pressure at all.
   - TAPE_COST and PREDATION only kill, with no replacement.
   - The RESOURCE_LIMITED environment is inert in every world.
6. **D4.** Z8_SLOTTED ignores the mutation operator.
   - 87% of ffa6's "OPERAND" mutations land on opcodes; in 7ae3 it is 0%.
   - ffa6 therefore gets about 8x the mutation supply, and every 7ae3-vs-ffa6 contrast is confounded.
7. **D5.** Both critical anticheat guards can never fire, so `voided` is always False.
8. **D8 and D9.**
   - D8: a mutual acceptance reads as depth 2 instead of 1.
   - D9: a pair-tape relabel keeps the victim's stale age, competence and slot owner.
9. **D10.** C-A3-INTERNALIZE's event clauses are redundant: L either fixed or went extinct in every eligible run. Of the 8 events, 4 rest on transient state-free genomes.

   | reading | events |
   |---|---|
   | as coded | 8 |
   | at the final checkpoint | 4 (exactly the bar) |
   | majority reading | 3 |

10. **Patches.** P1–P3 and an X-TASK-GATE readout ship as monkeypatches, with tests.
    - Every defect check fails on frozen code and passes once patched.
    - The design gates (D2, D3) reproduce and cannot be fixed by a code patch.

## 1. `Runner.run` / `step`: order of operations and RNG draws

**World RNG.**
- There is one: `Random((seed*1000003) ^ crc32(cell_id))` (world.py:127).
- `cell_id` hashes only the grammar factors. So these runner kwargs leave the stream unchanged: implant*, easy_niche_disabled, migration_disabled, output_gate, cue_cost.

**Private streams**, which never touch the world RNG: the competence episodes, the P-11 assay, the reset_axis RANDOM and SCHEDULE draws, and XTG's shuf_rng.

**The steps of one epoch:**
1. **`_env_epoch`** (COEVO: builds env_pop; every 25 epochs it re-draws and clears val_cache).
2. **`_validate`** every val_every epochs. The spec is `_env_spec_for(o)`; the cache is keyed on the genome only (D1).
3. **`_pressure_epoch`**.
4. **Execution.** Pair tape: a niche-blind shuffle, the gate draw under TASK_GATED, `_pair_interact`, copy-mutation drawn from the world RNG, and `_mutate` per half (ATOMIC applies a second one).
5. **`_external_births`** (EXTERNAL only).
6. **`_migrate`**. Under migration_disabled it returns before any draw, so H3 arm C is unpaired from epoch 0.
7. **Cap and reap.**

**Consequences:**
- **Behaviour shifts the stream.** Any behavioural difference shifts all later world-RNG draws, because the VM's copy-mutation draws from the world RNG.
- **The pair-tape population is never replenished.** `_place` is called only in `run()` and `_external_births`, so a kill shrinks it permanently and the reaper is unreachable.
- **Pair execution ignores energy and resumes nothing.** It uses `t['slice']`, not `_slice_len`. It always starts at `start`, while registers persist, so `Org.pc` is unused on the pair tape.

## 2. `_pair_interact`: what a "birth" is

**Sequence.** The two organisms execute a then b; each half is mutated and written back; fidelity is computed on the mutated bytes. If accepted, the P-11 assay runs, then `_lin_birth(next_oid, src.oid, victim niche, causal, rec)`, then the victim is relabelled in place.

- **D8.** In a mutual acceptance, the second edge reads `src.oid` after the first relabel, giving a false depth 2. Shown: edges (128←1), (129←128). Latent; it needs padding.
- **D9.** A relabel keeps the victim's age, born, comp, held, probe, energy and births. `slot_owner` still names the old oid, and `birth_niche` is never set for the new one.
  - PREDATION can never target a relabelled organism.
  - The reaper treats newborns as old.
- **Niches are labels only:** pairing ignores them.

## 3. The ATOMIC runner (DS:47-62)
- **Correct:** tag restoration, and the P-11 RNG is untouched.
- **Latent:** `runner_cls` does not enforce `atlas_axis = NONE`. With RECOMBINATION on, ATOMIC would keep accepted splices.
- **Code-only assumption:** under TASK_GATED, organisms that are gated out neither interact nor mutate. The gate therefore throttles mutation supply about 6.7x.

## 4. Screen seeding and caches

**Determinism.**
- `run_de.competent` (sha256), `fair_assay` (g.hex()) and run_ci/run_xmi `sf` are deterministic per genome.
- **D12:** `run_dd.screen` seeds on the index of the genome in the sorted checkpoint list, re-drawn at every checkpoint.
  - The labelled-COMPETENT probability is 0.036, 0.21 and 0.55 at a true per-seed rate of 0.3, 0.4 and 0.5.
  - 8 of the 49 DENSE_COPY L2 runs rest on a best rate below 0.6. The SIGNAL survives.

**Leaks and gaps.**
- No module-level cache leaks; every pool uses maxtasksperchild = 1.
- `world.z8 = dense` reaches neither `tasks.z8` nor `world.z8taint`. This is equivalent today.
- The self-tests are blind to `run_tainted` and to flags.

## 5. run_ci / run_xmi (D10)

**How run_ci tracks L.** L follows every predecessor-accepted birth and ignores the P-11 flag, unlike run_de. `discard(child)` is a no-op.

**Why the event rule reduces.** In all 26 eligible runs, free_in_L == free exactly when L_share ≥ 0.5. L_share only ever takes the values {0, 0.664, 1}. So the event amounts to "L fixed, plus at least one state-free genome at some checkpoint".

**Transient events:**

| run | last state-free epoch | state-free genomes then | at final |
|---|---|---|---|
| ffa6 27000012 | 1600 | 1 | 0 |
| ffa6 27000024 | 1900 | 1 | 0 |
| ffa6 27000051 | 1200 | 11 | 0 |
| ffa6 27000052 | 1600 | 7 | 0 |

**Event counts:** 8 as coded, 4 at the final checkpoint, 3 on a majority reading.

**run_xmi** is correct in itself (the Shim and the replay gate). But it inherits the transient endpoint, and with L_share binary, X is close to determined by L_share.

## 6. X-TASK-GATE pre-execution audit

**Checked and sound:**
- SHUF's private RNG: OK.
- `_validate(force = True)` after `run()` is harmless, but it does nothing (D7): `run()` already ends with a forced validate, and the second call is 100% cache hits.
- The "regime" depth ruler is only partly appropriate: it is historical and run-level, it can be inflated by D8, and its eligibility (25/72) came from a pressure-free world (D3).
- `prov` under EXTERNAL: OK.

**Defects:**
- **D13.** INIT ≠ sorting under ATOMIC.
- **D1.** ffa6 is NICHES_HIGH_MIG + COEVO_ENV with 4 niches. Seed 31,000,000's draw is XOR5A FR, XOR5A FR, ADD1 ABR, XOR1 FR.
- **D6.** A perfect ABR reader fails the filter `probe ≥ 3`.
- **D15.** A regime-blind echo of v^key scores held 0.738 with probe 3.0, and counts as competent in 200/200.
- **D14.** Stage 0 is EXTERNAL, private-slot only. It never exercises the gate, P-11 provenance or CD.
- **D9.** Stale competence becomes the gate input.

**Recommendation:** do not execute. Apply:
- P1 (cache key = genome + spec);
- the `xtg_patch` readout;
- a planted positive on the pair path for CD;
- renaming INIT as "no replication edge";
- a STATIC environment, or per-niche reporting;
- a re-freeze.

## 7. Defect table

| id | file:line | mechanism | severity | touches |
|---|---|---|---|---|
| D1 | W/world.py:576-584, 1090-1095 | cache keyed on genome only; spec varies by niche | INVALIDATES | C9 H3 readouts (15/64 A<B crossings from scoring alone); X-TASK-GATE; H4/E-4 COEVO; observatory COEVO multi-niche cells |
| D2 | world.py:1070-1078, 769-780, 981-982; H3 manifest | H3 pressures/environment inert on the pair tape; A ≡ B; C unpaired and not a transport control | INVALIDATES | C9 H3 NOT_DEMONSTRATED; the E-9 negative |
| D3 | world.py:727-733, 808/811, 461-473, 1147-1153, 303/911, 932-977 | 7 pressure levels identical on the pair tape; TAPE_COST/PREDATION are death without replacement; RESOURCE_LIMITED inert | BIASES | "native QD" framing; observatory pressure contrasts in PAIR cells |
| D4 | world.py:516-531 | SLOTTED offset ≠ instruction class; OPERAND hits opcodes 87%; about 8x supply | BIASES | all 7ae3-vs-ffa6 contrasts |
| D5 | anticheat.py:55, 61, 91, 102-104; world.py:174-175, 1323 | guards cannot fire; the splice is an invisible runner copy | BIASES | every "anticheat clean / not voided" claim |
| D6 | FR/x_task_gate/run_xtg.py:96-98 | base cue index for every niche | INVALIDATES (frozen) | XTG |
| D7 | run_xtg.py:95 | redundant all-cache revalidation; false comment | COSMETIC | XTG |
| D8 | world.py:843, 875-877 | src.oid read after relabel | COSMETIC (latent) | depth, prov, L trackers |
| D9 | world.py:877 | relabel keeps stale state | BIASES | XTG gate; PREDATION×PAIR |
| D10 | A3/c_a3_internalize/run_ci.py:50-55, 77-83, 116-125 | redundant clauses; transient endpoint; non-P-11 edges; the precheck does not replay | BIASES | C-A3 (8 → 4 → 3); X-MAT |
| D11 | A3/x_a3_fair/run_fair.py:126, 181-186, 90-102 | donor profiles truncated; OTHER unreachable | COSMETIC (S_ZERO 0.867 → 0.833) | X-A3-FAIR |
| D12 | W1/x_donor_discovery/run_dd.py:100, 110 | index-keyed, re-drawn screen | BIASES (mild) | W1 L2 |
| D13 | run_xtg.py:105, DS:53-61 | INIT ≠ sorting under ATOMIC | BIASES | XTG rule 3 |
| D14 | run_xtg.py:46-49, 128-135 | positive control on the wrong path | BIASES (design) | XTG |
| D15 | run_xtg.py:98; tasks.py:211-213 | regime-blind reader counted as competent | INVALIDATES the CS/CD reading | XTG |

**Minor items:**
- max_epochs = 0 is treated as falsy.
- The NONSTATIONARY shift is timed on the truncated epoch count.
- `_niche_spec` is dead code.
- The STRUCTURAL indel boundary uses the pre-indel genome.
- HELDOUT_GAP compares different organisms.
- `n_cross_events` counts validations.
- Pair-tape length can exceed n.
- `runner_cls` does not enforce atlas NONE.
- The self-tests are blind to run_tainted and to flags.
- On the pair tape the pc is not persisted.

**Verified as not defects:**
- SHUF;
- the private, deterministic screens (except run_dd);
- validation never draws from the world RNG;
- dense-alias scoring is equivalent;
- no cache leaks;
- run_xmi's Shim and retag;
- ATOMIC tag restoration;
- run_de's hook runs before the relabel and requires the causal flag;
- XTG's EXTERNAL provenance.

## 8. Demos (`demos/`)

| demo | demonstrates |
|---|---|
| `demo_d1_valcache_crossniche.py` | recorded held 1.0 vs true 0.25 |
| `demo_d2_h3_aliasing.py` | A == B in 64/64 bundles; A == C in 0/64 |
| `demo_d3_pressure_alias.py` | 7 pressure levels identical |
| `demo_d4_slotted_operator.py` | opcode hit share 0.874/0.867 vs 0.000 |
| `demo_d5_relabel_and_swap.py` | false depth 2; stale bookkeeping |
| `demo_d6_records.py` | D10 counts 8/4/3; D11; D12; D5 counters |
| `demo_d7_xtg_competent_ruler.py` | regime-blind competent in 200/200 |

## 9. Patches and tests

**Patches** (patches/world_patch.py):
- **P1:** cache key = (genome, spec).
- **P2:** donor identity is read before the relabel; the child's bookkeeping is reset; carried registers are counted.
- **P3:** SLOTTED mutation by instruction class.

**X-TASK-GATE readout:** patches/xtg_patch.py.

**Proposed diffs** (prose only):
- **anticheat:** remove or implement the dead guards.
- **run_fair:** save all donor profiles.
- **run_ci:** read the final checkpoint, and add a non-redundant comparator.
- **run_dd:** seed on the genome hash.
- **H3:** needs a redesign with a causal channel.

**tests/test_w2_8.py:** D1, D8, D9, D4 and D6/D15 each fail on frozen code and pass when patched. The design gates D2 and D3 cannot be fixed by a code patch. P2's neutrality was checked only trivially (5 epochs, 0 births).

## 10. Ledger entry (W2-8)

- **Result.**
  - 15 defects: 4 INVALIDATES (D1, D2, D6, D15), 7 BIASES, the rest COSMETIC, plus 10 minor items.
  - C9 H3 could not have come out positive.
  - X-TASK-GATE must not run as frozen.
  - On the pair tape, the task layer has no causal effect under 7 of 12 pressures.
  - C-A3 is fragile: 8 → 4 → 3.
- **Confidence.** High for D1–D9 and D15, and for the D10/D11 arithmetic. Medium for the D10 interpretation and the size of D12.
- **Strongest objection.** H3's "NOT_DEMONSTRATED" is still literally true, and C-A3's rule was applied as frozen.
  - Reply on H3: the label should be INVALID/UNTESTABLE, and the negative should be withdrawn.
  - Reply on C-A3: the verdict stands procedurally, but the rule does not measure "lineages come to consist of state-free genomes".
- **Next.**
  1. Re-register C9 H3 as INVALID.
  2. Re-read C-A3 at its final checkpoint (no compute needed).
  3. Name the D4 confound wherever cells are compared.
  4. Repair and re-freeze X-TASK-GATE.
  5. Measure D1's contamination of the observatory COEVO cells by replay.
