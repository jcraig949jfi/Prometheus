"""Controls for the review-queue smell detector (PAN-37; no database).

POSITIVE  each smell kind planted in code is reported at its line
NEGATIVE  the same patterns inside a docstring or a comment, a URL and a time format are NOT reported
CHEAT     a file that does not parse reports syntax_error only (no crash, no partial guesses);
          the score is zero for code nobody touched in 30 days, whatever its smells
"""
from pan.review import score, smells

PLANTED = '''import subprocess
LAKE = "C:/Prometheus-data/pan/lake"
HOST = "192.168.1.202"


def run(cmd):
    try:
        subprocess.run(cmd, shell=True)
    except:
        pass
    try:
        eval(cmd)
    except Exception:
        pass
'''

CLEAN = '''"""Writes to C:/Prometheus-data and talks to 192.168.1.202 -- in the docstring only."""
# a comment with D:/Prometheus and shell=True
URL = "https://example.org/a:b/c"
FMT = "%H:%M:%S"


def f(x):
    """eval(x) would be wrong; so would a bare except."""
    return x
'''


def test_positive_each_smell_at_its_line():
    s = smells(PLANTED)
    assert s["abs_path"] == [2]
    assert s["lan_ip"] == [3]
    assert s["shell_true"] == [8]
    assert s["bare_except"] == [9]
    assert s["eval_exec"] == [12]
    assert s["except_pass"] == [13]


def test_negative_docstrings_comments_urls_formats():
    assert smells(CLEAN) == {}


def test_long_function():
    body = "def big():\n" + "".join("    x{} = {}\n".format(i, i) for i in range(160)) + "    return 0\n"
    assert smells(body) == {"long_function": [1]}


def test_cheat_unparseable_and_untouched():
    assert smells("def broken(:\n    pass\n") == {"syntax_error": [0]}
    assert score(0, 0, 0, {"abs_path": [1], "bare_except": [2]}) == 0
    assert score(2, 4, 0, {}) == 6.0            # churn 3 x risk 2 (no test imports it)
    assert score(2, 4, 3, {"abs_path": [1]}) == 4.5
