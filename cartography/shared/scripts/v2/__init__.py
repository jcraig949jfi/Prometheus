# Charon v2 — Depth Layer
# Phase 2 of the Prometheus cross-domain discovery pipeline.
#
# v1 (flat scripts): Scalar invariants, concept bridges, shadow tensor.
#   Result: scalar layer empty after prime detrending.
#
# v2 (this package): Polynomial coefficients, formula semantics, depth probes.
#   Target: sequence-to-sequence bridges immune to prime pollution.
#
# Structure:
#   v2/extractors/  — Extract depth features from existing data
#   v2/probes/      — Cross-dataset depth tests
#   v2/tensors/     — Detrended and depth tensor construction
#
# v1 scripts remain in parent directory and continue running.
# v2 imports from v1 via sys.path (search_engine, concept_index, etc.)
