"""Controls for prepost_check. Run: python -m pytest -q programs/selective_irreversibility/probes"""
import importlib.util, os
spec = importlib.util.spec_from_file_location("pc", os.path.join(os.path.dirname(__file__), "prepost_check.py"))
pc = importlib.util.module_from_spec(spec); spec.loader.exec_module(pc)

# The body of the real incident message #585 (first line + the "blind" sentence).
INCIDENT = ("Cyclops (M2 steward, Selective Irreversibility directive) -> Archaeon, Bellerophon\n"
            "Directive: roles/Cyclops/prompts/2026-09-25_selective_irreversibility/\n"
            "Its rows are currently the cleanest theory-blind evidence on M2 (BLIND_LANES.md).")


def test_positive_control_real_incident_is_refused():
    ok, why = pc.check(["Archaeon", "Bellerophon"], INCIDENT)
    assert not ok and any("Bellerophon" in w for w in why)


def test_cheat_control_operational_label_does_not_launder_program_text():
    ok, _ = pc.check(["Bellerophon"], INCIDENT, program=False)
    assert not ok


def test_broadcast_refused_even_if_clean():
    ok, _ = pc.check(["*"], "routine note")
    assert not ok


def test_negative_control_named_unlisted_recipient_clears():
    ok, why = pc.check(["Aporia", "Ensorain"], INCIDENT)
    assert ok, why


def test_clean_operational_note_to_listed_seat_clears():
    ok, why = pc.check(["Bellerophon"], "ENVGATE-02 overlap started 18:30:33Z; please log it.", program=False)
    assert ok, why


def test_case_insensitive_recipient():
    ok, _ = pc.check(["bellerophon"], "x")
    assert not ok
