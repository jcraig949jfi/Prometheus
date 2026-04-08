@echo off
title T7-NEW-DATASETS
cd /d F:\Prometheus\cartography\shared\scripts
:loop
python research_cycle.py --tag T7 --provider deepseek --hypotheses 5 --loop 100 --tensor-review-every 20 --topic "Explore the 5 new datasets nobody has tested. Genus-2 curves (66K): do conductor distributions differ from EC conductors? Maass forms (300): do spectral parameter gaps match OEIS sequences? Lattices (21): do root lattice dimensions predict number field degrees? FindStat (1993 statistics): do statistic IDs correlate with OEIS sequence IDs? OpenAlex (10K concepts): do concept hierarchy levels predict mathlib import depth?"
goto loop
