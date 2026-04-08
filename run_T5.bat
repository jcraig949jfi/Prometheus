@echo off
title T5-SLEEPERS
cd /d F:\Prometheus\cartography\shared\scripts
:loop
python research_cycle.py --tag T5 --provider deepseek --hypotheses 5 --loop 100 --tensor-review-every 20 --topic "Hunt sleeping beauties. Use oeis_sleeping_beauties to find high-entropy low-connectivity sequences. Can you rotate a sleeper into alignment with Maass spectral parameters? Do sleeper growth rates match genus-2 conductor distributions? Test lattice determinant sequences against sleeper terms. The sleepers speak in quadratic forms and eta products, not Fibonacci."
goto loop
