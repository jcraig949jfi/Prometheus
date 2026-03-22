"""
Xenolexicon Specimen — the catalog entry for a captured novel tensor state.

Each specimen represents a computational state that was produced by an evolved
steering vector pushing the model into an unusual region of output space.
"""

import uuid
import time
import json
import torch
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
from .seti_logger import slog


@dataclass
class Specimen:
    """A captured novel tensor state with full provenance."""

    # ── Identity ────────────────────────────────────────────────────
    specimen_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    name: str = ""                      # Compound name (from naming engine)
    description: str = ""               # Human-approximation description

    # ── Provenance ──────────────────────────────────────────────────
    genome_layer: int = 0
    genome_norm: float = 0.0
    genome_position_ratio: float = 1.0
    generation: int = 0
    model_name: str = ""

    # ── Behavioral Signature ────────────────────────────────────────
    novelty_score: float = 0.0
    semantic_distance: float = 0.0      # Mean across provocations
    coherence_score: float = 0.0        # Mean across provocations
    perplexity_profile: list = field(default_factory=list)  # Per-provocation

    # ── Outputs ─────────────────────────────────────────────────────
    outputs: dict = field(default_factory=dict)  # provocation_name → text

    # ── Characterization ────────────────────────────────────────────
    reproducibility: float = -1.0       # -1 = not yet tested
    distinctness: float = -1.0          # -1 = not yet tested
    cross_substrate: Optional[bool] = None  # Post-MVP

    # ── Metadata ────────────────────────────────────────────────────
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S"))
    status: str = "candidate"           # candidate | validated | rejected

    def to_dict(self) -> dict:
        """Serialize to JSON-safe dict (no tensors)."""
        d = asdict(self)
        return d

    def save_json(self, path: Path):
        """Save this specimen metadata to a dedicated JSON file."""
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=4)
            slog.trace(f"Specimen metadata saved to {path}")
        except Exception as e:
            slog.error(f"Specimen JSON write failed: {e}")

    def save_to_jsonl(self, path: Path):
        """Append this specimen as a single JSON line."""
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(self.to_dict()) + "\n")
            slog.trace(f"Specimen {self.specimen_id} saved to {path}")
        except Exception as e:
            slog.error(f"Specimen JSONL write failed: {e}")

    @classmethod
    def from_dict(cls, d: dict) -> "Specimen":
        """Reconstruct from a JSON dict."""
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


def capture_specimen(
    genome,
    generation: int,
    model_name: str,
    fitness: float,
    metadata: dict,
    novelty_results: list,
    results_dir: Path,
) -> Specimen:
    """
    Create a Specimen from evaluation results and persist the genome vector.

    Args:
        genome: SteeringGenome that produced the novel output
        generation: Current generation number
        model_name: HuggingFace model identifier
        fitness: Overall novelty fitness score
        metadata: Dict from NoveltyFitnessEngine.evaluate_genome
        novelty_results: List of NoveltyResult from evaluation
        results_dir: Directory to save .pt files

    Returns:
        A populated Specimen instance
    """
    specimen = Specimen(
        genome_layer=genome.layer_index,
        genome_norm=genome.vector.norm().item(),
        genome_position_ratio=getattr(genome, 'position_ratio', 1.0),
        generation=generation,
        model_name=model_name,
        novelty_score=fitness,
        semantic_distance=metadata.get("mean_semantic_distance", 0.0),
        coherence_score=metadata.get("mean_coherence", 0.0),
        perplexity_profile=[round(r.perplexity, 2) for r in novelty_results],
        outputs={r.provocation_name: r.output_text for r in novelty_results},
    )

    # Save genome vector
    specimens_dir = results_dir / "specimens"
    specimens_dir.mkdir(parents=True, exist_ok=True)

    genome_path = specimens_dir / f"{specimen.specimen_id}.pt"
    try:
        torch.save({
            'layer_index': genome.layer_index,
            'vector': genome.vector.cpu(),
            'position_ratio': getattr(genome, 'position_ratio', 1.0),
            'novelty_score': fitness,
        }, str(genome_path))
        slog.trace(f"Specimen genome saved: {genome_path}")
    except Exception as e:
        slog.error(f"Failed to save specimen genome: {e}")

    # Save embedding centroid (mean of all provocation embeddings)
    valid_embeddings = [r.output_embedding for r in novelty_results
                        if r.output_embedding is not None]
    if valid_embeddings:
        centroid = torch.stack(valid_embeddings).mean(dim=0)
        centroid = centroid / (centroid.norm() + 1e-10)
        emb_path = specimens_dir / f"{specimen.specimen_id}_emb.pt"
        try:
            torch.save(centroid, str(emb_path))
            slog.trace(f"Specimen embedding saved: {emb_path}")
        except Exception as e:
            slog.error(f"Failed to save specimen embedding: {e}")

    slog.info(f"Specimen captured: {specimen.specimen_id} "
              f"(novelty={fitness:.4f}, layer={genome.layer_index}, "
              f"gen={generation})")

    # Save metadata JSON file (redundant but safe)
    json_path = specimens_dir / f"{specimen.specimen_id}.json"
    specimen.save_json(json_path)

    return specimen
