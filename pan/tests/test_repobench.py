"""Controls for the PAN-34 instrument's pure parts (no models, no database, no repository runs).

POSITIVE  A1 exclusion flags real imports and host/path strings; the function finder keeps
          3..60-line bodies with decorators in range; the original function round-trips
          through extract + splice byte-identically
NEGATIVE  `.keys()` and an unrelated word do NOT trip the exclusion (the defect A1 fixed);
          a block that does not define the target name is rejected
CHEAT     the prompt never contains the hidden body; relative imports resolve to the
          test's own package, not to a same-named module elsewhere
"""
import textwrap

from pan import repobench as rb

MOD = textwrap.dedent('''\
    import math


    def short(x):
        return x


    @staticmethod
    def scaled(values, k=2):
        """Multiply every value by k."""
        out = []
        for v in values:
            out.append(v * k)
        return out


    def __dunder__(self):
        a = 1
        b = 2
        return a + b
    ''')


def test_positive_violation_rule():
    assert rb.violation("import requests\n") == "import requests"
    assert rb.violation("from psycopg2.extras import execute_values\n") == "import psycopg2"
    assert rb.violation("from urllib import request\n") == "import urllib.request"
    assert rb.violation("import keys\n") == "import keys"
    assert rb.violation("x = get_key('a')\n") == "get_key"
    assert rb.violation("p = 'D:/Prometheus/x'\n") == "D:/"
    assert rb.violation("host = os.environ['EW_DB_HOST']\n") == "EW_DB_HOST"


def test_negative_keys_method_is_fine():
    assert rb.violation("d = {}\nfor k in d.keys():\n    pass\nmonkeys = 3\n") is None
    assert rb.violation("import json\nfrom collections import Counter\n") is None


def test_functions_and_round_trip(tmp_path):
    fns = {f[0]: f for f in rb.functions(MOD)}
    assert set(fns) == {"scaled"}                          # short: 1 body line; dunder skipped
    name, start, end, b0, ind = fns["scaled"]
    t = dict(name=name, start=start, end=end, body_start=b0, indent=ind, module="m.py")
    assert MOD.splitlines()[start - 1] == "@staticmethod"
    src = rb.function_source(MOD, t)
    code, err = rb.extract("```python\n" + src + "```", name)
    assert err is None
    (tmp_path / "m.py").write_text(MOD, encoding="utf-8")
    restore = rb.spliced(tmp_path, t, code)
    assert (tmp_path / "m.py").read_text(encoding="utf-8") == MOD     # original through the path = identical
    restore()
    restore = rb.spliced(tmp_path, t, "def scaled(values, k=2):\n    return [v * k for v in values]\n")
    assert "out.append" not in (tmp_path / "m.py").read_text(encoding="utf-8")
    restore()
    assert (tmp_path / "m.py").read_text(encoding="utf-8") == MOD


def test_negative_block_without_target():
    code, err = rb.extract("```python\ndef other():\n    return 1\n```", "scaled")
    assert code is None and "does not define" in err
    code, err = rb.extract("```python\ndef scaled(:\n```", "scaled")
    assert code is None and "syntax" in err


def test_cheat_prompt_hides_the_body():
    name, start, end, b0, ind = rb.functions(MOD)[0]
    t = dict(name=name, start=start, end=end, body_start=b0, indent=ind)
    p = rb.prompt_for(MOD, t)
    assert "out.append" not in p and "for v in values" not in p
    assert '"""Multiply every value by k."""' in p and "    ..." in p
    assert "Write the complete function `scaled`" in p


def test_cheat_relative_imports_resolve_locally():
    files = {"a/pkg/mod.py", "a/pkg/test_mod.py", "b/pkg/mod.py", "a/util.py"}
    src = "from .mod import f\nfrom ..util import g\nimport b.pkg.mod\n"
    got = rb.imported_modules("a/pkg/test_mod.py", src, files)
    assert got == {"a/pkg/mod.py", "a/util.py", "b/pkg/mod.py"}
    assert "a/pkg/test_mod.py" not in got


def test_credential_paths_never_materialized():
    for p in ("keys.py", "roles/X/api_key.json", "a/secrets/x.py", "a/.env", "creds/credentials.json"):
        assert rb.CRED_RE.search(p), p
    for p in ("pan/search.py", "archaeon/engine/kernel.py"):
        assert not rb.CRED_RE.search(p), p


def test_first_param_for_cheat2():
    assert rb.first_param("def f(a, b=1):\n    return a\n") == "a"
    assert rb.first_param("def f(*args, k=1):\n    return 1\n") == "args"
    assert rb.first_param("def f(*, k):\n    return k\n") == "k"
    assert rb.first_param("def f():\n    return 1\n") is None


def test_a2_exclusions_are_the_pass_body_passers():
    ex = rb.excluded()
    assert len(ex) == 18 and "RB-119" in ex


def test_shapes_and_mcnemar():
    assert rb.shape(True, "", "x") == "pass"
    assert rb.shape(False, "TRUNCATED at 1024 tokens; block does not define f at top level", "") == "empty response"
    assert rb.shape(False, "block does not define f at top level", "code") == "no definition"
    assert rb.shape(False, "TRUNCATED at 1024 tokens; syntax error in block: x", "code") == "syntax error"
    assert rb.shape(False, "1 failed, 2 passed in 0.3s", "code") == "test failed"
    assert rb.mcnemar_p(0, 0) == 1.0
    assert abs(rb.mcnemar_p(0, 6) - 2 / 64) < 1e-12        # all six discordant one way: p = 2 * 0.5**6
    assert rb.mcnemar_p(5, 5) == 1.0


def test_precommitment_scoring():
    he = {"ollama:gpt-oss:20b@nothink1024": 0.853, "ollama:qwen2.5-coder:14b@nothink1024": 0.853,
          "ollama:gemma3:12b@nothink1024": 0.773, "ollama:qwen3:8b@nothink1024": 0.779,
          "ollama:gpt-oss:20b@nothink4096": 0.908}
    an = {"configs": {"ollama:gpt-oss:20b@nothink1024": {"pass_at_1": 0.148},
                      "ollama:qwen2.5-coder:14b@nothink1024": {"pass_at_1": 0.415},
                      "ollama:gemma3:12b@nothink1024": {"pass_at_1": 0.246}}}
    pc = rb.precommitments(an, he)
    assert pc["P1"]["status"] == "PENDING" and not pc["P1"]["lost_on"]
    assert pc["P2"]["status"] == "LOST"                    # gemma3 > gpt-oss@1024
    assert pc["P3"]["status"] == "PENDING"
    an["configs"]["ollama:gemma3:12b@nothink1024"]["pass_at_1"] = 0.70    # within 0.15 of 0.773
    assert rb.precommitments(an, he)["P1"]["status"] == "LOST"


def test_size_arm_scoring_outside_family():
    he = {}
    an = {"configs": {"ollama:qwen2.5-coder:14b@nothink1024": {"pass_at_1": 0.415},
                      "ollama:qwen2.5-coder:32b@nothink1024": {"pass_at_1": 0.52}},
          "size_arm": {"only_big": 20, "only_small": 5, "p": rb.mcnemar_p(20, 5)}}
    assert rb.precommitments(an, he)["P4"]["status"] == "HOLDS"
    an["size_arm"] = {"only_big": 12, "only_small": 5, "p": rb.mcnemar_p(12, 5)}     # gain ok, p >= 0.05
    assert rb.precommitments(an, he)["P4"]["status"] == "LOST"
    assert "ollama:qwen2.5-coder:32b@nothink1024" not in rb.FAMILY
