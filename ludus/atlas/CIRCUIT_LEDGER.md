# Circuit ledger

Worlds used to invent or tune a circuit are **not evidence for it**.

## r0003 — myopic one-step stopping rule  (STOP)
- definition: `STOP iff P(death | continue) * pot >= E[immediate gain | continue]`
- invented on: ['FLIP7', 'MARTIAN_DICE'] | tuned on: —
- **untouched test worlds: 1** ['INCAN_GOLD']
- cannot test it (no STOP axis): ['CANT_STOP']
- predicted: retention >= 0.97 with a competent partner on the SELECT axis; registered in CYCLE_002 §8.1 before either world was built
- kill condition: retention materially below 0.97 in any world exposing a total-loss STOP interface, with a competent SELECT partner
- first failure: none recorded
- current scope: worlds with an accumulate-or-bank decision where death forfeits the ENTIRE pot. Untested where loss is partial - see BACKLOG item 2 (Coloretto), which was chosen to attack exactly this precondition.
- provenance: NOT invented from the seat's own vocabulary. It is the textbook one-step rule; it was written down because Flip 7's exact DP table was already sitting there to check it against, not because a concept suggested it.

## r0007 — survival-rate stopping  (STOP)
- definition: `stop once P(surviving one more draw) falls below 1/2`
- invented on: ['FLIP7'] | tuned on: —
- **untouched test worlds: 2** ['INCAN_GOLD', 'MARTIAN_DICE']
- cannot test it (no STOP axis): ['CANT_STOP']
- predicted: predicted to underperform r0003 wherever pot varies
- kill condition: n/a; retained as a control
- first failure: none recorded
- current scope: control only
- provenance: pot-blind control: it reads the risk and ignores the stake. Its whole job is to show whether the stake matters.

## r0010 — greedy immediate pot  (SELECT)
- definition: `take the option with the highest immediate pot`
- invented on: ['MARTIAN_DICE'] | tuned on: —
- **untouched test worlds: 0** (none — NO INDEPENDENT EVIDENCE)
- cannot test it (no SELECT axis): ['CANT_STOP', 'FLIP7', 'INCAN_GOLD']
- predicted: unregistered - this is a baseline, not a claim
- kill condition: n/a; retained as a floor
- first failure: none recorded
- current scope: baseline only
- provenance: the null-ish obvious baseline; no ontology in it

## r0011 — minimum consumption / capacity preservation  (SELECT)
- definition: `take the option consuming least irreversible capacity`
- invented on: ['MARTIAN_DICE'] | tuned on: —
- **untouched test worlds: 0** (none — NO INDEPENDENT EVIDENCE)
- cannot test it (no SELECT axis): ['CANT_STOP', 'FLIP7', 'INCAN_GOLD']
- predicted: unregistered before first run - a retrospective number, and it must not be read as a test
- kill condition: already below the null circuit in its only world
- first failure: MARTIAN_DICE (retention 0.2501, below null r0013 0.7398)
- current scope: NONE. Retained as a fossil per charter §42, not as a candidate.
- provenance: CONTAMINATION FLAG. This circuit was NOT suggested by data. It was written because charter v1 §23 talks about 'option preservation' and the seat reached for its own vocabulary. It then scored 0.2501 in Martian Dice - far below the null circuit r0013 at 0.7398. Recorded because a concept-seeded circuit that FAILS is the cheapest possible evidence about how much the seat's vocabulary is worth.

## r0012 — one-ply lookahead select  (SELECT)
- definition: `take the option whose single next draw has the best greedy expected pot`
- invented on: ['MARTIAN_DICE'] | tuned on: —
- **untouched test worlds: 0** (none — NO INDEPENDENT EVIDENCE)
- cannot test it (no SELECT axis): ['CANT_STOP', 'FLIP7', 'INCAN_GOLD']
- predicted: retention >= 0.90 in For Sale, and r0011 stays near the bottom. Registered in BACKLOG.md before For Sale exists.
- kill condition: the ORDERING of SELECT circuits reverses outside push-your-luck - that would mean SELECT circuits are genre-mediated, not interface-mediated
- first failure: none recorded
- current scope: push-your-luck worlds with a live SELECT axis. ONE family. Surviving For Sale would be evidence, NOT a universal circuit.
- provenance: shallow-search baseline, not a concept

## r0014 — pot gain per unit capacity  (SELECT)
- definition: `maximise pot gain divided by capacity consumed`
- invented on: ['MARTIAN_DICE'] | tuned on: —
- **untouched test worlds: 0** (none — NO INDEPENDENT EVIDENCE)
- cannot test it (no SELECT axis): ['CANT_STOP', 'FLIP7', 'INCAN_GOLD']
- predicted: unregistered before first run
- kill condition: fails to beat the null circuit r0013 in any world with a live SELECT axis
- first failure: none recorded
- current scope: provisional; one world, retrospective number
- provenance: CONTAMINATION FLAG. Same origin as r0011 - written from the seat's own 'spend capacity only when it pays' intuition, not from any observation.

## r0015 — two-ply myopic stopping  (STOP)
- definition: `stop iff continuing two draws under greedy play has negative expected change`
- invented on: ['FLIP7', 'MARTIAN_DICE'] | tuned on: —
- **untouched test worlds: 1** ['INCAN_GOLD']
- cannot test it (no STOP axis): ['CANT_STOP']
- predicted: unregistered
- kill condition: COLLISION RISK: if r0015 never separates from r0003 in any world, one of them is redundant and the bench must hunt a world that separates them or retire one.
- first failure: none recorded
- current scope: provisional
- provenance: depth variant of r0003, written to test whether depth buys anything on the STOP axis
