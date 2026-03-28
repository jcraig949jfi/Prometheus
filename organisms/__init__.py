"""
Mathematical Organisms for Project Prometheus.

Each organism encapsulates a mathematical domain as executable operations
with typed inputs/outputs, enabling cross-domain chaining.
"""

from .base import MathematicalOrganism
from .information_theory import InformationTheory
from .topology import Topology
from .chaos_theory import ChaosTheory
from .bayesian_inference import BayesianInference
from .game_theory import GameTheory
from .immune_systems import ImmuneSystems
from .network_science import NetworkScience
from .signal_processing import SignalProcessing
from .statistical_mechanics import StatisticalMechanics
from .dynamical_systems import DynamicalSystems
from .prime_theory import PrimeTheory
from .algebraic_number_theory import AlgebraicNumberTheory
from .analytic_number_theory import AnalyticNumberTheory
from .geometric_number_theory import GeometricNumberTheory
from .probabilistic_number_theory import ProbabilisticNumberTheory
from .combinatorial_number_theory import CombinatorialNumberTheory
from .computational_number_theory import ComputationalNumberTheory
from .number_geometry_bridge import NumberGeometryBridge

ALL_ORGANISMS = [
    InformationTheory,
    Topology,
    ChaosTheory,
    BayesianInference,
    GameTheory,
    ImmuneSystems,
    NetworkScience,
    SignalProcessing,
    StatisticalMechanics,
    DynamicalSystems,
    PrimeTheory,
    AlgebraicNumberTheory,
    AnalyticNumberTheory,
    GeometricNumberTheory,
    ProbabilisticNumberTheory,
    CombinatorialNumberTheory,
    ComputationalNumberTheory,
    NumberGeometryBridge,
]

__all__ = [
    "MathematicalOrganism",
    "InformationTheory",
    "Topology",
    "ChaosTheory",
    "BayesianInference",
    "GameTheory",
    "ImmuneSystems",
    "NetworkScience",
    "SignalProcessing",
    "StatisticalMechanics",
    "DynamicalSystems",
    "PrimeTheory",
    "AlgebraicNumberTheory",
    "AnalyticNumberTheory",
    "GeometricNumberTheory",
    "ProbabilisticNumberTheory",
    "CombinatorialNumberTheory",
    "ComputationalNumberTheory",
    "NumberGeometryBridge",
    "ALL_ORGANISMS",
]
