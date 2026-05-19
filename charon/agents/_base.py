"""
CharonAgent base class — thin subclass over HarmoniaAgent that points
state + artifact dirs under `charon/agents/<name>/` and sets the
operator label to "Charon".

Everything else (heartbeat, deepseek_complete, pythia_enqueue_dr,
tail_stream, load_state / save_state, write_artifact, tick wrapper) is
inherited verbatim from `harmonia.agents._base.HarmoniaAgent`. The
shared scaffolding lives there; Charon does not duplicate it.

Subclasses override `name`, `role`, `run_tick(dry_run)`, and
`self_generate_backlog()`. See Harmonia's exemplars at
`harmonia/agents/{phylax,sophia,iris,argos,telos}/daemon.py` for the
contract.
"""
from __future__ import annotations

from pathlib import Path

from harmonia.agents._base import HarmoniaAgent, REPO_ROOT

CHARON_AGENTS_DIR = REPO_ROOT / "charon" / "agents"


class CharonAgent(HarmoniaAgent):
    """Charon-swarm base. Repoints state + artifact dirs to
    `charon/agents/<name>/{state,artifacts}/`.
    """

    operator: str = "Charon"
    machine: str = "M2"

    def __init__(self):
        super().__init__()
        self.state_dir = CHARON_AGENTS_DIR / self.name.lower() / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir = CHARON_AGENTS_DIR / self.name.lower() / "artifacts"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)


def get_charon_agent(name: str) -> CharonAgent:
    """Import + instantiate one of the five children by lowercase name."""
    name = name.lower()
    if name == "stygian":
        from charon.agents.stygian.daemon import StygianAgent
        return StygianAgent()
    if name == "lethe":
        from charon.agents.lethe.daemon import LetheAgent
        return LetheAgent()
    if name == "acheron":
        from charon.agents.acheron.daemon import AcheronAgent
        return AcheronAgent()
    if name == "moros":
        from charon.agents.moros.daemon import MorosAgent
        return MorosAgent()
    if name == "hecate":
        from charon.agents.hecate.daemon import HecateAgent
        return HecateAgent()
    raise ValueError(f"unknown charon agent: {name}")
