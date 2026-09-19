"""Atlas harvesters. Each module exposes VERSION and run(args) -> counts.
A harvester reads sources (git objects, files by stat, SELECTs) and writes
only to schema atlas. Bump VERSION whenever what it extracts changes, so a
recomb pass is distinguishable from the pass it revises."""

ORDER = ["reference", "commits", "archaeon_campaigns", "frontier", "npe", "vivarium", "pew", "local_files",
         "frontier_runs_m2",   # Atlas-M2 (host M2): receipts under runs/ -> the same attempt/segment keys
         "catalog",            # Atlas (M1): roles/Atlas/catalog/ECOSYSTEMS.jsonl -> atlas.ecosystem
         "proposals"]          # Atlas (M1): roles/Atlas/proposals/*/EXPERIMENTS.jsonl (kind=proposal, PLANNED)
