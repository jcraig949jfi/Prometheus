# Hestia audit 1 -- dossier G1: Aether (AGE native-circuitry engine)

VERDICT: SALVAGE_COMPONENT -- the copy-only, fixed-aim, radius-1 byte lattice (aeth01.v1 and its
one-switch neighbours) is measured-trivial and should not be scaled; carry forward the causal
instrument stack (one-bit twins with checked locality, counterfactual parents, value provenance,
known-answer lane) and exactly one untested lead (recoil x exchange, mob_r1x1e0), whose
already-designed causal assay (DEV-4/TEST-4) is the decisive next experiment.

Auditor: Hestia audit worker, 2026-10-06. Read-only. Model-family conflict of interest applies
(AUDIT_PLAN s4): the Aether seat is the same model family; an independent reviewer should attack
this verdict.

---------------------------------------------------------------------------------------------------
## 0. Identity
---------------------------------------------------------------------------------------------------

- Paths: Aether/ (1434 tracked files; Aether/runpod excluded except as a scale constraint),
  roles/Aether/ (44 files), ops/campaigns/C-002/ (CONFIRMED Aether: CAMPAIGN.md line 1 "C-002 --
  Aether research block", Thread TH-007, experiments E-003..E-012 all Aether).
- Seat: Aether. Hosts BUCKKEEP (to 2026-10-05), then SPECTREX5/M2 with an RTX 5060 Ti
  (Aether/pivot/AETH_ER01_REVIEW_2026-10-05.md header).
- Tree read: worktree C:/Prometheus-worktrees/hestia-boot-2026-10-06 at 3fed30ac9 (merge of
  origin/main). Latest Aether commits seen: c2bead7b5 (AIM02 RESULT), 79ec4b8d0 (AIM02 packet).
- Entry point: Aether/AETHER_ENGINE_CARD.md (v1, 2026-09-27).

READ (core): Aether/runpod/aeth01_canary/aeth01_cpu_oracle.py (full; the reference transition law),
Aether/observatory/aeth03_variants.py (full; all 25 variant laws), Aether/V2B/AIM01/aim01_run.py
(reaim1 rule, lines 1-60, 100-120), Aether/observatory/aeth03_propagation.py (docstring and function
map), Aether/production/aeth00.py (header). Result documents: AETHER_ENGINE_CARD.md;
AETH-01/FIRST_LIGHT_01_2026-09-22.md (full); AETH-01/NATIVE_CIRCUITRY_01_2026-09-24.md (full);
AETH-01/AETH-02_CLOSE_2026-09-24.md (s0-s2); AETH-03/RESEARCH_BLOCK_SYNTHESIS_2026-09-27.md (full);
pivot/AETH_ER01_REVIEW (s0-s3), pivot/AETH_AIM01_REVIEW (full), pivot/AETH_AIM02_REVIEW (full),
pivot/AETHER_REVIEW_2026-09-27.md (s0 only); V2B/TEST-1, TEST-2, TEST-3 RESULT.md (heads),
TEST-3/OPERATOR_REVIEW.md, V2B/CAMPAIGN_STATE.json; C-002 CAMPAIGN.md and RESULT.md of E-004,
E-005, E-006, E-008 (head), E-009, E-010, E-011, E-012; roles/Aether/calibration/LEDGER.md (full),
roles/Aether/STATUS.md (top). Committed rows checked directly: V2B/AIM02/production/REDUCTION.json
(decision, gates) and one unit file (L1D50_s0.json); V2B/AIM01/production/REDUCTION.json
(decision); V2B/ER01/production/REDUCTION.json (decision, 37 units);
AETH-01/evidence/2026-09-22_optimized_scale_run/{verdict.txt,scale_report.txt}.

NOT READ: Aether/runpod/* beyond the oracle and the scale receipt; AETHER_SPEC.md,
AETHER_DOCTRINE.md, AETHER_CONCEPT.md, PHYSICS_SPEC_DRAFT.md, AETH01_REPAIRED_FREEZE_CANDIDATE.md;
AETH-03/PHYSICS_DESIGN_01..03 and RCV_REINTERPRETATION (only via their summaries in E-004/E-006 and
the synthesis); AETH-03/evidence/*, most of AETH-01/evidence/*; V2B DEV packets, ER01 RESULT.md
body, AIM01/AIM02 PREREGISTRATION.md and RULES.json; Aether/observatory/aeth_prov.py and
aeth_mobility.py bodies (only signatures); the 50+ test files; roles/Aether journals, handoffs,
reviews/promexec FINDINGS; C-002 E-003, E-007 bodies. No engine was run. Numbers attributed to
those unread files are taken from the documents that cite them and are tiered accordingly.

---------------------------------------------------------------------------------------------------
## 1. Mechanism (code, cited)
---------------------------------------------------------------------------------------------------

### 1.1 Substrate: aeth01.v1 (Aether/runpod/aeth01_canary/aeth01_cpu_oracle.py)

- State: H x W torus, each site 5 uint8 fields (opcode, arg0, arg1, payload, energy) (l.18-20).
  Per-site state 2^40; a 512^2 lattice has 10^(3.16e6) states (scratch calc below).
- Exactly ONE active opcode: WRITE = 0x01 (l.22). The other 255 opcode values are inert matter
  (l.117 `if opcode != WRITE_OPCODE: continue`).
- An active site with energy >= write_cost emits exactly one proposal: its OWN payload byte into
  ONE field (arg1 mod 5) of ONE von Neumann neighbour (arg0 mod 4) (l.124-131). Energy-field writes
  transfer min(payload, energy - cost) (l.127-128).
- Contests (several proposals on the same target-field) are won by a SplitMix64 hash of
  (seed, tick, target, field, source) (l.80-88, 154-169). The hash includes the tick, so the
  winner is re-drawn pseudorandomly every tick: arbitration is a noise source, not a gate.
- Commit REPLACES the target byte (l.185-186); with probability mut_numer/2^32 (0.1 in all
  science) one bit of the stored value flips ("Mu", l.91-100, 184-185).
- Energy: write cost, contest losers' transfers destroyed, maintenance decay, Bernoulli
  replenishment (l.195-252).

What this law can and cannot express, read off the code:
- A site's "program" is a fixed 3-tuple (direction 4, field 5, payload 256): 4*5*256 = 5,120
  behaviours, and it NEVER changes its own aim or payload; only a neighbour's write can.
- Out-degree is exactly 1 per active site, in-degree <= 4. The realised write graph is a partial
  function, so "every component is one cycle with in-trees" is a theorem
  (NATIVE_CIRCUITRY_01 l.54-59, 465-469 say so themselves).
- There is no combining operation: REPLACE only. No AND/XOR/ADD of two inputs exists in v1. The
  only data-dependent switch is indirect: a byte written into a neighbour's opcode field turns it
  into a writer iff the byte equals 0x01.

### 1.2 Variant laws (Aether/observatory/aeth03_variants.py)

25 laws total, each one written rule change on a shared code path asserted bit-identical to v1
(l.1-10, 73-111): add (commit old+payload mod 256, l.16-18, 281-282), hys (incumbent-favouring
arbitration, l.19-23, 243-245), chg, cnd (second opcode 0x02 with a 2-bit guard, l.29-33, 237-240),
str (energy-steered aim, l.34-36, 180-181), mov, rcv (a site that received a write fires once
next tick; one hidden bit/site, l.44-49, 177-178), m4, fwd (relay forwards the received byte,
l.195-199; a calibration law by construction), rcv_* combinations and three lesions (rcv_sfx,
rcv_adr, rcv_sfz, l.113-125), and the 8-law mob_r?x?e? enumeration (l.74-82, 271-296):
r = recoil (emitter's arg0 += displaced byte), x = exchange (emitter's payload := displaced byte),
e = energy aim. Plus reaim1 (Aether/V2B/AIM01/aim01_run.py l.8-18, 117-118): a winning writer
advances its own arg0 by 1.

Only add (mod-256 sum) and cnd (2-bit equality guard) introduce anything like a combining or
conditional primitive; only mob r/x and reaim1 let a write change the WRITER.

### 1.3 Instruments

- One-bit twin propagation assay (aeth03_propagation.py l.15-45): exact causal generation via
  radius-1 locality, locality violations checked every tick (must be 0), counterfactual
  single-parent audit; SUSTAINED = generation >= 5, radius >= 5, still adding after tick 50
  (classify, l.315-325).
- prov0 value provenance (aeth_prov.py, class Provenance l.54; body NOT READ) with rungs
  P3_far / P4_transformed / P5_composed / P6_deep.
- P1 mobility ruler (aeth_mobility.py l.50, 103): FROZEN / COUNTER / CYCLING / ENDOGENOUSLY_MOBILE.
- AIM02 non-AIM richness meter (distinct values U, N16/N64 novelty, late discovery, return gaps).
- Known-answer lane (E-007): expected result hashes from committed evidence, cross-host.

Documented claims vs code: the documents are, unusually, NOT ahead of the code. The engine card
itself states "Nothing here computes a task" (ENGINE_CARD l.99-100) and that none of the three
assembly preconditions has been observed (l.60-69). No "reasoning" or "circuit" claim is made in
any current Aether document I read; the AGE "native circuitry" framing was tested and returned
negative by the seat itself.

---------------------------------------------------------------------------------------------------
## 2. Evidence (tiered)
---------------------------------------------------------------------------------------------------

OBSERVED = committed rows/result files on main that I opened; CLAIMED = stated in a committed
document whose underlying rows I did not open; DESIGNED = specified, not run.

E1 FIRST_LIGHT (6 worlds, 4096^2, 5,000 ticks, A40, $2.02). CLAIMED (firstlight.jsonl committed,
   not opened). Regime A freezes byte-identically for 4,249 ticks; no spatial structure (64x64
   block-mean SD 1.107-1.727 vs noise floor ~1.11); compression 0.91-0.95; 0 detectors existed to
   run ("A count of zero here means not measured", FIRST_LIGHT l.225-230). Seat's own reading:
   "No endogenous dynamics ... a fixed assignment graph settling to a fixed point" (l.315-322).
E2 NATIVE_CIRCUITRY_01 (3 x 2048^2 x ~50k ticks, $2.61). CLAIMED. Stationary by ~1,000-2,500 ticks
   to 4 decimals; 72% of edges write the value already present; 86% of landed template writes are
   redundant and ~38% of all template change is the injected bit-flip (l.354-362); persistent edges
   (1,754 sampled) contested 0 times vs ~29 expected (l.269-290) -- persistence = absence of
   opposition; spatially indistinguishable from random (ratio 0.999); energy edges 3-6 of 54,000
   persistent. Verdict: "There is persistent structure. It is not circuitry." (l.386). Caveat:
   calibration ledger 2026-09-24 records that the per-tick classification actually compared
   against a state 250 ticks earlier (+7.3% STATE_CHANGING bias) and that the "observer
   consistency check" was an algebraic identity (LEDGER l.89-109).
E3 AETH-02 falsifiers ($0, 256^2). CLAIMED (falsifiers_256.json committed, not opened). H1:
   lesioning a persistent edge gives recurrence 0.000 and target occupancy 0.000 out to +500 ticks
   (k=224) vs sham 0.92-0.99 (CLOSE l.47-66); 92.3% of sites show no net template change over 64
   ticks (l.80-88). H2: instantaneous edge fraction predicted by independence to ratio 1.002.
E4 AETH-03 law ladder + C-002 (E-003..E-012). Partly OBSERVED via RESULT tables (reductions
   committed; unit files for E-006 kept off-repo). v1 OFF: max radius 2 at +10,000 ticks (E-005);
   rcv = calibration law (96% of secondary differences are the rule's own two quantities; same
   origin flipped at three times reaches identical sites, Jaccard 1.0, 24/24; E-004).
   rcv_add 22/128 sustained (replicated on fresh seeds, E-009), rcv_str 15/128 (two of four fresh
   seeds individually below the 0.10 floor). Lesions: rcv_sfx 4/128 (STEERING_REQUIRED, E-010),
   rcv_adr 10/128 (PARTIAL, E-011), rcv_sfz 6/128 exactly on the boundary (E-012). Cause probe:
   neither carries origin content (E-006).
E5 V2B TEST-1/2/3. OBSERVED at RESULT-table level (REDUCTION.json present). TEST-1: prov0
   qualifies on the fwd positive control (P3_far 0.125 vs rcv 0.012, v1 0); composition P5 = 2/256
   (0.0078) for rcv_add, 0 elsewhere. TEST-2: every OFF law is FROZEN or COUNTER (add-family 66-83%
   constant-step increments). TEST-3: mob_r1x1e0/e1 ENDOGENOUSLY_MOBILE 4/4 seeds, exchange-only
   CYCLING (revisit 0.92), recoil-only COUNTER (0.70); r1x1 P5_composed 0.008 (2/256), "No
   content-transport claim is admissible" (TEST-3 RESULT); ruler blind to varying-step counters,
   which is exactly what r1x1 may be.
E6 ER01 (4 energy economies x 8 seeds + dup = 37 units, 512^2 x 50k). OBSERVED (REDUCTION.json
   decision opened): late frozen fraction 0.9865-0.9880 in every economy; R1/R2 class
   MOBILE_BUT_TRIVIAL with attack low_novelty=true and spatially_confined=true; ever-changed 37.3%
   regardless of economy. Energy is a rate knob (0.41x-3.14x), not a mobility switch.
E7 AIM01 (2 laws x 3 densities x 8 seeds, 49 units, 512^2 x 30k). OBSERVED (REDUCTION.json):
   INITIAL_GEOMETRY_DOMINANT true; reaim expands ever-changed by +0.37/+0.45/+0.39, 8/8 seeds.
   Frozen label REAIM_NONTRIVIAL_CANDIDATE rested on an instrument artifact (the seat's own
   post-hoc: non-AIM novelty 0.099-0.105 at the 0.10 floor; AIM01 review l.36-41, 119-137).
E8 AIM02 (65 units, 512^2 x 6k). OBSERVED (REDUCTION.json decision opened): NOVELTY, REPERTOIRE,
   DISCOVERY, TRANSITIONS seeds_beating_both = 0/8 at every density; only RECURRENCE (return-time
   ratio 2.0) material; DISCOVERY median diff 0.0. Changing site-fields hold mean U = 2.04-2.13
   distinct values (flicker 2.01); late-half discovery 0.0000. Offer probe: each target is fed by
   ~2 writers with near-fixed payloads (AIM02 review l.87-92). Disposition RICHNESS_WEAK, reading
   REAIM_MOBILE_BUT_TRIVIAL.
E9 Scale. OBSERVED (scale_report.txt l.21): 16384^2 = 268M sites at 7.42 s/tick on an A40,
   CANARY_PASS. Bulk statistics at 256^2 match 2048^2 within 0.1-0.4% (AETH-02_CLOSE s0, CLAIMED).
E10 DEV-4 / TEST-4 causal-descendant assay for r1x1 (decodability impulse response vs exchange-only,
   single-site restore). DESIGNED only (TEST-3/OPERATOR_REVIEW.md); no TEST-4 directory exists on
   main; the programme pivoted to ER01/AIM01/AIM02 on v1 instead.

Total compute spent on science trajectories (scratch calc): First Light 5.0e11, NC01 6.2e11,
AIM01 3.9e11, AIM02 1.0e11 site-ticks = 1.6e12 site-ticks, almost all on unstructured random soup.

---------------------------------------------------------------------------------------------------
## 3. Matrix
---------------------------------------------------------------------------------------------------

### 3a. Combinatorial explosion and reachability

Search spaces (scratch: aether_calc.py in the session scratchpad):
- State space: 2^(40 N^2); log10 = 3.16e6 at 512^2, 2.0e8 at 4096^2. Irrelevant in practice,
  because the reachable set is tiny: v1 reaches stationarity in 1,000-2,500 ticks and freezes
  92-99% of the lattice (E2, E3, E6).
- Behaviour space of one writer: 5,120 fixed (direction, field, payload) tuples. A writer
  cannot reproduce itself: it touches 1 of 20 neighbour-field slots forever (fixed aim, l.124-126),
  and copying a 4-byte template needs 4 coordinated writers. Self-replication is unreachable in v1
  from a single site by construction.
- Spontaneous relay desert. Probability a random neighbour is a writer that points at a given next
  site, into its opcode field, with payload 0x01 (i.e. creates a new writer onward), at 50% WRITE
  density: 0.5 x 1/4 x 1/5 x 1/256 = 9.8e-5 per link. Expected number of such length-L chains in a
  512^2 soup: L=1: 102; L=2: 0.01; L=3: 1e-6; L=5: 9e-15. Any multi-step signal pathway must
  therefore be either built by hand or emerge through dynamics; v1 dynamics freeze before they can
  build one. This is the arithmetic behind "a one-bit difference stays within ~1 site"
  (E-005: v1 OFF max radius 2 at +10,000 ticks).
- Fan-in at stationarity (activity 0.191, p = 0.191/20 per neighbour): P(0)=0.962, P(1)=0.037,
  P(2)=5.4e-4. Most targets have one writer; with REPLACE-only commits and fixed payloads the
  number of distinct values a target can ever hold is <= its fan-in plus injected flips. AIM02
  measured exactly this bound: U ~ 2 (E8).
- Reachable set is fixed by initial conditions: ever-changed support scales with initial WRITE
  density 0.194/0.374/0.532 and 92-96% of everything that ever changes lies inside the initial
  writers' aim support (AIM01, E7). The reachable set is a property of the soup, not the law.
- Law space: 25 hand-written laws, each one or two switches from v1. No generative model over
  laws; the search is a manual walk of radius ~2 around one point in rule space, in one energy
  regime (until ER01) and one initial-condition family (random soup, never seeded structures:
  ENGINE_CARD l.162-164).
- Measured hit rates: SUSTAINED propagation best 22/128 = 0.17 (rcv_add, a trace-accumulation
  effect, not content); composition P5 = 2/256 = 0.0078 (best law, rcv_add and r1x1); late novel
  values 0.0000 (AIM02); richness families beating both comparators 0 of 8 seeds x 4 families x 3
  densities = 0/96 (AIM02 REDUCTION.json).
- Time: 95% of NC01's ticks (47,500 of 50,000 per world) were spent after stationarity
  (NC01 H5, l.542-548: the $2.61 would have bought ~59 seeds at 2,500 ticks).

### 3b. Cosplay vs foundation

- Who does the work called "circuitry": nobody. The edges are copy wires from a fixed aim; the
  cycles are a theorem of out-degree 1; persistence is the absence of a contest (0/1,754);
  state change is ~38% injected bit-flips through redundant copy channels (E2). The seat says this
  itself. The engine is not cosplaying reasoning in its claims; the substrate is simply below the
  threshold where reasoning-like structure could exist.
- Where an apparent positive appeared, the mechanism was the rule's own text: rcv propagates
  activation timing along its own relay (E-004); fwd carries content because its code forwards the
  byte (TEST-1); add's "transformation" is a counter (TEST-2, 66-83% constant-step);
  reaim's "nontrivial dynamics" was an EFFECT-subtraction artifact (AIM01) and then flicker over a
  wider area (AIM02). Each was caught by the seat's own preregistered or post-hoc attack.
- The only interaction-level result: recoil x exchange produces a qualitatively different regime
  than either switch alone (TEST-3: revisit 0.92 -> 0.165, counter 0.70 -> 0.013). That is a
  genuine "two insufficient mechanisms combine" phenomenon, but its ceiling is not known: it may be
  a variable-step local recurrence (the P1 ruler cannot see varying-step counters), and its
  composition rate is the same 2/256 floor as rcv_add.
- Ceiling of v1 and its one-switch neighbours, stated concretely: a REPLACE-only, fixed-payload,
  radius-1 medium whose targets hold <= ~2 values and whose writers never retarget themselves is a
  static wiring diagram plus noise. It cannot compute any function of two inputs (no combiner),
  cannot hold a contested gate (arbitration re-rolls each tick), and cannot grow its reachable set
  past the initial aim support. Untested and therefore OPEN: whether v1 is constructively universal
  with hand-placed structures (Wireworld-style). The equality-to-0x01 opcode switch suggests a
  conditional element exists in principle, but no seeded wire or gate was ever built.

### 3c. Substrate bottlenecks

- Representation: one instruction (WRITE) of 256 opcode values; 255 values are inert. The
  instruction set has no arithmetic or logic in v1. Cost: an 8-bit opcode field encodes 1 bit of
  behaviour.
- State/memory: no per-site memory beyond the 4 template bytes; a site's own program is
  overwritten by the same channel that carries data (data and code share fields with no
  protection), so any stored value is also a re-wiring. This both enables data-dependent rewiring
  and makes every stable wire fragile.
- Addressing: direction arg0 mod 4, field arg1 mod 5 -- radius 1, absolute, no indirection. One
  arg1 bit-flip changes the target field (the K2 mod-5 property, LEDGER 2026-09-26) -- every noise
  event re-wires.
- Credit assignment / selection: none by doctrine ("observation and intervention only; no
  steering", ENGINE_CARD l.57-58). Without heredity or selection, anything rare is never
  amplified; the 1e-6 expected length-3 relay will not be kept even if it forms.
- Compositionality: P5 = 2/256 is the measured floor across the best laws.
- Arbitration: tick-keyed hash = an unbiased coin; contested channels cannot persist (NC01 s7
  names memoryful arbitration as the smallest fix; never built).
- I/O bandwidth: none; there is no input or output channel to the world. A "task" would be
  steering by doctrine (ENGINE_CARD l.99-100), so there is no way to ask the substrate a question.
- Scale is NOT the bottleneck: 268M sites run at 7.42 s/tick, and 256^2 reproduces 2048^2 bulk
  statistics to 0.4%.

---------------------------------------------------------------------------------------------------
## 4. Deliverable sections
---------------------------------------------------------------------------------------------------

### Discovery Approach

Build the smallest exact, local, integer physics (bytes on a torus, one WRITE opcode, hashed
contests, energy bookkeeping), refuse to build in individuals, selection or objectives, and ask by
intervention whether differences travel, persist, combine, and eventually whether bounded
self-maintaining regions arise. When the baseline freezes, change exactly one rule at a time on a
code path proven bit-identical, preregister thresholds, and attack every positive with a
cause probe or a lesion. It is an artificial-chemistry / CA program in the "physics first, no organisms"
lineage (contrast Tierra/Avida, which start from programs), run with unusually strong measurement hygiene.

### The Brick Walls

1. Frozen, initial-condition-determined reachable set. 92-99% of the lattice is frozen
   (late frozen 0.9865-0.9880 in all four energy economies, ER01); 92-96% of all change lies inside
   the initial writers' aim support (AIM01). Energy, horizon (500 -> 10,000 ticks, E-005) and scale
   (256^2 -> 2048^2) do not move it.
2. No combinator, so no circuit. REPLACE-only with fixed payloads bounds each target to ~2 values
   (AIM02: U = 2.04-2.13, late discovery 0.0000, 0/96 seed-family-density cells beat flicker).
   Composition across every law tried: P5 <= 2/256.
3. Reachability desert for spontaneous structure: a 3-link writer-creating relay has expected count
   ~1e-6 in a 512^2 soup; with no heredity or selection nothing rare is ever amplified, and the
   doctrine forbids the pressure that could amplify it.
4. Manual law search: 25 laws in ~3 weeks, each hand-written, each a radius-1-or-2 step from v1;
   the method cannot cover a law space that is combinatorially vast, and every positive so far was
   the rule's own text (rcv, fwd, add) or an instrument artifact (AIM01).

### Seed Viability

The substrate as built is a dead end at the level of "native circuitry": it has been
measured-trivial along every axis the seat could vary, and its own reviewer question (AIM02 Q5,
"retire rather than patch rule by rule?") deserves a yes for the copy-only, REPLACE, P0, radius-1
family. What survives:

- The instrument stack (SALVAGE, high value). Exact one-bit twins with every-tick locality checks,
  counterfactual parents (adjacency generation equalled causal generation in 84-100% of 2,793
  audited events), a provenance tracker qualified against a positive control (fwd P3_far 0.125),
  a mobility ruler with declared shortcut attacks, and a cross-host known-answer lane (19 attempts,
  4 hosts, 0 disagreements). Judged as instruments (AUDIT_PLAN s3): they WOULD detect causal
  propagation and content transport if it arose, and they demonstrably caught three false
  positives. They would NOT yet detect computation: there is no controlled-input / functional-
  dependence assay, the P1 ruler is blind to varying-step counters, and the decodability ruler
  (DEV-4) was never built. Transfer target: any deterministic local engine (Z80 machines, PTE,
  Primordial), as the card proposes (TH-011).
- The recoil x exchange interaction (r1x1; LEAD, not a seed). The only law in which writing changes
  both the writer's wiring and its payload data-dependently, and the only case of two individually
  trivial mechanisms producing a new regime. It has no causal-reach evidence yet.
- The epistemic practice (preregistration, lesions that leave the effect a route to survive,
  calibration ledger). Exportable to every seat.

Not a VIABLE_SEED: no mechanism has been shown to compose, and the one candidate's decisive assay
is unrun. Not INSUFFICIENT_EVIDENCE: the v1 family's triviality is established by committed
rows across energy, horizon, density and scale.

### Evolutionary Roadmap

Step 0 -- the ONE decisive experiment (run before anything else, it is already designed):
TEST-4 on mob_r1x1e0, as agreed in Aether/V2B/TEST-3/OPERATOR_REVIEW.md. Laws: r1x1e0,
exchange-only r0x1e0 (required baseline), recoil-only r1x0e0, v1. Snapshot-and-branch twins;
plant K=8 byte values per origin; decode the planted value from cells at radius r=1..6, ticks
25..200; single-site restore of an intermediate B and measure the share of downstream C divergence
removed; own-history predictability vs shuffled control for the varying-step-counter question.
KILL CRITERION (freeze before running): if r1x1 above-chance decoding at r >= 2 does not exceed the
exchange-only baseline on >= 3 of 4 seeds, OR single-site restore at B removes no more C divergence
than in exchange-only (no generation-2 causal descendant), OR a site's next value is predicted by
its own last-k history plus the displaced byte at >= 0.9 held-out accuracy, then retire the entire
copy-only radius-1 aeth01 family (v1, rcv*, add*, mob*, reaim*) and stop law-patching it.
If it PASSES: r1x1 becomes the base law, and steps 1-4 start from it.

Step 1 -- constructive capability before spontaneous search. Hand-build, in the base law, a wire,
a fan-out, a two-input gate and a one-bit memory, Wireworld-style, and test each with the twin
instrument. If the law cannot host a hand-built gate, no amount of soup will find one; if it can,
the search problem becomes measurable (how far is the soup from a known gate in edit distance).
This replaces "unstructured sparse soup only" (ENGINE_CARD l.162-164).

Step 2 -- refactor the substrate to have a combinator and a protected program.
- Give commit an opcode-selected binary operation f(old, incoming) from a small typed table
  (replace, add, xor, and, min), so a site is a gate, not a wire. Separate code fields from data
  fields (write permission by field class) so data flow stops rewiring the circuit at every noise
  event.
- Memoryful arbitration (NC01 s7): priority carries across ticks, so a contested channel can be a
  stable switch.
- Formalism: treat the lattice as a graph-rewriting system (local rules as double-pushout
  productions, in the spirit of chemlambda / reaction automata, which AETH-01 design rejected and
  never built) or as a typed combinator chemistry (Fontana-Buss AlChemy: typed lambda terms that
  react by application), so that composition is a primitive of the physics rather than a hoped-for
  emergent.

Step 3 -- replace hand-walked law search with a law-space screen. Parameterise rules as
compositions of phase operators (decode/emit/arbitrate/commit/settle variants), enumerate
hundreds to thousands cheaply at 128^2 x 2,500 ticks (stationary-time measured: NC01 H5), and
screen automatically with P1 + decodability + an open-endedness battery (MODES: change, novelty,
complexity, ecology; Dolson et al.), plus effective information / causal emergence (Hoel) and an
MDL ratio (description length of the trajectory given the rule vs given the rule plus a
k-local predictor). Report Langton-lambda-like order parameters so the edge-of-chaos band can be
located rather than guessed.

Step 4 -- amplification, decided explicitly. The no-steering doctrine is what makes negatives
clean, and also what guarantees that a 1e-6 structure is never kept. Introduce, as a separate
arm with its own semantics id, the minimal amplifier that is not a task score: heredity of a
multi-site template (a copy rule acting on a 2x2 block) plus resource competition between
templates (multi-agent dynamics via shared energy), and test whether variants with longer causal
reach outcompete others (compositional credit assignment emerges only if reach pays energy).
Keep the doctrine arm as the control.

---------------------------------------------------------------------------------------------------
## 5. What would change this verdict
---------------------------------------------------------------------------------------------------

- Upgrade to VIABLE_SEED: TEST-4 passes all three clauses for r1x1 on >= 3/4 seeds (decoding at
  r >= 2 above exchange-only; a generation-2 causal descendant by single-site restore; not
  explained by own-history plus displaced byte), AND a hand-built two-input gate is shown to work
  in r1x1 under twin assay. That would be a composing mechanism with a credible path (Steps 2-4).
- Downgrade to DEAD_END: TEST-4 fails its kill criterion AND the instrument stack fails to transfer
  (e.g. the twin/locality assay cannot be adapted to a non-spatial engine such as the Z80
  machines or PTE, or reveals nothing there that their own instruments did not).
- Audit error I would accept: if the unread files (AETHER_SPEC, PHYSICS_DESIGN_01..03, aeth_prov.py
  body) contain a constructed-structure experiment or a combining primitive in v1 that I missed,
  sections 3a-3b on constructive capability are wrong. I found no such experiment in any result
  document, campaign table or CAMPAIGN_STATE.json, and the engine card says none exists.
