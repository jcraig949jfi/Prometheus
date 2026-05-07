"""Inference-time wrappers for the Ergon Learner.

Lives outside the model-weights / training surface. Wrappers here adjust
prompt protocol, decoding parameters, or post-processing — never the
model itself.
"""
