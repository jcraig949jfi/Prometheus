# What did `rcv` actually teach? — a new interpretation (research block, Block B)

Date: 2026-09-27. Campaign record: `ops/campaigns/C-002/E-004/`.
This document does **not** change the historical record.
PHYSICS_DESIGN_02 recorded `rcv` as UNRESOLVED under its preregistered
thresholds, and that stands. This is a new interpretation, reached with
evidence gathered afterwards.

**Interpretation: `rcv` is a CALIBRATION LAW — a known, mechanistically
explained propagator of activation timing — not an open scientific
candidate.** It is retained as an instrument control and closed as a
search direction.

The distinction the directive asked for is the axis of this document: a
phenomenon can be real while still being supplied by the rule written to
produce it.

## 1. What the rule forces directly

`rcv`'s one change: a site that received a winning template write on the
previous tick is active this tick. Unfold one step:

- a difference in WHETHER site x was written at t
- → a difference in whether x fires at t+1 (forced: the rule),
- → a difference in x's energy (it paid the write cost or not: forced by v1),
- → a difference in whether x's target y is written at t+1 (forced),
- → a difference in y's received flag (forced).

Every link is the rule or v1's cost accounting. The measured composition of
secondary differences matches that unfolding: in the mechanism probe
(`2026-09-26_rcv_falsifiers/rcv_probe_s1.json`, seed 1, 32 origins, OFF),
**269 of 359 secondary differences are the received flag and 75 are
energy — 96% are the two quantities the rule itself moves.** 80% of them
land in inert sites, which are exactly the sites the rule turns into relays.

## 2. What was NOT trivial from the definition

These follow from the rule and the v1 background together, and could not
be read off the rule alone; they are real, and they are consequences:

- **Damping.** Chains end. With perturbation off only 4.7% of origins
  sustain (6 of 128), max radius 11 in 400 ticks; the horizon study
  (E-005) shows radius 7 at +100 and still 7 at +10,000, with the share of
  origins still differing falling 0.78 → 0.62. The relay does not run
  away; it is limited by the write cost and by losing contests.
- **Branching.** 448 new differences had two or more differing parents;
  relays fork where a relay's target is itself about to relay.
- **Only inert relays carry it.** The partial-ring intervention
  (PHYSICS_DESIGN_02 §4.2): starving the ring's inert sites stops all
  crossing (0/128 vs sham 17/128); starving its WRITE sites barely matters
  (13/128). A WRITE emitter re-sends its own payload whatever it received;
  an inert relay fires BECAUSE it was written.
- **Generation piles up in place.** Over 10,000 ticks `rcv` OFF's
  adjacency generation climbs 8 → 13 at a fixed radius 7: differences
  flicker between relays that keep re-triggering each other.

## 3. What perturbation supplies

With injected perturbation on, the same law sustains 4.8× more often
(22.7% of origins), reaches radius 17 in 400 ticks, keeps growing to 39 by
+10,000, and 7 of 32 regions reach 28 sites (E-005). Without it, none of
that happens. The mechanism, **reasoned from the law and supported by the
audit**: a write that happens in only one world receives a perturbation bit
only in that world, so a timing difference becomes a template difference —
often an aim or field byte — that re-routes later relays. The assay audit
(PROPAGATION_ASSAY_AUDIT §4) shows the ON arm is also where adjacency and
true causation part most (16% of events), consistent with perturbation
seeding many incidental differences around the active front. **The
long-range part of `rcv`'s spread is the injected noise amplifying the
relay, not the substrate.**

## 4. Is any content transformed or composed?

**No evidence of transformation or composition.** With the content-cause
probe (PHYSICS_DESIGN_03 §5.4), `rcv` OFF, seeds 0-1: 332 new content
differences; 26% are writes that happened in one world only (a relay
fired in one twin), and where both worlds wrote, 59% of deep differences
are a different WRITER winning rather than the origin's bit arriving.
Only 5 content differences in 128 origins carried the origin's own bit
past generation 2 (E-006). What moves is which site fires and which
source wins; the substance of the origin's difference does not travel,
and nothing combines it with anything. With perturbation ON the content
counts rise (211 preserved at generation ≥ 2), consistent with §3: the
injected noise, not the relay, creates the content-level spread.

## 5. Does the substrate organise the relay, or only execute it?

**It executes a frozen map.** Post hoc probe
(`Aether/observatory/aeth03_rcv_paths.py`,
`Aether/AETH-03/evidence/2026-09-27_rcv_paths/`), perturbation off: the
same origin flipped at +0, +200 and +400 ticks sends its divergence to
**exactly the same sites** — Jaccard 1.0 in 24 of 24 pairs across two seeds.
That exact 1.0 was checked for an identity before being believed: the world
is not static (82% of sites change energy between the snapshots), but
**~93% of template bytes never change without perturbation** (the 6.7%
that do change settle in the first ticks and are the same set at +200 and
+400). A relay's aim and field live in template bytes, so the relay network
is fixed, and a difference injected at any time takes the same paths.
Flipping a DIFFERENT bit at the same site gives 0.72–0.77 overlap: which
bit (an aim bit, a field bit) matters; when does not.

Nothing in the substrate builds, maintains or re-routes the relay network.
It is the initial soup's argument bytes, frozen by the absence of anything
that rewrites them.

## 6. Decision

| option | chosen? | why |
|:--|:--|:--|
| remain UNRESOLVED as a candidate | no | the evidence now explains its propagation completely: forced by the rule (§1), limited by v1's costs (§2), amplified by injected noise (§3), carried along a frozen map (§5) |
| treat as calibration / positive control | **yes** | it is the only law with a known, intervened-on, multi-generation propagation mechanism — the right test for any new assay (does the assay see it? does an intervention that leaves a route cut it?) |
| another scoped interpretation | recorded | "`rcv` shows that a local rule CAN carry a difference through inert matter for many generations; it does not show that a substrate can" |

The search consequence is sharper than "`rcv` failed": **propagation that
matters has to be propagation the rule does not itself spell out, on a
medium that can change under the dynamics**. `rcv` has neither.
