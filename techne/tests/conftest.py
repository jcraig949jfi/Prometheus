"""techne/tests configuration.

`slow` marker (TECHNE-21, 2026-09-12). Measured on 2026-09-12: techne/tests runs in ~760 s,
of which THREE tests in test_mahler_batch.py own 720 s (249 + 236 + 235 s; the next slowest
test in the whole directory is 7.56 s). They are marked slow so the directory gives a fast
regression signal:

    python -m pytest techne/tests -q -m "not slow"     # ~45 s
    python -m pytest techne/tests -q                   # everything, ~13 min

Marking does not skip: an unmarked run still executes them. The three are authority and
composition tests over the full Mossinghoff corpus (8,625 polynomials despite the "178" in
one test's name -- TECHNE-20 owns that population question); nothing here changes what
they check.
"""


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: takes minutes, not seconds; deselect with -m 'not slow'")
