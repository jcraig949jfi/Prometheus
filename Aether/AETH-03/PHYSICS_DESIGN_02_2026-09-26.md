# AETH-03 PHYSICS DESIGN 02 — can a local difference propagate?

Date: 2026-09-26. Seat: Aether. Directive:
`roles/Aether/prompts/2026-09-26_next_round/DIRECTIVE.md` (verbatim,
manifest-verified).

**PREREGISTRATION FIRST.** CANDIDATE PHYSICS, PROPAGATION ASSAY and the
thresholds in §2.4 were committed before any propagation run at the
reported size. OBSERVED, INTERVENTION RESULTS, MECHANISTIC EXPLANATION
and the verdict sections are filled in afterwards and say so.

`aeth01.v1` is unmodified and is the baseline. Cost: CPU only, $0.00.

**Result, in one paragraph (added after the runs).** Of four laws
assayed against v1 (1,280 twin pairs, zero locality violations), `mov`
and `m4` are killed as local, `add` is closed as local, and **`rcv` is the
only law in which a one-bit difference propagates over multiple
generations with injected perturbation off** — weakly (6 of 128 origins
sustained, to generation 12 and radius 11, branching), below the
preregistered bar for an intervention (UNRESOLVED). Attacked anyway: a
partial-ring intervention that leaves the ring's WRITE emitters powered
still stops all crossing (0/128 vs sham 17/128) when only the ring's
inert sites are starved, while starving only the WRITE sites barely
matters (13/128). What propagates is **activation timing along `rcv`'s own
receipt relay through inert matter** — 92% of secondary differences are
"who fired" and energy, 8% content. No candidate earns scale-up. The
full-ring ablation specified in §2.4 turned out to be forced by the law
and is reported as a semantics check, not evidence.

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

*Written after the runs.* Evidence:
`Aether/AETH-03/evidence/2026-09-26_propagation/` (20 assay files, one
null self-test). Regenerate every number below with

    python Aether/observatory/aeth03_propagation_reduce.py \
        Aether/AETH-03/evidence/2026-09-26_propagation

**Instrument checks.** 0 locality violations across all 1,280 twin pairs.
The full-size null self-test (v1, 8 origins × 2 arms × 400 ticks) never
differed.

### 3.1 Perturbation OFF (the primary arm), 128 origins per law

| | v1 | add | mov | rcv | m4 |
|:--|--:|--:|--:|--:|--:|
| INERT / DIRECT / SECONDARY / SUSTAINED | 63/55/10/0 | 24/73/30/1 | 72/55/1/0 | 39/37/46/**6** | 65/57/6/0 |
| P_esc (radius ≥ 3) | 0.008 | 0.062 | 0.000 | **0.203** | 0.008 |
| P_sec (generation ≥ 2) | 0.078 | 0.242 | 0.008 | **0.406** | 0.047 |
| P_sust | 0.000 | 0.008 | 0.000 | **0.047** | 0.000 |
| M, generation-1 share of new differences | 0.732 | 0.898 | 0.989 | **0.399** | 0.615 |
| new differences, gen ≥ 2 / gen ≥ 5 | 92 / 52 | 117 / 19 | 1 / 0 | **1,018 / 289** | 201 / 0 |
| max generation / max radius | 56 / 3 | 6 / 5 | 2 / 2 | 12 / **11** | 3 / 3 |
| G_s (median max gen, sustained) | — | 5 | — | **10.5** | — |
| branch points | 18 | 32 | 4 | **448** | 55 |
| died by +400 | 0.219 | 0.016 | 0.414 | 0.336 | 0.234 |
| P_sust per seed 0/1/2/3 | 0/0/0/0 | 0/0/.031/0 | 0/0/0/0 | 0/.094/.031/.063 | 0/0/0/0 |

No law saturates: median differing fraction at +400 is 0.000 for every
law and no origin reaches radius 60.

### 3.2 Perturbation ON, 128 origins per law

| | v1 | add | mov | rcv | m4 |
|:--|--:|--:|--:|--:|--:|
| P_esc / P_sec / P_sust | .031/.188/0 | .062/.258/.008 | .047/.078/0 | **.414/.523/.227** | .023/.109/0 |
| M | 0.760 | 0.872 | 0.947 | **0.282** | 0.791 |
| max generation / max radius | 56 / 4 | 6 / 5 | 3 / 4 | 19 / **17** | 3 / 3 |

### 3.3 Verdicts, preregistered thresholds applied verbatim

- **`mov` — KILLED** (K1 local, K2 mechanical: 98.9% of new differences
  are generation 1). §8's named risk arrived: 41% of divergences *die*,
  because the differing byte is moved into a neighbour and the source is
  zeroed in both worlds.
- **`m4` — KILLED** (K1 local; radius never exceeds 3).
- **`add` — UNRESOLVED by the numbers, narrowly** (K1 escaped by 0.012,
  K2 by 0.002). One origin in 128 sustained, max radius 5, 90% of new
  differences generation 1. **Closed by the directive's standing
  instruction** ("if its footprint still remains local, close it"): its
  median radius is 1 and it is not a propagation law. The extra
  state-change Round 01 measured does not become reach.
- **`rcv` — UNRESOLVED.** Not killed: K1–K4 all clear. J3 passes (median
  depth 10.5 among sustained origins). **J1 fails** (P_sust 0.047 < 0.10)
  and **J2 fails** (seed 0 had no sustained origin). It did not earn the
  intervention by the preregistered gate.

### 3.4 What is real in `rcv`, at its correct width

With injected perturbation OFF, `rcv` is the only law in which most of a
one-bit difference's descendants are *secondary*: 60% of new differences
are generation ≥ 2, chains reach generation 12 and radius 11, and 448 new
differences had two or more differing parents (branching). Six origins
in 128 sustained, in three of four seeds. That is **weak, genuine,
multi-generation propagation**, and by the directive it is now attacked
with falsifiers rather than read as an activity metric (§4). With
perturbation ON it is 4.8× more frequent (22.7% sustained, radius 17).

### 3.5 A caution the v1 control supplied

v1 reaches **generation 56 without ever leaving radius 3**: a difference
that heals and re-appears between neighbours accumulates generations in
place (265 re-entries). Generation depth alone is not reach. The
SUSTAINED class requires radius ≥ 5 for exactly this reason, and every
claim here about `rcv` is made on radius and generation together.

## 4. INTERVENTION RESULTS

*Written after the runs.* `rcv` did not earn the §2.4 intervention (J1,
J2 failed). The directive requires weak but genuine multi-generation
propagation to be attacked with falsifiers, so it was run anyway and is
**labelled as beyond the preregistered gate**. Evidence:
`Aether/AETH-03/evidence/2026-09-26_rcv_falsifiers/`. Ring at Manhattan
radius 5–6 around the origin, re-applied before every tick in both
twins; sham = the same ring shape centred n/4 away; outcome = the
divergence reaching radius ≥ 8. 4 seeds × 32 origins per arm; origins
drawn independently of the assay's.

### 4.1 Full-ring starvation (the §2.4 arm) — FORCED BY THE LAW, not evidence

| perturbation | ablation beyond ring | sham beyond ring |
|:--|--:|--:|
| OFF (the specified arm) | 0 / 128 | 1 / 128 |
| ON (labelled extension, better powered) | 0 / 128 | 17 / 128 |

The OFF arm is underpowered, as §2.4's own numbers predicted (3.1% of
assay origins reach radius 8). **More importantly, the ON result is
guaranteed by the semantics.** In every aeth03 law influence travels only
by emission, and a site with energy 0 cannot emit, so a fully starved
closed ring blocks every difference by construction. It confirms the law
does what it says. It is not a falsifier, and it is recorded in the
calibration ledger as a design error (the same trap as the clamp
firewall rejected earlier the same day, in another form).

### 4.2 Partial-ring starvation — the non-trivial test (post hoc, committed before running)

Motivated by the mechanism probe (§5): starve only ONE class of ring
site, classified from world A each tick and applied to both twins, so the
other class can still carry influence across. Prediction written before
the runs: starving the inert ring sites cuts reach beyond the ring by
≥ 50%; starving the WRITE ring sites cuts it by < 50%. Inert-relay
reading falsified if the inert arm cuts it by < 20%.

| perturbation ON | ablation beyond ring | sham beyond ring | reduction | reached radius ≥ 5 (abl / sham) |
|:--|--:|--:|--:|--:|
| starve **inert** ring sites only | **0 / 128** | 17 / 128 | **100%** | 28 / 32 |
| starve **WRITE** ring sites only | 13 / 128 | 17 / 128 | 24% | 34 / 32 |

**Not falsified.** With the ring's WRITE emitters fully powered, nothing
crosses once the ring's inert sites are starved. With the inert sites
powered and the WRITE emitters starved, crossing is almost unchanged.
Spread *up to* the ring is unaffected in both (28–34 vs 32), so the
intervention acts on crossing, not on the source.

## 5. MECHANISTIC EXPLANATION

*Written after the runs.* Probe: `aeth03_rcv_probe.py` (post hoc,
descriptive), seed 1, 32 origins, perturbation off.

- At stationarity **42% of all active sites under `rcv` are active only
  because they were written** (1,377 receipt-only vs 1,898 WRITE-active).
  Every winning template write fires its target once, which writes
  another site, which fires once: receipt-triggered emission chains run
  through inert matter everywhere, all the time.
- **80% of secondary differences land in inert sites**, and 88% of newly
  differing sites are receipt-active on the next tick.
- **What differs is mostly *who fired*:** of 359 secondary differences,
  269 are the received flag and 75 are energy (the write cost paid or not);
  template bytes account for 30 (8%) and opcode for none.

So `rcv` propagates **differences in activation timing** — an extra or a
missing firing — along its own relay primitive through inert matter. The
partial-ring test (§4.2) confirms the carrier: the inert relays, not the
WRITE emitters. A WRITE emitter re-sends its own payload whatever it
received, so an arriving difference passes through it only if it lands
in its own bytes; a receipt-activated inert site fires *because* it was
written, so a difference in whether it was written becomes a difference
in what it does one hop further on.

*Reasoned from the law, not measured:* why it is weak without
perturbation (4.7% of origins sustained): each
relay hop costs WRITE_COST, relays lose arbitration contests, and a
relay's direction is its own fixed arg0, so a chain is a random walk that
ends when it walks into a starved or out-competed site. *Also reasoned,
not measured:* why perturbation
amplifies it 4.8×: a write that happens in one world and not the other
receives a bit perturbation only in the world where it happens, so every
activation difference also seeds a template difference, including arg0
and arg1, which re-aims later relays. Perturbation turns timing
differences into topology differences.

## 6. KILLED CANDIDATES

- **`mov`** — K1 + K2. Moving bytes makes differences *die*: in 41% of
  origins the differing byte is moved on and the source zeroed in both
  worlds. 98.9% of new differences are generation 1. §8's named risk.
- **`m4`** — K1. Removing the K2 perturbation channel from the field
  selector does nothing for reach (radius ≤ 3). It was never a propagation
  candidate; its original question (do arg1-mediated cycles persist
  without the K2 channel?) was not asked here and remains open.
- **`add`** — closed. UNRESOLVED by the numbers, narrowly; closed under
  the directive's instruction because its footprint stays local (median
  radius 1, max 5, 1/128 sustained). Counting is not communication, and
  Round 01's extra state change does not become reach.

## 7. UNRESOLVED CANDIDATES

- **`rcv`** — UNRESOLVED by the preregistered gate (J1: 0.047 < 0.10;
  J2: seed 0 had no sustained origin), with the strongest evidence of any
  law so far: weak, genuine, branching, multi-generation propagation
  without injected perturbation, carried by an identified, intervened-on
  mechanism. **What it is and is not, at the correct width:** it
  propagates *activation timing* through a relay the rule itself defines
  ("written → fire once"). That is close to the directive's warning about
  a rule that directly encodes the communication it produces, and it is
  recorded as such: `rcv`'s reach is largely its own primitive working as
  specified. What travels is not content (8% template bytes), and nothing
  composes along the way.

## 8. CANDIDATES THAT EARNED SCALE-UP

**None.** No law passed §2.4's gate, and `rcv`'s signal, though real,
is its own relay primitive carrying timing rather than content. No GPU
spend is proposed or made.

### What Round 02 changes about the question

1. **Propagation is possible under a primitive local rule** — but in the
   only law that has it, what propagates is *whether something fired*,
   and it rides a relay the rule builds in.
2. **Conservative transfer (`mov`) is actively anti-propagating**: moving
   a byte takes the difference with it and often erases it.
3. **Perturbation is an amplifier of divergence, not a source of
   structure** (4.8× in `rcv`), because it converts activation differences
   into template differences. Any future claim about propagation must be
   made with perturbation off first.

### Proposed next question (not built)

Can *content* ride a relay? The one-change candidate that asks it
without composing two mechanisms is **`fwd`: a receipt-activated site
emits the value it received rather than its own payload** — a single
change to `rcv`'s emission value, tested only against `rcv` as its
baseline. Its named risk is the directive's own warning: it may directly
encode a message path, so its first falsifier must be whether forwarded
content is *transformed* or composed anywhere, not merely relayed.
