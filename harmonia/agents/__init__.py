"""Harmonia agent swarm — Phylax, Sophia, Iris, Argos, Telos.

Each agent is a self-tickable daemon with a `run_tick()` entry point and
a `self_generate_backlog()` source. The rotation orchestrator at
`scripts/harmonia_loop.py` cycles through them under `/loop`.

See `harmonia/agents/_base.py` for the shared base class and helper APIs.
"""

AGENT_NAMES = ["phylax", "sophia", "iris", "argos", "telos"]
