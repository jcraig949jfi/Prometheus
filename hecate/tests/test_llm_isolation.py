"""AUDIT_X: the isolated call's temp cwd is visible to the model in its
environment block, so its name must not carry role or experiment words."""
from hecate import llm

BANNED = ("hecate", "prometheus", "alien", "meta", "gravity", "autopsy", "aporia")


def test_iso_prefix_is_neutral():
    assert not any(w in llm.ISO_PREFIX.lower() for w in BANNED)


def test_wrapper_uses_the_neutral_prefix():
    src = open(llm.__file__, encoding="utf-8").read()
    assert 'prefix="hecate' not in src and "prefix=ISO_PREFIX" in src
