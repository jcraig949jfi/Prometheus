from hecate.meta.scrub import check, mechanism_text, scrub


def test_names_fields_eponyms_acronyms_novelty_removed():
    t = ("A novel Stochastic Sparse Equilibrium Search (SSES) couples Kalman Filtering "
         "with sparse coding and Hebbian updates from Neuroscience; the Kalman gain "
         "and the SOC regime are new.")
    s = scrub(t)
    assert check(s) == []
    for gone in ("Kalman", "Hebbian", "SSES", "SOC", "novel", "Neuroscience", "Stochastic Sparse"):
        assert gone.lower() not in s.lower(), (gone, s)
    assert "gain" in s and "regime" in s           # content words survive


def test_check_fires_on_unscrubbed_text():
    # cheat control: a check that could not fire would pass unscrubbed text
    assert "Kalman Filtering" in check("uses Kalman Filtering and Topology")
    assert "Biology" in check("borrowed from biology")


def test_plural_and_hyphen_variants():
    s = scrub("error-correcting codes, Phase Transition, cellular-automata, genetic algorithm")
    assert check(s) == []


def test_mechanism_text_is_blind_to_metadata():
    m = {"arm": "T", "unit": 3, "statement": "Topology x Evolution", "what_exists": ["a", "b"]}
    s = mechanism_text(m)
    assert "arm" not in s and "unit" not in s and check(s) == []
