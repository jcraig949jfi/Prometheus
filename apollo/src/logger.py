"""
logger.py — Append-only JSONL lineage logging + dashboard.
"""

import json
import time
from pathlib import Path


def log_organism(genome, fitness, generation: int,
                 path: str = "F:/Prometheus/apollo/lineage/lineage.jsonl"):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    record = {
        'genome_id': genome.genome_id,
        'generation': generation,
        'parent_ids': genome.lineage.get('parent_ids', []),
        'mutations_applied': genome.lineage.get('mutations_applied', []),
        'source_tool': genome.source_tool,
        'gene_count': genome.gene_count,
        'wiring_hash': genome.wiring_hash(),
        'has_self_referential_wiring': genome.has_self_referential_wiring(),
        'fallback_count': genome.fallback_count,
        'fitness': {
            'adjusted_margin_accuracy': fitness.adjusted_margin_accuracy,
            'margin_calibration': fitness.margin_calibration,
            'novelty_score': fitness.novelty_score,
            'ncd_independence': fitness.ncd_independence,
            'raw_accuracy': fitness.raw_accuracy,
        },
        'crash_count': fitness.crash_count,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
    }
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record) + '\n')


def log_dashboard(generation: int, population: list, fitness_vectors: list,
                  archive_size: int, compilation_survival: float,
                  path: str = "F:/Prometheus/apollo/dashboard/status.jsonl"):
    import numpy as np

    accuracies = [fv.adjusted_margin_accuracy for fv in fitness_vectors]
    calibrations = [fv.margin_calibration for fv in fitness_vectors]
    gene_counts = [g.gene_count for g in population]
    self_ref = [g.has_self_referential_wiring() for g in population]
    fb = [g.fallback_count for g in population]

    record = {
        'generation': generation,
        'population_size': len(population),
        'compilation_survival_pct': compilation_survival,
        'median_margin_accuracy': float(np.median(accuracies)) if accuracies else 0.0,
        'best_margin_accuracy': float(max(accuracies)) if accuracies else 0.0,
        'median_calibration': float(np.median(calibrations)) if calibrations else 0.0,
        'pct_self_referential': sum(self_ref) / len(self_ref) if self_ref else 0.0,
        'pct_with_fallback': sum(1 for f in fb if f > 0) / len(fb) if fb else 0.0,
        'novelty_archive_size': archive_size,
        'median_gene_count': float(np.median(gene_counts)) if gene_counts else 0.0,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
    }
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record) + '\n')
