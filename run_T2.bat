@echo off
title T2-ANALYTIC
cd /d F:\Prometheus\cartography\shared\scripts
:loop
python research_cycle.py --tag T2 --provider deepseek --hypotheses 8 --loop 60 --tensor-review-every 25 --topic "Find structural bridges between LMFDB modular form levels, Fungrim formula symbol patterns, and ANTEDB zero-density exponent bounds. Do Maass form spectral parameters correlate with ANTEDB bounds or Fungrim zeta formulas? Do Maass Fricke eigenvalues predict modular form properties? Bridge spectral theory to analytic number theory. Focus on verbs not nouns."
goto loop
