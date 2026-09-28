# raid_B toy -- multiple transient memories (MTM) -- PREREGISTRATION

Status: EXPLORATORY. Written 2026-09-28 before any code was run. Not edited
after the first run (any change goes in RESULT.md as a labelled deviation).
Odysseus expeditionary worker, raid B (memory in materials).

## Question

Source phenomenon (Keim & Nagel, PRL 107, 010603, 2011; Paulsen, Keim &
Nagel, PRE 88, 032306, 2013; review Keim, Paulsen, Zeravcic, Sastry & Nagel,
RMP 91, 035002, 2019): a driven, dissipative, disordered system with NO
learning rule, trained by cyclic driving at several amplitudes, stores ALL of
them for a while, then, under continued driving of the same inputs, forgets
all but the largest. Adding noise keeps all of them indefinitely.

Kill-test question: is this signature a generic property of any
"threshold-activated, random-kick, absorbing-state" substrate, including a
Prometheus-like lattice rule with no particles, no geometry of shear, and
activity that spreads (no organism boundary)? And WHICH ingredient carries the
"forget all but one" part? Hypothesis H_nest: the forgetting is carried by
NESTING of absorbing sets (a state quiet at amplitude a2 is quiet at every
a < a2). If the rule is made non-nested, memories should persist without
competition (no transience) -- then "transient" is a statement about a
partial order, not about capacity or learning.

## Worlds

W1 PARTICLES (source replication; Corte et al. 2008 random organisation as used
by Keim & Nagel). N disks, diameter 1, box Lx x Ly, x periodic, y in [0,Ly]
(no wrap). One cycle of amplitude g: particle i at (x,y) is displaced to
x + s*y for s from 0 to g and back. Pair i,j "collides" in the cycle iff some
s in [0,g] brings centres closer than 1. Every particle involved in >= 1
collision receives a random displacement uniform in a disk of radius
eps = 0.5 (y clipped to the box). Noise (when on): every particle
independently, with prob p_noise per cycle, receives the same kind of kick.

W2 LATTICE-NESTED (Prometheus-like lattice rule). L x L periodic lattice,
4-neighbour, integer phase s in Z_Q, Q = 64. Circular distance d(s,t).
A site is ACTIVE under amplitude a iff some neighbour has d < a. All active
sites (computed synchronously) redraw s uniformly at random. Noise: each
site redraws with prob p_noise per cycle. Nested by construction:
quiet(a2) subset quiet(a1) for a1 < a2.

W3 LATTICE-SPREAD (no organism boundary). W2 plus: every neighbour of an
active site also redraws with prob p_spread = 0.25 (activity leaks into
quiet matter). Still nested (spread only originates at active sites).

W4 LATTICE-BAND (anti-analogy control, non-nested). As W2 but a site is active
under amplitude a iff some neighbour has d in [a - w, a), w = 3. Absorbing sets
for different amplitudes are not nested.

## Training protocol

Two amplitudes g1 < g2, applied alternately (g1, g2, g1, g2, ...), from a
uniformly random initial state. Controls per world: SINGLE (g2 only, same
number of cycles), and RAND (the untrained random initial state).
Checkpoints: t_mid and t_long cycles (fixed below). Noise: p_noise = 0 and
p_noise = p_on (fixed below). 5 seeds (1..5) per condition; pilot seed 999
only.

## Readout (static, no dynamics applied to the trained state)

C(a) = fraction of units (particles or sites) that WOULD be active in one
cycle of amplitude a from the current state (for W4, readout uses the W2
nested criterion d < a, so that one ruler is used for every lattice world;
additionally W4 reports band-readout Cb(a) as secondary).
Grid: W1 a in 0.1 steps over [0.1, 2*g2]; lattice a in steps of 1 over
[1, 2*a2]. Seed-averaged C.
Kink K(a) = [C(a+H) - C(a)]/H - [C(a) - C(a-H)]/H, H = one grid step for
lattice, H = 0.2 for W1.

MEMORY DETECTED at trained amplitude g iff
  K(g) > 0.02 per unit-step (lattice) / 0.05 per unit strain (W1)
  AND K(g) > 3 * SD of K over grid points at least 3H away from g1 and g2.
(For W4 with the band readout, memory at g is a DIP: Cb(g) < 0.5 * median Cb
 over grid points >= 3H away from g1, g2; reported secondary.)

## Predictions (source-conformant signature = "MTM")

P1 (mid, noise off): memories at g1 AND g2 both detected.
P2 (long, noise off): g2 detected, g1 NOT detected (forgotten).
P3 (long, noise on): g1 AND g2 detected.
P4 SINGLE control: no memory detected at g1 at any checkpoint.
P5 RAND control: no memory detected at g1 or g2.
A world "shows MTM" iff P1..P5 all hold.

## Decision rules (kill test)

K1 If W1 fails MTM: the toy did not replicate the source; no inference about
   Prometheus (report as instrument failure).
K2 If W1 shows MTM and W2/W3 show MTM: signature is generic to nested,
   threshold-activated absorbing-state substrates; transplant to Prometheus
   lattices is NOT superficial at the level of mechanism; H_nest survives if
   W4 fails P2 (i.e. W4 keeps both memories without noise at t_long).
K3 If W2 shows MTM and W3 does not: spreading activity (no boundary) kills
   the memory -> the transplant needs locality of dissipation; this is the
   Prometheus-relevant constraint.
K4 If W4 also shows MTM (forgets g1 without noise): H_nest is KILLED; the
   forgetting is carried by something else.
K5 If W2 fails MTM: the translation to a lattice rule is superficial
   (KILLED AS ANALOGY for lattices) unless the failure is only P2 timing.

## Parameters fixed now (pilot may change only what is listed)

W1: N = 300, area fraction phi = 0.2 (Lx = Ly), g1 = 1.0, g2 = 2.0, eps 0.5,
    p_on = 0.002.
Lattice: L = 48, g1 = 5, g2 = 10, p_on = 0.0005.
t_mid, t_long: pilot (seed 999) picks t_long = first power of 2 cycles at
which SINGLE(g2), noise off, has C(g2) < 0.005 (cap 8192 lattice, 4096 W1),
and t_mid = t_long / 16 (at least 4). If SINGLE never absorbs within the cap,
the pilot may lower g1, g2 by factors of 0.75 (both, same factor) up to twice,
recorded. Nothing else may be tuned.

Runtime budget: <= 30 minutes wall total. If exceeded, W1 is cut first
(reduced N to 200) and this is recorded.
