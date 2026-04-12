"""ReasoningEpisode — standardized data format for the RLVF loop.

Every data point in the system flows as a ReasoningEpisode. The episode
carries its provenance tag to enforce the data separation invariant
(adversarial data never enters training).

This is the atomic unit connecting:
    Rhea (generates episodes) → Hephaestus tools (evaluate episodes)
    → Nemesis (adversarial episodes) → Coeus (learns from episodes)
"""

import json
import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

log = logging.getLogger("hephaestus.episode")


@dataclass
class ReasoningEpisode:
    """A single reasoning event with evaluation results."""

    # Identity
    episode_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Provenance (HARD TAG — enforced by data pipeline)
    # "training" | "evaluation" | "adversarial"
    provenance: str = "evaluation"

    # Task
    prompt: str = ""
    candidates: list[str] = field(default_factory=list)
    correct: str | None = None
    task_type: str = ""  # "trap" | "adversarial" | "synthetic" | "real"

    # Model output (filled by Rhea)
    model_id: str = ""
    lora_id: str = ""
    answer: str = ""
    reasoning_trace: list[str] = field(default_factory=list)
    self_reported_confidence: float = 0.0

    # Tool evaluations (filled by RLVF fitness)
    evaluations: list[dict] = field(default_factory=list)
    # Each: {"tool": str, "score": float, "reasoning": str}

    # Fitness (computed by RLVFFitness)
    fitness: float = 0.0
    fitness_detail: dict = field(default_factory=dict)
    # {"weighted_sum": float, "variance": float, "penalty": float, ...}

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, d: dict) -> "ReasoningEpisode":
        return cls(**{k: v for k, v in d.items()
                      if k in cls.__dataclass_fields__})

    @classmethod
    def from_json(cls, s: str) -> "ReasoningEpisode":
        return cls.from_dict(json.loads(s))

    def validate_provenance(self) -> bool:
        """Check that provenance is a valid tag."""
        return self.provenance in ("training", "evaluation", "adversarial")

    def is_training_safe(self) -> bool:
        """Can this episode be used for model training?

        ONLY episodes with provenance='training' are safe.
        This is the hard gate preventing adversarial data contamination.
        """
        return self.provenance == "training"


def save_episodes(episodes: list[ReasoningEpisode], path: Path):
    """Append episodes to a JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for ep in episodes:
            f.write(ep.to_json() + "\n")


def load_episodes(path: Path, provenance_filter: str | None = None
                  ) -> list[ReasoningEpisode]:
    """Load episodes from JSONL, optionally filtering by provenance."""
    episodes = []
    if not path.exists():
        return episodes
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ep = ReasoningEpisode.from_json(line)
            except (json.JSONDecodeError, TypeError) as e:
                log.warning("Skipping corrupt episode in %s: %s", path, e)
                continue
            if provenance_filter and ep.provenance != provenance_filter:
                continue
            episodes.append(ep)
    return episodes


def training_gate(episodes: list[ReasoningEpisode]) -> list[ReasoningEpisode]:
    """Hard gate: filter to ONLY training-safe episodes.

    This function exists as a safety mechanism. Any code path that feeds
    episodes into model training MUST pass through this gate.

    Raises ValueError if any adversarial episode would be passed through.
    """
    safe = []
    for ep in episodes:
        if ep.provenance == "adversarial":
            raise ValueError(
                f"PROVENANCE VIOLATION: Adversarial episode {ep.episode_id} "
                f"cannot enter training pipeline. This is a hard architectural "
                f"invariant (Rhea Batch 3: mixing cost 25 points metacognition)."
            )
        if ep.is_training_safe():
            safe.append(ep)
    return safe
