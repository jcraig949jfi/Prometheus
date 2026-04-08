@echo off
title T6-SHADOW-VOIDS
cd /d F:\Prometheus\cartography\shared\scripts
:loop
python research_cycle.py --tag T6 --provider deepseek --hypotheses 5 --loop 100 --tensor-review-every 20 --topic "Target the shadow tensor hot cells. Genus2-Lattices has bond_dim=1 sv=287 and ZERO tests - explore it. Do genus-2 conductors correlate with lattice determinants or kissing numbers? Test Maass-mathlib verb bridges (laplacian, level, zeta). Probe NumberFields-Polytopes (best_p=0.0065). Explore Isogenies-KnotInfo (z=19.5 needs size-bias check). These are the gravitational wells in our dark matter map."
goto loop
