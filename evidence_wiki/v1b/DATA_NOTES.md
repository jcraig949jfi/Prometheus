# Mnemosyne data-availability notes on V1-B proposals (post-scoring)

These notes do NOT alter any scored checklist cell; they are data-steward
annotations for anyone who executes a proposal.

## T5_control.md — stale table reference
The spec sources unfolded first-zero heights from `zeros.dirichlet_zeros`
"(184,830 rows)". That count is the 2026-04-16 state. As of the 2026-09-01
world-state survey, `prometheus_fire.zeros.dirichlet_zeros` is EMPTY (0
rows); the data survives verbatim in
`prometheus_fire.charon_duckdb.dirichlet_zeros` (184,830 rows). Executors
should repoint the query (same columns) — and note the emptying of
`zeros.dirichlet_zeros` remains an undocumented open question in
`mnemosyne/STATE.md`; this proposal is its first would-be consumer.

## T7_{control,wiki}.md — confirmed availability
Omega/Tamagawa are correctly treated as absent from the mirror (they are);
`bsd_joined` and `lfunc_lfunctions.leading_term` exist as cited.

## General
Any executed proposal should preflight its named tables against live counts
(`reltuples` or COUNT(*), never `n_live_tup` — known-stale stats trap).
