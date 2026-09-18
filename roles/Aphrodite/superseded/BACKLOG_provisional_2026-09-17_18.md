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

Added 2026-09-18 by the library commission (still PROVISIONAL):

APHRODITE-09 | TOY-RSI-1: CPU apparatus calibration for the transplant test -- planted-dividend positive control, memorised-vault cheat control, power simulation for 16/32/64 lineages | EXPERIMENT | rsi | L | APHRODITE-08 (charter) | prereg + detection curve for a planted dividend
APHRODITE-10 | Real small-model p/q test (QUESTIONS G1/G7): measure solve rate p and verifier false-accept q on a formally verifiable family; check M2's precision law | EXPERIMENT | weak-models | M | operator (host: M1/M2 RTX 5060 or RunPod; this seat designs only) | design file under library/designs/
APHRODITE-11 | Read Roesner and Kohno 2609.17817 for archive statistics (QUESTIONS M2): did clean ancestors survive? | RESEARCH | rsi | S | none | a paragraph in sources/ with page references
APHRODITE-12 | Standing news watch for RSI (monitor row, bound, accountable seat) or keep manual NEWS.md passes | DECISION | library | S | operator | MONITORS.md row or a recorded "manual only"
APHRODITE-13 | Distributional gate method for multi-cell prereg (QUESTIONS M1), validated on synthetic data where the model is true and false | METHOD | program | S | none | a tested helper + a note

Added 2026-09-18 after the Gemini Pro / ChatGPT reviews:

APHRODITE-14 | Campaign 0 assay simulator: synthetic lineages with known truth (planted dividend, none, memorised vault, planted module effect, exploiter lineage) through the full factorial + decomposition + hierarchical analysis; power and EQUIVALENCE curves vs lineages/families/instances | EXPERIMENT | rsi | L | APHRODITE-08 or an explicit go for Campaign 0 | prereg + verdict-recovery table (true vs assay verdict) + curves
APHRODITE-15 | delta proposal memo from downstream need (QUESTIONS N1) | METHOD | rsi | S | APHRODITE-14 curves | memo committed before any Campaign 1 data
APHRODITE-16 | I_0 protocol spec (five modules, typed memory store, resource handles, two-phase commit, null task) as a written interface, no implementation | DESIGN | rsi | M | none | spec file under library/designs/

Stopping rule adopted 2026-09-18 (packet feedback; inside the seat's own
lane, so the seat adopts it): the CPU swarm toys are STOPPED. More
analytic cells would not change a program decision. Swarm work
reactivates only when one of the boundary quantities becomes measurable
in a real swarm: false-accept vs solve rate (q vs p), error correlation
(rho), contagion vs verification (R0), exploit advantage vs audit
pressure (g vs a), availability of clean variants (r) or targeted cost
(c). No backlog item extends S1-S4.
APHRODITE-12 re-scoped: bounded news monitor SPEC written
(library/NEWS_MONITOR_SPEC.md); launch awaits the operator.
APHRODITE-14 re-scoped to the five-fixture assay qualification (TOY-RSI-1).
