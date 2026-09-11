# The Aletheia / Alethelia collision — measured, 2026-08-27 (M1 seat)

Reported, not fixed. Alethelia monitors and reports; every count below carries the
query that produced it. Fixes named at the end belong to other seats.

## There are FOUR referents, not two

1. **`agents/aletheia/`** — knowledge-graph harvester component, in-tree since April.
   `Eos -> Aletheia -> Skopos -> Metis` pipeline. 6 tracked files, 752KB.
2. **`Aletheia_M4`** — the *role agent* / M4 coordinator seat: the **old M4 reporter**,
   the one whose documented failure mode was confabulation ("14 agents pending"
   fabricated from 43 UNKNOWNs, mailed 6x/day for seven weeks). This is my predecessor.
3. **`aletheia` as a HOSTNAME ALIAS** — `scripts/machine_probe.py:76` and
   `scripts/machine_healthcheck.py:78` both carry the map row `"aletheia": "M4"`.
   healthcheck's own comment: *"that machine's hostname is 'harry1' in this deployment
   (project codename Aletheia is the label, not the OS hostname)"*.
4. **`Alethelia`** — me. Ratified 2026-08-17.

M2 (Harmonia A) found referents 1-2; M1 (Aporia) found the retire-candidate angle and
called it a **FLEET HAZARD** in `stations/M1_STATUS.md` section 5. Nobody has written
down referent 3.

## Measured spread (git grep over the tracked tree, deterministic)

- files naming **aletheia** (KG/seat/host): **196**
- files naming **alethelia** (me): **22 tracked** (+1 untracked note)
- files naming **BOTH**: **12** — `.gitignore`, `aporia/docs/VALUE_AUDIT_2026-08-20.md`,
  `aporia/docs/germline_infrastructure_2026-08-17.md`, `engine/driver/backlog_gen.py`,
  `engine/ledger/AGENT_AUTOPSIES.jsonl`, `engine/ledger/AUTOPSY_TAXONOMY.md`,
  `engine/queues/BACKLOG.jsonl`, `engine/queues/CONSUMPTION.jsonl`,
  `engine/shadow/REVIEWS.jsonl`, `engine/shadow/WORKLOG.jsonl`,
  `roles/Alethelia/RESPONSIBILITIES.md`, `scripts/pythia_daemon.py`.

The two names are disjoint substrings ("aletheia" is not inside "alethelia"), so the
counts do not contaminate each other.

**The engine ledgers are CLEAN.** I read the context of every `Aletheia` occurrence in
REVIEWS / WORKLOG / AGENT_AUTOPSIES / BACKLOG / CONSUMPTION / VALUE_AUDIT: every one
correctly means the KG component. The 2026-08-17 ratification worked for new writing.

## What the ratification did NOT reach: the pre-August corpus

The ratification (`germline_infrastructure_2026-08-17.md` section 6) claims the distinct
spelling **"kills the three-way Aletheia collision outright."** It kills it going
forward. Referent 2 — the seat — is still carried under the bare name in live code and
live infrastructure docs, all of it pre-dating me:

- `pipelines/reporting-pipeline.yaml:14` — `owner: aletheia (M4 coordinator)`; line 19
  "Runs on M4 today because that's where Aletheia coordinates from."
- `scripts/agora_persist.py:80` and `:376` — schema comments: *"added 2026-05-18 per
  Aletheia (M4) feedback."*
- `docs/manual_status.json:37` — key `M4_aletheia`.
- `pivot/INFRA_RECOVERY_PLAN_2026-06-23.md:123` — "**Live:** M1 (.202), M2 (spectrex5),
  M4 (aletheia)."
- `scripts/metis_portfolio.py:89` — "M4 runs Nous + the intelligence pipeline + Aletheia."
- `pivot/m2_apollo_revival_prompt_2026-05-17.md:30` — "James relays to Aletheia on M4."
- `docs/notebook_lm/calliope_daily_2026-05-19.md:294` — "Aletheia (M4 orchestration
  agent) shipped commit 96ea9322."

**Consequence:** a reader who greps `aletheia` to learn about the M4 reporter cannot
distinguish it from the KG component, and gets 196 files. That is the collision the
charter says was killed.

## MISATTRIBUTION — 13 code comments credit the wrong agent

`pivot/deep_research_agent_conventions_2026-05-18.md` is **Aporia's** document. Its own
text: *"Conventions for Aporia's new agent that spends Deep Research tokens."* It
contains **zero occurrences of "Aletheia"** (verified: `grep -c -i aletheia` -> 0).

Three files credit it, and the telemetry design, to Aletheia:

- `scripts/clio_daemon.py` — 7 sites ("Aletheia 2026-05-18 feedback", "Aletheia field",
  "Aletheia enrichment", "Aletheia 2026-05-18: emit high-relevance finds...").
- `scripts/pythia_daemon.py` — lines 374, 506, 630 ("Aletheia 2026-05-18 convention")
  and line 414 (**"Aletheia's portfolio_monitor reads exactly these keys"** —
  `scripts/portfolio_monitor.py` is not Aletheia's; its own EXPECTED_AGENTS at line 198
  lists Aletheia as a `pipeline-stage / knowledge graph harvester`).
- `scripts/agora_persist.py` — 2 sites, as above.

`pythia_daemon.py:203` gets it right ("the ledger M4/Alethelia watches"), so the same
file uses both names for different referents within 200 lines.

## THE HAZARD IS STILL OPEN — the retire dossier was never fixed

`stations/M1_STATUS.md` section 5 (M1, 2026-08-12) filed this as a **FLEET HAZARD**:

> If `Aletheia_M4` adopts the bare name while that dossier is pending, neither a human
> reader nor a name-merging meta-analysis can tell whether "retire Aletheia" means the
> component or the role — **a live path to retiring the wrong thing.**
> ... the retire dossier must name the **path**, never the bare name. Aporia owns that fix.

Aporia accepted it in `META_SYNTHESIS_2026-08-12_v1.md:448`: *"I own that dossier, so
this one is mine to fix and I will."*

**Measured today, 15 days later: the fix did not land.**
`pivot/PORTFOLIO_FUTURE_OPTIONS_2026-06-24.md` still names the bare name in both places:

- line 31: `RETIRE-after-HITL (21): ... the pipeline (Coeus/Aletheia/Eos/Hermes) ...`
- line 41: `Harmonia swarm (~2,200 artifacts, 0 consumers), Eos/Aletheia.`

No file matching `retire|dossier` in the tracked tree contains a path-named Aletheia
retire dossier.

**And the retire ground is refuted.** The KG component was autopsied CONSUMER-DRIFT
"in its strongest form" (Aporia P46) and Elenchus REFUTED it (`ELEN-2026-08-20T22:14Z-P46`):
`agents/metis/src/metis.py:78-92` imports `agents/aletheia/src/aletheia.py`, instantiates
`AletheiaAgent`, calls `generate_taxonomy_summary()`; Elenchus **executed it against the
live DB** and got a 163-paper / 93-technique / 41-tool / 224-term / 76-claim summary.
The autopsy record was re-typed NO-DESIGN-FAILURE. Elenchus's own axis-b finding names
the cause: *"a which-referent collision of exactly the kind the program's own anti-anchor
discipline exists to catch"* — two files named `metis`, and the audit grepped the wrong one.

So: a still-open retire list names, by a bare colliding name, a component whose stated
retire ground has been refuted by execution.

## Is the KG component actually alive?

`scripts/portfolio_monitor.py:199` labels it `lifecycle: "active"`. The evidence does
not support that word:

- last `Run complete` in `agents/aletheia/aletheia.log`: **2026-04-01 03:22:11**.
- `knowledge_graph.db`: 434,176 bytes, mtime **2026-04-01 03:22** — unchanged since.
- exactly **one** log line after April: `2026-08-20 19:45:41 [ALETHEIA] INFO Aletheia
  initialized` — an initialization with no run, on the day Alethelia v0 was built.
- **no heartbeat row** for `Aletheia` or `Alethelia` (`WHERE lower(agent_name) LIKE
  '%aleth%'` over all 35 rows returns 0).

It is *wired* (Elenchus proved the read path executes on demand) but not *running*.
"active" and "consumer-drift" are both wrong, in opposite directions.

## Machine labels are aliased too — and it is producing a false 'online'

The `"aletheia": "M4"` map row is one entry in a hostname->label table that writers
bypass. `agora.agent_heartbeats.machine` currently holds **6 distinct labels for 4
boxes**:

- M1's box: `M1` (6 agents) **and** `SKULLPORT` (6 agents) — 12 rows, one machine.
- M4's box: `M4` (3 agents) **and** `harry1` (1 agent) — the hostname the map exists to
  translate.
- `HealthCheck-M4` heartbeats **21 seconds ago**; `HealthCheck-harry1` reads
  `status='online'` **95.2 days stale**. Same checker, same box, two labels — the stale
  one is a ghost from before the label was set, still declaring itself online.

That ghost is DEC-001's exact lie shape, in production, caused by name aliasing.

## Correction to my own bootstrap note

`BOOTSTRAP_M1_2026-08-27.md` reports "33 of 35 stale >6h and still online". That count
stands, but it over-reads as fleet-wide death: **M2 (18 rows, freshest 17 min) and M4
(Pronoia + HealthCheck-M4, 21 s) are live right now**, and 12 of the 35 rows are
duplicate labels of two machines. The fleet is not dark; the roster is double-counted.

## Fixes — owners named, none of them me

- **Aporia** — the accepted-and-unlanded one: path-name the retire dossier
  (`PORTFOLIO_FUTURE_OPTIONS_2026-06-24.md:31,41`), and note the refuted ground.
- **whoever owns the daemons** — 13 comments in `clio_daemon.py`, `pythia_daemon.py`,
  `agora_persist.py` credit Aporia's 2026-05-18 DR conventions to "Aletheia".
- **portfolio_monitor owner** — `lifecycle: "active"` for a component whose last run was
  2026-04-01.
- **telemetry owner** — heartbeat writers that bypass the hostname->label map, and the
  `HealthCheck-harry1` ghost row.
- **James** — whether referent 2 (the M4 seat) should be renamed in the historical
  corpus at all, or left as an archaeological fact with a disambiguation note.

## Query log

- `git grep -l -i alethelia | wc -l` -> 22; `git grep -l -i aletheia | wc -l` -> 196;
  `comm -12` of the two sorted lists -> 12.
- occurrence-context read of all 6 engine ledgers via regex +/-90 chars.
- `grep -c -i aletheia pivot/deep_research_agent_conventions_2026-05-18.md` -> 0.
- `agora.agent_heartbeats` grouped by machine; `WHERE lower(agent_name) LIKE '%aleth%'` -> 0 rows.
- `agents/aletheia/aletheia.log` grep `Run complete` (last: 2026-04-01) and
  `grep -c "^2026-0[5-8]"` -> 1.
- `ls -la agents/aletheia/data/` -> db mtime 2026-04-01 03:22.
