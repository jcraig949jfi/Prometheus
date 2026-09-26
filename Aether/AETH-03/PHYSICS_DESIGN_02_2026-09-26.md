# AETH-03 PHYSICS DESIGN 02 — can a local difference propagate?

Date: 2026-09-26. Seat: Aether. Directive:
`roles/Aether/prompts/2026-09-26_next_round/DIRECTIVE.md` (verbatim,
manifest-verified).

**PREREGISTRATION FIRST.** CANDIDATE PHYSICS, PROPAGATION ASSAY and the
thresholds in §2.4 were committed before any propagation run at the
reported size. OBSERVED, INTERVENTION RESULTS, MECHANISTIC EXPLANATION
and the verdict sections are filled in afterwards and say so.

`aeth01.v1` is unmodified and is the baseline. Cost: CPU only, $0.00.

The question, from the directive: **can a local state difference causally
propagate into a larger region under primitive local physics?** Round 01
found that under v1 and five one-change laws a one-bit difference stayed
within about one site for 500 ticks.

---

## 1. CANDIDATE PHYSICS

Kernels: `Aether/observatory/aeth03_variants.py`. Tests:
`Aether/test/test_aeth03_variants.py` (21 passing; the shared path is
still bit-identical to `aeth01.v1`, observer included).

Laws in this round: **v1** (baseline), **add** (Round-01 control, see
§1.4), and the three ladder-2 laws exactly as PHYSICS_DESIGN_01 §8
defines them, with two deviations stated rather than hidden.

### 1.1 `mov` — conservative template transfer (`aeth03.mov.scout0`)
A source whose template proposal (fields 0–3) wins has its own payload
cleared to 0 after the tick: the byte moves instead of being copied.
Tie rule (not in §8, needed to make the law total): if the source itself
receives a winning payload write that tick, the incoming byte stands.
Targets: redundant re-copying; one-hop influence.
Risk (§8): payloads decay to 0 and the lattice goes inert.
**Causal radius 2**, not 1: whether a source's payload clears depends on
whether it won at its target, which depends on the target's other
neighbours. The assay searches parents at Manhattan ≤ 2 for `mov`, and
a test proves the assay would flag this effect if it were not declared.

### 1.2 `rcv` — receipt enables emission for one tick (`aeth03.rcv.scout0`)
A site that received a winning template write on the previous tick is
active this tick even if its opcode is not WRITE (needs energy ≥
WRITE_COST, pays it). Targets: activity cannot cross inert matter.
Risk (§8): trivial waves.
**Deviation from §8, stated:** §8 says ladder 2 adds no state, but
"received last tick" is one bit per site carried across ticks. `rcv` is
implemented as defined, with that bit, and the bit is part of the state
the assay compares.

### 1.3 `m4` — perturbation-neutral field selector (`aeth03.m4.scout0`)
Target field = `(arg1 >> 3) mod 5` instead of `arg1 mod 5`, so flips of
arg1's low three bits no longer change the field. Targets: the K2 channel
Round 01 found destroying arg1-mediated cycles. Not a propagation
candidate; assayed anyway, since the question now is propagation.
**Deviation from §8's example, stated:** §8 suggested "arg1 mod 8 folded
onto five fields"; any 8-to-5 fold gives three fields double weight
(including the destructive opcode and arg0), which would confound the
test. `(arg1 >> 3) mod 5` spreads 32 values 7/7/6/6/6 and meets §8's
actual requirement (some single-bit flips neutral).

### 1.4 `add` — Round-01 comparator
Unresolved in Round 01, with ~83% of its extra endogenous change being
constant-step counting. The directive's question for it here: does it
increase causal propagation DEPTH, not merely state-change rate? If its
footprint stays local it is closed. Counting is not credited as
communication.

## 2. PROPAGATION ASSAY

Instrument: `Aether/observatory/aeth03_propagation.py`. Controls:
`Aether/test/test_aeth03_propagation.py`.

### 2.1 Design
From a warmed world (128², B-balanced, 1,500 ticks with perturbation
on), fork twins A and B identical except for one bit in one field at one
origin — an active emitter (for `rcv`, active or receipt-activated), a
uniformly random field of five and a random bit. Step both 400 ticks under
the same law and the same hash-keyed perturbation stream, in two arms:
perturbation **OFF** (primary) and **ON**. 32 origins per seed, 4 seeds
(0–3) per law: 128 origins per law per arm.

### 2.2 Why the generations are exact
Every law is local (radius 1; `mov` radius 2) and perturbation is
identical in both worlds, so a site that does not differ and has no
differing neighbour cannot come to differ. Each newly differing site
therefore has at least one differing parent within the law's radius, and

    generation = 1 + min(generation of differing parents on the previous tick)

is the shortest causal chain from the origin. The assay checks the
parent condition every tick and counts violations; **any violation voids
the run.**

- **DIRECT MECHANICAL SPREAD:** generation 1.
- **SECONDARY CAUSAL SPREAD:** generation ≥ 2.
- **SUSTAINED** (per origin): max generation ≥ 5 AND max radius ≥ 5 AND a
  new maximum generation still appears after tick 50.
- **INERT:** only the flipped byte ever differs.

Also recorded: differing sites and (site, field) pairs, per-field counts,
radius, torus 4-connected components and largest component, duration,
died, re-entries, branch points (new differences with ≥ 2 differing
parents).

### 2.3 Instrument controls (tests; all pass before any run)
- **Null twin:** flip the bit twice; nothing ever differs.
- **Relay-chain positive control:** 21 emitters in a row relaying payload
  east; the difference must reach hop k at tick k with generation exactly
  k, and max generation = max radius = 21.
- **Detection control:** a `mov` contest where disabling one emitter
  changes whether a DIFFERENT emitter two sites away wins. Declared
  radius 2: a clean generation-1 edge. Forced radius 1: must be flagged as
  a locality violation. It is.

### 2.4 Thresholds (preregistered)

Computed per law from the 128 origins in the perturbation-OFF arm,
relative to v1 measured in the same assay:

    P_esc   fraction of origins whose max radius >= 3
    P_sust  fraction of origins classed SUSTAINED
    M       generation-1 share of all new differences (pooled)
    G_s     median max generation over SUSTAINED origins
    F       median differing fraction of the lattice at +400

**KILL — any one:**
- **K1 LOCAL:** P_esc ≤ max(2 × v1, 0.05) AND P_sust ≤ max(2 × v1, 0.02).
- **K2 MECHANICAL ONLY:** M ≥ 0.90.
- **K3 PERTURBATION-DEPENDENT:** P_sust(OFF) ≤ max(2 × v1(OFF), 0.02)
  while P_sust(ON) ≥ 0.10.
- **K4 NOISE:** F ≥ 0.25, or ≥ 50% of origins reach radius ≥ 60 (half the
  lattice) — saturation, not structure.

**EARNS AN INTERVENTION — all required:**
- **J1:** P_sust ≥ 0.10 AND ≥ 3 × v1's.
- **J2 reproducible:** P_sust ≥ 0.05 in each of the four seeds separately.
- **J3 depth:** G_s ≥ 8.
- **J4:** K4 not triggered.

A law meeting neither is **UNRESOLVED** and is stated as such.

**INTERVENTION (only for laws that earn it) — carrier ablation.** In both
twins, every tick, set energy to 0 on a two-site-thick ring at Manhattan
radius 5–6 around the origin (nothing on the ring can emit or relay by
activity). Sham: the same number of ring sites, the same treatment,
centred ≥ 20 sites away. Measure the share of origins whose divergence
reaches Manhattan radius ≥ 8 (outside the ring).
**Propagation through active matter is supported if** ablation cuts that
share by ≥ 80% relative to sham. If it does not, the law moves
influence through starved matter and the mechanism is investigated
before anything else is claimed.

What passing all of this would mean, at its correct width: *this law
lets a one-bit difference cause a multi-generation causal chain that
depends on the medium it travels through.* Not communication, not
computation, and no GPU spend on that alone.

## 3. OBSERVED
*Filled in after the runs.*

## 4. INTERVENTION RESULTS
*Filled in after the runs.*

## 5. MECHANISTIC EXPLANATION
*Filled in after the runs.*

## 6. KILLED CANDIDATES
*Filled in after the runs.*

## 7. UNRESOLVED CANDIDATES
*Filled in after the runs.*

## 8. CANDIDATES THAT EARNED SCALE-UP
*Filled in after the runs.*
