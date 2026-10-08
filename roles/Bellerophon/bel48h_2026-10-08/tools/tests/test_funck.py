import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
from funck import functional
from prometheus.z80atlas import vm
from prometheus.z80atlas.world import Config


def test_funck_controls_from_review_b():
    copy = Config(reproduction="ENDOGENOUS_COPY", physics="v2"); part = Config(reproduction="ENDOGENOUS_PARTIAL", physics="v2")
    assert functional(vm.replicator(64), copy)["FUNCTIONAL"]
    assert functional(bytes.fromhex("07000840030815ff") + bytes([0xAA]) * 56, part)["FUNCTIONAL"]       # FN1b prefix replicator
    assert not functional(bytes.fromhex("0840079015ff"), copy)["FUNCTIONAL"]                            # FP1 zero sprayer
    assert not functional(bytes.fromhex("0101084011ff"), part)["FUNCTIONAL"]                            # ONE_BYTE
