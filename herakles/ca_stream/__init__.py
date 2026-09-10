"""ca_stream_v1: streaming wrapper over the radius-3 CA library. H2 alpha.

`herakles.evca` is imported and NOT modified. See `core` for the pinned
update order, reset semantics, declared readout class and fitting budget.
"""
from . import core  # noqa: F401
from .core import (  # noqa: F401
    CaStreamError, N_CELLS, HORIZON, N_STREAMS, INITIAL_STATE,
    RIDGE_LAMBDA, DECISION_THRESHOLD,
    Substrate, CaSubstrate, ShiftRegister, ShiftXorRegister,
    DirectInput, FrozenRandom,
    all_streams, target_delayed_recall, target_temporal_xor, warmup_mask,
    TASKS, partitions, run_streams, fit_readout, score_readout,
    build_targets, catalogue_digest,
)
