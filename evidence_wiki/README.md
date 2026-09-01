# Prometheus Evidence Wiki / Mnemosyne Evidence Tensor — V0

Owner: **Mnemosyne**. Charter:
`roles/Mnemosyne/prompts/CHARTER_EVIDENCE_WIKI_V0_2026-09-01.txt`
(sha256 `c81a2127…ba758ba0ead`). Architecture: `docs/ARCHITECTURE_V0.md`.
Benchmarks: `benchmarks/results_v0.json`. Case studies:
`docs/CASE_STUDIES_V0.md`.

One knowledge substrate (Postgres schema `ew` in `prometheus_fire`), many
rebuildable projections (wiki, REST, BM25, embeddings, graph, sparse
coordinates, CP/Tucker/TT). Derived content can never become evidence.

## Running the service (M1)

```
cd evidence_wiki
python -m ew.service          # binds per config.json (default 0.0.0.0:8377)
```

- Firewall rule `Mnemosyne Evidence Wiki 8377` (inbound TCP 8377,
  remote 192.168.1.0/24 + localhost, private/domain profiles) is registered
  on M1.
- Human UI: `http://<M1>:8377/wiki` · Health: `/api/v1/health` ·
  Freshness: `/api/v1/version`.
- **No watchdog yet** (documented V1 item): if M1 reboots, restart by hand
  or register a Task Scheduler job mirroring
  `scripts/register_intelligence_watchdog.ps1`.

## Agents: use the `evidence-wiki` skill

`.claude/skills/evidence-wiki/SKILL.md` — read-before-reinventing, write-
after-earning, corrections are non-destructive. Python client:
`evidence_wiki/ew/client.py` (`EW_SERVICE_URL` to point at M1 from M2–M4).

## V0 verdict (2026-09-01)

- Gates **G1–G5, G7–G18 PASS** (provenance, epistemic separation, retrieval,
  cross-linking, contradiction surfacing, reproducibility, contamination
  quarantine, usability, network, idempotency, multi-writer, parity,
  staleness). One caveat: G11 full four-machine reachability is verified
  from M1 only until the peer machines next come online.
- **G6 = TENSOR_NOT_YET_JUSTIFIED.** At 81 findings / 99 coordinates, the
  curated typed substrate (canonical mechanism terms) dominates
  cross-vocabulary retrieval (MRR 0.605 vs 0.078 BM25 / 0.062 embeddings /
  0.023 CP); the marginal baseline beats CP/Tucker/TT on held-out missing
  cells; CP factors are seed-unstable (mean matched cosine 0.58) and do not
  recover mechanism groups (ARI 0.03). Per charter §28 the tensor machinery
  is retained as rebuildable derived views and re-evaluated when the corpus
  grows (V1 trigger suggestion: ≥1000 coordinates).

## Layout

```
config.json                 service + db + auth config (V0 shared token; see A9 note)
migrations/                 001 schema · 002 evidence_terms · 003 mapping many-to-many
ew/                         store (canonical writes+queries) · coords · compiler ·
                            search · service (REST+wiki) · wiki · client · ontology
ingest/ingest_gold.py       charter §23 pipeline exercised on the gold corpus
gold/                       harvest_{a,b,c}.jsonl · curation_v1.json · id_map.json ·
                            benchmark_holdout.json
benchmarks/run_benchmarks.py + results_v0.json
tests/test_distributed_demo.py + distributed_demo_results.json
docs/                       ARCHITECTURE_V0.md · CASE_STUDIES_V0.md
derived/                    rebuildable artifacts (delete + rebuild == same hashes)
```
