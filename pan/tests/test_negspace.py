"""PAN-43 mechanics (no evaluator scores): suite composition, contract streams, the static guard, the runner, the
DSL's analytic labels."""
from pan.negspace import calibration as cal
from pan.negspace import domain, dsl


def test_suite_and_contract_streams_are_as_frozen():
    s = domain.suite()
    assert len(s) == 24 and sum(1 for _, _, w in s if w is not None) == 3 and max(len(x) for _, x, _ in s) == 200
    assert len(domain.contract_streams()) == 20
    assert domain.contract_output([4, 5, 6, 7, 8]) == [0, 0, 0, 4, 5]


def test_static_guard_blocks_unsafe_code_and_passes_calibration():
    assert domain.static_guard("import os\nclass Mechanism:\n    pass\n")
    assert domain.static_guard("class Mechanism:\n    def step(self, x):\n        return eval('1')\n")
    assert domain.static_guard("class Mechanism:\n    def step(self, x):\n        return x.__class__\n")
    assert domain.static_guard("def f():\n    pass\n")
    assert all(domain.static_guard(s) is None for s in cal.M.values())


def test_runner_reports_outputs_and_coverage():
    r = domain.run(cal.M["list"])
    assert domain.satisfies_contract(r) and set(r["lines"]) >= domain.executable_lines(cal.M["list"])
    assert "error" in domain.run("class Mechanism:\n    def __init__(self, world):\n        pass\n    def step(self, x):\n        return 1 // 0\n")


def test_dsl_labels_are_analytic():
    base = dict(storage="list", d=3, reset="none", cap=None, noop=False)
    assert dsl.label(base, dict(base, storage="ring", noop=True)) == "EQUIVALENT"
    assert dsl.label(base, dict(base, d=2)) == "DISTINCT"
    assert dsl.label(base, dict(base, storage="world")) == "DISTINCT"
    assert dsl.label(base, dict(base, cap=100)) == "DISTINCT"
    assert dsl.label(base, dict(base, cap=1000)) == "UNRESOLVED"
    assert dsl.label(dict(base, cap=100), dict(base, cap=1000)) == "DISTINCT"
    pairs = dsl.sample_pairs(30, 5)
    assert len(pairs) == 30 and {lab for _, _, lab in pairs} == {"EQUIVALENT", "DISTINCT", "UNRESOLVED"}
    assert all(domain.static_guard(dsl.source(p)) is None for p, _, _ in pairs)
