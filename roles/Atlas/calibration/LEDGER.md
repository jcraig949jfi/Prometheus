# Atlas calibration ledger

Currency: 2026-09-19. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently.

date | call made | what was true | corrected by | changed practice
2026-09-19 | CW01 PERTURBATIONS.superseded_by holds a perturbation id; minted it into an experiment key | it is prose naming SFE experiments ("C5-05 / C5-03 (representation B ...)") | npe/2 (ids parsed out; 4 prose-keyed edges pruned) | prose fields are parsed for ids, never keyed; a negative-control test asserts no key contains prose
2026-09-19 | EVIDENCE.perturbation_id is always a P- id | it also names SFE experiments (C5-01...), bare campaigns (C5), loop steps (RECONCILE-3) and directives | npe/3 | every foreign id is resolved against the index or kept as an observation on the idea
2026-09-19 | frontier '<family>/<hash>' spec ids descend from '<family>' | the family is not an experiment; 207 dangling DESCENDANT_OF edges | frontier/3 (family kept in extract, edges pruned) | a declared-looking edge whose parent is not an indexed entity is re-examined before it ships
2026-09-19 | first comb pass (R02/R13) reported 'repeated weak effects' | 14 of 14 were schema fields (n_min, attacked, min_effect) repeated by one receipt format | comb/2 (MEASURED filter) | a recurrence rule must exclude the source format's own field inventory; eligibility counts next (ATLAS-18)
2026-09-19 | a manual DELETE through the query helper fixed stale edges | the helper never commits; nothing was deleted | prune rule in common.flush | fixes go through a versioned harvester pass, never ad hoc SQL
2026-09-19 | 'G-R16-*' exp ids belong to NPE round 16 | R16 is a regime label; rounds ran r1..r8 (the survey had said so) | npe/4 + migration 005 (mis-keyed rows removed) | a parsed number is checked against the known range before it becomes identity
2026-09-19 | the M2 helper is a second instance of seat Atlas (INSTANCES.md, D-24 amendment 3) | the operator made it a separate seat, Atlas-M2 ('not an instance of Atlas'); I read 'brother' through the pattern I knew | Atlas-M2 in comms #499; SIBLINGS.md replaces INSTANCES.md | when the operator names a relationship, quote the words and ask the other party before encoding a structure around them
