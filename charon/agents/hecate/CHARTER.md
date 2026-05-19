# Hecate Charter — continuous gradient archaeology

## Role

One tick = re-run gradient archaeology over the growing kill ledger,
compute MI(`kill_pattern`, operator-class) with a permutation-null
baseline, identify the largest kill_pattern clusters, emit a
`gradient_archaeology_run` artifact. Turns the one-shot 0.725-bit MI
result (README §thesis) into a continuous health-and-emergence signal.

## Inputs

Native: scans `theseus/corpus/*.jsonl.gz` (Theseus's TheseusRecord
emissions are the substrate's primary kill source — each record carries
`kill_pattern`, `kill_vector`, `generator_id` which is the operator-class
proxy). Falls back to other detected kill-ledger locations if Theseus's
corpus is absent (see daemon.py `LEDGER_CANDIDATES`).

## Outputs (per tick)

- `gradient_archaeology_<utc>.md` under `artifacts/` containing:
  - ledger size
  - top kill_pattern frequencies
  - top generator_id frequencies
  - MI(kill_pattern, generator_id) observed
  - MI permutation-null baseline (N=200 shuffles by default)
  - mi_z score (drift indicator)
  - top kill-pattern clusters (≥N members) — candidate primitive_proposals
  - alarm flags if mi_z drops below threshold

## Anti-capture safeguard

Publishes null-permuted MI alongside observed MI every tick. If
`mi_z < 2.0` for ≥7 consecutive ticks, raises a SELF_AUDIT_ALARM —
either the signal is decaying or the operator_class taxonomy has gone
stale and needs Aporia/Techne attention.

## Cron slot

Nightly (02:00 local) — low priority; runs when no other agent is
firing. Hecate's analysis cost scales with ledger size; cache prior
analysis to incrementalize.

## Dependencies

numpy, sklearn (or scipy fallback) for MI computation. All already in
the project per the README's reqs.
