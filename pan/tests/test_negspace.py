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


def test_primary_endpoint_controls_amendment_a1():
    """POSITIVE: a contract-satisfying mechanism behaviorally DISTINCT from every known class (environmental storage AND
    a visible horizon cap) is one novel class; its executed-no-op twin does not add a second (EQUIVALENT merges).
    NEGATIVE: a renamed supported mechanism is eq_supported, not novel. CHEAT (A1): a cap-1000 twin of the supported
    mechanism differs only in code the suite never executes -- UNKNOWN against a known class is tallied, never novel."""
    from pan.negspace import harness
    novel = dsl.source(dict(storage="world", d=3, reset="none", cap=100, noop=False))
    twin = dsl.source(dict(storage="world", d=3, reset="none", cap=100, noop=True))
    recs = [dict(i=i, guard=None, src=s) for i, s in
            enumerate([novel, twin, cal.M["list_renamed"], cal.M["history_cap1000"]])]
    e = harness.endpoints(recs)
    assert e["executable"] == 4 and e["contract"] == 4
    assert e["novel_classes"] == 1 and e["eq_supported"] == 1 and e["unresolved_vs_known"] == 1
    assert harness.endpoints(recs[2:])["novel_classes"] == 0


def test_novel_representatives_carry_witnesses_for_adjudication():
    """A3: the D-arm smoke's 'novel class' was a horizon-cap VARIANT (outputs 0 after the cap; the frozen F-horizon-cap
    reference freezes its memory instead). The endpoint must expose that witness, not hide it in a count."""
    from pan.negspace import harness
    variant = dsl.source(dict(storage="ring", d=3, reset="none", cap=100, noop=True))
    e = harness.endpoints([dict(i=0, guard=None, src=variant)])
    assert e["novel_classes"] == 1
    w = e["novel_representatives"][0]["witness_vs_known"]["F-horizon-cap"]
    assert w["stream"] == "long200" and w["step"] == 100 and (w["a"], w["b"]) == (0, 5)


def test_symbolic_arm_uses_its_exclusion_library_a4():
    """A4: before the fix D and Dx drew the same shuffled sequence whatever was rejected, so the counterfeit control was
    vacuous by construction. NEGATIVE: with no library (A-style, unarmed) nothing is rejected. POSITIVE: the real library
    rejects at least once, and a rejected proposal's behavioral class is never drawn again."""
    from pan.negspace import evaluators as ev
    from pan.negspace import harness
    recs = harness.run_arm("D", 30, seed=1)
    rej = [r["src"] for r in recs if r.get("excluded_by") and not any(h.startswith("accepted-") for h in r["excluded_by"])]
    assert rej, "real library never rejected anything in 30 draws"
    later = [r["src"] for r in recs]
    for x in rej:
        i = later.index(x)
        assert not any(ev.behavioral(x, y)["verdict"] == "EQUIVALENT" for y in later[i + 1:])
    d, dx = [r["src"] for r in recs], [r["src"] for r in harness.run_arm("Dx", 30, seed=1)]
    assert d != dx
