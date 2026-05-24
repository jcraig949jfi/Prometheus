"""Charon agent swarm — Stygian, Lethe, Acheron, Moros, Hecate.

Five looping child-agents that automate Charon's recurring mandate
(attack execution, anti-anchor mining, coordinate-collision detection,
cross-pollination, kill-geometry analysis). Each is a `CharonAgent`
subclass with `run_tick()` + `self_generate_backlog()`. The rotation
orchestrator at `scripts/charon_loop.py` cycles through them under
`/loop`.

See `charon/agents/_base.py` for the shared base class. Inherits from
`harmonia.agents._base.HarmoniaAgent` — the reusable scaffolding lives
there.

Design doc: `charon/agents/DESIGN_2026-05-19.md`.
"""

AGENT_NAMES = ["stygian", "lethe", "acheron", "moros", "hecate", "nephele", "pollux"]
