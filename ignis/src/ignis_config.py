from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml
import logging
import re


@dataclass
class ModelTarget:
    """Per-model configuration for the multi-model search cycle."""
    name: str                           # HuggingFace model ID
    target_layer_ratio: float = 0.75    # Where to inject (0.0=embed, 1.0=final)
    early_layer_ratio: float = 0.50     # Below this ratio = "shortcut" penalty zone
    generations_per_cycle: int = 50     # How many gens to run before rotating
    sigma_override: Optional[float] = None  # Per-model initial sigma (overrides global)
    seed_norm_override: Optional[float] = None  # Per-model inception seed norm (overrides global)
    tag: Optional[str] = None           # Optional tag for multi-config runs of same model

    @property
    def slug(self) -> str:
        """Filesystem-safe name derived from the model ID (+ tag if present)."""
        base = re.sub(r'[/\\:.]', '_', self.name).lower()
        if self.tag:
            base = f"{base}_{self.tag}"
        return base

    def target_layer(self, n_layers: int) -> int:
        """Compute the absolute target layer from the ratio."""
        return max(1, int(n_layers * self.target_layer_ratio))

    def early_layer_cutoff(self, n_layers: int) -> int:
        """Compute the absolute early-layer cutoff from the ratio."""
        return max(0, int(n_layers * self.early_layer_ratio))


@dataclass
class IgnisConfig:
    # Results root (per-model subdirs created automatically)
    results_dir: Path = Path("results/ignis")

    # Evolution (global defaults, can be overridden per-model)
    generations: int = 50
    population_size: int = 20
    mutation_rate: float = 0.1

    # ── Injection Intensity ─────────────────────────────────────────────
    # Norm to scale the inception seed and random baseline vectors to.
    # Default 3.0 gives CMA-ES room to grow intensity without starting
    # in the "Hallucination Zone" where small models (≤1B) produce
    # incoherent output. Larger models may tolerate higher norms (5.0+).
    # Per-model override available via ModelTarget.seed_norm_override.
    seed_norm: float = 3.0

    # ── Pre-Registered Decision Criteria ──────────────────────────────
    # Participation Ratio thresholds for "vector vs manifold" determination
    pr_vector_threshold: float = 3.0    # PR < 3 → single vector (point discovery)
    pr_manifold_threshold: float = 5.0  # PR > 5 → manifold (distributed mechanism)
    # PR in [3, 5] → ambiguous, needs more data

    # PC1 variance explained: how much of the elite variance is 1D
    pc1_min_variance: float = 0.60      # PC1 must explain ≥60% for "vector" claim

    # Sign-flip asymmetry: steered score must be ≥ this × sign-flip score
    sign_flip_asymmetry_ratio: float = 1.5

    # Discovery fitness threshold (must exceed random baseline by this factor)
    discovery_min_fitness: float = 2.0
    discovery_vs_random_ratio: float = 3.0  # evolved best / random baseline mean

    # Model rotation
    models: List[ModelTarget] = field(default_factory=lambda: [
        ModelTarget(name="Qwen/Qwen2.5-0.5B-Instruct")
    ])
    cycle_continuously: bool = True     # Loop forever through model list

    # Output sync (e.g., Google Drive mirror)
    sync_output_dir: Optional[Path] = None  # If set, results are copied here after each save

    # Alerts
    email_to: Optional[str] = None
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None

    def model_results_dir(self, model: ModelTarget) -> Path:
        """Per-model results subdirectory."""
        return self.results_dir / model.slug

    def model_state_file(self, model: ModelTarget) -> Path:
        """Per-model CMA-ES state file."""
        return self.model_results_dir(model) / "state.json"

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "IgnisConfig":
        target_path = path if path else Path("configs/ignis.yaml")
        if not target_path.exists():
            return cls()
        with open(target_path, "r") as f:
            data = yaml.safe_load(f)

        # Convert strings to Path objects
        if "results_dir" in data:
            data["results_dir"] = Path(data["results_dir"])
        if "sync_output_dir" in data and data["sync_output_dir"]:
            data["sync_output_dir"] = Path(data["sync_output_dir"])

        # Parse models list
        if "models" in data:
            raw_models = data.pop("models")
            data["models"] = [
                ModelTarget(**m) if isinstance(m, dict) else ModelTarget(name=m)
                for m in raw_models
            ]
        # Legacy single-model support: convert model_name to models list
        elif "model_name" in data:
            model_name = data.pop("model_name")
            sigma = data.get("mutation_rate")
            gens = data.get("generations", 50)
            data["models"] = [ModelTarget(
                name=model_name,
                sigma_override=sigma,
                generations_per_cycle=gens
            )]

        # Remove legacy fields that don't exist on the dataclass
        for legacy_key in ["state_file", "early_layer_cutoff", "crossover_rate", "model_name"]:
            data.pop(legacy_key, None)

        return cls(**data)

    def __str__(self):
        model_names = [m.name for m in self.models]
        return f"Ignis Config: {len(self.models)} models {model_names}, Pop {self.population_size}"
