"""Stage 17 TDD tests — 15 more gen families (parametrized).

Test plan per gen (5 tests):
  1. Module imports without error (class exists)
  2. Class instantiates
  3. .next() emits a TheseusRecord (within first 100 calls)
  4. Emitted record has the expected claim_kind
  5. Role classification is DISCOVERY

Compact via parametrization. Each gen described by:
  (gid, module_name, class_name, expected_claim_kind)
"""
from __future__ import annotations

import importlib
import pytest

from theseus.emit.record_schema import TheseusRecord
from theseus.generators.base import GeneratorRole


# (gid, module, class_name, expected claim_kind)
GENS = [
    ("l2", "l2_formalization_skeleton", "L2FormalizationSkeletonGenerator", "formalization_skeleton"),
    ("m2", "m2_compression", "M2CompressionGenerator", "corpus_compression"),
    ("p1", "p1_modus_ponens_chain", "P1ModusPonensChainGenerator", "modus_ponens_chain"),
    ("q1", "q1_modular_varying_p", "Q1ModularVaryingPGenerator", "modular_varying_p"),
    ("r1", "r1_subset_relation", "R1SubsetRelationGenerator", "subset_relation"),
    ("s1", "s1_triangle_inequality", "S1TriangleInequalityGenerator", "triangle_inequality"),
    ("t1", "t1_multi_hop_deduction", "T1MultiHopDeductionGenerator", "multi_hop_deduction"),
    ("u1", "u1_quantifier_swap", "U1QuantifierSwapGenerator", "quantifier_swap"),
    ("v1", "v1_counterfactual_invariance", "V1CounterfactualInvarianceGenerator", "counterfactual_invariance"),
    ("w1", "w1_closure_under_operation", "W1ClosureUnderOperationGenerator", "closure_under_operation"),
    ("x1", "x1_partial_information", "X1PartialInformationGenerator", "partial_information"),
    ("y1", "y1_analogical_transfer", "Y1AnalogicalTransferGenerator", "analogical_transfer"),
    ("z1", "z1_order_dependence", "Z1OrderDependenceGenerator", "order_dependence"),
    ("aa1", "aa1_confidence_calibration", "Aa1ConfidenceCalibrationGenerator", "confidence_calibration"),
    ("bb1", "bb1_false_dichotomy", "Bb1FalseDichotomyGenerator", "false_dichotomy"),
]


def _load(module: str, class_name: str):
    mod = importlib.import_module(f"theseus.generators.{module}")
    return getattr(mod, class_name)


def _exercise(gen, max_calls=100):
    for _ in range(max_calls):
        r = gen.next()
        if r is not None:
            return r
    return None


@pytest.mark.parametrize("gid,module,class_name,expected_kind", GENS)
def test_imports(gid, module, class_name, expected_kind):
    cls = _load(module, class_name)
    assert cls is not None


@pytest.mark.parametrize("gid,module,class_name,expected_kind", GENS)
def test_instantiates(gid, module, class_name, expected_kind):
    cls = _load(module, class_name)
    g = cls(batch_id=f"test-{gid}")
    assert g.generator_id == gid


@pytest.mark.parametrize("gid,module,class_name,expected_kind", GENS)
def test_emits_record(gid, module, class_name, expected_kind):
    cls = _load(module, class_name)
    g = cls(batch_id=f"test-{gid}")
    rec = _exercise(g)
    assert isinstance(rec, TheseusRecord)


@pytest.mark.parametrize("gid,module,class_name,expected_kind", GENS)
def test_claim_kind(gid, module, class_name, expected_kind):
    cls = _load(module, class_name)
    g = cls(batch_id=f"test-{gid}")
    rec = _exercise(g)
    assert rec is not None
    assert rec.claim_kind == expected_kind


@pytest.mark.parametrize("gid,module,class_name,expected_kind", GENS)
def test_role_discovery(gid, module, class_name, expected_kind):
    cls = _load(module, class_name)
    assert cls.role == GeneratorRole.DISCOVERY
