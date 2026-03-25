import torch
from dataclasses import dataclass
from typing import Optional
from ignis_logger import slog

@dataclass
class SteeringGenome:
    layer_index: int
    vector: torch.Tensor
    id: Optional[str] = None
    fitness: float = 0.0
    position_ratio: float = 1.0  # 0.0=first token, 1.0=last token (default: last-token injection)
    exploration_type: str = "main"  # "main" vs "scout" (for layer-diversity tracking)
    # RPH proxy fields — populated by score_rph_proxies() when rph_proxies.enabled: true
    # Defaults of 0.0 / False are safe sentinels (old .pt files load cleanly via .get())
    rph_delta_cf: float = 0.0       # Counterfactual sensitivity (SBERT semantic distance)
    rph_mi_step: float = 0.0        # Stepwise mutual information (PCA + shuffled baseline)
    rph_ecr: float = 0.0            # Error correction rate (Phase 2 — not yet implemented)
    rph_passes: int = 0             # Number of RPH criteria passed (0–3)
    rph_precipitation_candidate: bool = False  # True if classify_vector() == PRECIPITATION_CANDIDATE
    # RLVF fields — populated by score_rlvf() when forged tools available
    rlvf_fitness: float = 0.0           # F(T) = Σwᵢ·Sᵢ - λ·σ(S)
    rlvf_variance: float = 0.0         # Tool disagreement (gaming indicator)
    rlvf_n_tools: int = 0              # Number of tools that scored

    def save(self, path: str):
        """Persist genome to disk. Returns True on success, False on failure."""
        try:
            torch.save({
                'layer_index': self.layer_index,
                'vector': self.vector.cpu(),
                'fitness': self.fitness,
                'position_ratio': self.position_ratio,
                'exploration_type': self.exploration_type,
                'rph_delta_cf': self.rph_delta_cf,
                'rph_mi_step': self.rph_mi_step,
                'rph_ecr': self.rph_ecr,
                'rph_passes': self.rph_passes,
                'rph_precipitation_candidate': self.rph_precipitation_candidate,
                'rlvf_fitness': self.rlvf_fitness,
                'rlvf_variance': self.rlvf_variance,
                'rlvf_n_tools': self.rlvf_n_tools,
            }, path)
            slog.trace(f"Genome saved → {path}  (layer={self.layer_index}, fitness={self.fitness:.4f}, "
                        f"norm={self.vector.norm().item():.4f})")
            return True
        except Exception as e:
            slog.error(f"Genome save FAILED → {path}: {e}")
            return False

    @classmethod
    def load(cls, path: str) -> Optional["SteeringGenome"]:
        """Load genome from disk. Returns None on failure instead of crashing."""
        try:
            data = torch.load(path, weights_only=False)
            genome = cls(
                layer_index=data['layer_index'],
                vector=data['vector'],
                fitness=data.get('fitness', 0.0),
                position_ratio=data.get('position_ratio', 1.0),
                exploration_type=data.get('exploration_type', 'main'),
                rph_delta_cf=data.get('rph_delta_cf', 0.0),
                rph_mi_step=data.get('rph_mi_step', 0.0),
                rph_ecr=data.get('rph_ecr', 0.0),
                rph_passes=data.get('rph_passes', 0),
                rph_precipitation_candidate=data.get('rph_precipitation_candidate', False),
            )
            slog.trace(f"Genome loaded ← {path}  (layer={genome.layer_index}, "
                        f"fitness={genome.fitness:.4f}, norm={genome.vector.norm().item():.4f})")
            return genome
        except FileNotFoundError:
            slog.warning(f"Genome file not found: {path}")
            return None
        except Exception as e:
            slog.error(f"Genome load FAILED ← {path}: {e}")
            return None
