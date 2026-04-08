@echo off
title T3-GEOMETRIC
cd /d F:\Prometheus\cartography\shared\scripts
:loop
python research_cycle.py --tag T3 --provider deepseek --hypotheses 8 --loop 60 --tensor-review-every 25 --topic "Cross the geometric divide. Do lattice kissing numbers correlate with polytope f-vectors? Do lattice dimensions predict space group orders? Test E8 and Leech lattice properties against genus-2 curve invariants. Do pi-Base topological properties predict Mizar hub articles? Bridge lattices to crystallography to polytopes."
goto loop
