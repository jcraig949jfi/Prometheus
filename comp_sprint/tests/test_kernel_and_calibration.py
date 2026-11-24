"""Phase 0 tests (RED first) for comp_sprint: Track 3B-Boolean kernel, meter, NPN, exact SAT."""
import pytest


def test_meter_accounting_and_invariants():
    from comp_sprint.meter import WorkMeter

    m = WorkMeter(cpu_usd_per_core_hour=0.05)
    m.charge_evals(100, phase="offline_eval")
    m.charge_sat_call(seconds=0.25, phase="offline_eval")
    m.charge_llm_proposal(usd=0.02, accepted=False, phase="sleep_propose")
    m.charge_llm_proposal(usd=0.03, accepted=True, phase="sleep_propose")

    snap = m.snapshot()
    # Failed proposals MUST be included in fixed crystallization cost F.
    assert snap["fixed_llm_usd"] == pytest.approx(0.05)
    assert snap["llm_proposals_total"] == 2
    assert snap["llm_proposals_accepted"] == 1
    assert snap["eval_units"] == 100
    assert snap["sat_calls"] == 1
    assert snap["sat_seconds"] == pytest.approx(0.25)

    # Break-even N* = F / (v_L - v_M)
    n_star = WorkMeter.break_even_n(fixed_f=10.0, v_naked=0.50, v_unplugged=0.10)
    assert n_star == pytest.approx(25.0)
    assert WorkMeter.break_even_n(fixed_f=10.0, v_naked=0.10, v_unplugged=0.10) is None


def test_xag_circuit_eval_and_macro_flattening_no_discount():
    from comp_sprint.circuit import Gate, XAGCircuit, Macro, verify_truth_tables

    # Build a 3-input 2-output full adder in XAG:
    # s = x0 ^ x1 ^ x2 (2 XOR gates)
    # c = ((x0 ^ x2) & (x1 ^ x2)) ^ x2  (only 1 AND + 3 XOR = 4 gates total with sharing!)
    # Wait: s = (x0 ^ x1) ^ x2; let t0 = x0 ^ x2, t1 = x1 ^ x2, t2 = t0 & t1, c = t2 ^ x2, s = t0 ^ x1.
    # That's 4 gates total for BOTH sum and carry!
    fa = XAGCircuit(
        n_inputs=3,
        gates=(
            Gate("XOR", 0, False, 2, False),  # node 3: x0 ^ x2
            Gate("XOR", 1, False, 2, False),  # node 4: x1 ^ x2
            Gate("AND", 3, False, 4, False),  # node 5: (x0 ^ x2) & (x1 ^ x2)
            Gate("XOR", 5, False, 2, False),  # node 6: carry
            Gate("XOR", 3, False, 1, False),  # node 7: sum = (x0 ^ x2) ^ x1
        ),
        outputs=((7, False), (6, False)),
    )
    tts = fa.truth_tables()
    assert len(tts) == 2
    # Verify every 3-bit input row (0..7)
    for x in range(8):
        b0, b1, b2 = (x >> 0) & 1, (x >> 1) & 1, (x >> 2) & 1
        s_exp = (b0 + b1 + b2) & 1
        c_exp = 1 if (b0 + b1 + b2) >= 2 else 0
        assert ((tts[0] >> x) & 1) == s_exp
        assert ((tts[1] >> x) & 1) == c_exp

    assert fa.gate_count() == 5
    assert fa.and_count() == 1
    assert verify_truth_tables(fa, tts)

    # Anti-cheating check: instantiating a macro MUST flatten to real primitive gates,
    # never counting a 5-gate macro as 1 gate, while strash deduplicates shared sub-DAGs.
    m = Macro.from_circuit("full_adder", fa)
    rebuilt = XAGCircuit.from_macro_calls(
        n_inputs=3,
        calls=[(m, (0, 1, 2))],
        outputs=[("call0", 0, False), ("call0", 1, False)],
    )
    assert rebuilt.truth_tables() == tts
    assert rebuilt.gate_count() == 5

    # Two identical macro calls on the SAME inputs deduplicate via structural hashing.
    dedup = XAGCircuit.from_macro_calls(
        n_inputs=3,
        calls=[(m, (0, 1, 2)), (m, (0, 1, 2))],
        outputs=[("call0", 0, False), ("call1", 1, False)],
    )
    assert dedup.truth_tables() == tts
    assert dedup.gate_count() == 5


def test_npn_4_input_exact_222_classes():
    from comp_sprint.npn import enumerate_npn4_classes, npn4_canonical

    classes = enumerate_npn4_classes()
    # Mathematical fact: there are exactly 222 NPN equivalence classes of 4-input Boolean functions.
    assert len(classes) == 222
    assert sum(classes.values()) == 65536
    # Constants 0x0000 and 0xFFFF must be in the same NPN class of size 2.
    assert npn4_canonical(0x0000) == npn4_canonical(0xFFFF)
    assert classes[npn4_canonical(0x0000)] == 2


def test_sat_exact_matches_bfs_on_xag_and_aig_sample():
    from comp_sprint.npn import enumerate_npn4_classes
    from comp_sprint.sat_exact import exact_bfs_4input, sat_exact_synthesize

    classes = sorted(enumerate_npn4_classes().keys())
    bfs_xag = exact_bfs_4input(basis="XAG", max_gates=4)
    # Test 25 diverse NPN classes across gate counts 0..4 against independent SAT-exact solver.
    sample = [tt for tt in classes if tt in bfs_xag][:25]
    assert len(sample) == 25
    for tt in sample:
        bfs_k = bfs_xag[tt]
        circ = sat_exact_synthesize(n_inputs=4, targets=(tt,), basis="XAG", max_gates=bfs_k)
        assert circ is not None
        assert circ.gate_count() == bfs_k
        assert circ.truth_tables() == (tt,)
        if bfs_k > 0:
            # Must be UNSAT at bfs_k - 1 (true optimality proof!)
            smaller = sat_exact_synthesize(n_inputs=4, targets=(tt,), basis="XAG", max_gates=bfs_k - 1)
            assert smaller is None


def test_multi_output_sat_exact_full_adder():
    from comp_sprint.sat_exact import sat_exact_synthesize

    # 3-input full adder: exact minimum XAG size is 5 gates (and only 1 AND gate!).
    # Wait: verify exact XAG minimum for 2-output full adder!
    # Sum = 0b10010110 = 0x96, Carry = 0b11101000 = 0xE8
    sum_tt = 0x96
    carry_tt = 0xE8
    circ = sat_exact_synthesize(n_inputs=3, targets=(sum_tt, carry_tt), basis="XAG", max_gates=5)
    assert circ is not None
    assert circ.truth_tables() == (sum_tt, carry_tt)
    assert circ.gate_count() <= 5
    # Prove optimality: check whether 4 gates is UNSAT
    circ4 = sat_exact_synthesize(n_inputs=3, targets=(sum_tt, carry_tt), basis="XAG", max_gates=4)
    assert (circ4 is None and circ.gate_count() == 5) or (circ4 is not None and circ.gate_count() == 4)


def test_knuth_taocp_4a_xag_le4_distribution():
    from collections import Counter
    from comp_sprint.npn import enumerate_npn4_classes
    from comp_sprint.sat_exact import exact_bfs_4input

    classes = enumerate_npn4_classes()
    bfs = exact_bfs_4input(basis="XAG", max_gates=4)
    c_hist = Counter(bfs.values())
    f_hist = Counter()
    for tt, k in bfs.items():
        f_hist[k] += classes[tt]
    # Exact Knuth TAOCP Vol. 4A s7.1.2 Table 1 / OEIS A056287 values for k = 0..4:
    assert dict(c_hist) == {0: 2, 1: 2, 2: 5, 3: 20, 4: 34}
    assert dict(f_hist) == {0: 10, 1: 60, 2: 456, 3: 2474, 4: 10624}
