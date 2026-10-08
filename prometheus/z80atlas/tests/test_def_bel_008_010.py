"""Regression tests for DEF-BEL-008/009/010 (Nestor's Wave-2 defect-class sweep, comms #1207; confirmed in #1211;
recorded in roles/Bellerophon/WORK_STATE.json).

As in test_forensic_regressions.py, each test (a) REPRODUCES the defect on the historical default -- those assertions
stay green, because the default is kept replayable byte-for-byte (golden_v1.json) -- and (b) asserts the repaired
property under the opt-in switch: Config.glineage_rule = "PROVENANCE" (008), Config.init_draws = "PAIRED" (009),
geometry rep_rule = "written" (010)."""
from __future__ import annotations

from prometheus.z80atlas import vm, geometry
from prometheus.z80atlas.tasks import Task
from prometheus.z80atlas.world import World, Config


# ---- the switches are invisible at their defaults ----------------------------------------------------------------------
def test_defaults_leave_config_dict_unchanged():
    d = Config().to_dict()
    assert "glineage_rule" not in d and "init_draws" not in d                 # historical plan hashes unchanged
    d2 = Config(glineage_rule="PROVENANCE", init_draws="PAIRED").to_dict()
    assert d2["glineage_rule"] == "PROVENANCE" and d2["init_draws"] == "PAIRED"


# ---- DEF-BEL-008: genetic lineage assigned by resemblance (label-as-content) ---------------------------------------------
# The writer LDIR-copies all 64 of its own bytes into the partner window, then edits two bytes of ITSELF. The partner was a
# near-clone of the writer's pre-execution tape (one byte different) from another lineage. Every child byte was physically
# moved from the writer, but the child now resembles the partner (63/64) more than the edited writer (62/64).
SELF_COPY_THEN_EDIT = bytes([vm.LD_S_n, 0, vm.LD_T_n, 64, vm.LD_C_n, 64, vm.LDIR,
                             vm.LD_A_n, 0x55, vm.LD_T_n, 20, vm.LD_pT_A, vm.LD_T_n, 21, vm.LD_pT_A, vm.HALT])


def _self_copy_birth(rule, physics="v2"):
    cfg = Config(reproduction="ENDOGENOUS_COPY", cells=16, ticks=5, physics=physics, glineage_rule=rule)
    w = World(cfg, 9)
    w.cells = [None] * 16
    pre = SELF_COPY_THEN_EDIT + bytes(64 - len(SELF_COPY_THEN_EDIT))
    writer = w._spawn(0, bytearray(pre), None, "init")
    clone = bytearray(pre); clone[40] = 0x99
    partner = w._spawn(1, clone, None, "init")
    mem, tr = w._execute(writer, partner.tape, [1])
    writer.tape = bytearray(mem[:64])
    w._apply_reproduction(writer, 1, mem, tr)
    child = w.cells[1]
    assert child is not partner and bytes(child.tape) == pre               # a birth happened; the child is the writer's pre-tape
    return w, writer, partner, child


def test_008_resemblance_mislabels_a_physical_self_copy_as_a_capture():
    w, writer, partner, child = _self_copy_birth("RESEMBLANCE")
    assert child.glineage == partner.glineage and w.captures == 1            # the defect: content decided the descent label
    assert writer.replications == 0                                          # ... and under v2 the true copier is not credited


def test_008_provenance_labels_by_where_the_bytes_came_from():
    w, writer, partner, child = _self_copy_birth("PROVENANCE")
    assert child.glineage == writer.glineage and w.captures == 0
    assert writer.replications == 1


def test_008_provenance_counts():
    cfg = Config(reproduction="ENDOGENOUS_COPY", cells=16, ticks=5, physics="v2", glineage_rule="PROVENANCE")
    w = World(cfg, 9); w.cells = [None] * 16
    pre = SELF_COPY_THEN_EDIT + bytes(64 - len(SELF_COPY_THEN_EDIT))
    writer = w._spawn(0, bytearray(pre), None, "init")
    partner = w._spawn(1, bytearray(range(100, 164)), None, "init")
    mem, tr = w._execute(writer, partner.tape, [1])
    assert w._provenance_counts(tr, partner) == (64, 0)                     # all 64 window bytes moved from [0,L)
    assert w._provenance_counts(tr, None) == (64, 0)


def _one_byte_write(rule, target_present=True):
    cfg = Config(reproduction="ENDOGENOUS_PARTIAL", cells=16, ticks=5, physics="v2", glineage_rule=rule)
    w = World(cfg, 9); w.cells = [None] * 16
    writer = w._spawn(0, bytearray(bytes([vm.LD_A_n, 0x77, vm.LD_T_n, 70, vm.LD_pT_A, vm.HALT]) + bytes(58)), None, "init")
    partner = w._spawn(1, bytearray(range(100, 164)), None, "init") if target_present else None
    mem, tr = w._execute(writer, partner.tape if partner else None, [1])
    writer.tape = bytearray(mem[:64])
    w._apply_reproduction(writer, 1, mem, tr)
    return w, writer, partner, w.cells[1]


def test_008_provenance_one_byte_write_over_a_partner_is_still_the_partners_material():
    w, writer, partner, child = _one_byte_write("PROVENANCE")
    assert child.glineage == partner.glineage and w.captures == 1           # 63 unwritten bytes are the target's
    assert writer.replications == 0                                          # v2 C8 still holds: a capture credits nobody


def test_008_provenance_constructed_child_in_an_empty_cell_keeps_the_writers_label():
    w, writer, _, child = _one_byte_write("PROVENANCE", target_present=False)
    assert child.glineage == writer.glineage and w.captures == 0
    assert w.birth_class[child.id][3] == "constructed"                       # no moved material: recorded as constructed
    assert writer.replications == 1                                          # the writer did cause the birth


# ---- DEF-BEL-009: transplant slots take 0 world-RNG draws (same seed is not CRN-paired) ----------------------------------
def _pair(init_draws):
    rep = vm.replicator(64).hex()
    base = dict(reproduction="ENDOGENOUS_COPY", cells=64, ticks=5, init_draws=init_draws)
    w_tx = World(Config(init_tapes=(rep,), **base), 4)
    w_ct = World(Config(**base), 4)
    return w_tx, w_ct


def test_009_historical_init_desynchronises_the_world_rng():
    w_tx, w_ct = _pair("HISTORICAL")
    assert w_tx.rng.getstate() != w_ct.rng.getstate()                       # the defect: same seed, different streams
    shared = [i for i, (a, b) in enumerate(zip(w_tx.cells, w_ct.cells))
              if a is not None and b is not None and a.mechanism == "init" and b.mechanism == "init"]
    assert any(w_tx.cells[i].tape != w_ct.cells[i].tape for i in shared)     # even the shared random slots differ


def test_009_paired_init_keeps_the_world_rng_common():
    w_tx, w_ct = _pair("PAIRED")
    assert w_tx.rng.getstate() == w_ct.rng.getstate()                       # identical stream after init
    n_tx = sum(1 for c in w_tx.cells if c is not None and c.mechanism == "transplant")
    assert n_tx > 0
    for a, b in zip(w_tx.cells, w_ct.cells):
        assert (a is None) == (b is None)
        if a is not None and a.mechanism == "init":
            assert a.tape == b.tape                                          # every shared random slot is the same tape
    w_tx.run(); w_ct.run()                                                   # and both still run


def test_009_paired_init_also_pairs_seeded_worlds():
    base = dict(reproduction="ENDOGENOUS_COPY", cells=64, ticks=5, init_draws="PAIRED")
    a = World(Config(init="SEEDED_REPLICATOR", **base), 6)
    b = World(Config(init="RANDOM", **base), 6)
    assert a.rng.getstate() == b.rng.getstate()


# ---- DEF-BEL-010: geometry's zero padding + zero child window inflate `replicates` ---------------------------------------
# A short tape that writes ONE byte (equal to its own byte 0) into the window and halts. Under ENDOGENOUS_PARTIAL need = 1.
ONE_BYTE = bytes([vm.LD_A_n, vm.LD_A_n, vm.LD_T_n, 64, vm.LD_pT_A, vm.HALT])


def test_010_v1_rule_scores_a_one_byte_writer_as_a_replicator():
    cfg = Config(reproduction="ENDOGENOUS_PARTIAL")
    import random
    e = geometry._eval(ONE_BYTE, cfg, Task("INC"), random.Random(1))
    assert e["replicates"] is True                                           # the defect: 58 untouched zero bytes 'match'


def test_010_written_rule_does_not():
    cfg = Config(reproduction="ENDOGENOUS_PARTIAL")
    import random
    e = geometry._eval(ONE_BYTE, cfg, Task("INC"), random.Random(1), rep_rule="written")
    assert e["replicates"] is False


def test_010_written_rule_keeps_the_real_replicator():                       # positive control: a true copier still replicates
    import random
    rep = vm.replicator(64)
    for repro in ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL"):
        e = geometry._eval(rep, Config(reproduction=repro), Task("INC"), random.Random(1), rep_rule="written")
        assert e["replicates"] is True, repro


def test_010_scan_records_the_rule_only_off_default():
    cfg = Config(reproduction="ENDOGENOUS_PARTIAL")
    v1 = geometry.scan(ONE_BYTE, cfg, Task("INC"), 3, n=8)
    wr = geometry.scan(ONE_BYTE, cfg, Task("INC"), 3, n=8, rep_rule="written")
    assert "rep_rule" not in v1 and wr["rep_rule"] == "written"
    assert v1["base_replicates"] is True and wr["base_replicates"] is False
    dc = geometry.damage_cliff(ONE_BYTE, cfg, Task("INC"), 3, trials=4, rep_rule="written")
    assert dc["rep_rule"] == "written" and dc["base_replicates"] is False


# ---- review A (BEL-48H, 2026-10-08): multi-hop material origin, validation, the zero-sweep hole ----------------------------
def _counts(code, partner=None, repro="ENDOGENOUS_COPY", layout="SHARED"):
    cfg = Config(reproduction=repro, cells=16, ticks=5, physics="v2", glineage_rule="PROVENANCE", layout=layout)
    w = World(cfg, 9); w.cells = [None] * 16
    t = bytearray(64); t[:len(code)] = code
    a = w._spawn(0, t, None, "init")
    b = w._spawn(1, bytearray(partner if partner is not None else bytes(range(100, 164))), None, "init")
    mem, tr = w._execute(a, b.tape, [1])
    return w._provenance_counts(tr, b), tr


def test_reviewA_window_staged_self_copy_is_writer_material():
    S, T, C, X = vm.LD_S_n, vm.LD_T_n, vm.LD_C_n, vm.LDIR
    code = bytes([S, 0, T, 64, C, 64, X, S, 64, T, 64, C, 64, X, vm.HALT])     # self -> window, then window -> window
    assert _counts(code)[0] == (64, 0)                                          # was (0, 64) = 'capture' (review A p1)


def test_reviewA_scratch_staged_copy_is_writer_material():
    S, T, C, X = vm.LD_S_n, vm.LD_T_n, vm.LD_C_n, vm.LDIR
    code = bytes([S, 0, T, 0x80, C, 64, X, S, 0x80, T, 64, C, 64, X, vm.HALT])  # self -> scratch -> window
    assert _counts(code)[0] == (64, 0)                                          # was (0, 0) = 'constructed'


def test_reviewA_register_move_copy_is_writer_material():
    # LD S,0 ; LD T,64 ; LD B,64 ; loop: LD A,(S) ; LD (T),A ; INC S ; INC T ; DJNZ loop ; HALT
    # 5 instructions per byte: 40 bytes fit the 256-step budget; the 24 unwritten bytes stay the target's
    code = bytes([vm.LD_S_n, 0, vm.LD_T_n, 64, vm.LD_B_n, 40, vm.LD_A_pS, vm.LD_pT_A, vm.INC_S, vm.INC_T, vm.DJNZ_d, 0xFA, vm.HALT])
    (nw, nt), tr = _counts(code, repro="ENDOGENOUS_PARTIAL")
    assert (nw, nt) == (40, 24)
    assert all(o == off for off, o in tr.win_origin.items())                    # each byte from its own position


def test_reviewA_computed_bytes_are_constructed_and_target_shift_is_target():
    code = bytes([vm.LD_T_n, 64, vm.LD_B_n, 64, vm.INC_A, vm.LD_pT_A, vm.INC_T, vm.DJNZ_d, 0xFB, vm.HALT])   # writes 1,2,3,...
    assert _counts(code)[0] == (0, 0)
    code2 = bytes([vm.LD_S_n, 65, vm.LD_T_n, 64, vm.LD_C_n, 63, vm.LDIR, vm.HALT])                       # partner shifted by one
    assert _counts(code2)[0] == (0, 64)                                         # 63 moved target bytes + 1 unwritten


def test_reviewA_separated_layout_carries_origin_across_halves():
    S, T, C, X = vm.LD_S_n, vm.LD_T_n, vm.LD_C_n, vm.LDIR
    first = bytes([S, 0, T, 0x80, C, 64, X, vm.HALT])                          # half 1: self -> scratch
    code = bytearray(64); code[:len(first)] = first
    code[32:32 + 8] = bytes([S, 0x80, T, 64, C, 64, X, vm.HALT])               # half 2: scratch -> window
    (nw, nt), tr = _counts(bytes(code), layout="SEPARATED")
    assert nw == 64 and nt == 0


def test_reviewA_switch_values_are_validated():
    import pytest
    for kw in ({"glineage_rule": "PROVENENCE"}, {"init_draws": "paired"}):
        with pytest.raises(ValueError):
            World(Config(**kw), 1)
    import random
    with pytest.raises(ValueError):
        geometry._eval(ONE_BYTE, Config(), Task("INC"), random.Random(1), rep_rule="writen")


def test_reviewA_zero_sweep_is_not_a_replicator_under_written():
    import random
    sweep = bytes([vm.LD_S_n, 0x80, vm.LD_T_n, 64, vm.LDIR, vm.HALT])          # copies scratch zeros over the window
    for layout in ("SHARED", "SEPARATED"):
        cfg = Config(reproduction="ENDOGENOUS_COPY", layout=layout)
        assert geometry._eval(sweep, cfg, Task("INC"), random.Random(1))["replicates"] is True              # v1 hole
        assert geometry._eval(sweep, cfg, Task("INC"), random.Random(1), rep_rule="written")["replicates"] is False


def test_reviewB_S1b_laundered_partner_material_is_target():
    # review B S1b: the writer copies the partner's window into its OWN region, then from there into the window
    # (one-hop 'laundering'); multi-hop origin resolves every moved byte to the partner
    import random
    code = bytes.fromhex("0740082003201507200840032015015a087f11ff")
    partner = bytes(random.Random(0).randrange(256) for _ in range(64))
    (nw, nt), _ = _counts(code + bytes([0xAA]) * (64 - len(code)), partner=partner, repro="OVERWRITE")
    assert nt > nw and nw == 0
