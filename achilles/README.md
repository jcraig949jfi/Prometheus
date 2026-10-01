# achilles/ -- the Prometheus fleet census (seat: Achilles)

Owner: Achilles (roles/Achilles; charter roles/Achilles/prompts/2026-09-30_charter/).

One authoritative, evidence-backed map of the whole fleet, rebuilt every 6
hours from git, seat files, the fleet-order ledgers and the M1 database, and
published through the machinery Prometheus already has.

    achilles/census/sources.py   evidence collectors (git, roles/, ops/, comms, ew, agora)
    achilles/census/classify.py  deterministic rules (attribution, experiments, state)
    achilles/census/build.py     canonical snapshot prometheus.fleet_census.v2 (+ delta, anomalies)
    achilles/census/render.py    HTML page, email block, markdown -- renderings only
    achilles/census/run.py       one cycle: sync, build, write, commit, push, receipt, park
    achilles/census/tests/       controls (positive, negative, cheat)
    achilles/deploy/             run_census.cmd + register_fleet_census.ps1 (task PrometheusFleetCensus)

Outputs (all from the one snapshot):

    docs/fleet/fleet_state.json   canonical snapshot (extends ops/fleet/CENSUS.json v1)
    docs/fleet/index.html         https://jcraig949jfi.github.io/Prometheus/fleet/
    docs/fleet/email_census.json  census section embedded by scripts/send_brief_email.py
    docs/fleet/FLEET_CENSUS.md    markdown compatibility artifact
    docs/fleet/run_status.json    last attempted / last successful run (freshness)
    roles/Achilles/census/runs/<YYYY-MM>.jsonl   durable run receipts

Rules: roles/Achilles/CLASSIFICATION_RULES.md. Registry of seat roles and
engines (first-run reconstruction, re-verified every run):
roles/Achilles/census/registry/. Reconstruction of the older reporting
stack: roles/Achilles/RECONSTRUCTION_2026-09-30.md.

Run by hand (no push):

    set EW_DB_HOST=192.168.1.202
    python -m achilles.census.run --publish-root <a non-canonical worktree> --no-sync --no-push

Tests: `python -m pytest -q achilles/census/tests`.
