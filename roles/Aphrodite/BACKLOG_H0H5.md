# Aphrodite backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-09-17. PROVISIONAL. The schema requires 20 to 60 items;
this file holds 3 because the seat has no charter yet and inventing more
would be fabrication, not a backlog. It is rewritten to the schema on the
day the charter lands (APHRODITE-01).

APHRODITE-01 | Commit the charter verbatim under roles/Aphrodite/prompts/<date>_charter/ with a MANIFEST and rewrite RESPONSIBILITIES.md around it | ENGINE | program | S | operator (the charter itself) | MANIFEST.md verifying under python -m comms.manifest verify; RESPONSIBILITIES.md with a one-sentence contract
APHRODITE-02 | File the 20-60 item backlog in the schema, first five startable today, XL rows naming decision ids | ENGINE | program | S | APHRODITE-01 | this file, rewritten, passing a line-count and column-count check
APHRODITE-03 | Register every standing loop the charter creates in roles/base-role/MONITORS.md, or record that it creates none | ENGINE | program | S | APHRODITE-01 | a MONITORS.md row per loop, or a journal line stating none

Added 2026-09-17 by the RSI commission (still PROVISIONAL; below the floor):

APHRODITE-04 | Preregister and run a replication of X2 (competent-start self-improver; leaky vs honest accounting) with the eligible range computed from step sizes, >= 30 chains, a hidden-vs-visible evaluator arm (DGM) | EXPERIMENT | rsi | M | none | prereg commit before rows; rows + verdicts in one commit
APHRODITE-05 | E3 v2: verifier with out-of-support probes (unseen shapes) and a better-than-chance fallback, so a false admitted rule can cost accuracy | EXPERIMENT | rsi | S | none | prereg + rows; H3c-style negative control passes or fails with CI
APHRODITE-06 | Dream-RSI toy: replay-simulator policy search over a logged search tree; test monotone replay score vs live score and off-support blindness | EXPERIMENT | rsi | M | none | prereg + rows
APHRODITE-07 | ModularRSI toy: scoped per-module vs joint mutation as module interaction density rises | EXPERIMENT | rsi | M | none | prereg + rows
APHRODITE-08 | Ask the operator whether RSI mechanism instruments are the seat's charter (then APHRODITE-01/02) | DECISION | program | XL | operator | charter committed verbatim
