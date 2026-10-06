"""Runtimes: pure functions (input_checkpoint, spec) -> (trace, output_checkpoint). CONTRACT s2.

synthetic.v1 is deterministic CPU busy-work: no organisms, no world, no science (Lane C)."""

SYNTHETIC_V1 = {"name": "moonshot.synthetic", "version": 1}


def run_synthetic_v1(input_checkpoint: bytes, spec: dict):
    raise NotImplementedError("C-008-T001")


REGISTRY = {}


def lookup(runtime: dict):
    raise NotImplementedError("C-008-T001")
