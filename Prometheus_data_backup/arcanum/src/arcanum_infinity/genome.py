import torch
from dataclasses import dataclass
from typing import Optional
from .seti_logger import slog

@dataclass
class SteeringGenome:
    layer_index: int
    vector: torch.Tensor
    id: Optional[str] = None
    fitness: float = 0.0
    position_ratio: float = 1.0  # 0.0=first token, 1.0=last token (default: last-token injection)
    exploration_type: str = "main"  # "main" vs "scout" (for layer-diversity tracking)

    def save(self, path: str):
        """Persist genome to disk. Returns True on success, False on failure."""
        try:
            torch.save({
                'layer_index': self.layer_index,
                'vector': self.vector.cpu(),
                'fitness': self.fitness,
                'position_ratio': self.position_ratio,
                'exploration_type': self.exploration_type,
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
