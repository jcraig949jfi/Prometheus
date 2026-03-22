"""
Xenolexicon Configuration — extends Ignis config with novelty parameters.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import yaml
import re


@dataclass
class ModelTarget:
    """Per-model configuration (identical to Ignis)."""
    name: str
    target_layer_ratio: float = 0.75
    early_layer_ratio: float = 0.50
    generations_per_cycle: int = 50
    sigma_override: Optional[float] = None
    seed_norm_override: Optional[float] = None

    @property
    def slug(self) -> str:
        return re.sub(r'[/\\:.]', '_', self.name).lower()

    def target_layer(self, n_layers: int) -> int:
        return max(1, int(n_layers * self.target_layer_ratio))

    def early_layer_cutoff(self, n_layers: int) -> int:
        return max(0, int(n_layers * self.early_layer_ratio))


@dataclass
class XenoConfig:
    """Xenolexicon configuration — novelty search parameters."""

    # ── Results ──────────────────────────────────────────────────────
    results_dir: Path = Path("results/xenolexicon")

    # ── Evolution (CMA-ES, same as Ignis) ──────────────────────────
    generations: int = 50
    population_size: int = 20
    mutation_rate: float = 0.1
    seed_norm: float = 3.0

    # ── Novelty Fitness ──────────────────────────────────────────────
    target_perplexity: float = 50.0        # Sweet spot for coherence scoring
    novelty_threshold: float = 0.3         # Min score to capture specimen
    max_new_tokens: int = 128              # Generation length for provocations

    # ── Specimen Characterization ────────────────────────────────────
    distinctness_threshold: float = 0.1    # Min cosine distance for catalog
    reproducibility_runs: int = 3          # Re-runs for reproducibility check
    reproducibility_threshold: float = 0.7 # Min pairwise cosine for "reproducible"
    random_baseline_samples: int = 5       # Random vectors for calibration

    # ── Naming ───────────────────────────────────────────────────────
    naming_max_tokens: int = 128

    # ── Model Rotation ───────────────────────────────────────────────
    models: List[ModelTarget] = field(default_factory=lambda: [
        ModelTarget(name="Qwen/Qwen2.5-0.5B-Instruct")
    ])
    cycle_continuously: bool = False       # Single pass for MVP

    # ── Output Sync ──────────────────────────────────────────────────
    sync_output_dir: Optional[Path] = None

    def model_results_dir(self, model: ModelTarget) -> Path:
        return self.results_dir / model.slug

    def model_state_file(self, model: ModelTarget) -> Path:
        return self.model_results_dir(model) / "state.pt"

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "XenoConfig":
        target_path = path if path else Path("configs/xenolexicon.yaml")
        if not target_path.exists():
            return cls()
        with open(target_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if "results_dir" in data:
            data["results_dir"] = Path(data["results_dir"])
        if "sync_output_dir" in data and data["sync_output_dir"]:
            data["sync_output_dir"] = Path(data["sync_output_dir"])

        if "models" in data:
            raw_models = data.pop("models")
            data["models"] = [
                ModelTarget(**m) if isinstance(m, dict) else ModelTarget(name=m)
                for m in raw_models
            ]

        return cls(**data)

    def __str__(self):
        model_names = [m.name for m in self.models]
        return (f"Xenolexicon Config: {len(self.models)} models {model_names}, "
                f"Pop {self.population_size}, target_ppl={self.target_perplexity}")


def load_config(path: str = "configs/xenolexicon.yaml") -> XenoConfig:
    """Helper for the arcanum_infinity package interface."""
    return XenoConfig.load(Path(path))
