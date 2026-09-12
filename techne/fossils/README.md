# The computational fossil vault

Operator directive 2026-09-12: `roles/Techne/prompts/2026-09-12_fossil_harvest/OPERATOR.md`
(sha256 in the MANIFEST beside it). Techne acquires humanity's runnable computational
machinery, pins its ancestry, makes it run, proves it runs, and hands Nyx the bodies.
**Techne does not decompose the machinery. Nyx performs the chop.**

Nothing here says which functions matter, where an organ boundary is, or what Nyx should
find. The records are context: what humans built each system to do, where it came from, how
to run it, how we know it runs.

## What is tracked, and what is not

Two halves. The DURABLE, cross-machine half is tracked in git under
`techne/fossils/specimens/<specimen_id>/`:

    record.json          the package record (schema: techne/fossils/record.py)
    UPSTREAM_HASHES.txt   sha256 of every upstream file + a tree hash
    recipe.json          exactly how the body was built and run
    receipts/            one run receipt per attempt (append-only)
    harness/             Techne's minimal smoke inputs (a CNF, a SQL script, ...)
    patches/, environment/, NOTES.md  as needed

The BODIES are host-local and gitignored, under the vault root (default
`<canonical checkout>/vault/fossils/<specimen_id>/`, overridable by `$TECHNE_FOSSIL_VAULT`
or `techne/config.local.json` "fossil_vault"):

    upstream/            the immutable fetched artefact(s) + extracted tree -- NEVER edited
    build/, run/         build products and receipted run inputs/outputs (disposable)
    recovered/           any disassembly/decompilation, labelled RECOVERED REPRESENTATION

A tree hash in the record lets any machine re-fetch and confirm it has the same bytes.
Bodies are not committed (they are large and, for some, redistribution is limited); the
record says where they are and what they hash to.

## Tools

    python -m techne.fossils.harvest acquire <id>   # fetch per record.source_origin, extract, hash
    python -m techne.fossils.harvest run <id>        # execute recipe.json -> a receipt
    python -m techne.fossils.harvest verify <id>     # re-hash the body against the record
    python -m techne.fossils.harvest status          # one line per specimen
    python -m techne.fossils.harvest summary         # the directive's success measures

Records are authored in batches: `python -m techne.fossils.batches.batch01` writes the
records, `...batch01_recipes` writes the recipes and harnesses.

## Run classifications (record.py)

RUNNABLE_NATIVE / RUNNABLE_CONTAINER / RUNNABLE_VM / RUNNABLE_EMULATED / BUILDS_BUT_NOT_RUN /
SOURCE_ONLY / BINARY_ONLY / BLOCKED_DEPENDENCY / BLOCKED_PLATFORM / BROKEN_UPSTREAM /
LEGAL_RESTRICTION / NOT_ATTEMPTED. Test: UPSTREAM_TESTS_PASS/FAIL,
UPSTREAM_DRIVERS_RUN_NO_ORACLE (the shipped tests ran but no reference output exists here to
grade them), TECHNE_SMOKE_HARNESS_PASS/FAIL, NO_TESTS.

## Preserved worlds

Old software wants old worlds. `techne/fossils/environment/fossil-c-toolchain.Dockerfile`
is a Debian 12 image (gcc 12, gfortran 12, bison 3.8, flex 2.6) for yacc-era C. Where a
specimen needs an even older compiler (MiniSat 2.2.0's 2010 C++ is rejected by gcc 13) the
recipe names a pinned image (`gcc:4.9`) rather than rewriting the source. A compatibility
choice is recorded in the recipe's notes; the algorithm is never modernised.

## Batch 01 (2026-09-12): 13 specimens, 13 lineages, 5 decades

    linpackd-netlib-1979       Fortran 77   dense linear solve + the LINPACK MFLOPS benchmark
    minpack-netlib-1980        Fortran 77   Levenberg-Marquardt / Powell hybrid nonlinear solvers
    clips-6.4.2-nasa           C            NASA production-rule expert-system shell (Rete)
    minisat-2.2.0              C++          the reference CDCL SAT solver (built in gcc:4.9)
    spin-6.5.2-holzmann        C+yacc       explicit-state model checker (Promela)
    graphplan-blum-furst-1995  C            STRIPS planning via planning graphs
    tscp-1.81-kerrigan-1997    C            didactic alpha-beta chess engine
    ldpc-codes-neal-2001       C            belief-propagation error-correcting codes
    sqlite-3.49.1-amalgamation C            embedded ACID SQL database (VDBE, B-tree, planner)
    ncompress-5.0-lzw-1985     C            the Unix compress(1) LZW lineage
    tinyscheme-1.42            C+Scheme     a small embeddable Scheme interpreter (GC, call/cc)
    c-cmaes-hansen             C            Hansen's reference CMA-ES evolution strategy
    go-explore-uber-2022       Python 3     archive-based hard-exploration RL (source pin for Nyx)

12 of 13 carry an executable receipt (go-explore is SOURCE_ONLY by Nyx's request -- a
source-at-pinned-revision pin with the blocking dependency named, no environment built).
The handoff for Nyx is `roles/Techne/FOSSIL_HANDOFF_NYX_2026-09-12.md` and each record's
`nyx_handoff` block.
