# BUILDER-EXPERIMENT specifications: heredity primitives that belong below NPE

**Inference harvest, 2026-09-30 (Nestor). Revision 2**, with red-team fixes applied (m5, m11; B5's hijack is scoped to SELF-using copiers). NPE's two weeks of corrections point to eight measurement primitives. Each is
engine-agnostic and should exist below any specific world. Every correction in NPE's record is a case of one of these being
missing or malformed.

Each spec below gives:
- **Contract:** the interface, which is engine-neutral;
- **Certifies**, and what it does **NOT** certify;
- **Acceptance fixtures:** each must include a case built to FAIL (memory `guard_that_cannot_fire`), plus a planted positive
  on real data (Harmonia F8);
- **NPE adapter notes**;
- **Existing parts** to reuse.

Nothing here is built. These are specifications for a Builder lane, to be dispatched by Aporia.

---

## B1. Reproduction certificate ladder (ancestry / authorship certification)

**Why.** One word, "replicator", was used for five different things:
- similarity (the 1,031);
- construction (P-11, 57);
- informative construction (not painting);
- transmission (CVT-R);
- recurrent transmission.

Every level was later mistaken for the one above it.

**Contract.** `certify(event_or_genome, level) -> {PASS, FAIL, NOT_VERIFIED, reasons}`. The levels are strictly ordered:

| level | name | test |
|---|---|---|
| L0 | resemblance | fidelity only. Never licenses anything |
| L1 | construction | P-11-style counterfactual rebuild of a randomized partner by the actor's own writes |
| L2 | informative construction | L1 + source diversity ≥ threshold (distinct source loci per transmitted locus; separates painters; Archaeon v0 `source_diversity`) + random-passenger control |
| L3 | transmission | CVT-R: a parental single-site variant appears in the product |
| L4 | recurrent transmission | L3 over 2+ generations |
| L5 | in-world heredity | L4 observed on in-world births, not assays |

**Required:**
- NOT_VERIFIED as a third outcome (memory `check_needs_a_third_outcome`);
- context coverage (see B4);
- a **random-passenger control**, because NOP or zero padding inflates L1/L2 (FOR Q3, ADV2 D8).

**Acceptance fixtures:**
- 0x36 painter: L1 PASS, L2 FAIL.
- the real near-zero specimen 5e20dc8a... (95% 0x00, which passed P-11 3/3): expected L1 PASS and L2 FAIL. A trivially inert
  all-zero genome is too easy a fixture (RT m11).
- `LD E,40 ; E5` with NOP padding vs random padding: the two must differ at L2.
- Artemis's panel: complement child, host-executed guest, two cooperating tapes, budget-limited bytewise copier.
- A planted real copier from NPE's corpus must PASS L3.

**Existing parts:**
- Artemis `challenge/p11/certs.py` (CVT-2/CVT-R);
- Odysseus recert;
- Archaeon attribution v0 + `source_diversity`;
- NPE `p11.py`.

---

## B2. Causal-copy tracer with WHOSE, not WHERE (causal copy tracing)

**Why.**
- z8taint tags record the niche where a value was made (WHERE), not the maker (FF-13).
- X-MAT had to key its maker classes on the very label it audited.
- A copy-mutation flip correctly makes new material, but nobody could say *whose* copy.

**Contract.** A per-byte provenance record `(origin_actor_id, origin_event, op_class ∈ {copied, computed, immediate,
copy_error, world_mutation, residue})`, carried through registers and memory with the engine's own semantics. The
`actor_id` is a content-family or site id, never a lineage label.

**Required:**
- a **bit-identity self-test** against the untraced engine, plus a non-vacuity control (the dense_taint E1–E3 pattern:
  0/600 mismatches, 551/600 non-vacuous);
- a **planted-transplant positive control**: foreign material inserted into a family must read as foreign after N
  generations (X-MAT lacked this; Harmonia #1057);
- a **non-parental-founder null** (F8).

**Acceptance fixtures:**
- register-routed copy (`LD A,(HL); LD (DE),A`) keeps the source actor;
- an ALU result takes the executor;
- a copy flip takes the executor with op_class copy_error;
- a hijack (partner executes the owner's code) credits the executing context as actor and the owner as code-owner (see B5).

**Existing parts:**
- NPE `z8taint.py` + `dense_taint.py`;
- Archaeon reference tracer (fixtures 451/451);
- Nestor ancestry-replay `z8shadow.py`.

---

## B3. Parent-free propagation detector

**Why.** Patterns spread without certified parent edges:
- 9cba: the founder label reaches 0.98–1.0 of the population with 0/120 certified founder edges (U-W6);
- founder-less runaways (U-X6);
- AN8, where the victim self-converts;
- the splice's resemblance events;
- convergence.

A lineage-edge-based heredity reading cannot see these. Worse, it credits them to someone.

**Contract.** Given occupancy trajectories of content families (B7) and the certified edge set (B1), return the share of
each family's occupancy gain that no certified edge explains. Break it down by mechanism:
- label transfer through uncertified overwrites;
- resemblance without writes;
- hijack;
- residue / convergence.

**Acceptance fixtures:**
- the splice-only world (RECOMBINATION): ≥ 90% unexplained, as a resemblance mechanism;
- a 7ae3 ATOMIC runaway: mostly certified;
- a convergent population with no copier: unexplained, as convergence.

**NPE adapter.** `births_similar_no_write` is already a perfect marker of the splice artefact (906/910 vs 0/121; U-X4 and
C 5.4). Extend it to per-event mechanism labels.

---

## B4. Reproductive closure assay (context coverage and self-restoration)

**Why.** Five failures share this root:
- "Competent" was scored at one context point (zero registers, blank partner).
- "State-free" at two fixed random vectors.
- A single-k self-state ruler read one phase of a periodic orbit (E §3.2).
- The two state-free rulers disagreed (E anomaly 1).
- The screen missed anti-zero copiers (c2a8: 0.00 from zero, 0.81 from random contexts).

**Contract.**
`closure(genome, world) -> {context_set_measure μ(𝒞), origin_in_set, phase_advance Δ, orbit_period, closure_index}`.
- It enumerates the **engine-relevant context space exhaustively**. On NPE that is the low 7 bits of the pointer registers
  and the count mod tape-length, per side: about 128 × 128 per side, seconds per genome.
- It iterates the genome's own context map to test whether it returns into its working set.
- It reports the **scaffold-dependence vector**: which supplied quantities (address, count, placement, side, partner
  content) the reproduction requires.

**Acceptance fixtures:**
- a copier with count ≡ 0 mod 128: closed without initialization;
- the same copier at count 298: orbit period 64, not closed;
- `LD L,0 ; LD E,40 ; E5` with random padding: closed by immediates;
- `LD E,40 ; E5`: origin-only.

**Existing parts:**
- X-A3-FAIR `fair_assay`;
- the self-location delegate `selfloc.py`;
- ADV2's phase probes (scratchpad `probe4-6.py`, to be ported).

---

## B5. Write-authority and execution-context measurement

**Why.** The world records the executing context as author (FF-31), so four things went unseen:
- **Partners can execute a SELF-using founder's code** (7ae3, SELF-enabled cells). The 200/400 overwrites vanish when
  SELF+LDIR are zeroed, and the partner's context wrote 12,485 of 12,549 changed bytes (U-W1).
- **Symmetric erosion:** self 3,507 vs partner 3,241.
- **Self wrong-side import**, the dominant mode for typical SELF-free copiers: 17,203 own vs 13,391 partner bytes (U-W1b).
- **Composite ATOMIC:** it discards self-writes and keeps predecessor overwrites.

**Contract.** Per interaction, a byte-event graph:
- **EXEC**(context → code positions, with the code-owner of those positions at execution time);
- **WRITE**(context → position);
- **READ**(position → value source).

From it, derive per-event motif labels:
- copy: owner executes its own code, reading its own bytes;
- hijack: EXEC context ≠ code-owner;
- paint: the value comes from an immediate;
- wrong-side import;
- residue: unwritten;
- self-modification.

Also derive per-site write-authority time series.

**Acceptance fixtures:**
- 7ae3 at side 0 vs a random partner: hijack;
- 7ae3 at side 1: copy;
- a 0x36 painter: paint;
- an interaction with no writes: residue.

**Existing parts:**
- NPE `prov`/`prov_lit`;
- Archaeon causal lens (executor vs donor vs host body; FF-11 pre-rename oid);
- Nestor's hijack check (`forensics/nestor_hijack_check.py`).

---

## B6. Lineage depth accounting that cannot be confused with takeover

**Why.** `max_causal_replication_depth` bundles four things:
- world-level, not founder-rooted;
- a maximum over a tree;
- broken by certification failures at 5–36% per edge, non-stationary (A 6.4);
- after takeover, it measures within-family turnover rather than establishment.

As a result, cb7f (copying in 8/8 runs) reads as "never established" (U-N2).

**Contract.** Report the following separately, never as one number:
- founder-rooted certified depth;
- world depth;
- per-window certification break rate;
- **within-family turnover rate** τ_F (promoted rewrites among members at saturation);
- **occupancy trajectory** O_F(t), from B7.

"Runaway" is retired in favour of "O_F ≥ ½ by t". Depth is kept only as a turnover diagnostic.

**Acceptance fixtures:**
- a planted family with copying but no turnover (cb7f-like): high occupancy, low depth;
- a planted family with turnover: depth grows linearly after saturation;
- a world depth reached with no founder-rooted chain.

---

## B7. Seeding / transplant provenance and content-family occupancy

**Why.**
- "Founder-descended" (anc) meant slot lineage: founder bytes run 13–25% (X-CONTENT) and 3–33% (X-MAT).
- Early vs late genomes share about 5/64 bytes.
- The 58–62/64 "divergence" figure is positional (F §3.3).
- Label and content split even in a toy built only on Φ (U-I6).

**Contract.**
- `family(content)` = identity ≥ θ on **transmitted positions** (from B1 L3 or FOR's Jacobian), with aligned, shift-tolerant
  comparison.
- `occupancy(family, t)`.
- `provenance(site, t) ∈ {seeded, transplanted, native-origin, re-acquired}`, keyed on content ancestry (B2), not labels.

**Required controls:**
- a planted descended positive under the same turnover regime (F8);
- a non-parental-founder null;
- a sham-label null: a random same-size set propagated by the same label rule (ADV1 K2).

**Acceptance fixtures:**
- X-CONTENT's replay (13–25%) must be reproduced;
- a sham label must not reproduce C-A3's EVENT pattern above its occupancy share.

---

## B8. Establishment vs maintenance decomposition (with a computed prior)

**Why.** Three errors came from mixing these up:
- "Establishment" was scored at run level and counted later re-acquisitions (U-F1: 8/23 "ESTABLISHED" D0s never copied).
- The S1–S5 stages were not nested (D U5).
- Rarity was misattributed: 8/144 is mostly establishment. Given takeover it is 8/15, or 8/11 with runaway too (dossier E §6.1).

**Contract.** Per implanted or first-appearing family, report a staged, *nested* record:

| stage | name | meaning |
|---|---|---|
| E0 | first own conversion | epoch |
| E1 | subcritical burst ends | stop epoch |
| E2 | occupancy ≥ k/N | |
| E3 | saturation, O_F ≥ ½ | |
| M1 | maintenance: O_F ≥ ½ held for T | |
| M2 | trait persistence | e.g. state-freedom present at the end |

Beside it, a **computed prior** from the family's single-interaction offspring law (m, P_est; ADV2 Q3) under the world's W.
Hazards are reported as rates per exposure (sites × copy events), not as run-level counts at a horizon (U-T6).

**Acceptance fixtures:**
- 7ae3 under ATOMIC: observed E3 ≈ P_est 0.52 (U-S1);
- a run whose first donor never converts but which is re-acquired: E0 = never for the first family, and the second family
  is reported separately.

---

## Cross-cutting rules the primitives enforce

1. **No ruler is frozen before a planted positive shows it can PASS on real data**, and a built-to-fail fixture shows it can
   FAIL (F8; memories `frozen_instrument_is_not_validated`, `guard_that_cannot_fire`).
2. **Labels never license content claims.** Every "descended / inherited / lineage-carried" statement carries a B7 content
   check and names its level (B1).
3. **Screens use random passengers**, never NOP or zero padding.
4. **The world rule W is reported beside every heredity result.** ATOMIC is a quantizer and germline, not a neutral runner.
5. **Execution context and code ownership are always recorded separately (B5).**
