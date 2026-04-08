@echo off
title T8-COLD-CELLS
cd /d F:\Prometheus\cartography\shared\scripts
:loop
python research_cycle.py --tag T8 --provider deepseek --hypotheses 5 --loop 100 --tensor-review-every 20 --topic "Explore cold cells with zero tests. Focus on FindStat pairs: FindStat-OEIS (do combinatorial statistic counts appear in sequences?), FindStat-KnotInfo (do permutation statistics predict knot invariants?), FindStat-LMFDB (do partition statistics match conductor distributions?). Also probe Genus2-Maass (zero tests, both from LMFDB), Lattices-OpenAlex (bond_dim=2 unexplored), and Maass-OpenAlex (spectral theory in academic literature)."
goto loop
