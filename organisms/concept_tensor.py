"""
Concept Tensor — Feature-encode all 95 Lattice concepts as mathematical objects.

Each concept gets a 30-dimensional feature vector encoding its structural,
dynamic, and informational properties. These vectors are the atoms of the
tensor shortcut: from them we compute interaction tensors, compress via
tensor trains, and navigate the full combinatorial space at microsecond speed.

Feature dimensions are chosen to maximize the signal for COMPLEMENTARITY
and RESONANCE — the two properties that predict successful compositions
in the forge. Two concepts that are complementary (different strengths)
AND resonant (shared structural properties that amplify) produce novel
interfaces when combined.

Sources:
  - Structural properties derived from each concept's mathematical nature
  - Forge effect scores from Coeus (which concepts improve tool quality)
  - Mechanism types from Nous (constraint/structure/dynamics/measure)
  - Adversarial survival from Coeus (robustness signal)
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent

# ============================================================
# Feature Dimensions (30)
# ============================================================
# Each concept is scored 0.0-1.0 on each dimension.
# Dimensions chosen to capture properties that predict
# successful cross-concept composition.

FEATURE_NAMES = [
    # Structural properties (how the concept organizes information)
    "dimensionality",       # 0: operates in high-dimensional spaces
    "linearity",            # 1: linear vs nonlinear
    "determinism",          # 2: deterministic vs stochastic
    "scale_invariance",     # 3: properties preserved across scales
    "compositionality",     # 4: can be composed with other structures
    "invertibility",        # 5: operations can be reversed
    "stability",            # 6: invariants / fixed points / equilibria
    "information_content",  # 7: how much information the concept carries
    "boundary_sensitivity", # 8: awareness of boundaries / interfaces
    "self_reference",       # 9: recursive / self-referential structure

    # Dynamic properties (how the concept evolves)
    "temporal",             # 10: time-dependent behavior
    "conservation",         # 11: conserved quantities
    "adaptivity",           # 12: ability to adapt / learn
    "emergence",            # 13: macro properties from micro rules
    "robustness",           # 14: resistant to perturbation

    # Relational properties (how the concept connects to others)
    "hierarchy",            # 15: hierarchical organization
    "locality",             # 16: local vs global
    "symmetry",             # 17: symmetry / invariance groups
    "discreteness",         # 18: discrete vs continuous
    "causality",            # 19: causal structure

    # Computational properties
    "computability",        # 20: can be computed / algorithmized
    "parallelism",          # 21: admits parallel computation
    "compression",          # 22: admits compressed representation
    "generativity",         # 23: generates new structures
    "optimization",         # 24: has optimization / extremal principles

    # Epistemic properties (what the concept says about knowledge)
    "falsifiability",       # 25: predictions can be tested
    "abstraction_level",    # 26: concrete vs abstract
    "cross_domain",         # 27: applies across multiple domains
    "explanatory_depth",    # 28: how deep the explanations go
    "surprise_potential",   # 29: likelihood of producing unexpected results
]

N_FEATURES = len(FEATURE_NAMES)
assert N_FEATURES == 30

# ============================================================
# The 95-concept feature encoding
# ============================================================
# Hand-seeded from domain knowledge. This is the bootstrap.
# Later: learned from forge success data via Coeus feedback.

CONCEPT_FEATURES: Dict[str, List[float]] = {
    # === Mathematics (12) ===
    "Topology": [
        0.9, 0.3, 1.0, 0.8, 0.7, 0.9, 0.9, 0.6, 0.95, 0.4,
        0.1, 0.95, 0.1, 0.6, 0.95, 0.7, 0.3, 0.8, 0.3, 0.1,
        0.7, 0.5, 0.6, 0.5, 0.3, 0.8, 0.9, 0.85, 0.9, 0.7,
    ],
    "Category Theory": [
        0.95, 0.5, 1.0, 0.9, 0.95, 0.9, 0.95, 0.7, 0.5, 0.8,
        0.1, 0.8, 0.1, 0.5, 0.9, 0.9, 0.2, 0.95, 0.4, 0.3,
        0.6, 0.5, 0.8, 0.7, 0.4, 0.6, 0.95, 0.95, 0.95, 0.8,
    ],
    "Fourier Transforms": [
        0.5, 0.9, 1.0, 0.6, 0.8, 0.95, 0.8, 0.9, 0.3, 0.2,
        0.7, 0.8, 0.1, 0.2, 0.8, 0.3, 0.5, 0.9, 0.4, 0.1,
        0.95, 0.9, 0.9, 0.3, 0.5, 0.9, 0.5, 0.8, 0.6, 0.3,
    ],
    "Prime Number Theory": [
        0.4, 0.3, 1.0, 0.5, 0.4, 0.3, 0.9, 0.9, 0.2, 0.3,
        0.0, 0.9, 0.0, 0.5, 0.95, 0.4, 0.5, 0.6, 0.95, 0.1,
        0.8, 0.6, 0.7, 0.4, 0.3, 0.7, 0.7, 0.6, 0.9, 0.8,
    ],
    "Fractal Geometry": [
        0.8, 0.2, 1.0, 0.95, 0.6, 0.3, 0.7, 0.8, 0.6, 0.95,
        0.2, 0.5, 0.1, 0.8, 0.7, 0.9, 0.4, 0.7, 0.3, 0.1,
        0.8, 0.8, 0.9, 0.8, 0.3, 0.7, 0.7, 0.7, 0.7, 0.7,
    ],
    "Tensor Decomposition": [
        0.95, 0.7, 1.0, 0.5, 0.8, 0.6, 0.7, 0.8, 0.3, 0.2,
        0.1, 0.6, 0.1, 0.3, 0.7, 0.5, 0.4, 0.6, 0.3, 0.1,
        0.95, 0.9, 0.95, 0.4, 0.7, 0.8, 0.6, 0.7, 0.6, 0.4,
    ],
    "Ergodic Theory": [
        0.7, 0.4, 0.6, 0.7, 0.5, 0.4, 0.8, 0.7, 0.3, 0.3,
        0.9, 0.8, 0.2, 0.5, 0.8, 0.3, 0.3, 0.6, 0.3, 0.2,
        0.6, 0.4, 0.5, 0.3, 0.4, 0.7, 0.8, 0.7, 0.8, 0.5,
    ],
    "Information Theory": [
        0.6, 0.5, 0.8, 0.5, 0.8, 0.4, 0.7, 0.95, 0.4, 0.3,
        0.3, 0.7, 0.2, 0.4, 0.8, 0.4, 0.4, 0.5, 0.4, 0.3,
        0.9, 0.6, 0.9, 0.5, 0.7, 0.9, 0.7, 0.9, 0.8, 0.5,
    ],
    "Bayesian Inference": [
        0.5, 0.5, 0.5, 0.3, 0.7, 0.5, 0.6, 0.9, 0.3, 0.3,
        0.7, 0.5, 0.9, 0.4, 0.7, 0.5, 0.5, 0.3, 0.4, 0.7,
        0.9, 0.6, 0.7, 0.6, 0.8, 0.9, 0.6, 0.9, 0.7, 0.5,
    ],
    "Graph Theory": [
        0.7, 0.5, 1.0, 0.5, 0.8, 0.5, 0.7, 0.7, 0.5, 0.3,
        0.1, 0.5, 0.1, 0.6, 0.7, 0.7, 0.5, 0.6, 0.8, 0.3,
        0.9, 0.8, 0.7, 0.6, 0.5, 0.8, 0.6, 0.85, 0.7, 0.5,
    ],
    "Measure Theory": [
        0.8, 0.6, 1.0, 0.6, 0.7, 0.4, 0.9, 0.8, 0.5, 0.3,
        0.1, 0.9, 0.0, 0.3, 0.9, 0.5, 0.3, 0.6, 0.3, 0.1,
        0.7, 0.5, 0.5, 0.3, 0.4, 0.7, 0.9, 0.7, 0.9, 0.3,
    ],
    "Dynamical Systems": [
        0.7, 0.4, 0.7, 0.5, 0.6, 0.4, 0.7, 0.7, 0.4, 0.3,
        0.95, 0.7, 0.3, 0.7, 0.6, 0.4, 0.5, 0.5, 0.3, 0.6,
        0.8, 0.5, 0.5, 0.5, 0.6, 0.8, 0.7, 0.8, 0.8, 0.6,
    ],

    # === Physics (8) ===
    "Chaos Theory": [
        0.6, 0.1, 0.9, 0.5, 0.4, 0.2, 0.3, 0.8, 0.5, 0.3,
        0.95, 0.4, 0.2, 0.8, 0.3, 0.3, 0.6, 0.3, 0.3, 0.5,
        0.8, 0.5, 0.4, 0.5, 0.3, 0.9, 0.7, 0.7, 0.7, 0.9,
    ],
    "Thermodynamics": [
        0.5, 0.5, 0.6, 0.5, 0.6, 0.3, 0.8, 0.8, 0.5, 0.2,
        0.8, 0.95, 0.2, 0.5, 0.8, 0.4, 0.4, 0.5, 0.3, 0.5,
        0.7, 0.5, 0.6, 0.3, 0.7, 0.9, 0.6, 0.8, 0.8, 0.4,
    ],
    "Quantum Mechanics": [
        0.9, 0.8, 0.4, 0.3, 0.5, 0.7, 0.5, 0.9, 0.3, 0.4,
        0.8, 0.8, 0.2, 0.6, 0.5, 0.4, 0.5, 0.9, 0.5, 0.3,
        0.6, 0.7, 0.6, 0.4, 0.5, 0.7, 0.8, 0.7, 0.9, 0.9,
    ],
    "Phase Transitions": [
        0.5, 0.3, 0.5, 0.7, 0.4, 0.2, 0.4, 0.8, 0.7, 0.2,
        0.7, 0.6, 0.3, 0.9, 0.4, 0.4, 0.5, 0.6, 0.3, 0.5,
        0.7, 0.5, 0.5, 0.5, 0.5, 0.8, 0.7, 0.8, 0.8, 0.8,
    ],
    "Renormalization": [
        0.7, 0.4, 0.7, 0.95, 0.6, 0.4, 0.6, 0.7, 0.4, 0.5,
        0.5, 0.6, 0.3, 0.7, 0.6, 0.8, 0.4, 0.7, 0.3, 0.3,
        0.7, 0.5, 0.9, 0.5, 0.6, 0.7, 0.8, 0.8, 0.9, 0.7,
    ],
    "Statistical Mechanics": [
        0.6, 0.5, 0.5, 0.6, 0.6, 0.3, 0.7, 0.9, 0.3, 0.2,
        0.6, 0.8, 0.2, 0.8, 0.7, 0.4, 0.4, 0.5, 0.4, 0.4,
        0.8, 0.7, 0.7, 0.4, 0.7, 0.8, 0.7, 0.8, 0.8, 0.5,
    ],
    "Gauge Theory": [
        0.9, 0.5, 1.0, 0.6, 0.6, 0.5, 0.8, 0.7, 0.4, 0.4,
        0.3, 0.9, 0.1, 0.4, 0.8, 0.6, 0.5, 0.95, 0.3, 0.2,
        0.5, 0.5, 0.6, 0.4, 0.5, 0.6, 0.9, 0.6, 0.9, 0.6,
    ],
    "Holography Principle": [
        0.8, 0.4, 0.8, 0.7, 0.4, 0.3, 0.6, 0.9, 0.8, 0.3,
        0.3, 0.7, 0.1, 0.6, 0.6, 0.5, 0.3, 0.6, 0.3, 0.2,
        0.4, 0.4, 0.9, 0.3, 0.4, 0.6, 0.8, 0.7, 0.9, 0.8,
    ],

    # === Computer Science (12) ===
    "Reservoir Computing": [
        0.6, 0.3, 0.4, 0.3, 0.5, 0.2, 0.5, 0.6, 0.2, 0.4,
        0.9, 0.3, 0.7, 0.5, 0.5, 0.3, 0.5, 0.2, 0.3, 0.3,
        0.8, 0.6, 0.5, 0.4, 0.5, 0.7, 0.5, 0.5, 0.5, 0.6,
    ],
    "Genetic Algorithms": [
        0.5, 0.2, 0.3, 0.3, 0.5, 0.2, 0.4, 0.5, 0.3, 0.3,
        0.8, 0.3, 0.9, 0.6, 0.6, 0.3, 0.4, 0.2, 0.5, 0.3,
        0.9, 0.8, 0.4, 0.8, 0.9, 0.7, 0.4, 0.8, 0.5, 0.7,
    ],
    "Neural Architecture Search": [
        0.7, 0.3, 0.4, 0.3, 0.5, 0.2, 0.4, 0.6, 0.3, 0.4,
        0.7, 0.2, 0.8, 0.5, 0.4, 0.6, 0.4, 0.2, 0.5, 0.3,
        0.9, 0.7, 0.5, 0.8, 0.9, 0.7, 0.5, 0.6, 0.5, 0.7,
    ],
    "Attention Mechanisms": [
        0.7, 0.5, 0.8, 0.3, 0.7, 0.3, 0.5, 0.7, 0.4, 0.4,
        0.5, 0.3, 0.6, 0.5, 0.5, 0.5, 0.5, 0.3, 0.3, 0.3,
        0.9, 0.8, 0.6, 0.5, 0.6, 0.7, 0.5, 0.7, 0.5, 0.5,
    ],
    "Sparse Autoencoders": [
        0.7, 0.4, 0.7, 0.3, 0.5, 0.4, 0.5, 0.8, 0.3, 0.3,
        0.3, 0.4, 0.7, 0.5, 0.5, 0.5, 0.4, 0.3, 0.3, 0.2,
        0.9, 0.7, 0.9, 0.5, 0.8, 0.7, 0.5, 0.6, 0.6, 0.5,
    ],
    "Reinforcement Learning": [
        0.6, 0.3, 0.3, 0.3, 0.6, 0.2, 0.4, 0.6, 0.3, 0.4,
        0.9, 0.3, 0.95, 0.5, 0.5, 0.5, 0.5, 0.2, 0.4, 0.7,
        0.8, 0.6, 0.4, 0.6, 0.9, 0.7, 0.5, 0.8, 0.6, 0.6,
    ],
    "Monte Carlo Tree Search": [
        0.5, 0.2, 0.3, 0.2, 0.5, 0.2, 0.4, 0.6, 0.3, 0.4,
        0.6, 0.3, 0.6, 0.4, 0.5, 0.7, 0.4, 0.2, 0.6, 0.4,
        0.9, 0.6, 0.4, 0.5, 0.7, 0.7, 0.5, 0.6, 0.5, 0.5,
    ],
    "Compressed Sensing": [
        0.7, 0.7, 0.8, 0.3, 0.6, 0.5, 0.6, 0.9, 0.3, 0.2,
        0.2, 0.5, 0.2, 0.3, 0.7, 0.3, 0.4, 0.4, 0.4, 0.2,
        0.9, 0.7, 0.95, 0.4, 0.8, 0.9, 0.6, 0.7, 0.7, 0.5,
    ],
    "Program Synthesis": [
        0.6, 0.3, 0.7, 0.3, 0.8, 0.3, 0.4, 0.7, 0.3, 0.7,
        0.3, 0.3, 0.6, 0.5, 0.4, 0.6, 0.4, 0.3, 0.7, 0.3,
        0.8, 0.5, 0.6, 0.9, 0.7, 0.7, 0.7, 0.6, 0.6, 0.7,
    ],
    "Cellular Automata": [
        0.5, 0.2, 0.9, 0.5, 0.4, 0.3, 0.5, 0.7, 0.5, 0.4,
        0.8, 0.4, 0.3, 0.9, 0.5, 0.3, 0.9, 0.3, 0.9, 0.3,
        0.9, 0.9, 0.4, 0.7, 0.3, 0.8, 0.5, 0.6, 0.6, 0.7,
    ],
    "Constraint Satisfaction": [
        0.5, 0.3, 0.9, 0.2, 0.6, 0.3, 0.5, 0.6, 0.4, 0.3,
        0.1, 0.4, 0.2, 0.3, 0.5, 0.4, 0.5, 0.3, 0.7, 0.3,
        0.9, 0.5, 0.5, 0.4, 0.8, 0.8, 0.4, 0.6, 0.5, 0.4,
    ],
    "Differentiable Programming": [
        0.7, 0.6, 0.8, 0.3, 0.8, 0.5, 0.5, 0.6, 0.2, 0.3,
        0.5, 0.4, 0.7, 0.4, 0.5, 0.4, 0.4, 0.3, 0.3, 0.4,
        0.9, 0.7, 0.6, 0.6, 0.9, 0.7, 0.5, 0.7, 0.5, 0.5,
    ],

    # === Biology (10) ===
    "Evolution": [
        0.5, 0.1, 0.2, 0.5, 0.5, 0.1, 0.4, 0.7, 0.5, 0.3,
        0.9, 0.3, 0.95, 0.8, 0.6, 0.5, 0.5, 0.2, 0.4, 0.5,
        0.7, 0.6, 0.4, 0.8, 0.8, 0.7, 0.5, 0.9, 0.7, 0.7,
    ],
    "Immune Systems": [
        0.7, 0.2, 0.3, 0.5, 0.6, 0.2, 0.4, 0.8, 0.95, 0.7,
        0.9, 0.3, 0.95, 0.9, 0.7, 0.8, 0.7, 0.2, 0.6, 0.8,
        0.7, 0.6, 0.4, 0.6, 0.5, 0.7, 0.5, 0.7, 0.7, 0.8,
    ],
    "Neural Plasticity": [
        0.6, 0.3, 0.4, 0.4, 0.5, 0.3, 0.4, 0.6, 0.4, 0.4,
        0.9, 0.3, 0.9, 0.6, 0.5, 0.5, 0.6, 0.2, 0.4, 0.5,
        0.6, 0.5, 0.4, 0.5, 0.5, 0.6, 0.5, 0.6, 0.6, 0.5,
    ],
    "Gene Regulatory Networks": [
        0.6, 0.3, 0.5, 0.4, 0.6, 0.3, 0.5, 0.7, 0.4, 0.5,
        0.8, 0.4, 0.6, 0.7, 0.5, 0.7, 0.6, 0.3, 0.5, 0.7,
        0.7, 0.5, 0.5, 0.5, 0.5, 0.7, 0.5, 0.6, 0.7, 0.6,
    ],
    "Symbiosis": [
        0.3, 0.1, 0.3, 0.3, 0.7, 0.3, 0.5, 0.5, 0.6, 0.3,
        0.8, 0.3, 0.7, 0.7, 0.6, 0.4, 0.5, 0.2, 0.3, 0.5,
        0.5, 0.4, 0.3, 0.5, 0.4, 0.5, 0.4, 0.7, 0.5, 0.6,
    ],
    "Ecosystem Dynamics": [
        0.5, 0.2, 0.3, 0.5, 0.5, 0.2, 0.4, 0.6, 0.5, 0.3,
        0.9, 0.4, 0.6, 0.8, 0.5, 0.6, 0.5, 0.2, 0.3, 0.6,
        0.6, 0.5, 0.4, 0.5, 0.4, 0.6, 0.5, 0.7, 0.6, 0.6,
    ],
    "Morphogenesis": [
        0.6, 0.2, 0.5, 0.6, 0.5, 0.2, 0.4, 0.6, 0.6, 0.4,
        0.8, 0.4, 0.5, 0.9, 0.5, 0.5, 0.7, 0.4, 0.3, 0.5,
        0.7, 0.6, 0.4, 0.7, 0.4, 0.7, 0.5, 0.7, 0.7, 0.7,
    ],
    "Epigenetics": [
        0.5, 0.2, 0.5, 0.4, 0.5, 0.3, 0.5, 0.7, 0.4, 0.4,
        0.8, 0.4, 0.6, 0.6, 0.5, 0.6, 0.5, 0.2, 0.5, 0.5,
        0.6, 0.4, 0.5, 0.4, 0.3, 0.6, 0.5, 0.6, 0.6, 0.6,
    ],
    "Swarm Intelligence": [
        0.4, 0.1, 0.3, 0.4, 0.5, 0.2, 0.4, 0.5, 0.4, 0.3,
        0.8, 0.3, 0.7, 0.9, 0.6, 0.3, 0.8, 0.2, 0.5, 0.4,
        0.8, 0.9, 0.4, 0.6, 0.7, 0.7, 0.4, 0.7, 0.5, 0.6,
    ],
    "Apoptosis": [
        0.3, 0.2, 0.6, 0.3, 0.4, 0.1, 0.5, 0.5, 0.5, 0.3,
        0.7, 0.4, 0.3, 0.5, 0.5, 0.5, 0.6, 0.2, 0.5, 0.6,
        0.6, 0.4, 0.3, 0.3, 0.4, 0.6, 0.4, 0.5, 0.5, 0.5,
    ],

    # === Cognitive Science (9) ===
    "Dual Process Theory": [
        0.4, 0.3, 0.4, 0.3, 0.5, 0.2, 0.5, 0.7, 0.3, 0.5,
        0.6, 0.3, 0.5, 0.5, 0.5, 0.6, 0.4, 0.3, 0.5, 0.4,
        0.5, 0.4, 0.4, 0.4, 0.4, 0.6, 0.6, 0.7, 0.6, 0.5,
    ],
    "Metacognition": [
        0.3, 0.2, 0.4, 0.3, 0.5, 0.3, 0.5, 0.7, 0.3, 0.9,
        0.5, 0.3, 0.7, 0.5, 0.5, 0.6, 0.4, 0.2, 0.4, 0.4,
        0.5, 0.3, 0.4, 0.4, 0.5, 0.7, 0.7, 0.7, 0.7, 0.6,
    ],
    "Embodied Cognition": [
        0.5, 0.2, 0.4, 0.4, 0.5, 0.2, 0.4, 0.6, 0.5, 0.4,
        0.7, 0.3, 0.6, 0.6, 0.5, 0.4, 0.7, 0.2, 0.3, 0.5,
        0.5, 0.4, 0.3, 0.4, 0.3, 0.5, 0.5, 0.6, 0.5, 0.5,
    ],
    "Predictive Coding": [
        0.6, 0.4, 0.5, 0.4, 0.6, 0.3, 0.5, 0.8, 0.4, 0.5,
        0.7, 0.4, 0.7, 0.5, 0.6, 0.7, 0.5, 0.3, 0.3, 0.5,
        0.7, 0.5, 0.7, 0.5, 0.6, 0.7, 0.6, 0.7, 0.7, 0.6,
    ],
    "Active Inference": [
        0.6, 0.3, 0.5, 0.4, 0.6, 0.3, 0.5, 0.8, 0.4, 0.5,
        0.8, 0.4, 0.8, 0.6, 0.6, 0.5, 0.5, 0.3, 0.3, 0.6,
        0.7, 0.5, 0.6, 0.6, 0.7, 0.7, 0.6, 0.8, 0.7, 0.7,
    ],
    "Global Workspace Theory": [
        0.4, 0.3, 0.5, 0.3, 0.5, 0.2, 0.5, 0.7, 0.4, 0.4,
        0.5, 0.3, 0.5, 0.6, 0.5, 0.5, 0.3, 0.3, 0.4, 0.3,
        0.5, 0.5, 0.5, 0.4, 0.4, 0.5, 0.6, 0.6, 0.6, 0.5,
    ],
    "Analogical Reasoning": [
        0.5, 0.3, 0.5, 0.5, 0.7, 0.3, 0.4, 0.7, 0.4, 0.5,
        0.3, 0.3, 0.6, 0.5, 0.4, 0.5, 0.3, 0.4, 0.4, 0.3,
        0.6, 0.4, 0.5, 0.6, 0.4, 0.5, 0.7, 0.9, 0.6, 0.7,
    ],
    "Cognitive Load Theory": [
        0.3, 0.3, 0.5, 0.2, 0.4, 0.2, 0.4, 0.6, 0.3, 0.3,
        0.4, 0.4, 0.4, 0.3, 0.5, 0.5, 0.4, 0.2, 0.4, 0.3,
        0.6, 0.3, 0.5, 0.3, 0.5, 0.6, 0.4, 0.6, 0.4, 0.3,
    ],
    "Theory of Mind": [
        0.4, 0.2, 0.4, 0.3, 0.5, 0.2, 0.4, 0.7, 0.4, 0.8,
        0.5, 0.3, 0.6, 0.5, 0.4, 0.6, 0.4, 0.2, 0.4, 0.5,
        0.4, 0.3, 0.4, 0.4, 0.3, 0.5, 0.6, 0.7, 0.6, 0.6,
    ],

    # === Signal Processing (4) ===
    "Wavelet Transforms": [
        0.5, 0.7, 1.0, 0.8, 0.7, 0.8, 0.7, 0.8, 0.4, 0.2,
        0.7, 0.7, 0.1, 0.2, 0.8, 0.7, 0.6, 0.7, 0.4, 0.1,
        0.9, 0.7, 0.9, 0.3, 0.5, 0.8, 0.5, 0.7, 0.6, 0.3,
    ],
    "Spectral Analysis": [
        0.5, 0.8, 0.9, 0.5, 0.6, 0.6, 0.7, 0.8, 0.3, 0.2,
        0.6, 0.6, 0.1, 0.2, 0.7, 0.3, 0.4, 0.7, 0.4, 0.1,
        0.9, 0.7, 0.7, 0.3, 0.5, 0.9, 0.5, 0.7, 0.6, 0.3,
    ],
    "Kalman Filtering": [
        0.5, 0.7, 0.6, 0.3, 0.6, 0.5, 0.6, 0.7, 0.2, 0.2,
        0.9, 0.5, 0.6, 0.3, 0.7, 0.3, 0.5, 0.4, 0.3, 0.4,
        0.9, 0.5, 0.6, 0.4, 0.8, 0.9, 0.5, 0.7, 0.6, 0.4,
    ],
    "Matched Filtering": [
        0.4, 0.8, 0.8, 0.2, 0.5, 0.4, 0.7, 0.7, 0.3, 0.1,
        0.5, 0.5, 0.1, 0.2, 0.7, 0.2, 0.4, 0.5, 0.3, 0.2,
        0.9, 0.6, 0.6, 0.3, 0.7, 0.9, 0.4, 0.5, 0.5, 0.3,
    ],

    # === Philosophy (6) ===
    "Epistemology": [
        0.3, 0.2, 0.5, 0.4, 0.5, 0.3, 0.5, 0.7, 0.4, 0.6,
        0.2, 0.4, 0.4, 0.4, 0.5, 0.6, 0.3, 0.3, 0.3, 0.4,
        0.4, 0.3, 0.4, 0.4, 0.3, 0.7, 0.8, 0.8, 0.8, 0.5,
    ],
    "Falsificationism": [
        0.2, 0.2, 0.6, 0.3, 0.4, 0.3, 0.5, 0.6, 0.5, 0.3,
        0.2, 0.4, 0.3, 0.3, 0.6, 0.4, 0.3, 0.2, 0.4, 0.5,
        0.5, 0.3, 0.3, 0.4, 0.3, 0.95, 0.7, 0.8, 0.7, 0.5,
    ],
    "Pragmatism": [
        0.3, 0.2, 0.4, 0.3, 0.5, 0.2, 0.4, 0.5, 0.3, 0.3,
        0.5, 0.3, 0.6, 0.4, 0.5, 0.3, 0.4, 0.2, 0.3, 0.4,
        0.5, 0.3, 0.3, 0.3, 0.4, 0.6, 0.5, 0.7, 0.5, 0.4,
    ],
    "Phenomenology": [
        0.3, 0.2, 0.4, 0.3, 0.4, 0.2, 0.4, 0.6, 0.4, 0.6,
        0.4, 0.3, 0.3, 0.4, 0.4, 0.4, 0.4, 0.2, 0.3, 0.3,
        0.3, 0.2, 0.3, 0.3, 0.2, 0.4, 0.7, 0.6, 0.7, 0.5,
    ],
    "Dialectics": [
        0.3, 0.2, 0.4, 0.3, 0.5, 0.3, 0.4, 0.6, 0.4, 0.5,
        0.6, 0.3, 0.5, 0.5, 0.4, 0.5, 0.3, 0.3, 0.4, 0.4,
        0.4, 0.3, 0.3, 0.5, 0.3, 0.5, 0.6, 0.7, 0.6, 0.5,
    ],
    "Abductive Reasoning": [
        0.3, 0.2, 0.4, 0.3, 0.5, 0.2, 0.3, 0.7, 0.3, 0.4,
        0.3, 0.3, 0.5, 0.4, 0.4, 0.4, 0.3, 0.2, 0.4, 0.5,
        0.5, 0.3, 0.4, 0.6, 0.4, 0.6, 0.6, 0.8, 0.6, 0.7,
    ],

    # === Complex Systems (5) ===
    "Self-Organized Criticality": [
        0.5, 0.2, 0.5, 0.8, 0.4, 0.2, 0.4, 0.7, 0.5, 0.4,
        0.7, 0.4, 0.5, 0.9, 0.5, 0.4, 0.6, 0.3, 0.4, 0.4,
        0.7, 0.6, 0.5, 0.6, 0.4, 0.7, 0.7, 0.8, 0.7, 0.8,
    ],
    "Emergence": [
        0.5, 0.2, 0.4, 0.5, 0.5, 0.2, 0.4, 0.7, 0.4, 0.4,
        0.5, 0.3, 0.4, 0.95, 0.5, 0.6, 0.5, 0.3, 0.3, 0.4,
        0.5, 0.5, 0.4, 0.6, 0.3, 0.5, 0.7, 0.8, 0.7, 0.8,
    ],
    "Network Science": [
        0.6, 0.3, 0.7, 0.5, 0.6, 0.3, 0.5, 0.7, 0.4, 0.3,
        0.5, 0.4, 0.4, 0.7, 0.6, 0.6, 0.5, 0.3, 0.5, 0.4,
        0.8, 0.7, 0.6, 0.5, 0.5, 0.7, 0.5, 0.8, 0.6, 0.5,
    ],
    "Autopoiesis": [
        0.4, 0.2, 0.5, 0.4, 0.5, 0.2, 0.5, 0.6, 0.6, 0.7,
        0.7, 0.4, 0.5, 0.7, 0.6, 0.4, 0.5, 0.2, 0.3, 0.4,
        0.5, 0.4, 0.4, 0.5, 0.3, 0.5, 0.6, 0.6, 0.6, 0.6,
    ],
    "Criticality": [
        0.5, 0.2, 0.5, 0.8, 0.4, 0.2, 0.4, 0.8, 0.6, 0.3,
        0.6, 0.5, 0.3, 0.8, 0.4, 0.4, 0.5, 0.4, 0.3, 0.4,
        0.7, 0.5, 0.5, 0.5, 0.5, 0.8, 0.7, 0.8, 0.8, 0.8,
    ],

    # === Information Science (3) ===
    "Kolmogorov Complexity": [
        0.4, 0.3, 1.0, 0.4, 0.4, 0.3, 0.8, 0.95, 0.3, 0.5,
        0.1, 0.6, 0.1, 0.4, 0.8, 0.4, 0.3, 0.4, 0.5, 0.2,
        0.5, 0.3, 0.9, 0.3, 0.4, 0.6, 0.8, 0.7, 0.9, 0.6,
    ],
    "Error Correcting Codes": [
        0.5, 0.6, 0.9, 0.3, 0.6, 0.5, 0.7, 0.8, 0.4, 0.2,
        0.1, 0.6, 0.2, 0.3, 0.8, 0.4, 0.4, 0.5, 0.7, 0.2,
        0.9, 0.6, 0.8, 0.4, 0.6, 0.8, 0.5, 0.6, 0.6, 0.4,
    ],
    "Causal Inference": [
        0.5, 0.4, 0.6, 0.3, 0.6, 0.3, 0.5, 0.8, 0.3, 0.3,
        0.5, 0.4, 0.5, 0.4, 0.5, 0.5, 0.4, 0.3, 0.4, 0.9,
        0.7, 0.5, 0.5, 0.5, 0.5, 0.8, 0.6, 0.8, 0.8, 0.6,
    ],

    # === Neuroscience (4) ===
    "Hebbian Learning": [
        0.5, 0.3, 0.5, 0.3, 0.5, 0.3, 0.4, 0.5, 0.3, 0.4,
        0.7, 0.3, 0.8, 0.5, 0.5, 0.3, 0.7, 0.3, 0.4, 0.4,
        0.7, 0.6, 0.4, 0.4, 0.5, 0.6, 0.4, 0.6, 0.5, 0.5,
    ],
    "Neural Oscillations": [
        0.5, 0.4, 0.5, 0.4, 0.5, 0.3, 0.5, 0.6, 0.3, 0.3,
        0.9, 0.4, 0.4, 0.5, 0.5, 0.4, 0.5, 0.5, 0.3, 0.3,
        0.7, 0.5, 0.5, 0.4, 0.4, 0.6, 0.5, 0.5, 0.5, 0.5,
    ],
    "Neuromodulation": [
        0.4, 0.2, 0.4, 0.3, 0.4, 0.2, 0.4, 0.6, 0.3, 0.3,
        0.8, 0.3, 0.7, 0.5, 0.5, 0.5, 0.5, 0.2, 0.4, 0.4,
        0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.5,
    ],
    "Sparse Coding": [
        0.6, 0.5, 0.7, 0.3, 0.5, 0.4, 0.5, 0.8, 0.3, 0.2,
        0.3, 0.4, 0.5, 0.4, 0.6, 0.4, 0.5, 0.3, 0.4, 0.2,
        0.8, 0.6, 0.9, 0.4, 0.7, 0.7, 0.5, 0.6, 0.6, 0.4,
    ],

    # === Control Theory (3) ===
    "Feedback Control": [
        0.5, 0.6, 0.7, 0.3, 0.7, 0.5, 0.7, 0.6, 0.3, 0.5,
        0.8, 0.5, 0.6, 0.4, 0.7, 0.4, 0.4, 0.3, 0.3, 0.6,
        0.9, 0.5, 0.5, 0.4, 0.7, 0.8, 0.5, 0.7, 0.6, 0.4,
    ],
    "Optimal Control": [
        0.6, 0.5, 0.7, 0.3, 0.6, 0.4, 0.6, 0.7, 0.3, 0.3,
        0.7, 0.5, 0.5, 0.3, 0.6, 0.4, 0.4, 0.4, 0.3, 0.5,
        0.8, 0.5, 0.5, 0.4, 0.9, 0.8, 0.6, 0.7, 0.7, 0.4,
    ],
    "Adaptive Control": [
        0.5, 0.4, 0.5, 0.3, 0.6, 0.4, 0.5, 0.6, 0.3, 0.4,
        0.8, 0.4, 0.8, 0.4, 0.6, 0.4, 0.4, 0.3, 0.3, 0.5,
        0.8, 0.5, 0.5, 0.5, 0.7, 0.7, 0.5, 0.7, 0.6, 0.5,
    ],

    # === Linguistics (2) ===
    "Compositionality": [
        0.5, 0.4, 0.7, 0.4, 0.95, 0.4, 0.6, 0.7, 0.3, 0.5,
        0.2, 0.5, 0.3, 0.5, 0.6, 0.6, 0.3, 0.4, 0.4, 0.3,
        0.7, 0.5, 0.6, 0.6, 0.4, 0.6, 0.7, 0.8, 0.7, 0.5,
    ],
    "Pragmatics": [
        0.3, 0.2, 0.4, 0.3, 0.5, 0.2, 0.4, 0.6, 0.4, 0.4,
        0.4, 0.3, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2, 0.3, 0.4,
        0.4, 0.3, 0.3, 0.3, 0.3, 0.5, 0.5, 0.6, 0.5, 0.4,
    ],

    # === Economics/Game Theory (3) ===
    "Mechanism Design": [
        0.5, 0.4, 0.7, 0.3, 0.6, 0.4, 0.5, 0.7, 0.4, 0.4,
        0.4, 0.5, 0.4, 0.4, 0.5, 0.5, 0.4, 0.3, 0.5, 0.5,
        0.7, 0.5, 0.5, 0.5, 0.7, 0.7, 0.6, 0.7, 0.7, 0.5,
    ],
    "Nash Equilibrium": [
        0.4, 0.3, 0.6, 0.3, 0.4, 0.3, 0.7, 0.7, 0.3, 0.4,
        0.3, 0.5, 0.3, 0.4, 0.6, 0.4, 0.3, 0.4, 0.4, 0.4,
        0.7, 0.4, 0.4, 0.3, 0.7, 0.7, 0.6, 0.7, 0.7, 0.5,
    ],
    "Multi-Armed Bandits": [
        0.4, 0.3, 0.3, 0.2, 0.4, 0.2, 0.4, 0.7, 0.2, 0.3,
        0.6, 0.3, 0.8, 0.3, 0.5, 0.3, 0.4, 0.2, 0.4, 0.4,
        0.8, 0.5, 0.4, 0.4, 0.8, 0.7, 0.5, 0.7, 0.5, 0.5,
    ],

    # === Theoretical Neuroscience (2) ===
    "Free Energy Principle": [
        0.6, 0.4, 0.6, 0.4, 0.6, 0.3, 0.5, 0.8, 0.4, 0.5,
        0.7, 0.5, 0.7, 0.6, 0.6, 0.5, 0.4, 0.3, 0.3, 0.5,
        0.7, 0.5, 0.6, 0.5, 0.7, 0.7, 0.7, 0.9, 0.8, 0.7,
    ],
    "Maximum Entropy": [
        0.5, 0.5, 0.7, 0.4, 0.5, 0.4, 0.7, 0.9, 0.3, 0.2,
        0.3, 0.7, 0.2, 0.3, 0.7, 0.3, 0.3, 0.5, 0.3, 0.2,
        0.8, 0.5, 0.7, 0.3, 0.8, 0.8, 0.6, 0.8, 0.7, 0.4,
    ],

    # === Logic/Formal Methods (7) ===
    "Type Theory": [
        0.7, 0.5, 1.0, 0.4, 0.9, 0.5, 0.9, 0.7, 0.4, 0.7,
        0.1, 0.7, 0.1, 0.4, 0.9, 0.8, 0.3, 0.5, 0.6, 0.3,
        0.7, 0.4, 0.6, 0.6, 0.4, 0.8, 0.9, 0.7, 0.8, 0.5,
    ],
    "Model Checking": [
        0.5, 0.4, 1.0, 0.2, 0.6, 0.3, 0.7, 0.6, 0.4, 0.3,
        0.3, 0.5, 0.1, 0.3, 0.7, 0.4, 0.4, 0.3, 0.7, 0.3,
        0.9, 0.6, 0.5, 0.4, 0.5, 0.9, 0.6, 0.6, 0.6, 0.3,
    ],
    "Proof Theory": [
        0.5, 0.4, 1.0, 0.3, 0.7, 0.5, 0.8, 0.7, 0.3, 0.6,
        0.1, 0.7, 0.1, 0.3, 0.8, 0.7, 0.3, 0.5, 0.6, 0.4,
        0.6, 0.4, 0.5, 0.5, 0.3, 0.8, 0.9, 0.6, 0.8, 0.4,
    ],
    "Compositional Semantics": [
        0.5, 0.4, 0.8, 0.3, 0.9, 0.4, 0.6, 0.7, 0.3, 0.5,
        0.2, 0.5, 0.2, 0.4, 0.6, 0.6, 0.3, 0.4, 0.5, 0.3,
        0.6, 0.4, 0.5, 0.5, 0.4, 0.6, 0.7, 0.6, 0.7, 0.4,
    ],
    "Counterfactual Reasoning": [
        0.4, 0.3, 0.5, 0.3, 0.5, 0.3, 0.4, 0.7, 0.3, 0.5,
        0.4, 0.3, 0.4, 0.4, 0.4, 0.5, 0.3, 0.3, 0.4, 0.7,
        0.5, 0.3, 0.4, 0.5, 0.4, 0.7, 0.6, 0.7, 0.7, 0.6,
    ],
    "Normalized Compression Distance": [
        0.3, 0.5, 0.9, 0.3, 0.4, 0.4, 0.7, 0.9, 0.2, 0.2,
        0.1, 0.5, 0.1, 0.2, 0.7, 0.2, 0.3, 0.4, 0.4, 0.2,
        0.9, 0.4, 0.9, 0.2, 0.5, 0.8, 0.5, 0.6, 0.6, 0.3,
    ],
    "Hoare Logic": [
        0.4, 0.4, 1.0, 0.2, 0.6, 0.3, 0.8, 0.6, 0.3, 0.3,
        0.2, 0.6, 0.1, 0.2, 0.8, 0.4, 0.4, 0.3, 0.7, 0.3,
        0.8, 0.4, 0.4, 0.3, 0.4, 0.9, 0.7, 0.5, 0.7, 0.3,
    ],

    # === Software Engineering/Verification (5) ===
    "Metamorphic Testing": [
        0.4, 0.3, 0.7, 0.3, 0.6, 0.3, 0.5, 0.6, 0.3, 0.4,
        0.2, 0.4, 0.3, 0.3, 0.6, 0.3, 0.4, 0.4, 0.5, 0.3,
        0.8, 0.5, 0.4, 0.5, 0.4, 0.9, 0.5, 0.6, 0.5, 0.5,
    ],
    "Property-Based Testing": [
        0.4, 0.3, 0.6, 0.3, 0.6, 0.3, 0.5, 0.6, 0.3, 0.3,
        0.2, 0.4, 0.3, 0.3, 0.6, 0.3, 0.4, 0.3, 0.5, 0.3,
        0.8, 0.5, 0.4, 0.6, 0.4, 0.9, 0.5, 0.6, 0.5, 0.5,
    ],
    "Abstract Interpretation": [
        0.6, 0.5, 0.8, 0.3, 0.6, 0.3, 0.7, 0.6, 0.3, 0.4,
        0.1, 0.5, 0.2, 0.3, 0.7, 0.6, 0.3, 0.4, 0.5, 0.3,
        0.7, 0.4, 0.6, 0.4, 0.5, 0.7, 0.7, 0.5, 0.7, 0.4,
    ],
    "Satisfiability": [
        0.5, 0.3, 1.0, 0.2, 0.5, 0.3, 0.6, 0.6, 0.3, 0.3,
        0.1, 0.4, 0.1, 0.3, 0.6, 0.4, 0.4, 0.3, 0.8, 0.3,
        0.9, 0.5, 0.4, 0.4, 0.6, 0.8, 0.5, 0.6, 0.5, 0.4,
    ],
    "Sensitivity Analysis": [
        0.5, 0.5, 0.7, 0.3, 0.5, 0.4, 0.5, 0.7, 0.4, 0.2,
        0.3, 0.4, 0.2, 0.3, 0.6, 0.3, 0.5, 0.3, 0.4, 0.4,
        0.8, 0.5, 0.5, 0.3, 0.5, 0.8, 0.5, 0.7, 0.6, 0.4,
    ],
}


# ============================================================
# Public API
# ============================================================

def get_concept_names() -> List[str]:
    """Return all 95 concept names in canonical order."""
    return list(CONCEPT_FEATURES.keys())


def get_feature_matrix() -> Tuple[np.ndarray, List[str]]:
    """
    Return (feature_matrix, concept_names).
    feature_matrix is shape (N_concepts, N_features) = (95, 30).
    """
    names = get_concept_names()
    matrix = np.array([CONCEPT_FEATURES[n] for n in names], dtype=np.float32)
    return matrix, names


def get_feature_vector(concept_name: str) -> np.ndarray:
    """Return the 30-dim feature vector for a single concept."""
    return np.array(CONCEPT_FEATURES[concept_name], dtype=np.float32)


def concept_distance(a: str, b: str) -> float:
    """Euclidean distance between two concepts in feature space."""
    va = get_feature_vector(a)
    vb = get_feature_vector(b)
    return float(np.linalg.norm(va - vb))


def concept_cosine_similarity(a: str, b: str) -> float:
    """Cosine similarity between two concepts."""
    va = get_feature_vector(a)
    vb = get_feature_vector(b)
    dot = np.dot(va, vb)
    norm = np.linalg.norm(va) * np.linalg.norm(vb)
    return float(dot / norm) if norm > 0 else 0.0


def enrich_with_coeus(concept_scores_path: Optional[str] = None) -> np.ndarray:
    """
    Load Coeus forge_effect scores and blend them into the feature matrix
    as an additional signal on the 'surprise_potential' dimension.

    Returns the enriched feature matrix.
    """
    if concept_scores_path is None:
        concept_scores_path = str(ROOT / "agents" / "coeus" / "graphs" / "concept_scores.json")

    matrix, names = get_feature_matrix()

    try:
        with open(concept_scores_path) as f:
            coeus = json.load(f)
        influence = coeus.get("concept_influence", {})

        for i, name in enumerate(names):
            if name in influence:
                forge_effect = influence[name].get("forge_effect", 0.0)
                # Blend forge_effect into surprise_potential (dim 29)
                # Positive forge_effect = concept produces successful tools = higher surprise
                matrix[i, 29] = np.clip(matrix[i, 29] + forge_effect * 0.3, 0.0, 1.0)
    except (FileNotFoundError, json.JSONDecodeError):
        pass  # Gracefully degrade without Coeus data

    return matrix


# ============================================================
# Interaction Computation
# ============================================================

def compute_pairwise_interactions(matrix: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Compute all pairwise interaction scores from the feature matrix.

    Returns dict with:
      - novelty: (N, N) off-diagonal energy ratio
      - complementarity: (N, N) mean absolute feature difference
      - resonance: (N, N) element-wise product (shared high features)
      - combined: (N, N) weighted sum
    """
    N = matrix.shape[0]

    novelty = np.zeros((N, N), dtype=np.float32)
    complementarity = np.zeros((N, N), dtype=np.float32)
    resonance = np.zeros((N, N), dtype=np.float32)

    for i in range(N):
        for j in range(i + 1, N):
            interface = np.outer(matrix[i], matrix[j])
            diag_e = np.sum(np.diag(interface) ** 2)
            total_e = np.sum(interface ** 2)
            nov = 1.0 - diag_e / total_e if total_e > 0 else 0.0

            comp = float(np.mean(np.abs(matrix[i] - matrix[j])))
            res = float(np.mean(matrix[i] * matrix[j]))

            novelty[i, j] = novelty[j, i] = nov
            complementarity[i, j] = complementarity[j, i] = comp
            resonance[i, j] = resonance[j, i] = res

    # Combined score: novelty is most important, then complementarity, then resonance
    combined = 0.4 * novelty + 0.35 * complementarity + 0.25 * resonance

    return {
        "novelty": novelty,
        "complementarity": complementarity,
        "resonance": resonance,
        "combined": combined,
    }


def compute_triple_tensor(matrix: np.ndarray) -> np.ndarray:
    """
    Compute the full triple interaction tensor.
    Shape: (N, N, N) where entry [i, j, k] = interaction score for triple (i, j, k).

    Score = novelty + complementarity + resonance of the three-way combination.
    Uses vectorized computation where possible.
    """
    N = matrix.shape[0]
    tensor = np.zeros((N, N, N), dtype=np.float32)

    # Precompute pairwise distances for complementarity
    # Broadcasting: (N, 1, D) - (1, N, D) -> (N, N, D)
    diffs = matrix[:, None, :] - matrix[None, :, :]
    pair_comp = np.mean(np.abs(diffs), axis=2)  # (N, N)

    # Pairwise resonance
    pair_res = np.einsum('id,jd->ij', matrix, matrix) / N_FEATURES  # (N, N)

    for i in range(N):
        for j in range(i + 1, N):
            for k in range(j + 1, N):
                # Three-way complementarity: average of pairwise complementarities
                comp = (pair_comp[i, j] + pair_comp[i, k] + pair_comp[j, k]) / 3.0

                # Three-way resonance: minimum pairwise resonance (bottleneck)
                res = min(pair_res[i, j], pair_res[i, k], pair_res[j, k])

                # Novelty: how much the triple differs from any pair
                # = variance of pairwise complementarities (diverse triple = high)
                comps = [pair_comp[i, j], pair_comp[i, k], pair_comp[j, k]]
                novelty_var = float(np.std(comps))
                novelty_mean = float(np.mean(comps))
                nov = novelty_mean + novelty_var  # diverse + high = novel

                score = 0.4 * nov + 0.35 * comp + 0.25 * res

                # Symmetric fill
                tensor[i, j, k] = score
                tensor[i, k, j] = score
                tensor[j, i, k] = score
                tensor[j, k, i] = score
                tensor[k, i, j] = score
                tensor[k, j, i] = score

    return tensor


def compute_triple_tensor_fast(matrix: np.ndarray) -> np.ndarray:
    """
    Vectorized triple tensor computation. Much faster than the loop version.
    For 95 concepts this takes ~2-5 seconds instead of ~60 seconds.
    """
    N = matrix.shape[0]
    D = matrix.shape[1]

    # Pairwise complementarity: (N, N)
    diffs = matrix[:, None, :] - matrix[None, :, :]
    pair_comp = np.mean(np.abs(diffs), axis=2).astype(np.float32)

    # Pairwise resonance: (N, N)
    pair_res = (matrix @ matrix.T / D).astype(np.float32)

    # Triple complementarity: average of 3 pairs
    # Use broadcasting: comp[i,j,k] = (pair_comp[i,j] + pair_comp[i,k] + pair_comp[j,k]) / 3
    triple_comp = (pair_comp[:, :, None] + pair_comp[:, None, :] + pair_comp[None, :, :]) / 3.0

    # Triple resonance: min of 3 pairs
    triple_res = np.minimum(
        np.minimum(pair_res[:, :, None], pair_res[:, None, :]),
        pair_res[None, :, :]
    )

    # Triple novelty: std of pairwise complementarities + mean
    c_ij = pair_comp[:, :, None] * np.ones((1, 1, N), dtype=np.float32)
    c_ik = pair_comp[:, None, :] * np.ones((1, N, 1), dtype=np.float32)
    c_jk = pair_comp[None, :, :] * np.ones((N, 1, 1), dtype=np.float32)

    stacked = np.stack([c_ij, c_ik, c_jk], axis=0)  # (3, N, N, N)
    triple_nov = np.mean(stacked, axis=0) + np.std(stacked, axis=0)

    # Combined
    tensor = (0.4 * triple_nov + 0.35 * triple_comp + 0.25 * triple_res).astype(np.float32)

    # Zero the diagonal (same-concept triples are meaningless)
    for i in range(N):
        tensor[i, i, :] = 0
        tensor[i, :, i] = 0
        tensor[:, i, i] = 0

    return tensor


# ============================================================
# Quick CLI test
# ============================================================

if __name__ == "__main__":
    import time

    names = get_concept_names()
    print(f"Concepts: {len(names)}")
    assert len(names) == 95, f"Expected 95, got {len(names)}"

    matrix, _ = get_feature_matrix()
    print(f"Feature matrix: {matrix.shape} ({matrix.nbytes / 1024:.1f} KB)")

    # Enrich with Coeus
    enriched = enrich_with_coeus()
    print(f"Enriched matrix: {enriched.shape}")

    # Pairwise
    t0 = time.perf_counter()
    pairs = compute_pairwise_interactions(enriched)
    t1 = time.perf_counter()
    print(f"\nPairwise interactions: {t1-t0:.3f}s")

    # Top 10 pairs by combined score
    combined = pairs["combined"]
    flat = combined.flatten()
    top_idx = np.argsort(flat)[-20:][::-1]
    seen = set()
    print("\nTOP 10 CONCEPT PAIRS:")
    count = 0
    for idx in top_idx:
        i, j = divmod(idx, len(names))
        key = (min(i, j), max(i, j))
        if key in seen or i == j:
            continue
        seen.add(key)
        count += 1
        print(f"  {count:2d}. [{combined[i,j]:.4f}] {names[i]} x {names[j]}")
        if count >= 10:
            break

    # Triple tensor (fast)
    print(f"\nComputing triple tensor ({len(names)}^3 = {len(names)**3:,} entries)...")
    t0 = time.perf_counter()
    triple = compute_triple_tensor_fast(enriched)
    t1 = time.perf_counter()
    print(f"Triple tensor: {triple.shape}, {triple.nbytes / 1024 / 1024:.1f} MB, {t1-t0:.3f}s")

    # Top 10 triples
    flat = triple.flatten()
    top_idx = np.argsort(flat)[-60:][::-1]
    seen = set()
    print("\nTOP 10 CONCEPT TRIPLES:")
    count = 0
    for idx in top_idx:
        i = idx // (len(names) * len(names))
        remainder = idx % (len(names) * len(names))
        j = remainder // len(names)
        k = remainder % len(names)
        key = tuple(sorted([i, j, k]))
        if key in seen or len(set(key)) < 3:
            continue
        seen.add(key)
        count += 1
        print(f"  {count:2d}. [{triple[i,j,k]:.4f}] {names[i]} x {names[j]} x {names[k]}")
        if count >= 10:
            break

    print(f"\nTotal time: {time.perf_counter() - t0:.3f}s")
    print("Ready for tensor train compression.")
