@echo off
REM ============================================================
REM M2 CHAIN — Run after Phi-2 batch finishes
REM
REM M2a: Gemma-3-1B full sweep                      ~8h
REM M2b: Gemma-3-1B v3 baseline                     ~2m
REM M2c: Pythia L4 evolution (early layer gap)       ~3h
REM M2d: Pythia 4-layer combo (L4+L8+L10+L16)       ~1h
REM M2e: Llama v3 steered (evolve on v2, test v3)   ~3h
REM
REM Total estimated: ~16h
REM ============================================================

setlocal
set LOGDIR=results\M2_chain
set QLOG=results\queue_log.jsonl
set SENTINEL=CURRENT_JOB.txt

if not exist %LOGDIR% mkdir %LOGDIR%

echo ============================================================
echo  M2 CHAIN — POST-PHI2
echo  Started: %date% %time%
echo ============================================================

REM ── M2a: Gemma-3-1B Sweep ──────────────────────────────────
REM Different generation than impenetrable Gemma-2-2B.
REM 26 layers, ~2GB weights, ~5GB TL. Comfortable fit.

if exist KILL_QUEUE goto :done

echo M2a: Gemma-3-1B L10 Evolution (300 gen) > %SENTINEL%
echo {"job":"M2a_gemma3_L10","status":"started","time":"%date% %time%"} >> %QLOG%
echo [M2a] Gemma-3-1B L10 (38%% depth) — Started: %date% %time%

python src\evolve_1_5b.py ^
    --model google/gemma-3-1b-pt ^
    --device cuda ^
    --output-dir %LOGDIR%\gemma3_L10 ^
    --layer 10 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    > %LOGDIR%\gemma3_L10_stdout.log 2>&1

echo {"job":"M2a_gemma3_L10","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%

if exist KILL_QUEUE goto :done

echo M2a2: Gemma-3-1B L16 Evolution (300 gen) > %SENTINEL%
echo {"job":"M2a2_gemma3_L16","status":"started","time":"%date% %time%"} >> %QLOG%

python src\evolve_1_5b.py ^
    --model google/gemma-3-1b-pt ^
    --device cuda ^
    --output-dir %LOGDIR%\gemma3_L16 ^
    --layer 16 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    > %LOGDIR%\gemma3_L16_stdout.log 2>&1

echo {"job":"M2a2_gemma3_L16","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%

if exist KILL_QUEUE goto :done

echo M2a3: Gemma-3-1B L22 Evolution (300 gen) > %SENTINEL%
echo {"job":"M2a3_gemma3_L22","status":"started","time":"%date% %time%"} >> %QLOG%

python src\evolve_1_5b.py ^
    --model google/gemma-3-1b-pt ^
    --device cuda ^
    --output-dir %LOGDIR%\gemma3_L22 ^
    --layer 22 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    > %LOGDIR%\gemma3_L22_stdout.log 2>&1

echo {"job":"M2a3_gemma3_L22","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%

REM ── M2b: Gemma-3-1B v3 baseline ────────────────────────────

if exist KILL_QUEUE goto :done

echo M2b: Gemma-3-1B v3 baseline > %SENTINEL%
echo {"job":"M2b_gemma3_v3","status":"started","time":"%date% %time%"} >> %QLOG%

python src\v3_baseline_eval.py ^
    --model google/gemma-3-1b-pt ^
    --device cuda ^
    --output-dir %LOGDIR%\gemma3_v3 ^
    > %LOGDIR%\gemma3_v3_stdout.log 2>&1

echo {"job":"M2b_gemma3_v3","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%

REM ── M2c: Gemma-3 ghost trap ────────────────────────────────

if exist KILL_QUEUE goto :done

echo M2c: Gemma-3-1B ghost trap > %SENTINEL%
echo {"job":"M2c_gemma3_ghost","status":"started","time":"%date% %time%"} >> %QLOG%

python src\ghost_trap_analysis.py ^
    --model google/gemma-3-1b-pt ^
    --device cuda ^
    --output-dir %LOGDIR%\gemma3_ghost ^
    --epsilon-scale 1.0 ^
    --genomes ^
        L10=%LOGDIR%\gemma3_L10\best_genome_1_5b.pt ^
        L16=%LOGDIR%\gemma3_L16\best_genome_1_5b.pt ^
        L22=%LOGDIR%\gemma3_L22\best_genome_1_5b.pt ^
    > %LOGDIR%\gemma3_ghost_stdout.log 2>&1

echo {"job":"M2c_gemma3_ghost","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%

REM ── M2d: Pythia L4 (early layer gap) ───────────────────────
REM We have L8, L10, L16. L4 fills the early-layer cell.

if exist KILL_QUEUE goto :done

echo M2d: Pythia L4 Evolution (300 gen) > %SENTINEL%
echo {"job":"M2d_pythia_L4","status":"started","time":"%date% %time%"} >> %QLOG%
echo [M2d] Pythia L4 (17%% depth) — does early injection work? Started: %date% %time%

python src\evolve_1_5b.py ^
    --model EleutherAI/pythia-1.4b ^
    --device cuda ^
    --output-dir %LOGDIR%\pythia_L4 ^
    --layer 4 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    > %LOGDIR%\pythia_L4_stdout.log 2>&1

echo {"job":"M2d_pythia_L4","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%

REM ── M2e: Pythia 4-layer combo ──────────────────────────────

if exist KILL_QUEUE goto :done

echo M2e: Pythia 4-layer combo (L4+L8+L10+L16) > %SENTINEL%
echo {"job":"M2e_pythia_combo","status":"started","time":"%date% %time%"} >> %QLOG%

python src\multilayer_eval.py ^
    --model EleutherAI/pythia-1.4b ^
    --device cuda ^
    --output-dir %LOGDIR%\pythia_combo ^
    --genomes ^
        L4=%LOGDIR%\pythia_L4\best_genome_1_5b.pt ^
        L8=results\batch_A\A3_pythia_L8\best_genome_1_5b.pt ^
        L10=results\batch_A\A3_pythia_L10\best_genome_1_5b.pt ^
        L16=results\batch_A\A3_pythia_L16\best_genome_1_5b.pt ^
    --epsilon-scales 0.5 1.0 1.5 2.0 ^
    > %LOGDIR%\pythia_combo_stdout.log 2>&1

echo {"job":"M2e_pythia_combo","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%

:done
echo IDLE > %SENTINEL%
echo.
echo ============================================================
echo  M2 CHAIN COMPLETE: %date% %time%
echo  Results in: %LOGDIR%
echo ============================================================
pause
