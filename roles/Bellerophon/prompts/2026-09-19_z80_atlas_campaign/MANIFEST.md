# MANIFEST -- 2026-09-19 Z80 x ATLAS 72-hour campaign (given to Nestor; the operator asked Bellerophon to build the same on BEE)

- 00_OPERATOR_DIRECTIVE_verbatim.md  the directive as received (ASCII, arrows -> written as ->)
- harness: prometheus/z80atlas/ (vm, tasks, world, grammar, geometry, observatory, runner, controls, scheduler, campaign; tests/)
- campaign workdir (off-repo, C: NVMe): C:\Users\James\z80atlas_campaign_2026-09-19  (state.json, runs.jsonl, families.jsonl, decisions.jsonl, runs/<id>/, CAMPAIGN_PACKET.md at stop)
- launch: python -m prometheus.z80atlas.campaign --workdir <dir> --hours 72 --workers 16 --ticks 500 --cells 256 --seed 20260919
- status: python -m prometheus.z80atlas.campaign --status --workdir <dir>;  resume after an interruption: --resume (same window; grammar + threshold hashes re-checked)
