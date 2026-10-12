"""PAN-42: the REFUSE pattern for credential-shaped files (read from migration 014, as applied). No database."""
import re

from pan import PKG


def _pattern(rule_id):
    sql = (PKG / "migrations" / "014_access.sql").read_text(encoding="utf-8")
    m = re.search(r"\('" + re.escape(rule_id) + r"',\s*'((?:[^']|'')*)'", sql)
    return re.compile(m.group(1).replace("''", "'"), re.I)


def test_credential_files_are_refused_and_code_about_keys_is_not():
    rx = _pattern("R-credential-file")
    for p in (".env", "a/b/.env.local", "config/prod.env", "D:/Prometheus/api_keys.txt", "x/secrets.yaml",
              "creds/credentials", "gcp/credentials.json", "certs/server.pem", "home/.ssh/id_rsa", "id_ed25519.pub"):
        assert rx.search(p), p
    for p in ("pan/keys.py", "agents/eos/tests/test_credential_boundary.py", "cartography/oeis_keyword.txt",
              "proteus/eval/keyed_memory_witness.py", "docs/secret_hitler.md", "Aether/runpod/credentials.py"):
        assert not rx.search(p), p


def test_burned_holdout_rule_matches_only_the_declared_exposed_sets():
    rx = _pattern("C-cosmos-burned-holdout")
    assert rx.search("prometheus/cosmos/holdout/sealed_spec_F.json")
    assert rx.search("prometheus/cosmos/c3_holdout_D/sealed_spec_D.json")
    assert not rx.search("prometheus/cosmos/c3_holdout_D2/MANIFEST_D2.json")
    assert not rx.search("prometheus/cosmos/c3_holdout_D2/FIREWALL.md")
