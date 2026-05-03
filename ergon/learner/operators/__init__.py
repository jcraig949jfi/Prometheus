"""Mutation operator classes for the Ergon learner.

Per pivot/ergon_learner_proposal_v8.md:

- structural: Add/remove/swap nodes; rewire edges within type discipline
- symbolic: Bump arg values within type
- anti_prior: Anti-correlated with corpus frequency stats; KL >=1.0 nat per claim;
              descriptor-displacement requirement
- uniform: Resample atoms uniformly (strawman null)
- structured_null: Per-type sampler with uniform per-arg distributions

Plus deferred (v0.5+):
- neural: LoRA-fine-tuned policy mutation
- external_llm: Frontier LLM API mutation

Minimum-share enforcement at scheduler level: uniform >=5%, anti_prior >=5%,
structured_null >=5%; total non-prior-shaped >=15%.
"""
