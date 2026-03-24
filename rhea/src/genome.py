"""
Rhea genome: LoRA perturbations as an evolvable genome.

Unlike Ignis (which evolves steering vectors injected into the
residual stream), Rhea evolves actual weight perturbations via
LoRA adapters. The genome is the flattened LoRA parameter vector.

CMA-ES navigates this space — each individual in the population
is a different LoRA configuration applied to the seed model.

Seed: SmolLM2-135M-Instruct
LoRA targets: q_proj, v_proj, gate_proj (rank 4)
Genome dimensionality: ~800K parameters
"""

import torch
import numpy as np
from peft import LoraConfig, get_peft_model, set_peft_model_state_dict
from dataclasses import dataclass, field
from pathlib import Path


# LoRA configuration for the 135M seed
LORA_CONFIG = LoraConfig(
    r=4,
    lora_alpha=8,
    target_modules=["q_proj", "v_proj", "gate_proj"],
    lora_dropout=0.0,   # no dropout for evolution — deterministic fitness
    bias="none",
    task_type="CAUSAL_LM",
)


@dataclass
class LoraGenome:
    """A single evolvable individual: a flattened LoRA parameter vector."""
    genome_vector: np.ndarray          # flat 1D array — the CMA-ES search space
    fitness: float = 0.0
    ejection_suppression: float = 0.0  # monotonicity score from logit lens
    survival_rate: float = 0.0         # fraction of traps with correct in top-5
    generation: int = 0
    genome_id: str = ""
    metadata: dict = field(default_factory=dict)

    @property
    def dimensionality(self) -> int:
        return len(self.genome_vector)

    def save(self, path: str | Path):
        path = Path(path)
        torch.save({
            "genome_vector": self.genome_vector,
            "fitness": self.fitness,
            "ejection_suppression": self.ejection_suppression,
            "survival_rate": self.survival_rate,
            "generation": self.generation,
            "genome_id": self.genome_id,
            "metadata": self.metadata,
        }, path)

    @classmethod
    def load(cls, path: str | Path) -> "LoraGenome":
        data = torch.load(path, weights_only=False)
        return cls(
            genome_vector=data["genome_vector"],
            fitness=data.get("fitness", 0.0),
            ejection_suppression=data.get("ejection_suppression", 0.0),
            survival_rate=data.get("survival_rate", 0.0),
            generation=data.get("generation", 0),
            genome_id=data.get("genome_id", ""),
            metadata=data.get("metadata", {}),
        )


def get_lora_param_count(model) -> int:
    """Count trainable LoRA parameters after wrapping."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def get_lora_param_names(model) -> list[str]:
    """Get names of all LoRA parameters (for ordered flatten/unflatten)."""
    return [n for n, p in model.named_parameters() if p.requires_grad]


def flatten_lora_params(model) -> np.ndarray:
    """Extract all LoRA parameters into a single flat numpy array."""
    params = []
    for n, p in model.named_parameters():
        if p.requires_grad:
            params.append(p.data.cpu().numpy().flatten())
    return np.concatenate(params)


def unflatten_lora_params(model, flat_vector: np.ndarray):
    """
    Write a flat numpy vector back into the model's LoRA parameters.
    Must match the order from flatten_lora_params.
    """
    offset = 0
    for n, p in model.named_parameters():
        if p.requires_grad:
            numel = p.numel()
            chunk = flat_vector[offset:offset + numel]
            p.data.copy_(torch.from_numpy(chunk.reshape(p.shape)).to(p.device, p.dtype))
            offset += numel
    assert offset == len(flat_vector), (
        f"Vector length mismatch: expected {offset}, got {len(flat_vector)}"
    )


def apply_genome(model, genome: LoraGenome):
    """Apply a genome's parameters to a LoRA-wrapped model."""
    unflatten_lora_params(model, genome.genome_vector)


def extract_genome(model, generation: int = 0, genome_id: str = "") -> LoraGenome:
    """Extract current LoRA state as a genome."""
    return LoraGenome(
        genome_vector=flatten_lora_params(model),
        generation=generation,
        genome_id=genome_id,
    )
