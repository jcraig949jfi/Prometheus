# PREREG_P11 -- Does P-11 certify heredity, or only construction? Adversaries, candidate certificates, stop rules

Status: PHASE 1 DESIGN ONLY. Written 2026-09-28 by an Artemis worker (ubu002). No experiment has been run and no NPE code
has been executed. Every number below that is not quoted from a committed file (path@sha:line) is a PREDICTION or a
DESIGN VALUE and is fixed by this file before any execution.
Thread: roles/Artemis/backlog/threads/FR-011.md (NEW tally, lines 33-40). Prior art: roles/Artemis/backlog/prior_art/
PA_origin_of_replication.md (W14 Griesemer reproducer criterion; P4 detector fragility; U3 capacity transmission).
Operator question (intent): the WEAKEST additional criterion that separates genuine hereditary replication from
self-painting WITHOUT excluding unfamiliar legitimate replication mechanisms, and without privileging block copy or
conventional (high-entropy, identity-encoded) genomes.
Coordinator inputs folded in (2026-09-28): (i) NPE's own seeded BYTEWISE replicator is used as an NPE-native instance of
adversary 3 (specimen Z3n, s2); (ii) composition measures (dominant-byte share, same-composition shuffle baseline) are
DIAGNOSTICS ONLY and are not eligible to be selected as the certificate (s3, s5).

## 0. Pinned sources (all SHAs are ancestors of main)

| role | path | sha |
|---|---|---|
| P-11 implementation | roles/Nestor/campaigns/z80atlas-verify-2026-09-22/p11.py | f28e5fd72 (unchanged through d7641744d and main) |
| P-11 thresholds | roles/Nestor/campaigns/z80atlas-verify-2026-09-22/constants.py | d7641744d (P-11 values unchanged on main) |
| P-11 specification | roles/Nestor/campaigns/z80atlas-verify-2026-09-22/P11_SPEC.md | main (spec text; values match d7641744d) |
| VM that S1-C actually ran | roles/Nestor/campaigns/z80atlas-forensics-2026-09-23/substrate/z8.py | d7641744d |
| VM in the verify tree | roles/Nestor/campaigns/z80atlas-verify-2026-09-22/z8.py | d7641744d |
| original 72-h VM / grammar | roles/Nestor/campaigns/z80atlas-2026-09-19/z8.py, grammar.py | aa5833488 |
| world wiring of P-11 | roles/Nestor/campaigns/z80atlas-verify-2026-09-22/world.py | d7641744d |
| S1-C driver | roles/Nestor/campaigns/z80atlas-forensics-2026-09-23/forensic.py, p11_reassay.py | d7641744d |
| S1-C data | roles/Nestor/campaigns/z80atlas-forensics-2026-09-23/P11_REASSAY.jsonl, S1C_P11_REASSAY.md | d7641744d |
| NPE seeded-replicator calibration | roles/Nestor/campaigns/z80atlas-2026-09-19/CALIBRATION.json:128-140 | b05a34f1b |

VM version check (done in phase 1 by reading diffs, no execution): the verify z8.py differs from aa5833488 z8.py only by
(a) the P-11 provenance branch in the write path (write value unchanged; records `prov` on value change and `prov_lit`
on every write) and (b) the H1 output gate, which is a no-op at its default 0. The forensic substrate z8.py has the same
provenance branch plus an `ev` telemetry callback that defaults to None, and no H1 gate. Execution gate E0 (s6) confirms
equivalence empirically on this panel.

Later P-11 history checked: `git log --all -- .../p11.py` shows one commit (f28e5fd72). Later work USES P-11 without
changing it: X-DONOR-RATE fresh-state assay (roles/Nestor/campaigns/c9x-explore-2026-09-24/x_donor_rate/run_dr.py @3ba6d8a97),
X-CERT-BREAK (eb3076b50), X-STALL / X-STERILE (roles/Nestor/FINDINGS.md:305-316, "P-11 certifies a causal rebuild of the
victim half, not a fertile child").

## 1. P-11 as implemented, and exactly what it tests

### 1.1 Where it runs
An event is a PAIR_EXECUTION interaction on a pair tape: `tape = bytearray(_pow2(2*n))`, genome a at offset 0, b at offset n,
a executes first, then b, each for one slice of `t["slice"]` instructions (S 220, M 300, L 360; grammar.py:240-242
@d7641744d), from pc = own base, with carried registers (world.py:752-760, 786-812 @d7641744d). Only victim halves that pass
the PREDECESSOR criterion are assayed (world.py:793; forensic.py:185-192 in S1-C).

### 1.2 The criteria (p11.py @f28e5fd72; thresholds constants.py:37-45 @d7641744d)

| id | rule | code |
|---|---|---|
| P0 predecessor (prefilter, kept) | observed victim final fidelity to donor >= 0.90 (measured AFTER world mutation), victim fidelity to its own prior bytes < 0.90, donor `writes_other` >= 0.25 n | p11.py:153-156; constants.py:37-39 |
| C1 randomize | victim half := n uniform random bytes (seeded per draw); victim registers KEPT as observed | p11.py:117-122; P11_SPEC.md s3 item 3 |
| C2 rebuild | after re-executing the interaction (private tape, private RNG, same budget, ops mask, copy-mutation rate), victim fidelity to the donor's PRE-interaction genome >= 0.90 | p11.py:126-135; constants.py:41 |
| C3 directed set | D = positions where initial victim byte != donor byte and final == donor byte | p11.py:97-102 |
| C4 authorship | >= 0.90 of D last value-changed (`prov`) by the donor context; empty D fails | p11.py:136; constants.py:42 |
| C5 matched control | same draw with the donor's out-of-half writes blocked (z8 OWN policy): victim fidelity to donor < 0.90 | p11.py:87, 130-137; constants.py:43 |
| decision | draw passes iff C2 and C4 and C5; event is P-11 causal iff P0 and >= 2 of 3 draws pass | p11.py:145-147; constants.py:44-45 |

Fidelity is positional byte identity over the longer length (p11.py:54-60). The tape is freshly zeroed for every
interaction (p11.py:76-78), so nothing outside the two halves persists between interactions.

### 1.3 What P-11 tests, stated exactly
P-11 tests ONE interaction: "from this state, the donor's own writes turn a random partner half into a >= 90%
positional match of the donor's current bytes, and they are necessary for that." It is a test of causal CONSTRUCTION
of a donor-identical half.

What it does NOT test (each is a design fact read from the code, not an inference):
- It never perturbs the DONOR. The only counterfactual is on the victim (C1) and on the donor's write permission (C5).
  Whether the donor's VARIATION reaches the child is never asked. A donor that writes the same pattern whatever its own
  variable bytes are passes identically. This is the central gap.
- It is one generation deep. Whether the child can itself reproduce is not tested (FINDINGS.md:312 says the same).
- C2 is identity-encoded: the child must match the donor's own bytes. A child in a different encoding (complement,
  translation) fails C2 even when it deterministically regenerates the parent form.
- It assumes one donor and one victim half. Heredity carried by a host executing a guest's bytes, or by two cooperating
  tapes, has no single donor that writes a donor-identical copy.
- C2's threshold is a composition trap: a donor whose bytes are >= 90% one value X passes C2 by writing X over ~0.9 n
  cells, regardless of order. For near-homopolymers C2 is nearly the same as "wrote the dominant byte n times".
- C5 is nearly implied by C2+C4 (P11_SPEC.md s4; decisive in 2 of 7,919 events, S1C_P11_REASSAY.md:28-32).

### 1.4 Committed-data facts this preregistration starts from (no execution; my arithmetic over P11_REASSAY.jsonl @d7641744d)
- 57 runs with >= 1 P-11 event: BLOCK 47 / 531, BYTEWISE 10 / 500 (matches FR-011:33-40).
- Near-homopolymer first-P-11 donors (dominant byte share >= 0.90): BYTEWISE 10/10 (0x36 x5, 0xfc x2, 0x39, 0x01, 0xc0);
  BLOCK 14/47 (0x36 x7, 0x00 x2, 0x2a, 0xfb, 0xc3, 0x3a, 0x21). So 24 of 57 P-11 survivors are near-homopolymers, 12 of
  them 0x36. No donor falls in [0.80, 0.90). BYTEWISE donors containing ED B0/B8: 0; BLOCK: 34/47.
- P-11 depth: 55 runs depth 1, 2 runs depth 2 (both BLOCK: 7ae3f9c1437c8000-s54765-tL-a0, c2a87e5970ad345d-s80949-tL-a0).
- Only the FIRST P-11 donor genome per run is committed; victim genomes and pre-interaction registers are NOT committed
  (per-event files are gitignored, S1C_P11_REASSAY.md:3-6; the frozen observatory lives on another host, forensic.py:36-39).
  So the 57 events cannot be replayed exactly here; s4 uses a fresh-state re-assay (the X-DONOR-RATE protocol).

### 1.5 An analytic prediction about the BYTEWISE arm (zero CPU; tested by specimens Z3b, Z3u96)
A pair interaction is one slice from pc = base, so a copy must finish inside one slice. In z8 the cheapest bytewise
copy loop I can write is 5 instructions per byte (LD A,(HL); LD (DE),A; INC HL; INC DE; JR, unterminated); NPE's own
terminated loop is 8 per byte (world.py:256-262). A constant painter loop is 3 per byte (LD (HL),n; INC HL; JR). C2
needs ~0.9 n cells rebuilt. With setup cost ~2-7 steps: bytewise copier n_max ~ 71 (L), 59 (M), 43 (S) at 5/byte and
44 / 36 / 26 at 8/byte; painter n_max ~ 119 / 99 / 72. Prediction A0: in the 96-byte representations (Z8_SHARED,
Z8_SEPARATED) no bytewise copier can satisfy C2 at any tier while a painter can; in Z8_64 the 8-step loop cannot but a
5-step loop can at M/L. If true, P-11 in the BYTEWISE arm is structurally tilted toward painters for long genomes,
independently of what evolution produced. This is a claim about the budget, not about fitness.

## 2. Adversary specimens and ground truth

### 2.1 Ground-truth definition (fixed here)
"Hereditary" = there exist parental differences, reachable by single-byte substitution (the unit the world's mutation
operators produce), that cause consistent offspring differences which are themselves re-transmitted to later
generations. "Transmitted bits" (truth) = log2(number of distinct stably re-transmitted descendant classes reachable
from the specimen by one substitution, counting the unperturbed class). For copiers this is large and the measured
value is a LOWER BOUND set by the perturbation set; for the painter families it is small and exact. A child that is
built causally but is sterile carries 0 bits of heredity (Griesemer W14: reproduction must transmit the capacity to
reproduce). A one-generation "difference" that the child cannot pass on is construction, not heredity.

### 2.2 Harnesses
- H-PAIR (z8, NPE-native): `p11.interact` from p11.py @f28e5fd72 unchanged, on the S1-C z8 (forensic substrate
  @d7641744d). Fresh registers (None, 0, 0) for both halves. Donor side as stated per specimen. Budget, ops mask, copy
  rate and tape length from the specimen's cell by world.py rules (REP_LEN world.py:39, MUT_RATE :40, _ops_mask :205-219,
  tape = _pow2(2n) :754, slice grammar.py:240-242). Ops mask for PAIR_EXECUTION = 0x08 (SENSE) | 0x02 if self_location
  PRIMITIVE | 0x04 if PC_RELATIVE | 0x20 if BLOCK. No ALLOC/BIRTH bit in pair-tape cells.
- H-HOST (z8, NPE-native endogenous): my own stdlib host that calls NPE `z8.run` unchanged with FREE policy and
  on_alloc/on_birth callbacks giving one child slot, multi-slice with carried pc/registers, mirroring world._execute /
  _on_alloc / _on_birth semantics (world.py @d7641744d). Used only for Z3n. The child slot's pre-image is the draw's
  random bytes (the "victim" analogue).
- H-GUEST (z8): H-PAIR with a fixed host program in half 0 and the lineage genome in half 1; the next generation takes
  the half-0 result as the lineage genome and a fresh host. Used for Z5a.
- H-TV (toy, stdlib, needed where z8 cannot express the case): a byte VM module `tv.py` exposing the SAME interface
  p11.py expects of `z8` (Ctx(mem, base, length, policy=, rng=, copy_mut_rate=, sense=); attributes regs, fz, fc, prov,
  prov_lit, who, writes_other; constants OWN, ARENA; run(ctx, pc, budget, ops_enabled=)). The ORIGINAL p11.assay then
  runs unmodified on toy specimens: no port of P-11 is written.
- H-QUAD (toy): 4-region tape for the two-tape cooperative replicator (TV-5b).

### 2.3 Toy VM (TV) specification
Tape of T bytes, addresses mod T. Decoding is strand-symmetric: d(x) = x if x < 0x80 else x ^ 0xFF (so a byte and its
complement mean the same instruction). Heads: pc, R, W, counter K. Writes go through the same policy/provenance rule as
z8 (value-change -> prov = who; any write -> prov_lit = who; out-of-policy writes dropped and counted; writes outside
[base, base+n) count as writes_other).

| d(x) | name | effect (steps) |
|---|---|---|
| 01 | SEEK | R = base; W = (base + n) mod T; K = 0 (1) |
| 02 | MOV | if K < n: mem[W] = mem[R] (bit-flip with prob cmr); R++, W++, K++ (1) |
| 03 | CMOV | as MOV but writes mem[R] ^ 0xFF (1) |
| 04 | REP | if K < n: pc = pc - 1 (re-execute previous op) (1) |
| 05 | HALT | stop (1) |
| 06 | XCOPY | R = base XOR n; W = (R + 2n) mod T; copy n bytes (n) |
| 07 | INCC | mem[(base + n + 5) mod T] += 1 (1) |
| 10-1F | SPk | if k in the ISA's active painter alphabet: write d(x) at (base + n + j) mod T for j < n, then HALT (n); else NOP |
| 20 | PERIOD | write 0x20, 0x21 alternately at (base + n + j), j < n, then HALT (n) |
| 40 | HASH | write 0x40 then sha256-stream(own n bytes)[0:n-1] at base + n.., then HALT (n) |
| other | NOP | (1) |

Budget 4n + 16. n = 32 unless stated. Cargo bytes are sha256-derived from the specimen id (fixed seed), avoiding no values.

### 2.4 Specimens (required panel unless marked STRESS)

Hex is the full genome prefix; "+ cargo k" = k sha256-derived bytes. Truth bits for copiers are lower bounds as noted.

| id | adversary | harness / cell | genome | design facts (checked by gate G, s5) | truth: hereditary / bits | P-11 prediction |
|---|---|---|---|---|---|---|
| Z1 | 1 homopolymer self-painter (z8) | H-PAIR; Z8_SHARED n=96, tape 256, tier L (360), BYTEWISE/NONE mask 0x08; donor side 0 | `21 60 00 36 36 23 18 FB` + 0x36 x 88 | LD HL,0x0060; loop LD (HL),0x36; INC HL; JR -5 (3 steps/cell, 119 cells < 256, no self-overwrite); 0x36 share 90/96 = 0.9375; child = 0x36 x 96 (fid 0.9375); child as donor writes only address 0 (sterile) | NO; 0 bits. (One-generation construction: the operand at site 4 sets the child's colour, 8 "bits" that die with the sterile child) | CERTIFY |
| TV-1 | 1 closed homopolymer painter | H-TV; alphabet {0x10} | 0x10 x 32 | child = parent (closed, fertile); every single-site variant yields the same child (site 0 non-painter -> site 1 paints) | NO; 0 bits (fertile but variation-free) | CERTIFY |
| Z2 | 2 periodic low-entropy painter (z8) | H-PAIR; Z8_SHARED n=96, tier L, mask 0x08, side 0 | `21 60 00 36 36 23 36 23 23 18 F8` + positions 11..95 = 0x36 (even) / 0x23 (odd) | loop writes 0x36, 0x23 alternately (5 steps / 2 cells); child = (36 23) x 48; fid to parent 89/96 = 0.927; dominant share 0.48 (not a homopolymer); child sterile (every instruction = LD (HL),0x23 at HL = 0) | NO; 0 bits | CERTIFY |
| TV-2 | 2 closed periodic painter | H-TV | (20 21) x 16 | child = parent; site-0 variants fall through to site 2 | NO; 0 bits | CERTIFY |
| Z3 | 3 block copier (z8) | H-PAIR; Z8_32 n=32, tape 64, tier S, PRIMITIVE x BLOCK mask 0x2A; side-agnostic | `ED 32 54 5D 7B 81 5F ED B0 76` + cargo 22 | SELF; DE = base + 32 (wraps mod 64); LDIR 32 bytes; child = parent | YES; >= log2(1 + 3*22) = 6.07 (lower bound, m = 3) | CERTIFY |
| Z3b | 3 bytewise copier (z8) | H-PAIR; Z8_32, tier M (300), PRIMITIVE x BYTEWISE mask 0x0A | `ED 32 54 5D 7B 81 5F 7E 12 23 13 0B 78 B1 20 F7 76` + cargo 15 | NPE's own 8-step loop; 263 steps <= 300; child = parent | YES; >= log2(1 + 3*15) = 5.52 | CERTIFY |
| Z3u96 | 3 bytewise copier where one slice cannot finish (s1.5) | H-PAIR; Z8_SHARED n=96, tier L, mask 0x08, side 0 | `21 00 00 11 60 00 7E 12 23 13 18 FA` + cargo 84 | unterminated 5-step loop; copies ~71 of 96 cells (fid ~0.74); child's first 71 cells include the loop, so it copies again | YES (partial genome: ~71 heritable sites) | REJECT (C2) -> false negative |
| Z3n | 3 NPE-native seeded replicator (coordinator input) | H-HOST; Z8_64, ENDOGENOUS_COPY x PRIMITIVE x BYTEWISE mask 0x0B, tier S slices | z8.asm of world.py:256-262 source @d7641744d, expected `ED 32 ED 30 28 01 76 ED 32 7E 12 23 13 0B 78 B1 20 F7 ED 32 ED 31 76` + cargo 41 | assert asm output == this hex; BIRTH within 10 slices; child = parent; NPE's own REPL evidence rule (fid >= 0.90, wrote >= 0.50) passes. Caveat: the committed calibration run of this control carries flags SANDBOX_ESCAPE, STALE_RESIDUE_BIRTH (CALIBRATION.json:128-140 @b05a34f1b); the host records out-of-window writes | YES; >= log2(1 + 3*41) | N/A (P-11 is pair-tape only); REPL analogue reported |
| TV-3 | 3 toy copier | H-TV | `01 02 04 05` + cargo 28 | child = parent | YES; exhaustive V: >= log2(1 + 255*28) | CERTIFY |
| TV-4 | 4 complement cycle (offspring encoding differs) | H-TV | `01 03 04 05` + cargo 28 | child = complement(parent), which decodes as the same program; grandchild = parent | YES; same as TV-3 | REJECT (C2: fid ~0) -> false negative |
| Z5a | 5 host-mediated heredity (information in the guest, executed by the host) | H-GUEST; Z8_32, tier S, PRIMITIVE x BLOCK mask 0x2A; host in half 0, guest Q in half 1 | host `ED 32 54 5D 7D 81 6F ED B0 76` + cargo 22 (redrawn per generation); guest Q: byte 0 = 0x76, byte 9 = 0x76, other 30 bytes cargo | host: SELF; DE = own base; HL = base + 32 (partner); LDIR pulls Q over itself; pc then lands on Q[9] = HALT; Q halts at once; new half 0 = Q | YES at the (host + guest) system level; >= log2(1 + 3*30) | REJECT (P0: donor Q wrote 0 < n/4) -> false negative |
| TV-5b | 5 two cooperating tapes | H-QUAD; tape 4n = 128; pair (A0, A1) in regions 0,1; child pair appears in regions 2,3 | A0 = `06 05` + cargo 30; A1 = `06 05` + cargo 30 (different seeds) | A0 copies A1 -> region 3, A1 copies A0 -> region 2; neither member alone copies itself | YES (pair is the unit); >= log2(1 + 3*60) | REJECT (as the code can be run: either member as donor copies the victim onto itself; C2 fails) -> false negative |
| TV-6 | 6 positive control, 2-state painter | H-TV; alphabet {0x10, 0x11} | 0x10 x 32 (state A); 0x11 x 32 (state B) | A -> A, B -> B, closed; the site-0 substitution 0x10 -> 0x11 (also 0xEE) switches lineage state | YES; exactly 1 bit | CERTIFY |
| TV-6k | 6 positive control, 16-state painter | H-TV; alphabet 0x10..0x1F | 0x10 x 32 | 16 closed states reachable at site 0 | YES; exactly 4 bits (exhaustive V) | CERTIFY |
| Z6h | 6 low-entropy GENUINE copier (counter-example to any composition rule) | H-PAIR; Z8_SHARED n=96, tier L, BLOCK/NONE mask 0x28, side 0 | `21 00 00 11 60 00 01 60 00 ED B0 76` + 0x00 x 84 (state A); same with byte 95 = 0x01 (state B) | LDIR 96 bytes 0 -> 96; child = parent; dominant byte 0x00 share 88/96 = 0.917 (inside the BYTEWISE painters' 0.91-0.96 band) | YES; >= log2(1 + 3*84); the A/B pair demonstrates 1 realised bit | CERTIFY |
| TV-7 | STRESS: information-preserving scrambler (no resemblance) | H-TV | `40` + cargo 31 | child = 0x40 + hash(parent); each variant gives a distinct lineage whose form changes every generation | NOT hereditary in the resemblance sense (offspring carry information about, but do not resemble, parents); NOT in the adequacy set | REJECT (C2) |
| TV-8 | STRESS: copier with a generation counter | H-TV | `01 02 04 07 05` + cargo 27 | child = parent with site 5 incremented each generation | YES; all cargo except site 5 | CERTIFY |
| NAT-57 | natural P-11 survivors | H-PAIR in each run's own cell and tier | first_p11_event.donor_genome of each row with n_p11_events > 0 | s4 | unknown; predicted 0 bits for all 24 near-homopolymers | re-assayed fresh (s4) |

Why the toy VM is needed (z8 cannot express these, argued from the ISA at z8.py @d7641744d):
- Closed painters (TV-1, TV-2, TV-6): z8 has no single-byte instruction that both writes and advances a pointer (writes:
  LD (HL),r / LD (HL),n / LD (BC),A / LD (DE),A / INC,DEC (HL); advancing needs a separate INC or LDIR). So X^n is never
  a painter, and every z8 painter's child lacks the non-X machinery bytes: z8 painters are sterile. Z1/Z2 are the z8
  forms; TV-1/TV-2 remove sterility so that "fertile but variation-free" is tested separately from "sterile".
- Complement cycles (TV-4): the complement of z8 code is different code (ED B0 -> 12 4F = LD (DE),A; LD C,A). I found
  no z8 construction; this is not a proof of impossibility.
- Two cooperating tapes (TV-5b): p11.interact has exactly two halves and one donor.
- Environment-carried heredity is NOT specified: p11.interact zeroes the tape every interaction, and an environment
  cell that is merely never overwritten would be persistence, not transmission. Host-mediated heredity (Z5a) is the
  expressible branch of adversary 5.

## 3. Candidate certificates

Common machinery (H-*), fixed:
- Perturbation set V(G) for a genome of n sites: for each site i, m = 3 substitutions {x ^ 0x01, x ^ 0x80, r_i} where
  r_i is sha256-derived and != x, != the other two. For TV specimens V is EXHAUSTIVE (all 255 alternatives at every
  site; 32 x 255 = 8,160 variants) so that the painter-family bit counts are exact. For TV-5b, sites span both tapes
  (2n). For Z5a, sites are the guest's.
- Generations g = 1..4. The descendant at g is the victim half (or child slot / new half 0 / child pair) after the
  generation-g interaction, re-placed at the ORIGINAL donor side for g+1, with fresh registers.
- Common random numbers: victim/child-slot bytes for generation g, draw k (k = 0, 1, 2) are sha256(specimen, g, k),
  IDENTICAL across all variants. Copy mutation 0 for all certificate computations (the certificate is a property of the
  reproduction map); P-11 itself is run at the cell's copy rate as implemented.
- Difference signature: Delta_g(v, k) = {(pos, byte) : G_g(v, k)[pos] != G_g(0, k)[pos]}. Delta_g(v) is DEFINED iff the
  same non-empty signature occurs in >= 2 of the 3 draws (lethal variants leave draw-dependent residue and so drop out
  automatically).

| id | name | rule (accept iff) | what it privileges | treatment of 4 (re-encoding) | treatment of 5 (distributed / host) |
|---|---|---|---|---|---|
| FERT | capacity transmission (depth-2 closure) | P-11 certifies the event AND the draw's child, placed as donor against fresh random victims, is P-11-certified (>= 2 of 3 draws) | identity encoding (inherits C2) and the pair model; blind to variation | rejects (C2 at both steps) | rejects (P0 / C2) |
| CVT-1 | counterfactual variant transmission, 1 generation | >= 1 variant v with Delta_1(v) defined. TB1 = log2(1 + #distinct Delta_1 classes) | nothing about encoding or composition; but counts one-shot construction | accepts (difference re-encoded, still consistent) | accepts if the system state (both tapes / guest) is the measured unit |
| CVT-2 | CVT with re-transmission | >= 1 v with Delta_1(v) AND Delta_2(v) defined. TB2 = log2(1 + #distinct Delta_2 classes) | requires a fertile lineage; no encoding, composition, position or mechanism assumption | accepts | accepts (unit = declared system) |
| CVT-R | CVT with recurrent difference | CVT-2 AND (Delta_3(v) == Delta_2(v) OR Delta_4(v) == Delta_2(v)) for >= 1 v. TBR = log2(1 + #distinct recurrent Delta_2 classes) | adds "the transmitted difference comes back with period <= 2" (resemblance of form); a counter elsewhere in the genome does not break it (TV-8) | accepts (period 2) | accepts |
| LOCAL | template locality | >= 0.25 n sites i for which some v at i gives Delta_1(v) defined with exactly ONE position | template-style, one-to-one positional copying (conventional genomes) | accepts (complement is one-to-one) | accepts |
| SHUF | DIAGNOSTIC ONLY, not eligible | mean P-11 draw fidelity minus mean fidelity of the parent to 200 same-composition shuffles of itself >= 0.10 | high-entropy identity-encoded genomes; composition | rejects (fid ~0) | rejects |
| DOM | DIAGNOSTIC ONLY, not eligible | dominant-byte share < 0.80 (the rule the adversarial reviewer ruled out) | conventional genomes | n/a | n/a |

Notes on the ladder: CVT-1 is the minimum addition that asks P-11's missing question (perturb the donor, not the
victim). CVT-2 adds one more generation, which is Griesemer's capacity condition applied to the DIFFERENCE rather than
to the genome. CVT-R adds form recurrence. Each rung's acceptance set contains the next rung's. CVT certificates carry
their own causal content (the child difference is caused by the parent difference under common random numbers), so
they do not need P-11's C2 and can be read either standalone or as "P-11 causality (C4/C5) plus CVT". Because P-11's P0
and C2 reject specimens 4 and 5 by construction, "P-11 AND X" can never accept them; the adequacy test (s5) therefore
evaluates each certificate STANDALONE and reports "P-11 AND X" beside it.

Predicted confusion (A = accept, R = reject; x = wrong against truth). These are predictions, fixed now:

| specimen (truth) | P-11 | FERT | CVT-1 | CVT-2 | CVT-R | LOCAL | SHUF diag | DOM diag |
|---|---|---|---|---|---|---|---|---|
| Z1 (no) | A x | R | A x | R | R | R | R | R |
| TV-1 (no) | A x | A x | R | R | R | R | R | R |
| Z2 (no) | A x | R | A x | R | R | R | A x | A x |
| TV-2 (no) | A x | A x | R | R | R | R | A x | A x |
| Z3, Z3b, TV-3 (yes) | A | A | A | A | A | A | A | A |
| Z3u96 (yes) | R x | R x | A | A | A | A | R x | A |
| Z3n (yes) | n/a | n/a (REPL analogue A) | A | A | A | A | A | A |
| TV-4 (yes) | R x | R x | A | A | A | A | R x | A |
| Z5a (yes) | R x | R x | A | A | A | A | R x | A |
| TV-5b (yes) | R x | R x | A | A | A | A | R x | A |
| TV-6 (yes, 1 bit) | A | A | A | A | A | R x | R x | R x |
| TV-6k (yes, 4 bits) | A | A | A | A | A | R x | R x | R x |
| Z6h (yes) | A | A | A | A | A | A | A | R x |
| TV-7 STRESS (no) | R | R | A x | A x | R | R | R | A x |
| TV-8 STRESS (yes) | A | A | A | A | A | A | A | A |

Predicted outcome: P-11 is UNSOUND for heredity (certifies Z1, TV-1, Z2, TV-2 alongside Z3) and OVER-STRICT (rejects
TV-4, Z5a, TV-5b, Z3u96); CVT-2 is the weakest adequate certificate for the operator's required panel; CVT-R is needed
only if TV-7-type reproduction must count as non-hereditary.

## 4. The measurement

### 4.1 Constructed panel
For every specimen in s2.4: (a) design-fact gate G (below); (b) P-11 original: an OBSERVED event (specimen as donor at
its side, the other half = sha256-derived random bytes, cell copy rate), P0 evaluated on it, then p11.assay with K = 20
different event seeds; P-11 CERTIFIES iff P0 holds and assay pass rate >= 0.5; (c) FERT, CVT-1, CVT-2, CVT-R, LOCAL on
the V x 3 draws x 4 generations grid; (d) diagnostics SHUF, DOM, dominant byte, genome entropy. Output: one row per
specimen with every verdict, TB1/TB2/TBR, heritable fraction h = (#variants counted)/|V|, and the confusion table
against s2.4 truth. Sensitivity (reported, not decision-bearing): CVT-2 at the cell's copy rate; Z-specimens with the
donor at the other side where the construction is side-agnostic (Z3, Z3b).

### 4.2 Re-application to the 57 real P-11 survivors (sufficiency of committed data)
Committed data suffice only for a FRESH-STATE re-assay: donor genome + cell + tier are committed; the event's registers,
victim genome and epoch state are not. Protocol (the X-DONOR-RATE protocol, run_dr.py:32-56 @3ba6d8a97, applied to
these donors):
1. For each of the 57 rows: genome = first_p11_event.donor_genome; n, tier slice, ops mask, copy rate from the row's
   cell (cross-checked against world.Runner(cell, 1, tier) fields; any mismatch stops the run).
2. Fresh-state P-11: for each side s in {0, 1}, K = 50 assays with the partner half zero and victim randomized by the
   assay itself (exactly run_dr.py's call). Side s RECERTIFIES iff pass rate >= 0.5. A donor with no recertifying side is
   STATE_DEPENDENT and is reported but not classified.
3. For each recertifying side: FERT, CVT-1, CVT-2, CVT-R, LOCAL (m = 3 perturbations per site), SHUF, DOM.
4. Mechanism audit (descriptive, per BYTEWISE and per near-homopolymer donor): the per-step write address sequence of
   the donor in one fresh-state draw, summarised as steps per written cell and the set of written values.
5. Report by stratum: copy_primitive (BLOCK / BYTEWISE) x dominance (>= 0.9 / < 0.9) x representation; plus the two
   depth-2 BLOCK runs named in s1.4.
Also recorded: the 1,031 - 57 non-survivors are NOT re-assayed (their donor genomes are not committed).

## 5. Discriminator and STOP RULES (fixed before execution)

### 5.1 Execution gates (run first; failing a gate stops or excludes, never rescues)
- E0 VM equivalence: every z8 specimen's P-11 records and CVT descendants are byte-identical under the forensic
  substrate z8 and the verify z8 @d7641744d, and the aa5833488 z8 gives identical tapes with provenance off. Mismatch ->
  STOP, report, no verdicts.
- E1 determinism: each specimen's full record computed twice is identical. Mismatch -> STOP.
- E2 timing pilot: Z1 full pipeline timed; projected total > 45 CPU-min -> apply the ONE pre-registered fallback (natural
  K 50 -> 20; m stays 3), record it; still > 60 CPU-min -> STOP.
- G design-fact gates per specimen (s2.4 column "design facts", measured by the harness from tapes and step traces, not
  by any certificate). A failing specimen gets ONE repair (byte diff and reason logged in the result file) and is
  re-gated; failing again -> EXCLUDED and reported. If exclusions leave REQUIRED_NEG or REQUIRED_POS without any z8 or
  without any TV member, the affected verdict is INCONCLUSIVE.

### 5.2 D1: is P-11 sound as a HEREDITY certificate?
Sets: NEG = {Z1, Z2, TV-1, TV-2} (0 bits); POS_P11 = {Z3, Z3b, TV-3, TV-6, TV-6k, Z6h} (hereditary and inside P-11's
identity / pair model).
- P-11 UNSOUND FOR HEREDITY iff P-11 CERTIFIES >= 1 member of NEG AND >= 1 member of POS_P11 (same verdict on a 0-bit
  and a hereditary specimen: P-11 does not distinguish self-painting from copying).
- P-11 SOUND FOR HEREDITY (on this panel) iff it certifies NO member of NEG and ALL of POS_P11.
- Anything else: MIXED; each cell reported, no summary claim.
- Separately, P-11 OVER-STRICT (scope finding) iff it rejects >= 1 of {TV-4, Z5a, TV-5b, Z3u96}.
- A0 (s1.5) is SUPPORTED iff Z3u96 fails C2 AND Z1 passes C2 in the same cell and tier; otherwise NOT SUPPORTED.

### 5.3 D2: which certificate is the WEAKEST ADEQUATE one?
REQUIRED_POS = {Z3, Z3b, Z3u96, Z3n, TV-3, TV-4, Z5a, TV-5b, TV-6, TV-6k, Z6h}; REQUIRED_NEG = {Z1, Z2, TV-1, TV-2}.
- Eligible: FERT, CVT-1, CVT-2, CVT-R, LOCAL. SHUF and DOM are never eligible (coordinator ruling), whatever they score.
- ADEQUATE(X) iff X accepts every REQUIRED_POS specimen and rejects every REQUIRED_NEG specimen, AND (for the
  bit-reporting CVT family) the bit calibration is exact: TB(TV-6) = 1, TB(TV-6k) = 4, TB(TV-1) = TB(TV-2) = 0 at X's
  own generation. (FERT on Z3n uses NPE's REPL rule as its analogue; FERT is predicted inadequate regardless.)
- WEAKEST ADEQUATE = the adequate certificate with the LARGEST acceptance set over the whole panel (required + STRESS +
  recertified natural donors). Ties -> fewer generations required -> no instrumentation beyond tape reads.
- STRESS reporting (fixed wording): if the weakest adequate certificate accepts TV-7 and CVT-R is also adequate and
  rejects TV-7 while accepting TV-8, the result reads "X is the weakest adequate certificate for the required panel;
  CVT-R is required if information-preserving but non-resembling reproduction (TV-7) must count as non-hereditary."
  If CVT-R rejects TV-8, CVT-R is recorded as OVER-STRICT on counters and is not recommended.
- NO ADEQUATE CANDIDATE: report the failing cells. No threshold, perturbation set or generation count may be tuned
  after seeing results; any new candidate needs a new preregistration.

### 5.4 D3: the natural 57 (secondary, never overrides D1/D2)
Using the certificate selected by D2 (and all others as columns):
- N1 "In the BYTEWISE arm P-11 certified construction without heredity": iff >= 5 BYTEWISE donors recertify fresh AND
  every recertified BYTEWISE donor has selected-certificate TB = 0. Fewer than 5 recertify -> INCONCLUSIVE
  (state-dependent; registers not committed).
- N2 "P-11-certified heredity exists in the BLOCK arm": iff >= 1 recertified BLOCK donor has selected TB >= 1. The two
  depth-2 runs are reported by name.
- N3 painter share: (#recertified with selected TB = 0) / (#recertified), exact Clopper-Pearson 95% CI, overall and per
  stratum; plus the same share among near-homopolymers vs the rest.
- Prediction (fixed, falsifiable): all recertified near-homopolymer donors (BYTEWISE and BLOCK) have TB2 = 0; a
  majority of recertified BLOCK donors with ED B0/B8 and dominance < 0.9 have TB2 >= 1. If a near-homopolymer donor
  shows TB2 >= 1, that is reported as a counter-example to the painter reading, with its trace.

### 5.5 What the outcomes mean for the program (stated now)
- D1 UNSOUND: every P-11-based heredity statement (S1-C "57 survive", C-RUNAWAY depths, FR-011's BYTEWISE tally) must
  be read as a construction count until re-scored with the D2 certificate in a NEW file.
- D1 SOUND: the FR-011 reading "P-11 cannot tell painting from copying" is withdrawn in FR-011 with this file cited.
- D2 selects X: X is proposed (not imposed) to Nestor as a companion to P-11, with the specimens as its test fixtures.

## 6. Execution plan (phase 2, only when told to execute)

### 6.1 Foreign code (read-only copies, never imported from the repository tree)
```
SCR=/tmp/claude-1000/-home-jcraig-Prometheus/78a7bd7b-da69-4758-859e-8a39e0df5734/scratchpad/p11
mkdir -p "$SCR/d764" "$SCR/aa58"
env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE git -C /home/jcraig/Prometheus archive d7641744d \
  roles/Nestor/campaigns/z80atlas-verify-2026-09-22/p11.py \
  roles/Nestor/campaigns/z80atlas-verify-2026-09-22/constants.py \
  roles/Nestor/campaigns/z80atlas-verify-2026-09-22/z8.py \
  roles/Nestor/campaigns/z80atlas-verify-2026-09-22/world.py \
  roles/Nestor/campaigns/z80atlas-verify-2026-09-22/grammar.py \
  roles/Nestor/campaigns/z80atlas-verify-2026-09-22/tasks.py \
  roles/Nestor/campaigns/z80atlas-verify-2026-09-22/anticheat.py \
  roles/Nestor/campaigns/z80atlas-forensics-2026-09-23/substrate/z8.py \
  roles/Nestor/campaigns/z80atlas-forensics-2026-09-23/P11_REASSAY.jsonl | tar -x -C "$SCR/d764"
env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE git -C /home/jcraig/Prometheus archive aa5833488 \
  roles/Nestor/campaigns/z80atlas-2026-09-19/z8.py roles/Nestor/campaigns/z80atlas-2026-09-19/grammar.py | tar -x -C "$SCR/aa58"
```
If world.py needs a further module from the same tree, it is added from the SAME sha by the same command (logged).
The sha256 of every extracted file is written into each result file. The substrate z8 and the verify z8 are loaded as
separately named modules (importlib, as forensic.py:46-55 does); p11.py and constants.py come from the verify copy.
No NPE test suite is run.

### 6.2 Files to write (all under roles/Artemis/challenge/p11/)
- `fetch_foreign.sh` -- the two commands above plus the sha256 manifest.
- `tv.py` -- toy VM (s2.3), z8-compatible interface; stdlib only.
- `specimens.py` -- every genome in s2.4 as literal hex (plus the asm-derived Z3n with its equality assertion) and the
  design-fact gates G.
- `harness.py` -- H-PAIR / H-HOST / H-GUEST / H-TV / H-QUAD generation steppers; common-random-number draws; fresh
  registers; side re-placement.
- `certs.py` -- P-11 wrapper (P0 + p11.assay, K seeds), FERT, CVT-1/2/R, LOCAL, SHUF and DOM diagnostics.
- `run_panel.py` -- gates E0-E2, G; constructed panel -> `results/PANEL.jsonl`, `results/CONFUSION.json`.
- `run_natural.py` -- s4.2 -> `results/NATURAL_REAPPLY.jsonl`, `results/NATURAL_SUMMARY.json`.
- `verdict.py` -- applies D1-D3 mechanically to the result files -> `results/VERDICT.json`.
- After the run: `RESULT_P11.md` (human summary citing the result files). multiprocessing Pool(4) over specimens / donors.

### 6.3 Cost (estimate; E2 measures it)
Assumed z8 speed ~1-2 us per instruction in CPython, so ~1-2 ms per pair interaction at slice 360.
- Constructed z8 (8 specimens): <= (3*96 + 1) variants x 3 draws x 4 generations ~ 3.5k interactions each, plus P-11
  (20 x 6 interactions) and FERT: ~1 CPU-min total.
- Toy (9 specimens, exhaustive V = 8,161 variants x 12 interactions of <= 144 toy steps): ~3-5 CPU-min total.
- Natural: fresh-state P-11 57 x 2 sides x 50 x 6 interactions = 34k interactions (~1 CPU-min) + CVT on <= 114
  recertified sides x <= 3.5k interactions (<= 400k interactions, ~7-13 CPU-min).
- Total ~15-20 CPU-min, ~5 min wall on 4 threads; RAM < 300 MB (records are aggregated per variant as they stream).
  Ceiling 60 CPU-min / 2 GB enforced by E2 and a per-worker RSS check (abort above 450 MB per worker).

### 6.4 Outputs
`results/PANEL.jsonl` (one row per specimen: gates, P-11 per-seed records, every certificate, TB1/TB2/TBR, h,
diagnostics), `results/CONFUSION.json` (certificate x specimen vs truth), `results/NATURAL_REAPPLY.jsonl` (one row per
donor x side), `results/NATURAL_SUMMARY.json`, `results/VERDICT.json` (D1, D2, D3 as the rules above produce them), and
`RESULT_P11.md`. All pure ASCII, sort_keys JSON.

## 7. Preservation
- Nothing under roles/Nestor/ is modified, re-run in place, or rescored. P11_REASSAY.jsonl / .json, S1C_P11_REASSAY.md,
  FINDINGS.md E-2/E-3 and every frozen record stay as committed. "1,031 admissible under the predecessor criterion" and
  "57 surviving P-11" remain true statements about those instruments.
- The natural re-application is a NEW forensic assay on committed donor genomes from a fresh state; it is written only
  to roles/Artemis/challenge/p11/results/NATURAL_REAPPLY.jsonl and NATURAL_SUMMARY.json, reported BESIDE the S1-C numbers
  and never in their place, and it is labelled "fresh-state, not the original event state".
- This file is frozen at its first commit. Any amendment is appended as a dated section below with the reason, and any
  amendment made after execution starts voids the affected stop rule's pre-registered status.
