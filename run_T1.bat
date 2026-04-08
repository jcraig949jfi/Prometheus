@echo off
title T1-ARITHMETIC
cd /d F:\Prometheus\cartography\shared\scripts
:loop
python research_cycle.py --tag T1 --provider deepseek --hypotheses 8 --loop 60 --tensor-review-every 25 --topic "Bridge knot polynomial invariants with number field class numbers and regulators. Do isogeny graph node counts at prime p predict anything about knots with determinant p? Test genus-2 curve conductors against knot determinants. Do genus-2 Sato-Tate groups correlate with number field Galois groups? Search OEIS sleeping beauties. Test across bases."
goto loop
