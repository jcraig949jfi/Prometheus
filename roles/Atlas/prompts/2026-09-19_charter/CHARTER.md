# Atlas charter (operator, 2026-09-19)

The byte-faithful operator text is OPERATOR_CHARTER_verbatim.md in this
directory (it contains typographic apostrophes; this file is the ASCII
reading). Where the two differ, the verbatim file wins.

## One sentence

Atlas shadows every experiment engine in Prometheus (today the SFE and
the NPE; others will emerge) from a scientific perspective, and keeps a
clean, machine-aware, lineage-aware history of the experiments they ran
in a two-tier relational index on M1 Postgres, populated by rerunnable
extraction tools, so the program can comb back for (a) science it
missed, (b) weak signals to follow, (c) reruns with different starting
parameters, world types or organisms.

## The operator's requirements, itemised (reading, not new text)

R1  Shadow the SFE (Serendipity Foundry Engine; runs on M2, has run on
    both) and the NPE (Nestor Primordial Engine; runs on M1) as
    ecosystems, scientifically.
R2  A clean history of the experiments they ran: a detailed manifest
    (tier 1, the master parent index) backed by more detailed structured
    child tables (tier 2).
R3  Postgres on M1 holds the parent index and child tables.
R4  Sources: GitHub content (Archaeon, Nestor, and Harmonia A-F instances
    run experiments, write files and commit them, likely on active
    branches), log files, and for the SFE, PEW.
R5  POINTERS, not copies: do not extract all detailed data from PEW,
    GitHub or trace logs; record where each experiment's data lives.
R6  Campaigns: sequences of experiments are stacked into campaigns; the
    goal is hundreds of experiments in sequence and possibly farms, so
    the MACHINE an experiment ran on is first-class.
R7  Logs are machine-specific: this seat sees one machine first; another
    Atlas instance fills in the other machine. Infer what GitHub allows.
R8  Not just two engines: the model is engine-agnostic.
R9  Lineage: reruns with fixes, adjustments, bug fixes or more telemetry
    are linked to a parent where identifiable.
R10 DO NOT DISTURB the engines or detract from their progress. Shadow,
    collect, classify, organise.
R11 Build TOOLS that extract and surface the data, rerunnable, so later
    passes can recomb for a variable or dataset missed earlier.
