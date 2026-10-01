# forensics/ : functional-core analysis (read-only, VM calls only)

The report is `FORENSIC_FUNCTIONAL_CORE.md`. Run everything from this directory with `python -B`, so no `__pycache__`
is written into the campaign directories. All scripts run in a single process. None of them runs a world or an
evolution.

| step | command | output | what it does |
|---|---|---|---|
| 1 | `python -B core_map.py` | `core_map.json`, `core_map.log` | sample; competence rescreen; STATE_FREE; knockout map; roles; Q4 source diversity |
| 2 | `python -B reclassify.py` | updates `core_map.json` | side-aware instruction roles (knockouts are not redone) |
| 3 | `python -B ko_rates.py` | updates `core_map.json` | base rate and the knockout rates behind every NECESSARY call; COLLAPSE positions |
| 4 | `python -B minimal_prior.py` | `minimal_prior.json` | Q3: exhaustive 1- and 2-byte programs, sampled 3-byte programs, random genomes, planting |
| 5 | `python -B drift.py` | `drift.json` | Q5: earliest vs latest competent genomes within each run |
| 3b | `python -B slice.py` | updates `core_map.json` | dynamic backward slice of the copy operands; classes of necessary bytes |
| 4b | `python -B plant.py` then `python -B plant_rp.py` | `plant.json`, `plant_rp.json` | the `LD r,n ; E5/E7` family (zero vs random padding); reachability by offset |
| 5b | `python -B drift_slice.py` | `drift_slice.json` | Q5: entry-register dependence of the copy address, early vs late |
| 6 | `python -B summarize.py` | `summary.json` | aggregates for Q1, Q2 and Q4 (run after 1 to 3b) |

Shared modules:
- `fsetup.py` builds the runner and screen exactly as `run_ci._run` does.
- `ivm.py` is the dense VM, built by the same source transform as `run_dc.dense_z8`, plus passive trace and
  byte-origin hooks. Its equivalence to the frozen dense VM is checked by `ivm.equivalence`.

The total CPU is about 55 minutes. The long steps are `core_map.py` (~24 min) and `minimal_prior.py` (~23 min, of which ~16 min is the exhaustive 2-byte set).
`nestor_*.py` files in this folder are not part of this analysis.
