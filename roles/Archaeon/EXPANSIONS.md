# Archaeon — expansion register

Every recommendation that the program grow somewhere, addressed to a lane,
with the measurement that motivated it and what it would unblock. Entries move
`PROPOSED → ACCEPTED | DECLINED → DONE (commit)`. A register with no `DONE`
entries after a quarter is a finding about the register.

Sources: the substrate census wishlist (`archaeon.substrate_census`), the
template registry's PROPOSED-but-unrunnable set, and the program-health report
(`python -m archaeon.producer.health_report`). Nothing here is a verdict.

## Open

| # | lane | recommendation | measurement | unblocks | status |
|---|---|---|---|---|---|
| E1 | vivarium | carry `source_evidence.policy_version` and `template_id` into the PEW producer block | producer block holds queue ids only (checked 2026-09-06) | M-SIGNAL endpoint by policy | PROPOSED |
| E2 | vivarium | repeated execution via SFE `record_observation(replication=True)`, ordered, seed derivation declared | 1 row = 1 world = 1 observation; S17 needs >3 per world | M-ELIGIBLE, S17 eligibility | PROPOSED |
| E3 | daedalus | cross-tenant read grant, width per `INBOX_ARCHAEON_READ_GRANT_AND_FAMILIES.md` §2 | Archaeon owns 0 of 2,937 attested observations | the whole signal campaign | PROPOSED |
| E4 | daedalus | comparison-family arm contract (`families(kind=comparison)` + members) | no per-world arm field in the fossil | D2/D4 comparison mapping; Stage 0 arm rules | PROPOSED |
| E5 | daedalus | verify ordered `replication=True` semantics for the 2×2×2×4 shape | untested | M-ELIGIBLE | PROPOSED |
| E6 | vivarium | bind queue candidate sets to SFE `selection` families (`selected`/`alternative`) | candidate set is class-A in the queue only | class-A selection in the substrate | PROPOSED |
| E7 | vivarium | drop / mark RETIRED `archaeon.probe.v0` in `viv/kinds.py` | registered, `implemented=False`, no longer emitted | registry honesty | PROPOSED |
| E8 | proteus | fossilize `players`, `ecology`, `resources_used` on encounters | 0 / 5452 prod encounters carry any | D1/D2/D4 on PEW charts; richer charts | PROPOSED |
| E9 | proteus | populate `phenotype.score` | 2 / 6006 prod player fossils | PEW phenotype chart | PROPOSED |
| E10 | players | specimens crossing into SFE at scale; lineages of depth > 1 | 2 / 64 crossed; all 64 lineages size 1 | player families; D1 baselines | PROPOSED |
| E11 | harmonia | adopt-or-replace D1–D6 with qualified definitions | D1–D6 are first guesses; S17 rules are frozen and qualified | detector credibility | PROPOSED |
| E12 | harmonia | reconcile S17 narrative vs ledger direction (`serial_ac`, `rel_se` lower=fragile) | ledger verified by operator | Stage 0 provenance | PROPOSED |
| E13 | archaeon | templates per probe kind, parameterised by region coordinates | signal path draws the same random spec as the fallback | M-SIGNAL | PROPOSED |
| E14 | archaeon | coverage-weighted template draw (named policy, not the baseline) | uniform draw only | menu growth metric | PROPOSED |
| E15 | literature | per discipline: smallest bench experiment + smallest bench gap → PROPOSED templates | menu has 1 template, origin RNG | menu growth from ≥3 origins | PROPOSED |

## Done

| # | lane | recommendation | commit |
|---|---|---|---|
| D1 | archaeon | observation-level player attribution (`sfe.spec_players.v0`) | this branch |
| D2 | archaeon | declared tenancy + evidence filter + snapshot + schema guard (interim per Daedalus §2) | this branch |
| D3 | archaeon | substrate census as a time series with wishlist | this branch |
| D4 | archaeon | template registry; `random.v0` → `bitstring.uniform.v0` frozen baseline | this branch |
| D5 | archaeon | deployed as a scheduled task, not a daemon | 36b40870c |
| D6 | vivarium | PEW fossils to `prod` namespace; consumer token | 35f8a64bc, 0b2f92734 |
