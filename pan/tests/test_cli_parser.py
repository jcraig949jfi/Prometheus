"""The CLI parser must carry every attribute its dispatch reads. Regression: c22bf02f4 inserted subparsers between
atlas's `what` and its `--force`, so `--force` attached to another parser and `pan atlas snapshot` raised
AttributeError until 2026-10-11 ~10:55Z."""
import re
from pathlib import Path

from pan.__main__ import build_parser

SRC = (Path(__file__).resolve().parents[1] / "__main__.py").read_text(encoding="utf-8")


def _dispatch_attrs():
    """{cmd: {attributes read as a.<name> inside its `elif a.cmd == "<cmd>"` branch}}."""
    out = {}
    body = SRC.split("def main(argv=None):", 1)[1]
    parts = re.split(r'\n    (?:el)?if a\.cmd == "([a-z-]+)":', body)
    for cmd, block in zip(parts[1::2], parts[2::2]):
        out[cmd] = set(re.findall(r"\ba\.([a-z_]+)", block)) - {"cmd"}
    return out


def test_every_dispatched_attribute_exists_on_its_subparser():
    ap = build_parser()
    sub = next(a for a in ap._actions if a.dest == "cmd")
    missing = {}
    for cmd, attrs in _dispatch_attrs().items():
        sp = sub.choices.get(cmd)
        assert sp is not None, cmd
        dests = {a.dest for a in sp._actions}
        gone = attrs - dests
        if gone:
            missing[cmd] = sorted(gone)
    assert not missing, missing


def test_atlas_snapshot_force_and_lookup_parse():
    a = build_parser().parse_args(["atlas", "snapshot", "--force"])
    assert a.force is True
    a = build_parser().parse_args(["atlas", "lookup", "--table", "blind_spot", "--text", "x", "--limit", "3"])
    assert (a.table, a.text, a.limit) == ("blind_spot", "x", 3)
