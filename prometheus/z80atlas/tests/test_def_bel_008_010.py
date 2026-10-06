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
