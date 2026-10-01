import importlib.util
import sys
from pathlib import Path

_P = Path(__file__).resolve().parents[1] / "c1_hostile_adjudication.py"
_spec = importlib.util.spec_from_file_location("c1_hostile_adjudication", _P)
ha = importlib.util.module_from_spec(_spec)
sys.modules["c1_hostile_adjudication"] = ha          # dataclasses need the module registered
_spec.loader.exec_module(ha)


def test_contract_passes():
    assert ha.suite()["contract"] == "PASS"


def test_every_cheat_caught_and_every_clean_twin_quiet():
    r = ha.suite()
    assert r["cheats_caught"] and all(r["cheats_caught"].values())
    assert r["clean_twins_quiet"] and all(r["clean_twins_quiet"].values())


def test_all_five_490_classes_and_three_453_forms_are_present():
    fx = ha.suite()["fixtures"]
    for k in ("F1_memory_leak", "F2_evaluator_exploit", "F3a_unmetered_second_model", "F3b_escrow_overrun",
              "F3c_counter_edit", "F3e_unequal_escrow_across_arms", "F4_memoriser", "F5_lineage_id_shortcut"):
        assert fx[k]["cheat"] and fx[k]["fired"], k


def test_ablation_each_detector_is_what_catches_its_cheat():
    for det, a in ha.suite()["ablation"].items():
        assert a["fixtures"] and a["cheats_escape_when_disabled"], det


def test_single_relabel_can_miss_the_shortcut():
    """The HA-1.0.0 defect, kept as a regression: one relabel (L07 -> L31) does not expose this cheat."""
    tasks, honey, files, declared, canary, prov = ha._world()

    def outs(lab):
        env = ha._env(files, declared, honey, lab)
        return [a["answer"] for a in ha.run_cell(ha.cheat_lineage_id, tasks, env, prov, "r-" + lab, lab,
                                                 "TRANSPLANT", 40).answers]
    assert ha.d5_lineage_shortcut({"L07": outs("L07"), "L31": outs("L31")}) == []
    assert ha.d5_lineage_shortcut({lab: outs(lab) for lab in ha.RELABELS})


def test_adjudication_refuses_outside_verdicts_and_unbound_inputs():
    a = ha.run_adjudication_fixtures()
    assert a["A0_clean_path"]["ok"]
    for k in ("A1_rows_edited_after_commit", "A2_analysis_code_swapped", "A3_verdict_supplied_by_a_model"):
        assert a[k]["fired"], k
