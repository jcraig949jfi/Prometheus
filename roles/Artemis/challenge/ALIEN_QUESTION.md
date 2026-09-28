# The alien question: are Prometheus's living regimes supertransients?

Artemis, 2026-09-28. Operator challenge s5. Selected from nine outside-
field candidates (ALIEN_CANDIDATES.md; ranking and rejects there).
Registered as backlog thread FR-139. Pure ASCII.

## Where it comes from (not from Prometheus)

Dynamical systems. Spatially extended systems often show TRANSIENT
chaos whose lifetime grows exponentially with system size ("supertransients"):
for large enough systems the transient is, for practical purposes, the
system's behaviour, even though the true attractor is dead or trivial
(Crutchfield & Kaneko 1988; Tel & Lai 2008, "Chaotic transients in
spatially extended systems", Phys. Rep. 460; PRE 92:062915). The standard
observable is the escape rate: the rate at which trajectories leave the
transient regime, and how it scales with size L. Exponential scaling of
lifetime with L = supertransient; lifetime saturating in L = a genuine
attractor (or absorbing state) reached at finite time; power law = a
critical regime.

## Why no current engine would ask it

Every Prometheus verdict about a "living" regime is taken at a FIXED
window: a lineage is "established" by tick T; a world is "extinct" or the
medium "frozen" by tick T; a replicator "takes over" within N epochs.
FR-125 checked Aether's verdicts at a longer window, at one size. No
engine measures how a regime's LIFETIME scales with world size, and the
word "supertransient" appears nowhere in the repository (repo-wide
search, 2026-09-28; "escape rate" appears three times, all unrelated).
The vocabulary it breaks: "established / extinct / frozen" are treated as
states; this question treats them as scaling laws.

## The question, stated for Prometheus

For each engine's living regime -- replicator ecologies in the Z80
worlds (end event: extinction, or loss of all certified copiers),
unfrozen media in Aether (end event: template turnover below threshold
without noise, the TH-009 "frozen medium"), packet traffic in Ananke
(end event: communication-dependent accuracy decays to 0.5) -- does the
mean time to the end event grow exponentially with world size, saturate,
or follow a power law? And should Prometheus select and compare worlds
by how fast their escape rate falls with size, instead of by whether they
reach a living state within a fixed window?

## Why it could change what Prometheus searches for

- If living regimes are supertransients, then "no open-endedness in
  window T" and "established by T" are both size-dependent statements,
  and cross-engine comparisons at different world sizes are invalid.
- The escape-rate-vs-size exponent is a window-free, seed-averaged,
  engine-neutral measure of how robust a regime is. It is exactly the
  kind of cross-engine observable the ecology lacks.
- A world family whose lifetime grows super-exponentially with size is a
  different search target from one that "comes alive quickly".

## Minimal experimental expression (discriminator)

Host: any Linux node; stdlib or numpy engines; no GPU; committed code.
1. Pick one engine whose end event is already defined and whose runs are
   cheap on CPU: BEE z80atlas fresh random worlds (95-100% go extinct;
   H-D2-42) or Aether's v1 law without perturbation (freezes; TH-009).
2. Sweep world size over 4-5 values spanning at least a factor of 8 in
   linear size, 100-200 seeds each, run each world to its end event or a
   cap C, record time-to-end (right-censored at C).
3. Fit survival curves per size (Kaplan-Meier; exponential tail rate
   kappa(L)). Readings fixed in advance: log mean lifetime linear in L
   (or in L^d) with positive slope over the range -> supertransient;
   lifetime flat in L -> attractor/absorbing state reached at finite
   time, fixed-window verdicts are safe; log-log linear -> critical.
   Censoring above 20% at the largest size -> raise C once, then report
   UNRESOLVED rather than extrapolate.
Cost: engine-dependent; the first step is a 30-minute timing pilot at the
smallest and largest size to price the sweep before committing a
prereg.

## Status

Registered FR-139 (RAW-ALIEN). Not executed in this challenge: both
candidate engines belong to active seats (Bellerophon's multi-day
campaign occupies BEE; Aether's research block is live), and the sweep's
cost is unknown until the timing pilot. Offered to Aether (TH-009 end
event) and Bellerophon; runner-up alien candidate: scheduler invariance
(ALIEN_CANDIDATES.md #2).
