"""
Xenolexicon Specimen — the catalog entry for a captured novel tensor state.

Each specimen represents a computational state that was produced by an evolved
steering vector pushing the model into an unusual region of output space.

Updated with Token Autopsy + Naming Scaffold integration:
  - Token Autopsy: logit shadow, concept cloud, discard classification
  - Naming Scaffold: failure mode from the naming pass (field biologist, etc.)

This is a drop-in replacement for specimen.py. All new fields have sensible
defaults so existing code and existing JSONL records load without modification.
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

    # ── Token Autopsy ───────────────────────────────────────────────
    # Answers: "What was the model THINKING when it generated this?"
    autopsy_classification: str = ""    # TRUE_ARCANUM | COLLISION | ECHO | CHIMERA | UNCLASSIFIABLE
    autopsy_confidence: float = -1.0    # -1 = not yet analyzed
    autopsy_recommendation: str = ""    # KEEP | DISCARD | EXTRACT_FRAGMENT
    autopsy_discard_reason: str = ""    # Why it was classified this way
    autopsy_mundane_fraction: float = -1.0  # Fraction of prob mass in mundane domains
    autopsy_novelty_coherence: float = -1.0  # How coherent the novel signal is
    autopsy_dominant_domains: list = field(default_factory=list)  # Top concept domains
    autopsy_summary: str = ""           # Human-readable one-liner

    # ── Naming Scaffold ─────────────────────────────────────────────
    # Answers: "What happened when the model tried to INTERPRET what it generated?"
    # Scaffold modes: CLEAN_NAME | FIELD_BIOLOGIST | META_LINGUISTIC |
    #                 CONVERSATIONAL_BLEED | HALLUCINATED_CITATION |
    #                 PERSONA_BLEND | RAW_SCAFFOLD | UNCLASSIFIABLE
    scaffold_mode: str = ""
    scaffold_confidence: float = -1.0
    scaffold_interpretation: str = ""
    scaffold_density: float = -1.0      # Fraction of naming tokens with scaffold signals
    scaffold_neologism_count: int = 0   # Invented words detected in naming pass
    scaffold_cross_lingual_scripts: list = field(default_factory=list)  # Scripts that bled through

    # ── Characterization ────────────────────────────────────────────
    reproducibility: float = -1.0       # -1 = not yet tested
    distinctness: float = -1.0          # -1 = not yet tested
    cross_substrate: Optional[bool] = None  # Post-MVP

    # ── Metadata ────────────────────────────────────────────────────
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S"))
    status: str = "candidate"           # candidate | validated | rejected

    def to_dict(self) -> dict:
        """Serialize to JSON-safe dict (no tensors)."""
        return asdict(self)

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
        """Reconstruct from a JSON dict (ignores unknown keys for backwards compat)."""
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


def capture_specimen(
    genome,
    generation: int,
    model_name: str,
    fitness: float,
    metadata: dict,
    novelty_results: list,
    results_dir: Path,
    # ── Token Autopsy args (optional) ───────────────────────────
    autopsy_engine=None,    # TokenAutopsy instance (or None to skip)
    model=None,             # Model reference needed for autopsy
    prompt_text: str = "",  # The provocation prompt (for autopsy regeneration)
) -> "Specimen":
    """
    Create a Specimen from evaluation results and persist the genome vector.

    Backwards compatible: autopsy_engine, model, and prompt_text all default
    to None/"" so existing callers need zero changes.

    If autopsy_engine and model are provided, runs the full token autopsy:
    1. Re-generates with logit shadow capture (token-by-token)
    2. Builds concept cloud from the shadow
    3. Classifies the specimen (TRUE_ARCANUM / COLLISION / ECHO / CHIMERA)
    4. Saves autopsy report, shadow JSON, and cloud JSON

    Naming scaffold fields (scaffold_mode etc.) are populated externally by
    the screener after calling generate_specimen_name(), then calling
    NamingAutopsy.classify_scaffold() on the raw output.

    Args:
        genome: SteeringGenome with layer_index, vector, position_ratio
        generation: Current generation number
        model_name: HuggingFace model identifier
        fitness: Overall novelty fitness score
        metadata: Dict from NoveltyFitnessEngine.evaluate_genome
        novelty_results: List of NoveltyResult from evaluation
        results_dir: Directory to save .pt files
        autopsy_engine: Optional TokenAutopsy instance
        model: Optional model for autopsy re-generation
        prompt_text: The provocation prompt text

    Returns:
        A populated Specimen instance (with autopsy data if engine provided)
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

    # ── Token Autopsy ─────────────────────────────────────────────
    if autopsy_engine is not None and model is not None:
        _run_autopsy(
            specimen=specimen,
            autopsy_engine=autopsy_engine,
            model=model,
            genome=genome,
            prompt_text=prompt_text,
            specimens_dir=specimens_dir,
        )

    slog.info(f"Specimen captured: {specimen.specimen_id} "
              f"(novelty={fitness:.4f}, layer={genome.layer_index}, "
              f"gen={generation})")

    # Log token autopsy result if available
    if specimen.autopsy_classification:
        icon = {
            "TRUE_ARCANUM": "🏛️",
            "COLLISION": "💥",
            "ECHO": "🔁",
            "CHIMERA": "🧬",
            "UNCLASSIFIABLE": "❓",
        }.get(specimen.autopsy_classification, "?")
        slog.info(f"  {icon} Autopsy: {specimen.autopsy_classification} "
                  f"(confidence={specimen.autopsy_confidence:.0%}, "
                  f"rec={specimen.autopsy_recommendation})")
        if specimen.autopsy_discard_reason:
            slog.info(f"     Reason: {specimen.autopsy_discard_reason[:120]}")

    # Save metadata JSON (persists name/description/outputs redundantly but safely)
    json_path = specimens_dir / f"{specimen.specimen_id}.json"
    specimen.save_json(json_path)

    return specimen


def _run_autopsy(specimen, autopsy_engine, model, genome, prompt_text, specimens_dir):
    """
    Run the full token autopsy pipeline on a captured specimen.

    Re-generates the output token-by-token with full logit capture,
    builds the concept cloud, classifies the specimen, and saves all data.
    """
    try:
        slog.info(f"  🔬 Running token autopsy for {specimen.specimen_id}...")

        # Step 1: Capture logit shadow (re-generate token-by-token)
        shadow = autopsy_engine.capture_logit_shadow(
            model=model,
            genome=genome,
            prompt=prompt_text,
            max_new_tokens=128,
        )

        if shadow is None:
            slog.warning(f"  Autopsy: logit shadow capture failed")
            specimen.autopsy_classification = "UNCLASSIFIABLE"
            specimen.autopsy_discard_reason = "Logit shadow capture failed"
            return

        # Step 2: Build concept cloud
        cloud = autopsy_engine.build_concept_cloud(shadow, model)

        # Step 3: Classify
        classification = autopsy_engine.classify_specimen(cloud)

        # Step 4: Populate specimen fields
        specimen.autopsy_classification = classification.category
        specimen.autopsy_confidence = classification.confidence
        specimen.autopsy_recommendation = classification.recommendation
        specimen.autopsy_discard_reason = classification.discard_reason
        specimen.autopsy_mundane_fraction = cloud.mundane_fraction
        specimen.autopsy_novelty_coherence = cloud.novelty_coherence
        specimen.autopsy_dominant_domains = cloud.dominant_domains
        specimen.autopsy_summary = cloud.summary

        # Step 5: Save autopsy artifacts
        shadow_path = specimens_dir / f"{specimen.specimen_id}_shadow.json"
        try:
            with open(shadow_path, "w", encoding="utf-8") as f:
                json.dump(shadow.to_dict(), f, indent=2)
            slog.trace(f"  Logit shadow saved: {shadow_path}")
        except Exception as e:
            slog.warning(f"  Failed to save logit shadow: {e}")

        cloud_path = specimens_dir / f"{specimen.specimen_id}_cloud.json"
        try:
            with open(cloud_path, "w", encoding="utf-8") as f:
                json.dump(cloud.to_dict(), f, indent=2)
            slog.trace(f"  Concept cloud saved: {cloud_path}")
        except Exception as e:
            slog.warning(f"  Failed to save concept cloud: {e}")

        report = autopsy_engine.generate_autopsy_report(shadow, cloud, classification)
        report_path = specimens_dir / f"{specimen.specimen_id}_autopsy.txt"
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)
            slog.trace(f"  Autopsy report saved: {report_path}")
        except Exception as e:
            slog.warning(f"  Failed to save autopsy report: {e}")

    except Exception as e:
        slog.exception(f"  Autopsy failed for {specimen.specimen_id}: {e}")
        specimen.autopsy_classification = "UNCLASSIFIABLE"
        specimen.autopsy_discard_reason = f"Autopsy exception: {str(e)[:100]}"
