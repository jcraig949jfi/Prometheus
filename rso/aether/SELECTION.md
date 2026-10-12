# Aether phenomenon selection and demand gate (C-018-T020)

Author: Cadmus[harry1-1324c7b6], claude-sonnet-5-5 (Q2), headless on harry1. Written 2026-10-12. Read-only against `Aether/` and
`roles/Aether/`; nothing run on M2; no Aether registered seed, source file or frozen result touched. Base `origin/main`
`3f8cc0150`; `Aether/` last changed at `383bb3584`. Pinned engine files as read: `Aether/test/reference/gpu_aeth01.py` (197
lines, `gpu_step` at :111), `Aether/V2B/REACH01/R1/r1_test4.py` (227; `law_step` :76, `features` :131), `r1_reduce.py` (106;
`decode` :35), `Aether/V2B/PROP01/prop01_run.py` (tracer; clamp :223), `Aether/V2B/REACH01/R2/express01.py` (297).

## 1. Decision

**Narrow, do not reject. Aether supports P1, P2 and P3 as a bounded, independently discriminating native experiment, and the
P2-versus-P3 contrast the directive wants is demonstrable. Aether does NOT support P4 natively. Generation 4's first witness is
therefore the P1/P2/P3 family, with P4 declared UNSUPPORTED. No alternative spatial runtime is needed.**

| Claim | Verdict | One-line reason |
|---|---|---|
| P1 spatial influence | SUPPORTED, but the locality control cannot fail on any native law | kernel is a 4-neighbour gather (`gpu_aeth01.py:45,152`); the light-cone guard only has teeth against a counterfeit non-local law (section 4, C1) |
| P2 causal ancestry | SUPPORTED, as an INTERVENTIONAL assay only | clamp of an intermediate + non-ancestor clamp is native (`prop01_run.py:223`); attributed generation alone is NOT ancestry (section 5) |
| P3 information transmission | SUPPORTED | Aether's decoder, `r1_reduce.decode`, with its own ruler fixtures; reused unchanged |
| P2 vs P3 contrast | SUPPORTED on constructed chains (fixture B: ancestry without content; fixture E: content without ancestry) | section 3 |
| P4 transformation | UNSUPPORTED natively | `aeth01.v1` REPLACE has no state-dependent combination (C1/C3 fail by construction); it exists only under Aether's separate `aeth01.op_XOR/ADD/ROTX` wrapper laws, hand-planted, one-shot (section 6) |

Generation 4 does not reclassify TEST-4 (`RECOIL_EXCHANGE_CAUSAL_REACH_NOT_SUPPORTED`; content gone beyond radius 3). Every
result below is about the INSTRUMENT, or about a different observable than TEST-4 preregistered.

## 2. The first Aether question for an adapter campaign (re-worded)

*Given paired native executions with a single-site intervention, can the Observatory separate (a) whether a later site is a
causal descendant of an intermediate site (clamp-interventional ancestry), from (b) whether the planted source value is
recoverable at that later site (held-out decoding), and refuse to count either as the other?*

Native object (hypothesis-labelled, not a finding): on the TEST-4 laws, attributed generation and interventional ancestry may
disagree. A small probe with NEW seeds (section 5) found deep attributed trees (gen 9-20) whose single-site clamp removed almost
none of the descendants in 3 of 6 RX seeds. TEST-4 gated on a different quantity at 512^2/warm 1000, so this is a lead, not a
contradiction. It is exactly the P2 failure the directive warns about ("do not use an ancestry detector as a substitute").

## 3. Demand gate (new seeds, committed with command)

`rso/aether/demand/PREREG.md` (decision rules committed first, commit `b3e7a610b`), `fixtures.py`, `demand_gate.py`. Result
`rso/aether/demand/demand_result.json` (sha256 prefix `97be49769af7b594`). One process, ~4 min on harry1 CPU:

    python -m rso.aether.demand.demand_gate rso/aether/demand/demand_result.json

Seeds: phys 0xC18B0000+k, noise 0xC18C0000+k, surroundings 0xC18D0000+k, rng 0xC18A0000+k, native impulse 0xC18E0000+k (k=0..3);
disjoint from Aether's 0xE2010000/0xE2011000/0x1A9F and every constant in its tree (grep'd). Replay: a second full run is
identical apart from `wall_seconds` (checked). Kernel step is Aether's own `law_step` (V1 branch, i.e. `aeth01.v1`); decoder is
Aether's own `r1_reduce.decode`, feature extractor Aether's `features`.

Fixtures (hand-built: instrument qualification, NOT discovery). 4 seeds each, 8 labels, 36 origins/seed for decoding:

| Fixture | What it is | t0 sites | Ancestry (clamp) | Content (decode) | Reading |
|---|---|---|---|---|---|
| A content relay | v1 copy chain, 6 links | 1 | QUALIFIED (cut removes 4/4, non-ancestor 0/4, 4/4 seeds) | TRANSMITTED (acc 1.0 at r=1..6, Dstat .875) | ancestry + content |
| B wake chain | each link writes constant 1 into the next link's opcode; label in origin `arg1` (= 0 mod 5), never forwarded | 1 | QUALIFIED (4/4 removed by cut, 0 by non-ancestor) | ABSENT (acc .125 at every radius, Dstat 0.0000) | **structure WITHOUT content** |
| E pre-seeded | label written at t=0 into 7 east cells of an inert medium | **7** | ABSENT (cut removes 0) | TRANSMITTED (acc 1.0, Dstat .875) | **decodable WITHOUT a pathway; decoder alone says "transmitted"** |
| G gapped relay | A with the chain broken after link 2 | 1 | INSUFFICIENT (|Div|=1 < 3) | to r=3 only (1,1,1,.125,.125,.125) | destroyed pathway: reach tracks chain extent |
| N noise | label-unrelated random bytes in the same 7 cells | 7 | ABSENT | ABSENT (|Dstat| <= .008) | divergence without information |

Oracle recompute (independent of the kernel's own labels): in A and B the first-divergence tick of cell origin+k is exactly k
(k=3..6 -> 3,4,5,6) in all seeds (`first_tick` in the result). The 2x2 (B: P2+/P3-; E: P2-/P3+) is the contrast the directive
asked for. It is NOT evidence that native search found either: both are planted.

Locality counterfeit: a "teleport" law (v1 plus payload XOR-ed from (7,7) away each tick) is flagged by the light-cone guard in
4/4 seeds (radius/tick = 8.0). Native `V1` and `RX` worlds (4 seeds each, 64^2, one-bit payload impulse) pass in 8/8
(`locality_native`).

## 4. Falsifiability checklist (directive s2B; `rso/qualify/` has not landed, so the s2B six questions are applied directly)

Columns: (1) alternative represented; (2) pass observation; (3) fail observation; (4) outcome impossible by construction?;
(5) privileged access to the answer?; (6) does failure distinguish the mechanism from a simpler explanation?

| Control | (1) Alternative | (2) Pass | (3) Fail | (4) Impossible by construction? | (5) Privileged? | (6) Discriminates? |
|---|---|---|---|---|---|---|
| C1 light-cone locality | non-local transfer / teleport | radius <= tick | radius > tick | **Native: yes, cannot fail** (4-neighbour gather). Has teeth only against the counterfeit teleport law (fails 4/4) | none | only vs a non-local counterfeit; says nothing about native science. Report as a sanity guard |
| C2 clamp intermediate B | B is not on the pathway | downstream divergence removed (>= .8) | downstream persists | no (E: removes 0) | the clamp site is chosen from the recipe (origin+2) in fixtures | yes: separates pathway from co-incident divergence (E, N fail it) |
| C3 non-ancestor clamp (same Chebyshev distance) | damage spreading / any clamp suppresses | downstream unaffected (<= .2 removed) | downstream removed | no | none | yes: a clamp that removes everything would pass C2 alone |
| C4 pre-seeded (E) | decoder exploiting initial geometry | t0 sites == 1 and C2 passes | decoder "transmitted" with t0 sites != 1 or C2 fails | no | recipe known to the builder | yes: shows P3 without P2 exists, so decoding cannot stand in for transmission |
| C5 wake chain (B) | structure transport without usable content | ancestry QUALIFIED and decode at chance | decode > chance | **content-negative is by construction** (label never copied) | recipe known | yes for the P2/P3 DISSOCIATION; it does NOT test decoder sensitivity (that is C7/C8) |
| C6 gap (G) | reach not tied to the pathway | decode stops at the chain end | decode beyond the gap | no | recipe known | yes: reach must track extent (graded, not binary) |
| C7 noise (N) | divergence mistaken for information | Dstat ~ 0 despite divergence ~ 1 | Dstat >= .03 | no (the decoder could overfit) | none | yes: the decoder's false-positive rate on total divergence |
| C8 label-shuffled null (Aether, `r1_reduce.decode(null=True)`) | decoder reads geometry, not label | accuracy ~ chance | accuracy >> chance | no | none | yes, already in the TEST-4 ruler |
| C9 single-source / latest-input (P4) | simple routing | table is a function of >= 2 inputs | table equals a single input | **fails on REPLACE by construction**: `C3/REPLACE` output equals `b` (latest writer) | none | yes: the near-miss that makes P4 unsupported on `aeth01.v1` |
| C10 intervention identity | multi-site "impulse" passed off as a source | t0 differing sites == 1 | != 1 | no | needs the t=0 diff in the record | yes: E and N are the only fixtures it rejects |

**Limits stated plainly.** (i) The fixtures have exact accuracy 1.0, an EASY hand-built positive. TEST-4's real signal was
0.19 vs 0.14 near chance; sensitivity at that margin is NOT demonstrated here. A graded/diluted-content fixture (label written
into the chain with probability p) is a required adapter-stage control. (ii) The clamp sites are recipe-chosen, so C2/C3 outcomes
on A/B are recipe-predictable; they qualify the instrument, not a discovery. (iii) No near-miss weaker than B/E was built for
the decoder; the minimum required by directive s2B is met for P2-vs-P3 (B and E), not for decoder margin.

## 5. Native incidence probe (selection input only; new seeds, committed with command)

`rso/aether/demand/native_trace.py`, Aether's PROP01 tracer unchanged (`prop01_run.run_unit`), n=128, warm 300, H 400 (Aether
production: 512^2, warm 1000, 3000 ticks). Seeds rng/phys 0xC18A0000/0xC18B0000 + k, impulse 0xC18E0000. Results
`native_trace_result.json`. Commands:

    python -m rso.aether.demand.native_trace rso/aether/demand/native_trace_result.json RX 0 6
    python -m rso.aether.demand.native_trace rso/aether/demand/native_trace_result.json V1 0 4

| Law | seed | ever sites | attributed max gen | B descendants | still diverging under clamp of B |
|---|---|---|---|---|---|
| RX | 0 | 24 | 9 | 16 | 0 |
| RX | 1 | 14 | 4 | 9 | 8 |
| RX | 2 | 63 | 15 | 48 | 46 |
| RX | 3 | 83 | 20 | 61 | 60 |
| RX | 4 | 8 | 2 | 3 | 0 |
| RX | 5 | 7 | 2 | 2 | 0 |
| V1 | 0-3 | 2-4 | 1-2 | 0-2 (cut available in 1 of 4) | 0 |

Reading (not promoted): V1 trees are 1-2 generations. RX produces deep attributed trees in 4/6 seeds, but in 3 of those 4 the
single-site clamp leaves 89-98% of the attributed descendants diverging, so attributed generation and interventional ancestry
disagree there. No non-ancestor control was run in this probe, and warm 300 / 128^2 differ from TEST-4, so this is incidence
sizing for the selection, not a result. Cost: ~45 s per RX unit pair on one core.

## 6. P4: why it is unsupported natively

`Aether/V2B/REACH01/R2_EXPRESS01_RESULT.md`: under `aeth01.v1` (REPLACE) an incoming write replaces the target byte, so no site's
next value depends jointly on its prior state and an input: C1 and C3 fail. Rerun here with NEW surroundings seeds
(`p4_express01_tables`): `C3/REPLACE` strict dependence a=False, b=True, output a function of `b` alone and equal to an input
(the single-source/copy alternative); `C3/XOR`, `C3/ADD`, `C4/XOR`, `C4/ADD` are strict on every input, equal no single input,
surroundings-invariant under both new seeds, and ablating A removes dependence on a. So the capability exists only under
Aether's separate wrapper laws (`express01.py:96`, `aeth01.op_<OP>`), hand-planted, one-shot, with energy set to
execution-only. That is a different `semantics_id` from every law TEST-4 and the running Aether experiments use; adopting it
as the Observatory's carrier would be a physics choice owned by Aether (directive s6), and the only discovery evidence
(LADDER01: 1/40 autonomous, a low-information value-detector motif; `72H_SYNTHESIS.md` s4) is search-assisted and
arbitration-fragile. **P4 stays UNSUPPORTED for Generation 4.** If Aether later promotes an op law to a native default, P4 is
reconsiderable with C9 as its first control.

## 7. Resources, trust boundary, cost

- Demand run ~4 min + native probe ~10 min on ONE harry1 core; nothing on M2/GPU. A confirmatory native experiment of the
  section-2 object at 128^2 costs ~45 s per paired unit (cut adds one more world); 100 units ~ 1.3 core-hours, inside the
  MWO-0004 R2 envelope. 512^2 is ~16x per tick and is not needed for the instrument question.
- Trust boundary: the Observatory consumes native paired executions. Correctness of ANCESTRY requires a native replay (clamp
  needs to re-execute the engine); this dependence is explicit and cannot be avoided without re-implementing the law, which
  directive s7 forbids. Independently recomputable without the engine: the decoder (from stored features), the divergence
  masks, the t0 identity, the light-cone ratio, and the fixture oracle ticks. CPU and GPU kernels are Aether-conformant
  (`r1_conformance.py`); this gate used the CPU reference only.
- Reused: `r1_test4.law_step/features`, `r1_reduce.decode`, `prop01_run`. New: fixtures, runner, preregistration.

## 8. What TEST-4 already settles, and what this leaves open

Settled by TEST-4 (preserved, not re-asked): RX/X/R/V1 payload decodability by radius and its collapse beyond r=3; RX not
beating X by the 0.02 margin in any of 8 seeds; the count of clamp-verified multi-generation trees at 512^2.

Not settled and now the adapter's job: (1) the P2-vs-P3 dissociation as a registered, qualified assay (B/E counterfeits,
C10 identity); (2) attributed-versus-interventional ancestry agreement on native trees with the non-ancestor control (section 5
lead); (3) decoder sensitivity at a margin like TEST-4's 0.05 (needs the graded fixture). Open decision for Palamedes: whether
(2) is worth a native confirmatory run; the preregistration and stopping rule must be frozen before any outcome is inspected.

## 9. Limitations

Q2 author; hand-built fixtures with exact outcomes; no Q3 challenge yet (Pallas, after freeze); the native probe is small and
without the non-ancestor control; one impulse type and one origin rule (as in TEST-4); CPU-reference only.
