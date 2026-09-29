# Foreign mechanisms translated into executable Prometheus tests (expedition 1)

Currency: 2026-09-28. Odysseus. Directive s10, s17 item 8. Five fields each
(source phenomenon; mechanism; Prometheus translation; kill test; alien
content), plus territory and the nearest familiar explanation. Full entries
with citations: foreign/raid_A/RAID.md, foreign/raid_B/RAID.md,
MAP_CHANGES.md. Prior-work searched before each (prior_work_search.sh).
Pure ASCII.

## F1 Genetic assimilation of world-supplied scaffolding  (territory I, proposed; D, C)
SOURCE: Waddington (1953): a trait first induced by the environment becomes
  constitutive after selection; ecological scaffolding (Black et al. 2020).
MECHANISM: a function supplied externally lets lineages persist long enough
  for internal variants of it to be selected; withdrawal then reveals
  whether the function moved inside.
TRANSLATION: Z80 world (BEE or NPE); unit = tape lineage; the gift = reset
  self-location registers / destination address in the input / block copy;
  arms NEVER, ALWAYS, ABRUPT, GRADUAL withdrawal; observable = retained
  function after withdrawal (recert harness: behaviour without gift;
  mechanism by knockout) vs NEVER at matched generations and random-walk
  budget.
KILL: withdrawn-gift lineages no better than NEVER -> the gift only masked
  the need.
ALIEN CONTENT: Prometheus treats gifts as fixed physics (authored or not);
  this makes authorship TEMPORAL -- machinery that is lent, then removed.
Nearest familiar explanation: ordinary selection for the function (ruled
  out by the NEVER arm at matched budget).
Evidence it is not an analogy: the census's three Z80 survivors are all
  internalisation events (census/CENSUS_A_z80.md).

## F2 Cryptic vs silent variation  (C; B)
SOURCE: cryptic genetic variation (neutral under normal conditions, expressed
  under perturbation) accumulates and fuels adaptation after environmental
  change (Gibson & Dworkin 2004; Paaby & Rockman 2014 -- cited, UNVERIFIED
  this session).
MECHANISM: neutrality in EXPRESSED-but-buffered positions stores variation
  that perturbation releases; neutrality in never-executed positions does
  not.
TRANSLATION: Z80 world variant where more of the tape is executed under
  some conditions (entry point or control flow depends on an environment
  epoch), making neutral mutations latent rather than silent; observable =
  bacc behaviour counts after a perturbation, and time to adapt after an
  environment switch.
KILL: the latent-neutral world adapts no faster than the silent-neutral
  world at matched mutation load and neutral fraction.
ALIEN CONTENT: bacc showed 94% of Z80 neutral probes hit never-executed
  bytes; Prometheus counts neutrality but has no silent/latent distinction.
Nearest familiar explanation: higher mutation rate (matched by design).

## F3 Invasion-dependency map (facilitation / priority effects)  (D; A)
SOURCE: ecological succession -- early species change conditions so later
  ones can establish (facilitation); arrival order changes outcomes
  (priority effects). raid_A EC-1.
MECHANISM: type B invades a world only because A altered it; information
  need not pass between them.
TRANSLATION: any engine with species/lineages; for each pair (A, B): does B
  invade (i) the pristine world, (ii) a world with A present, (iii) a world
  where A was removed but its modifications left? Arrival-order twins.
KILL: B invades (iii) no more than (i): nothing was built into the world.
ALIEN CONTENT: a route to "building on" that needs no inheritance and no
  record -- accumulation in the world's state, measured without reading it.
Nearest familiar explanation: shared environment exposure (the pristine arm).

## F4 Stochastic corrector (group selection in splitting compartments)  (D; A)
SOURCE: Szathmary & Demeter (1987): compartments that split with random
  sorting let cooperating replicators persist against parasites and link.
  raid_B.
MECHANISM: sampling noise at division plus selection among compartments
  builds a higher-level unit.
TRANSLATION: BEE/NPE tapes in small compartments that split at a size
  threshold with random sorting; arms: compartments vs lattice-only;
  compartment-size sweep; observable: linkage (co-transmission) of
  complementary tapes, parasite load, compartment-level heritability.
KILL: no co-transmission beyond the lattice-only arm at any compartment size.
ALIEN CONTENT: the Z80 worlds have space but no division events; the unit
  above the tape is never tested (map O2, no engine).
Nearest familiar explanation: spatial structure alone (the lattice arm).

## F5 Self-stabilisation as an arbitrary-start certificate  (E; A)
SOURCE: Dijkstra (1974): a system converges to legitimate states from ANY
  start (convergence) and stays there (closure). raid_A DA-1.
TRANSLATION: for any claimed emergent structure, re-run from arbitrary
  (scrambled) starting states: does it RE-FORM? Report convergence and
  closure separately.
KILL: the structure re-forms only from the historical initialisation.
ALIEN CONTENT: separates "robust once formed" from "an attractor of the
  dynamics"; contested -- Artemis folds it into robustness (FR-133).

## Killed as analogy (kept so they are not re-imported)
reflective towers (need an installed interpreter); Futamura projections
(speed only -- the recompute arm covers it); amorphous computing / growing
point language (compiled designed programs); genetic-code error
minimisation (the opcode map is installed); demographic "Tasmania" ratchet
(mutation-selection balance renamed); pigeon/navigator cumulative culture
(ordinary optimisation along a chain); conformity/prestige bias and naming
games (frequency-dependent selection); gossip protocols; negative selection
as a mechanism (kept only as a null control); multiple transient memories
(toy stored only the maximum drive -- not reproduced); natural induction as
a learning rule (attractor reshaping; kill test failed).
