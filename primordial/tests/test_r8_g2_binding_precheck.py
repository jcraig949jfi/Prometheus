"""R8 G2 (PC 1789523009420-0): the anti-prior CELL-BINDING PRE-CHECK, and redaction by construction.

Aimed at the BUILD_R8 G2 acceptance list: planted cells whose pressure cannot bind, whose oracle can never fire and whose
discriminator has zero resolving power are REJECTED with recorded reasons (each planted from the actual round 7 cell);
the published list, replacements included, is reproducible from seed 20260921 alone; the rejected set becomes rows.
"""
from __future__ import annotations

import dataclasses
import json

import numpy as np
import pytest

from primordial.score import anti_prior as AP
from primordial.tests.test_score_anti_prior import Store, _pred

AP01 = {"representation": "affine_plastic", "world": "w13", "pressure": "held_out_seeds", "substrate": "numpy",
        "channel": "metered_stream"}
AP03 = {"representation": "small_program", "world": "signal_world_d1", "pressure": "byte_charge",
        "substrate": "falkordb_cypher", "channel": "metered_stream"}
AP04 = {"representation": "bitset", "world": "w13", "pressure": "regime_switching", "substrate": "numba_fused",
        "channel": "none"}
CLEAN = {"representation": "tucker", "world": "nk_stub", "pressure": "cpu_ttl", "substrate": "graphblas",
         "channel": "none"}


@dataclasses.dataclass
class Mech:
    lin_ops: tuple
    yield_reg: int
    act_targets: tuple
    obs_regs: tuple


def mechs(**by_world):
    return lambda w: by_world.get(w)


def failed(pc):
    return [c for c in AP.CHECKS if not pc["checks"][c]["ok"]]


# ---- acceptance 1: pressure cannot bind ---------------------------------------------------------------------------

def test_planted_unbindable_pressure_is_rejected_with_its_reason():
    pc = AP.binding_precheck(AP04)                                  # the real w13 Mechanics
    assert not pc["ok"] and failed(pc) == ["pressure_binds"]
    (why,) = pc["checks"]["pressure_binds"]["reasons"]
    assert why.startswith("PRESSURE_CANNOT_BIND") and "yield reg 5" in why and "C-R7-AP-04" in why
    assert pc["reasons"] == [f"pressure_binds:{why}"]


def test_the_binding_rule_reads_world_structure_not_the_cell_name():
    no_path = Mech(lin_ops=((0, 3, 1, 1, 2, 7),), yield_reg=5, act_targets=(5,), obs_regs=(9,))
    via_lin = Mech(lin_ops=((5, 3, 1, 1, 2, 7),), yield_reg=5, act_targets=(5,), obs_regs=(9,))
    via_obs = Mech(lin_ops=((0, 3, 1, 1, 2, 7),), yield_reg=5, act_targets=(5,), obs_regs=(0,))
    reader = dict(AP04, representation="tucker")
    assert "pressure_binds" in failed(AP.binding_precheck(reader, mechanics=mechs(w13=no_path)))   # any genome
    assert AP.binding_precheck(AP04, mechanics=mechs(w13=via_lin))["ok"]          # the flip reaches the yield register
    assert AP.binding_precheck(reader, mechanics=mechs(w13=via_obs))["ok"]        # observable flip, reader can act on it
    assert "pressure_binds" in failed(AP.binding_precheck(AP04, mechanics=mechs(w13=via_obs)))      # a tape cannot
    unknown = AP.binding_precheck(AP04, mechanics=mechs())                        # no Mechanics: fail closed
    assert not unknown["ok"] and unknown["checks"]["pressure_binds"]["reasons"][0].startswith("UNVERIFIABLE")


# ---- acceptance 2: the oracle can never fire -------------------------------------------------------------------

def test_planted_cell_whose_oracle_can_never_fire_is_rejected():
    pc = AP.binding_precheck(AP01)
    assert not pc["ok"] and failed(pc) == ["oracle_fires"]
    assert "ORACLE_CANNOT_FIRE" in pc["reasons"][0] and "C-R7-AP-01" in pc["reasons"][0]
    measured = AP.binding_precheck(CLEAN, evidence={"oracle_eligible": 0})
    assert failed(measured) == ["oracle_fires"]
    assert AP.binding_precheck(CLEAN, evidence={"oracle_eligible": 3})["ok"]


# ---- acceptance 3: zero resolving power ----------------------------------------------------------------------

def test_planted_zero_resolving_power_cell_is_rejected():
    pc = AP.binding_precheck(AP03)
    assert not pc["ok"] and failed(pc) == ["discriminator_resolves"]
    assert "ZERO_RESOLVING_POWER" in pc["reasons"][0] and "C-R7-AP-03" in pc["reasons"][0]
    pinned = {"control": [31.71875] * 32, "cell": [31.71875] * 32}                # AP-03's rows, exactly
    pc2 = AP.binding_precheck(CLEAN, evidence={"null_samples": pinned})
    assert failed(pc2) == ["discriminator_resolves"] and "64 null-sample values" in pc2["reasons"][0]
    spread = {"control": [31.71875] * 31 + [30.0], "cell": [31.71875] * 32}
    assert AP.binding_precheck(CLEAN, evidence={"null_samples": spread})["ok"]


def test_d1_rule_is_the_payoff_inequality_not_a_world_ban():
    try:
        from primordial.lingua import signal as S
        assert AP.D1_METERED["symbol_bits"] == int(np.ceil(np.log2(S.N_ACT)))
    except ImportError:
        pytest.skip("lingua.signal unavailable")
    assert AP.binding_precheck(dict(AP03, channel="none"))["ok"]
    cheap = dict(AP.D1_METERED, alpha_int=0)
    orig = AP.D1_METERED
    try:
        AP.D1_METERED = cheap
        assert AP.binding_precheck(AP03)["ok"]
    finally:
        AP.D1_METERED = orig


def test_control_identical_and_every_rule_runs_without_short_circuit():
    blind = {"representation": "bitset", "world": "w13", "pressure": "obs_delay", "substrate": "numpy",
             "channel": "metered_stream"}
    pc = AP.binding_precheck(blind, evidence={"intervention_magnitude": 0})
    assert failed(pc) == ["oracle_fires", "control_differs"]
    assert len(pc["checks"]["control_differs"]["reasons"]) == 2                   # both control rules reported
    assert pc["checks"]["control_differs"]["basis"] == ["observation_pressure_needs_reader", "intervention_nonzero"]
    assert AP.binding_precheck(CLEAN)["checks"]["pressure_binds"]["basis"] == []     # no rule applied: recorded as such


# ---- acceptance 4: reproducible from the seed alone, replacements included ------------------------------------

GRID = {"representation": ["bitset", "tucker", "affine_plastic", "small_program"],
        "world": ["w13", "signal_world_d1", "nk_stub"],
        "pressure": ["regime_switching", "obs_delay", "cpu_ttl"],
        "substrate": ["numpy"], "channel": ["none", "metered_stream"]}


def test_r8_list_replaces_rejections_from_the_same_seeded_permutation():
    rec = AP.draw_candidates(round_id="r8", n=20, now=1.0, grid=GRID)
    assert rec["seed"] == 20260921 and rec["precheck"] == AP.PRECHECK_VERSION and rec["n"] == 20
    assert rec["rejected"], "the planted grid must force replacements"
    names, sizes = list(GRID), [len(GRID[x]) for x in GRID]
    perm = np.random.Generator(np.random.PCG64(20260921)).permutation(int(np.prod(sizes))).tolist()
    expect_cells, expect_rej = [], []
    for pos, f in enumerate(perm):                             # independent re-derivation: seed + precheck only
        if len(expect_cells) == 20:
            break
        c = {x: GRID[x][int(i)] for x, i in zip(names, np.unravel_index(f, sizes))}
        (expect_cells if AP.binding_precheck(c)["ok"] else expect_rej).append((pos, c))
    assert rec["cells"] == [c for _, c in expect_cells] and rec["positions"] == [p for p, _ in expect_cells]
    assert [(r["draw_position"], r["cell"]) for r in rec["rejected"]] == expect_rej
    assert sorted(rec["positions"] + [r["draw_position"] for r in rec["rejected"]]) == list(range(rec["examined"]))
    assert all(AP.binding_precheck(c)["ok"] for c in rec["cells"])
    again = AP.draw_candidates(round_id="r8", n=20, now=999.0, grid=GRID)
    assert {**again, "ts": 0} == {**rec, "ts": 0}


def test_candidates_publishes_r8_once_with_rejections_in_the_record_and_legacy_rounds_are_unchanged():
    s = Store()
    rec = AP.candidates(s, round_id="r8", n=20, now=1.0, grid=GRID)
    assert AP.published(s, round_id="r8") == rec and rec["rejected"]
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.candidates(s, round_id="r8", n=20, grid=GRID)
    assert e.value.reason == "CANDIDATES_ALREADY_PUBLISHED"
    r7 = AP.candidates(s, round_id="r7", n=20, now=1.0, grid=GRID)                # v3 draw, byte-identical
    n_cells = int(np.prod([len(v) for v in GRID.values()]))
    flats = sorted(np.random.Generator(np.random.PCG64(20260919)).choice(n_cells, size=20, replace=False).tolist())
    names, sizes = list(GRID), [len(GRID[x]) for x in GRID]
    assert set(r7) == {"round", "seed", "ts", "n", "grid_cells", "cells"} and r7["n"] == len(flats) == 20
    assert r7["cells"] == [{x: GRID[x][int(i)] for x, i in zip(names, np.unravel_index(f, sizes))} for f in flats]


def test_r8_seed_row_is_the_frozen_value_and_unknown_rounds_still_fail_closed():
    assert AP.SEEDS["r8"] == (20260921, 20260922) and AP.seeds("r8") == (20260921, 20260922)
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.draw_candidates(round_id="r9", grid=GRID)
    assert e.value.reason == "SEED_NOT_FIXED"


def test_real_r8_grid_draw_is_deterministic_and_every_admitted_cell_passes():
    try:
        rec = AP.draw_candidates(round_id="r8", now=0.0)
    except Exception as exc:                                    # noqa: BLE001
        pytest.skip(f"worlds file unavailable: {exc}")
    assert rec["n"] == 48 and not rec["short"] and rec == AP.draw_candidates(round_id="r8", now=0.0)
    assert all(AP.binding_precheck(c)["ok"] for c in rec["cells"])
    assert not any(c in rec["cells"] for c in (AP01, AP03, AP04))


def test_empty_pool_refuses():
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.draw_candidates(round_id="r8", grid={"representation": ["bitset"], "world": ["w13"],
                                                "pressure": ["regime_switching"], "substrate": ["numpy"],
                                                "channel": ["none"]})
    assert e.value.reason == "EMPTY_POOL"


# ---- acceptance 5: the rejected set is committed residue ----------------------------------------------------

def test_rejection_reasons_become_residue_rows(monkeypatch, tmp_path):
    rec = AP.draw_candidates(round_id="r8", n=20, now=1.0, grid=GRID)
    rows = AP.residue_rows(rec)
    head, body = rows[0], rows[1:]
    assert head["kind"] == "anti_prior_precheck_summary" and head["rejected"] == len(body) == len(rec["rejected"])
    assert head["examined"] == head["admitted"] + head["rejected"] and sum(head["by_check"].values()) >= len(body)
    assert all(r["reasons"] and r["failed_checks"] and "cell" in r for r in body)
    text = json.dumps(rows)
    assert not any(f'"{f}"' in text for f in ("arm", "rank", "quantile", "prior_p_pass"))
    written = []

    class FakeWriter:
        def __init__(self, path, exp_id, commit_every_s=60.0, repo=None):
            written.append(("open", str(path), exp_id))

        def __enter__(self):
            return self

        def __exit__(self, *a):
            written.append(("close",))

        def write(self, row):
            written.append(("row", row))

    import primordial.fabric.rows as rows_mod
    monkeypatch.setattr(rows_mod, "RowWriter", FakeWriter)
    path = AP.write_residue(rec, path=tmp_path / "r8.jsonl")
    assert written[0] == ("open", path, "anti-prior-precheck-r8") and written[-1] == ("close",)
    assert [w[1] for w in written[1:-1]] == rows
    with pytest.raises(AP.PriorLedgerError):
        AP.residue_rows(AP.draw_candidates(round_id="r7", n=5, now=1.0, grid=GRID))


# ---- redaction by construction -----------------------------------------------------------------------------

def _r8_store():
    s = Store()
    grid = {"representation": [f"r{i}" for i in range(48)]}
    AP.candidates(s, round_id="r8", n=48, now=50.0, grid=grid)
    for i in range(48):
        AP.seal(s, _pred(f"pr{i:02d}", round(0.01 + 0.02 * i, 3), c={"representation": f"r{i}"}), "predictor",
                round_id="r8")
    return s


def test_experimenter_records_are_built_from_a_whitelist(monkeypatch):
    s = _r8_store()
    (out,) = AP.assign(s, "C-R8-AP-01", now=200.0, round_id="r8")
    assert set(out) == {"exp_id", "round", "cell"}
    stored = json.loads(s.hget("pm:prior:r8:assign", "C-R8-AP-01"))
    assert {"arm", "rank", "quantile", "u", "prediction_id"} <= set(stored)          # the conductor record keeps them
    assert AP.public_assignment(s, "C-R8-AP-01", round_id="r8") == out
    s.hset("pm:prior:r8:assign", "C-R8-AP-01", json.dumps({**stored, "prior_p_pass": 0.06, "new_secret": 1}))
    assert AP.public_assignment(s, "C-R8-AP-01", round_id="r8") == out              # new fields never leak by default
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.public_view({"exp_id": "x", "cell": {"representation": "r0", "arm": "anti_prior"}})
    assert e.value.reason == "REDACTION_LEAK"


def test_experimenter_cannot_read_a_prior_while_the_round_is_live_even_with_a_receipt():
    s = _r8_store()
    AP.assign(s, "C-R8-AP-01", now=200.0, round_id="r8")
    pid = json.loads(s.hget("pm:prior:r8:assign", "C-R8-AP-01"))["prediction_id"]
    with pytest.raises(AP.PriorLedgerError) as e:
        AP.read(s, pid, "experimenter", receipt_filed=lambda x: True, round_id="r8")
    assert e.value.reason == "EXPERIMENTER_READ_DENIED" and "live" in e.value.detail
    assert AP.read(s, pid, "conductor", round_id="r8")["prior_p_pass"] is not None
    assert AP.read(s, pid, "experimenter", receipt_filed=lambda x: True, round_id="r8", round_live=False)["cell"]


def test_gate_probe_finds_the_precheck_entrypoint():
    assert callable(AP.binding_precheck)
