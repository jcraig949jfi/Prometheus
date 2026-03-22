"""
Xenolexicon Database — persistent catalog of captured specimens.

Stores specimens as JSONL with companion .pt files for genome vectors
and embedding centroids. Provides distinctness checking against the
existing catalog.
"""

import json
import torch
from pathlib import Path
from typing import List, Optional
from .specimen import Specimen
from .seti_logger import slog


class XenolexiconDB:
    """
    Manages the persistent catalog of specimens.

    Storage layout:
        results/xenolexicon/{model_slug}/
        ├── xenolexicon.jsonl          # One JSON line per specimen
        ├── specimens/
        │   ├── {id}.pt               # Genome vector
        │   └── {id}_emb.pt           # Output embedding centroid
        └── baselines/
            └── unsteered_embeddings.pt
    """

    def __init__(self, results_dir: Path, distinctness_threshold: float = 0.1):
        self.results_dir = results_dir
        self.distinctness_threshold = distinctness_threshold
        self.catalog_path = results_dir / "xenolexicon.jsonl"
        self.specimens_dir = results_dir / "specimens"

        # In-memory cache of validated specimen embeddings for distance checks
        self._embedding_cache: List[torch.Tensor] = []
        self._specimen_ids: List[str] = []

        # Ensure directories exist
        self.specimens_dir.mkdir(parents=True, exist_ok=True)

        # Load existing embeddings on startup
        self._load_embedding_cache()

    def _load_embedding_cache(self):
        """Load all existing specimen embeddings into memory for distance checks."""
        self._embedding_cache.clear()
        self._specimen_ids.clear()

        if not self.catalog_path.exists():
            slog.debug("No existing catalog found — starting fresh")
            return

        try:
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    sid = entry.get("specimen_id", "")
                    status = entry.get("status", "candidate")

                    if status == "rejected":
                        continue

                    emb_path = self.specimens_dir / f"{sid}_emb.pt"
                    if emb_path.exists():
                        emb = torch.load(str(emb_path), weights_only=False)
                        self._embedding_cache.append(emb.float())
                        self._specimen_ids.append(sid)

            slog.info(f"Loaded {len(self._embedding_cache)} specimen embeddings from catalog")

        except Exception as e:
            slog.error(f"Failed to load embedding cache: {e}")

    def check_distinctness(self, embedding: torch.Tensor) -> tuple:
        """
        Check if a new specimen is sufficiently distinct from all existing ones.

        Args:
            embedding: Normalized embedding centroid of the candidate

        Returns:
            (is_distinct: bool, min_distance: float, nearest_id: str)
        """
        if not self._embedding_cache:
            return True, 1.0, ""

        embedding = embedding.float()
        distances = []
        for cached_emb in self._embedding_cache:
            cos_sim = torch.dot(embedding, cached_emb.to(embedding.device)).item()
            distance = max(0.0, 1.0 - cos_sim)
            distances.append(distance)

        min_dist = min(distances)
        min_idx = distances.index(min_dist)
        nearest_id = self._specimen_ids[min_idx]

        is_distinct = min_dist >= self.distinctness_threshold

        slog.debug(f"Distinctness check: min_dist={min_dist:.4f}, "
                   f"threshold={self.distinctness_threshold}, "
                   f"nearest={nearest_id}, distinct={is_distinct}")

        return is_distinct, min_dist, nearest_id

    def add_specimen(self, specimen: Specimen, embedding: Optional[torch.Tensor] = None):
        """
        Add a specimen to the catalog.

        Updates the JSONL file and the in-memory embedding cache.
        """
        specimen.save_to_jsonl(self.catalog_path)

        if embedding is not None:
            self._embedding_cache.append(embedding.float().cpu())
            self._specimen_ids.append(specimen.specimen_id)

        slog.info(f"Catalog entry added: [{specimen.status}] "
                  f"'{specimen.name}' ({specimen.specimen_id}) "
                  f"novelty={specimen.novelty_score:.4f}")

    def catalog_size(self) -> int:
        """Number of specimens in the embedding cache (excludes rejected)."""
        return len(self._embedding_cache)

    def get_catalog_summary(self) -> dict:
        """Return summary statistics for the current catalog."""
        if not self.catalog_path.exists():
            return {"total": 0, "validated": 0, "candidates": 0, "rejected": 0}

        counts = {"total": 0, "validated": 0, "candidate": 0, "rejected": 0}
        try:
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line.strip())
                        counts["total"] += 1
                        status = entry.get("status", "candidate")
                        counts[status] = counts.get(status, 0) + 1
        except Exception as e:
            slog.error(f"Catalog summary failed: {e}")

        return counts
