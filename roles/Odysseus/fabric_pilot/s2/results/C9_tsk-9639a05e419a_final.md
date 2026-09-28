Claim C9 is confirmed at commit 59b94b4ed: Atlas does not index envgate, envgate2 or z80atlas, and there is no lens field anywhere in `atlas/`.

- **Where the claim comes from:** it is in `roles/Artemis/selftest/runs/R-34/REPORT.md:36-38` and again at `:114-115`.
- **The Archaeon harvester skips these directories:** `atlas/harvest/archaeon_campaigns.py:59` only picks up paths that match `archaeon/(campaign\d+)/`. So `archaeon/envgate/`, `archaeon/envgate2/` and `archaeon/z80atlas/{census,denovo}/` are left out, even though all four have `PREREG.json` files.
- **No other harvester picks them up either:**
  - A case-insensitive search for `envgate|z80atlas` across all of `atlas/`, including `atlas/registry.json`, finds nothing.
  - The Nestor harvester only covers graphworld and cw01 (`atlas/harvest/npe.py:28-31`), so Nestor's `z80atlas-*` campaigns are not indexed.
  - None of the registry's local roots point at these directories (`atlas/registry.json:273-408`).
  - The commits harvester only counts how many paths each commit touches (`atlas/harvest/commits.py:37`); it doesn't link them to experiments.
  - The `roles/Atlas` input files contain neither name. The Z80 entry in `roles/Atlas/catalog/ECOSYSTEMS.jsonl:78` is an outside Z80 paper, not Prometheus's z80atlas.
- **No lens field:** searching `atlas/` for `lens`, `varied` or `held_substrate` finds nothing. The `OBSERVED` matches are labels on facts, not a lens field.

One limit: I judged "not indexed" from the harvester code and registry. I couldn't look at the live Atlas database.

The verdict is in `out/verdict.json`.

VERDICT: CONFIRMED