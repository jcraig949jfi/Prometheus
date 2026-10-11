"""Controls for the 2026-10-10 catch-up adapters (workgraph, theseus, aether): pure parsing rules only.

Each class/regex gets a case that must FAIL to match or must NOT map to a
favourable class, so a loosened rule cannot pass silently."""
from atlas.harvest import aether, theseus, workgraph


def test_theseus_not_supported_is_never_positive():
    assert theseus.verdict_class("NOT SUPPORTED. The difference is <= 0")[0] == "NEGATIVE"
    assert theseus.verdict_class("H-TASK NOT SUPPORTED")[0] == "NEGATIVE"
    assert theseus.verdict_class("SUPPORTED, on one seed.")[0] == "POSITIVE"
    assert theseus.verdict_class("H-TASK SUPPORTED -- deep descendants")[0] == "POSITIVE"


def test_theseus_bespoke_words_stay_unknown():
    for w in ("RANDOM-BEATS-RECURSION.", "DETECTOR BLIND.", "NO-HELP. Selection", "WALL-AT-v0_1."):
        assert theseus.verdict_class(w) == ("UNKNOWN", "LOW"), w
    assert theseus.verdict_class("VOID by the frozen rule")[0] == "INVALID"
    assert theseus.verdict_class("INDETERMINATE (no preregistered clause met). Not SUPPORTED")[0] == "INCONCLUSIVE"


def test_theseus_verdict_line_mid_sentence_and_header_prereg():
    t = "Runs ...\none-sided Fisher p 3.9e-10. VERDICT: SUPPORTED -- under task selection\n"
    assert theseus.VERDICT_LINE.search(t).group(1).startswith("SUPPORTED")
    assert theseus.VERDICT_LINE.search("no verdict word here: SUPPORTED") is None
    m = theseus.PREREG_REF.search("# THESEUS-27 verdict (prereg roles/Theseus/prereg/2026-10-08_structure_selection/, 0b8e3740b)")
    assert m.groups() == ("2026-10-08_structure_selection", "0b8e3740b")
    assert theseus.PREREG_REF.search("# THESEUS-40 verdict: third seed for 36/37") is None


def test_theseus_verdict_table_rows_only_under_a_verdict_header():
    t = ("| a | b | verdict |\n|---|---|---|\n| H-SEL | x | SUPPORTED |\n| H-LAW | y | NOT SUPPORTED |\n\n"
         "| a | b | c |\n|---|---|---|\n| H-OTHER | x | SUPPORTED |\n")
    rows = theseus._verdict_table(t)
    assert [(h, w) for h, w, _ in rows] == [("H-SEL", "SUPPORTED"), ("H-LAW", "NOT SUPPORTED")]


def test_aether_tokens():
    assert aether.verdict_class("ROUTING_NO_GAIN")[0] == "NEGATIVE"
    assert aether.verdict_class("OFFER_REPERTOIRE_SUPPORTED") == ("POSITIVE", "MEDIUM")
    assert aether.verdict_class("MULTIGENERATION_WEAK")[0] == "WEAK_POSITIVE"
    assert aether.verdict_class("rcv_add REPLICATED; rcv_str REPLICATED") == ("POSITIVE", "LOW")
    assert aether.verdict_class("MOBILE_BUT_TRIVIAL (extent energy-invariant)") == ("UNKNOWN", "LOW")
    assert aether.verdict_class("HORIZON_DEPENDENT (clause iii only)")[0] == "UNKNOWN"
    m = aether.ATT.match("T-007__A-001__runpod-aether-units-20260927T155823Z.json")
    assert m.group("mode") == "runpod"
    assert aether.ATT.match("RESULT.json") is None


def test_workgraph_paths_and_ids():
    P = workgraph._PATH
    assert P.match("ops/campaigns/C-004/tasks/C-004-T023A/TASK.json").group(2) == "C-004-T023A"
    assert P.match("ops/campaigns/C-004/tasks/C-004-OP1/TASK.json").group(2) == "C-004-OP1"
    assert P.match("ops/campaigns/C-009/tasks/C-009-T030/attempts/A-001/RECEIPT.json").groups() == \
        ("C-009", "C-009-T030", "A-001")
    assert P.match("ops/campaigns/C-009/tasks/C-009-T030/LEASE.json") is None
    assert workgraph._cid("C-004 (INCOMPLETE CLOSURE)") == "C-004"
    assert workgraph._cid("see C-004") is None
    assert workgraph._clean({"c": ["a" + chr(0) + "b"]}) == {"c": ["a<NUL>b"]}
