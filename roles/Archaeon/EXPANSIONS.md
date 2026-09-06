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
| E2 | vivarium | repeated execution via SFE `record_observation(replication=True)`, ordered, seed derivation declared | 1 row = 1 world = 1 observation; S17 needs >3 per world | M-ELIGIBLE, S17 eligibility | **DONE** b70d7a665 (spec v3 `repeat`, live: 4 obs in one world, in order) |
| E3 | daedalus | cross-tenant read grant, width per `INBOX_ARCHAEON_READ_GRANT_AND_FAMILIES.md` §2 | Archaeon owns 0 of 2,937 attested observations | the whole signal campaign | **CODE DONE, NOT LIVE** 2fa52de86 — M1 still serves schema_version 6 (`source_commit 7167d3b05`), `/v2/read/observations` → 404 (probed 2026-09-06). Then: harmonia-m2 worlds into a topology group, Harmonia grants Archaeon's client (`cli_` registered 2026-09-06), and the probe must show the INTENDED observations with census + family metadata. `python -m archaeon.producer.readback_probe` |
| E4 | daedalus | comparison-family arm contract (`families(kind=comparison)` + members) | no per-world arm field in the fossil | D2/D4 comparison mapping; Stage 0 arm rules | **RULING RECOMMENDED** (operator, 2026-09-06): arm is design provenance bound by the sealed family manifest, never in `spec_hash`; acceptance = same execution hash under labels A/B, reassignment refused, PEW preserves binding. Harmonia to confirm; Daedalus to bind. `roles/Daedalus/INBOX_ARCHAEON_ARM_KEY_CONFLICT.md` |
| E5 | daedalus | verify ordered `replication=True` semantics for the 2×2×2×4 shape | untested | M-ELIGIBLE | PROPOSED |
| E6 | vivarium | bind queue candidate sets to SFE `selection` families (`selected`/`alternative`) | candidate set is class-A in the queue only | class-A selection in the substrate | PROPOSED |
| E7 | vivarium | drop / mark RETIRED `archaeon.probe.v0` in `viv/kinds.py` | registered, `implemented=False`, no longer emitted | registry honesty | **DONE** b70d7a665 (RETIRED, meaning preserved) |
| E8 | mnemosyne | fossilize `players`, `ecology`, `resources_used` on encounters | 0 / 5452 prod encounters carry any | D1/D2/D4 on PEW charts; richer charts | PROPOSED |
| E9 | mnemosyne | populate `phenotype.score` (Proteus supplies phenotype; PEW ingests it) | 2 / 6006 prod player fossils | PEW phenotype chart | PROPOSED |
| E10 | players | specimens crossing into SFE at scale; lineages of depth > 1 | 2 / 64 crossed; all 64 lineages size 1 | player families; D1 baselines | PROPOSED |
| E11 | harmonia | adopt-or-replace D1–D6 with qualified definitions | D1–D6 are first guesses; S17 rules are frozen and qualified | detector credibility | PROPOSED |
| E12 | harmonia | reconcile S17 narrative vs ledger direction (`serial_ac`, `rel_se` lower=fragile) | ledger verified by operator | Stage 0 provenance | **DONE** b5498c162 (frozen rule correct; narrative was wrong; mechanism verified) |
| E13 | archaeon | templates per probe kind, parameterised by region coordinates | signal path draws the same random spec as the fallback | M-SIGNAL | **PROPOSED TEMPLATE + WIRED**: `bitstring.resample_region.v0` in the inbox (seed_root, length taken from the fired region); tick draws it under `menu.region_directed.v0` once ADMITTED. Admission is the operator's |
| E14 | archaeon | coverage-weighted template draw (named policy, not the baseline) | uniform draw only | menu growth metric | PROPOSED |
| E15 | literature | per discipline: smallest bench experiment + smallest bench gap → PROPOSED templates | menu has 1 template, origin RNG | menu growth from ≥3 origins | **DONE** 19ad79d2e (Herakles: 69 PROPOSED templates; 68 are expansion requests; 41 requests collapse to 7 bench gaps, largest = the outcome rule) |
| E16 | vivarium | `outcome_rule` aggregation over repeats (`any`/`all`/`max`/`min` over the trajectory) | 4 inbox walk templates measurable only on the last observation; Herakles request #22 is the smallest of 28 | every repeat-based design; `falsification_walk.v0` as designed | PROPOSED |
| E17 | operator | admission-time ranges for `falsification_walk.v0` (`steps`, `step_scale`, envelope threshold) -- a disclosed salvage fix, not a bench change | measurable TODAY on `random_walk_v0` with a scalar `displacement` rule | first complete inbox experiment | PROPOSED |

## Done

| # | lane | recommendation | commit |
|---|---|---|---|
| D1 | archaeon | observation-level player attribution (`sfe.spec_players.v0`) | this branch |
| D2 | archaeon | declared tenancy + evidence filter + snapshot + schema guard (interim per Daedalus §2) | this branch |
| D3 | archaeon | substrate census as a time series with wishlist | this branch |
| D4 | archaeon | template registry; `random.v0` → `bitstring.uniform.v0` frozen baseline | this branch |
| D5 | archaeon | deployed as a scheduled task, not a daemon | 36b40870c |
| D6 | vivarium | PEW fossils to `prod` namespace; consumer token | 35f8a64bc, 0b2f92734 |
