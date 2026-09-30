# Theseus calibration ledger

Currency: 2026-09-30. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. Empty at creation:
the seat has made no calls.

date | call made | what was true | corrected by | changed practice
2026-09-30 | P2 one-shot viable fraction pairs > triplets > sextuplets | flat: P 0.703, B 0.707, C 0.720 (Wilson CIs overlap) | v0 REPORT (theseus/runs/v0_2026-09-30/REPORT.json) | the size cap (MAXRULES) and seeded binding make arity nearly irrelevant to viability; test arity only with the cap as an explicit variable
2026-09-30 | P4 DEEP-lane raw-human rule fraction < 0.2 | 0.27 (VERY_DEEP 0.14): unchanged G0 rules survive many collisions because binding copies contiguous runs verbatim | v0 REPORT genealogy | genealogical depth does not dilute human material as fast as generation count suggests; report rule-level provenance beside depth, never depth alone
2026-09-30 | P9 Spearman(generation, distance to one-shot union) > 0.1 | 0.08 (euclid_z), 0.10 (cosine), 0.08 (quantile_l1); lineage-shuffle perm p 0.018: detectable, small | v0 REPORT depth_vs_arity | a statistically detectable drift is not a niche expansion; state effect sizes next to p
2026-09-30 | (design) DEEP / VERY_DEEP lanes contain only generation >= 5 synthetic parents | entities.eligible admits evolved lenses (generation-0 synthetic roots) in DEEP and VERY_DEEP, so some D children have generation 1; D and E are blurred | seat's own reading of the gen-5 log line | eligibility tests the property (generation, human ancestry) not the kind label; lens parents belong only to the lens lane
2026-09-30 | (design) the ecology is reproducible from the master seed | coalition pools iterate a Python set of string ids, whose order depends on PYTHONHASHSEED | seat's own code review during the run | every iteration that feeds an RNG choice is over a sorted list; runs set PYTHONHASHSEED=0
2026-09-30 | (design) lensDependencies records dependence on a lens | it is inherited transitively through ancestry; measured dependence (held-out residual drop) is ~0.004 for the candidates that carry it | v0 strongest-candidate table | "requires evolved lens L" is only ever stated from a measured drop against a null, never from the field
2026-09-30 | (design) VISUAL_EXPORT covers the strongest candidates | empty file: ids sorted alphabetically picked one-shot arm ids that are not in the registry; silent | v0 run directory listing | exports assert non-empty when candidates exist
