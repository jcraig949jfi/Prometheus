# Hephaestus evidence harness (Necromancer pass, 2026-09-10)

Archaeology only. The forge itself (LLM APIs) was NEVER run. Hephaestus's own loaders
(`load_ledger`, `TRAPS`, `_ncd_baseline`, `trap_generator_extended`) were run as instruments
after an apparatus control (LAW N14): `openai` is stubbed
(`m=types.ModuleType("openai"); m.OpenAI=object; sys.modules["openai"]=m`) and
`agents/hephaestus/src` is put on `sys.path`. No network, no keys, no model calls.

Run every script from the repo root:

    python engine/necropolis/dossiers/hephaestus_evidence/<script>.py

Each script writes `<script>_result.json` next to itself (override the output dir with `SP=<dir>`).

| script | question | result file | headline |
|---|---|---|---|
| `heph_ledger_shape.py` | Q1 (why `api_call_failed` is a scrap OUTCOME; yield with instrument rows separated) and Q2 (priority / battery-version recoverability) | `heph_ledger_shape_result.json` | 6651 unique keys; 2861 keys first-buried by API failure, **0 ever retried**; yield excl. instrument rows W1 0.229 -> W2 0.0083 -> W4 0.018 -> W5 0.0057; battery size inferable per row from accuracy denominators (15 -> 186/93/62/31) |
| `heph_battery_floor.py` | does the forge's pass gate carry its answer? chance floor + random/constant tools through a replica of `run_trap_battery`'s gate | `heph_battery_floor_result.json` | 15-trap: chance acc 0.417, NCD baseline 0.267 (below chance), **random tool passes the gate 92.75%**; 186-trap: floor 0.324, random passes 2.4% ~= observed forge yield among battery-tested (0.7-2.2%) |
| `heph_nemesis_consumer.py` | did a contemporaneous consumer (Nemesis adversarial battery, 92 prompts x 140 tools) see skill? | `heph_nemesis_consumer_result.json` | population median 0.386 vs floor 0.370; correct answer first-or-last in 87/92 prompts; the top tools (0.73-0.77) are first-or-last pickers scoring **0.0 on middle-position prompts** |

Ledger windows (W0..W5) are cut at `agents/hephaestus/src/hephaestus.py` commit timestamps
(`git log --format='%h %ci %s' -- agents/hephaestus/src/hephaestus.py`); see `apparatus` in the
ledger-shape result for the exact boundaries.
