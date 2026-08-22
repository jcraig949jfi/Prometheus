"""Offline tests for prometheus_llm. No network, no keys required.

Run:  python -m unittest discover -s prometheus_llm/tests -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from prometheus_llm import client, extract_json, parse_target  # noqa: E402
from prometheus_llm.registry import get_spec  # noqa: E402
from prometheus_llm.types import Completion  # noqa: E402


class TestParseTarget(unittest.TestCase):
    def test_provider_only(self):
        self.assertEqual(parse_target("groq"), ("groq", ""))

    def test_model_id_containing_slashes(self):
        # the reason the separator is ":" and not "/"
        self.assertEqual(parse_target("openrouter:stealth/ox-alpha"),
                         ("openrouter", "stealth/ox-alpha"))

    def test_case_and_whitespace(self):
        self.assertEqual(parse_target("  OpenRouter : gpt-x "),
                         ("openrouter", "gpt-x"))


class TestRegistry(unittest.TestCase):
    def test_unknown_provider_raises(self):
        with self.assertRaises(ValueError):
            get_spec("nope")

    def test_ollama_needs_no_key(self):
        self.assertFalse(get_spec("ollama").requires_key)

    def test_openrouter_defaults(self):
        s = get_spec("openrouter")
        self.assertEqual(s.kind, "openai")
        self.assertEqual(s.default_model, "stealth/ox-alpha")


class TestExtractJson(unittest.TestCase):
    def test_bare(self):
        self.assertEqual(extract_json('{"a": 1}'), {"a": 1})

    def test_fenced_with_lang(self):
        self.assertEqual(extract_json('```json\n{"a": 1}\n```'), {"a": 1})

    def test_fenced_without_lang(self):
        self.assertEqual(extract_json('```\n{"a": 1}\n```'), {"a": 1})

    def test_embedded_in_prose(self):
        t = 'Sure! Here you go:\n{"a": [1, 2]}\nHope that helps.'
        self.assertEqual(extract_json(t), {"a": [1, 2]})

    def test_nested_braces(self):
        self.assertEqual(extract_json('x {"a": {"b": {"c": 3}}} y'),
                         {"a": {"b": {"c": 3}}})

    def test_brace_inside_string_does_not_close_early(self):
        self.assertEqual(extract_json('{"a": "} not the end {", "b": 2}'),
                         {"a": "} not the end {", "b": 2})

    def test_escaped_quote_inside_string(self):
        self.assertEqual(extract_json(r'{"a": "he said \"hi\" }"}'),
                         {"a": 'he said "hi" }'})

    def test_top_level_array(self):
        self.assertEqual(extract_json("noise [1, 2, 3] noise"), [1, 2, 3])

    def test_garbage_returns_none(self):
        self.assertIsNone(extract_json("no json here at all"))

    def test_empty_returns_none(self):
        self.assertIsNone(extract_json(""))


class TestCompletion(unittest.TestCase):
    def test_truthiness(self):
        self.assertTrue(Completion(ok=True, text="hi"))
        self.assertFalse(Completion(ok=False))

    def test_empty_content_summary_names_the_cause(self):
        c = Completion(ok=False, empty_content=True, finish_reason="length",
                       reasoning="x" * 50, provider="p", model="m")
        s = c.summary()
        self.assertIn("EMPTY_CONTENT", s)
        self.assertIn("raise max_tokens", s)

    def test_to_dict_drops_raw_by_default(self):
        c = Completion(ok=True, raw={"big": "payload"})
        self.assertNotIn("raw", c.to_dict())
        self.assertIn("raw", c.to_dict(include_raw=True))


class _Stub:
    """Scripted adapter: returns queued Completions, records token budgets."""

    def __init__(self, *results):
        self.results = list(results)
        self.budgets = []
        self.calls = 0

    def __call__(self, spec, model, msgs, max_tokens, temperature, timeout, extra):
        self.calls += 1
        self.budgets.append(max_tokens)
        r = self.results.pop(0) if self.results else Completion(ok=False,
                                                               error="exhausted")
        r.provider, r.model = spec.name, model
        return r


class TestCompleteBehaviour(unittest.TestCase):
    def setUp(self):
        self._saved = dict(client._ADAPTERS)

    def tearDown(self):
        client._ADAPTERS.clear()
        client._ADAPTERS.update(self._saved)

    def _install(self, stub):
        for k in list(client._ADAPTERS):
            client._ADAPTERS[k] = stub

    def test_success_passthrough(self):
        self._install(_Stub(Completion(ok=True, text="hello")))
        r = client.complete("hi", target="openrouter")
        self.assertTrue(r.ok)
        self.assertEqual(r.text, "hello")

    def test_http_200_with_empty_content_is_not_ok(self):
        # the ox-alpha trap: 200 + tokens burned + nothing to use
        self._install(_Stub(Completion(ok=False, empty_content=True,
                                       finish_reason="stop", status=200)))
        r = client.complete("hi", target="openrouter", retries=0,
                            auto_expand=False)
        self.assertFalse(r.ok)
        self.assertTrue(r.empty_content)

    def test_auto_expand_widens_budget_then_succeeds(self):
        stub = _Stub(
            Completion(ok=False, empty_content=True, finish_reason="length",
                       status=200),
            Completion(ok=True, text="PONG"),
        )
        self._install(stub)
        r = client.complete("hi", target="openrouter", max_tokens=100,
                            retries=3)
        self.assertTrue(r.ok)
        self.assertEqual(stub.budgets, [100, 400])  # 4x widening

    def test_auto_expand_disabled_does_not_widen(self):
        stub = _Stub(
            Completion(ok=False, empty_content=True, finish_reason="length",
                       status=200),
            Completion(ok=True, text="PONG"),
        )
        self._install(stub)
        r = client.complete("hi", target="openrouter", max_tokens=100,
                            retries=0, auto_expand=False)
        self.assertFalse(r.ok)
        self.assertEqual(stub.budgets, [100])

    def test_fallback_moves_to_next_target(self):
        stub = _Stub(
            Completion(ok=False, status=402, error="Insufficient Balance"),
            Completion(ok=True, text="from backup"),
        )
        self._install(stub)
        r = client.complete("hi", target="deepseek", fallback=["openrouter"],
                            retries=0)
        self.assertTrue(r.ok)
        self.assertEqual(r.text, "from backup")
        self.assertEqual(r.provider, "openrouter")

    def test_unknown_provider_in_chain_is_survivable(self):
        self._install(_Stub(Completion(ok=True, text="ok")))
        r = client.complete("hi", target="bogus", fallback=["openrouter"],
                            retries=0)
        self.assertTrue(r.ok)

    def test_all_targets_failing_returns_last_failure(self):
        self._install(_Stub(Completion(ok=False, status=402, error="a"),
                            Completion(ok=False, status=401, error="b")))
        r = client.complete("hi", target="deepseek", fallback=["openrouter"],
                            retries=0)
        self.assertFalse(r.ok)
        self.assertEqual(r.status, 401)

    def test_require_raises_on_failure(self):
        self._install(_Stub(Completion(ok=False, status=500, error="boom")))
        with self.assertRaises(client.LLMError):
            client.complete("hi", target="openrouter", retries=0, require=True)

    def test_council_returns_every_target_including_failures(self):
        self._install(_Stub(Completion(ok=True, text="1"),
                            Completion(ok=False, status=402, error="dead"),
                            Completion(ok=True, text="3")))
        out = client.council("q", ["openrouter", "deepseek", "gemini"],
                             retries=0)
        self.assertEqual(list(out), ["openrouter", "deepseek", "gemini"])
        self.assertEqual(sum(1 for c in out.values() if c.ok), 2)


class TestMessageShaping(unittest.TestCase):
    def test_system_prepended(self):
        m = client._messages("u", system="s")
        self.assertEqual([x["role"] for x in m], ["system", "user"])

    def test_explicit_messages_win(self):
        given = [{"role": "user", "content": "x"}]
        self.assertEqual(client._messages("ignored", "ignored", given), given)


class TestListModelsAuthHeaders(unittest.TestCase):
    """Discovery must use each provider's own auth header.

    Regression: list_models() sent `Authorization: Bearer` to Anthropic, which
    always 401s even for a valid key. Because the anthropic spec has no
    default_model, health() resolved through discovery and reported the
    provider DEAD with "key invalid or revoked" -- a header bug misread as a
    credential fact.
    """

    def setUp(self):
        self._real_get = client.requests.get
        self.seen = {}

        class _Resp:
            status_code = 200
            def raise_for_status(self): pass
            def json(self): return {"data": [{"id": "m1"}]}

        def _fake_get(url, headers=None, timeout=None):
            self.seen["url"] = url
            self.seen["headers"] = headers or {}
            return _Resp()

        client.requests.get = _fake_get
        self._saved_key = client._key_for
        client._key_for = lambda spec: "TESTKEY"

    def tearDown(self):
        client.requests.get = self._real_get
        client._key_for = self._saved_key

    def test_anthropic_uses_x_api_key_not_bearer(self):
        client.list_models("anthropic")
        h = self.seen["headers"]
        self.assertEqual(h.get("x-api-key"), "TESTKEY")
        self.assertIn("anthropic-version", h)
        self.assertNotIn("Authorization", h)

    def test_openai_compatible_still_uses_bearer(self):
        client.list_models("groq")
        h = self.seen["headers"]
        self.assertEqual(h.get("Authorization"), "Bearer TESTKEY")
        self.assertNotIn("x-api-key", h)


if __name__ == "__main__":
    unittest.main(verbosity=2)
