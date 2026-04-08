@echo off
title T4-STRUCTURAL
cd /d F:\Prometheus\cartography\shared\scripts
:loop
python research_cycle.py --tag T4 --provider deepseek --hypotheses 8 --loop 60 --tensor-review-every 25 --topic "Map the proof graph. Do Mizar hub articles reference concepts that appear in FindStat statistics? Do mathlib module import patterns predict which genus-2 Sato-Tate groups have formal proofs? Test Metamath theorem density against ANTEDB bound improvements. Use OpenAlex concept hierarchy to find academic topics that bridge our empirical datasets."
goto loop
