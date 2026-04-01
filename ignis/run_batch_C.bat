@echo off
REM ============================================================
REM BATCH C — Architecture Sweep: Llama + Gemma
REM
REM C1: Llama-3.2-1B baseline eval                  ~30m
REM C2: Llama L8 evolution (300 gen)                 ~3h
REM C3: Llama L12 evolution (300 gen)                ~3h
REM C4: Llama multi-layer combo                      ~30m
REM C5: Llama ghost trap                             ~15m
REM C6: Gemma-2-2B baseline eval                     ~30m
REM C7: Gemma-2-2B L10/L16/L22 evolution             ~9h
REM C8: Gemma ghost trap                             ~15m
REM
REM Total estimated: ~17-22h
REM
REM Llama-3.2-1B: 16 layers, ~2.5GB weights, ~6GB TL
REM Gemma-2-2B: 26 layers, ~4GB weights, ~9GB TL
REM Both fit comfortably in 16GB.
REM
REM SKIP/KILL:
REM   Create SKIP_C2 through SKIP_C8 to skip jobs
REM   Create KILL_QUEUE in ignis/ to abort
REM ============================================================

setlocal
set LOGDIR=results\batch_C
set QLOG=results\queue_log.jsonl
set SENTINEL=CURRENT_JOB.txt

if not exist %LOGDIR% mkdir %LOGDIR%

echo ============================================================
echo  BATCH C — ARCHITECTURE SWEEP: LLAMA + GEMMA
echo  Started: %date% %time%
echo  Log: %LOGDIR%
echo ============================================================

REM ── C1: Llama-3.2-1B Baseline ──────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo C1: Llama-3.2-1B Baseline Eval > %SENTINEL%
echo {"job":"C1_llama_baseline","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [C1] Llama-3.2-1B baseline — what's the starting SR?
echo [C1] Started: %date% %time%
echo.

python src\multilayer_eval.py ^
    --model meta-llama/Llama-3.2-1B ^
    --device cuda ^
    --output-dir %LOGDIR%\C1_llama_baseline ^
    --genomes DUMMY=nonexistent.pt ^
    > %LOGDIR%\C1_llama_baseline_stdout.log 2>&1

REM If the dummy genome approach fails, fall back to a simple eval
if %ERRORLEVEL% neq 0 (
    echo [C1] Multilayer baseline failed, running stability test with 1 run as baseline check
    python src\stability_test.py ^
        --model meta-llama/Llama-3.2-1B ^
        --device cuda ^
        --output-dir %LOGDIR%\C1_llama_baseline ^
        --n-runs 1 ^
        --epsilon-scale 0.0 ^
        > %LOGDIR%\C1_llama_baseline_stdout.log 2>&1
)

set C1_EXIT=%ERRORLEVEL%
echo {"job":"C1_llama_baseline","status":"finished","exit_code":%C1_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [C1] Finished (exit=%C1_EXIT%): %date% %time%

REM ── C2: Llama L8 Evolution ─────────────────────────────────
REM Llama-3.2-1B has 16 layers. L8 = 50%% depth.

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_C2 (
    echo [C2] SKIP_C2 detected. Skipping.
    echo {"job":"C2_llama_L8","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :c3
)

echo C2: Llama L8 Evolution (300 gen) > %SENTINEL%
echo {"job":"C2_llama_L8","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [C2] Llama L8 — mid-depth layer (50%% of 16-layer model)
echo [C2] Started: %date% %time%
echo.

python src\evolve_1_5b.py ^
    --model meta-llama/Llama-3.2-1B ^
    --device cuda ^
    --output-dir %LOGDIR%\C2_llama_L8 ^
    --layer 8 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    > %LOGDIR%\C2_llama_L8_stdout.log 2>&1

set C2_EXIT=%ERRORLEVEL%
echo {"job":"C2_llama_L8","status":"finished","exit_code":%C2_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [C2] Finished (exit=%C2_EXIT%): %date% %time%

:c3

REM ── C3: Llama L12 Evolution ─────────────────────────────────
REM L12 = 75%% depth. Analogous to Pythia L16 / Qwen L21.

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_C3 (
    echo [C3] SKIP_C3 detected. Skipping.
    echo {"job":"C3_llama_L12","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :c4
)

echo C3: Llama L12 Evolution (300 gen) > %SENTINEL%
echo {"job":"C3_llama_L12","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [C3] Llama L12 — late layer (75%% of 16-layer model)
echo [C3] Started: %date% %time%
echo.

python src\evolve_1_5b.py ^
    --model meta-llama/Llama-3.2-1B ^
    --device cuda ^
    --output-dir %LOGDIR%\C3_llama_L12 ^
    --layer 12 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    > %LOGDIR%\C3_llama_L12_stdout.log 2>&1

set C3_EXIT=%ERRORLEVEL%
echo {"job":"C3_llama_L12","status":"finished","exit_code":%C3_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [C3] Finished (exit=%C3_EXIT%): %date% %time%

:c4

REM ── C4: Llama Multi-Layer Combo ─────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_C4 (
    echo [C4] SKIP_C4 detected. Skipping.
    echo {"job":"C4_llama_combo","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :c5
)

echo C4: Llama Multi-Layer Combo (L8+L12) > %SENTINEL%
echo {"job":"C4_llama_combo","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [C4] Llama combo — additive or superadditive?
echo [C4] Started: %date% %time%
echo.

python src\multilayer_eval.py ^
    --model meta-llama/Llama-3.2-1B ^
    --device cuda ^
    --output-dir %LOGDIR%\C4_llama_combo ^
    --genomes ^
        L8=%LOGDIR%\C2_llama_L8\best_genome_1_5b.pt ^
        L12=%LOGDIR%\C3_llama_L12\best_genome_1_5b.pt ^
    --epsilon-scales 0.5 1.0 1.5 2.0 ^
    > %LOGDIR%\C4_llama_combo_stdout.log 2>&1

set C4_EXIT=%ERRORLEVEL%
echo {"job":"C4_llama_combo","status":"finished","exit_code":%C4_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [C4] Finished (exit=%C4_EXIT%): %date% %time%

:c5

REM ── C5: Llama Ghost Trap ────────────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_C5 (
    echo [C5] SKIP_C5 detected. Skipping.
    echo {"job":"C5_llama_ghost","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :c6
)

echo C5: Llama Ghost Trap Analysis > %SENTINEL%
echo {"job":"C5_llama_ghost","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [C5] Ghost trap on best Llama genome — bypass or amplification?
echo [C5] Started: %date% %time%
echo.

REM Use both Llama genomes for ghost trap
python src\ghost_trap_analysis.py ^
    --model meta-llama/Llama-3.2-1B ^
    --device cuda ^
    --output-dir %LOGDIR%\C5_llama_ghost ^
    --epsilon-scale 1.0 ^
    --genomes ^
        L8=%LOGDIR%\C2_llama_L8\best_genome_1_5b.pt ^
        L12=%LOGDIR%\C3_llama_L12\best_genome_1_5b.pt ^
    > %LOGDIR%\C5_llama_ghost_stdout.log 2>&1

set C5_EXIT=%ERRORLEVEL%
echo {"job":"C5_llama_ghost","status":"finished","exit_code":%C5_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [C5] Finished (exit=%C5_EXIT%): %date% %time%

:c6

REM ── C6: Gemma-2-2B Baseline ────────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_C6 (
    echo [C6] SKIP_C6 detected. Skipping.
    echo {"job":"C6_gemma_baseline","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :c7
)

echo C6: Gemma-2-2B Baseline Eval > %SENTINEL%
echo {"job":"C6_gemma_baseline","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [C6] Gemma-2-2B baseline — Gemma-1B was "impenetrable", is 2B different?
echo [C6] Started: %date% %time%
echo.

python src\stability_test.py ^
    --model google/gemma-2-2b ^
    --device cuda ^
    --output-dir %LOGDIR%\C6_gemma_baseline ^
    --n-runs 1 ^
    --epsilon-scale 0.0 ^
    > %LOGDIR%\C6_gemma_baseline_stdout.log 2>&1

set C6_EXIT=%ERRORLEVEL%
echo {"job":"C6_gemma_baseline","status":"finished","exit_code":%C6_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [C6] Finished (exit=%C6_EXIT%): %date% %time%

:c7

REM ── C7: Gemma-2-2B Evolution (3 layers) ────────────────────
REM Gemma-2-2B has 26 layers. Test L10 (38%%), L16 (62%%), L22 (85%%).

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_C7 (
    echo [C7] SKIP_C7 detected. Skipping.
    echo {"job":"C7_gemma_evolve","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :c8
)

echo C7a: Gemma-2-2B L10 Evolution (300 gen) > %SENTINEL%
echo {"job":"C7a_gemma_L10","status":"started","time":"%date% %time%"} >> %QLOG%
echo [C7a] Gemma L10 (38%% depth) — Started: %date% %time%

python src\evolve_1_5b.py ^
    --model google/gemma-2-2b ^
    --device cuda ^
    --output-dir %LOGDIR%\C7_gemma_L10 ^
    --layer 10 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    > %LOGDIR%\C7_gemma_L10_stdout.log 2>&1

set C7a_EXIT=%ERRORLEVEL%
echo {"job":"C7a_gemma_L10","status":"finished","exit_code":%C7a_EXIT%,"time":"%date% %time%"} >> %QLOG%

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo C7b: Gemma-2-2B L16 Evolution (300 gen) > %SENTINEL%
echo {"job":"C7b_gemma_L16","status":"started","time":"%date% %time%"} >> %QLOG%
echo [C7b] Gemma L16 (62%% depth) — Started: %date% %time%

python src\evolve_1_5b.py ^
    --model google/gemma-2-2b ^
    --device cuda ^
    --output-dir %LOGDIR%\C7_gemma_L16 ^
    --layer 16 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    > %LOGDIR%\C7_gemma_L16_stdout.log 2>&1

set C7b_EXIT=%ERRORLEVEL%
echo {"job":"C7b_gemma_L16","status":"finished","exit_code":%C7b_EXIT%,"time":"%date% %time%"} >> %QLOG%

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo C7c: Gemma-2-2B L22 Evolution (300 gen) > %SENTINEL%
echo {"job":"C7c_gemma_L22","status":"started","time":"%date% %time%"} >> %QLOG%
echo [C7c] Gemma L22 (85%% depth) — Started: %date% %time%

python src\evolve_1_5b.py ^
    --model google/gemma-2-2b ^
    --device cuda ^
    --output-dir %LOGDIR%\C7_gemma_L22 ^
    --layer 22 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    > %LOGDIR%\C7_gemma_L22_stdout.log 2>&1

set C7c_EXIT=%ERRORLEVEL%
echo {"job":"C7c_gemma_L22","status":"finished","exit_code":%C7c_EXIT%,"time":"%date% %time%"} >> %QLOG%

:c8

REM ── C8: Gemma Ghost Trap ────────────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_C8 (
    echo [C8] SKIP_C8 detected. Skipping.
    echo {"job":"C8_gemma_ghost","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :done
)

echo C8: Gemma Ghost Trap Analysis > %SENTINEL%
echo {"job":"C8_gemma_ghost","status":"started","time":"%date% %time%"} >> %QLOG%
echo [C8] Ghost trap on best Gemma genome — Started: %date% %time%

REM Use best Gemma genome for ghost trap (pick highest SR layer)
python src\ghost_trap_analysis.py ^
    --model google/gemma-2-2b ^
    --device cuda ^
    --output-dir %LOGDIR%\C8_gemma_ghost ^
    --epsilon-scale 1.0 ^
    --genomes ^
        L10=%LOGDIR%\C7_gemma_L10\best_genome_1_5b.pt ^
        L16=%LOGDIR%\C7_gemma_L16\best_genome_1_5b.pt ^
        L22=%LOGDIR%\C7_gemma_L22\best_genome_1_5b.pt ^
    > %LOGDIR%\C8_gemma_ghost_stdout.log 2>&1

set C8_EXIT=%ERRORLEVEL%
echo {"job":"C8_gemma_ghost","status":"finished","exit_code":%C8_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [C8] Finished (exit=%C8_EXIT%): %date% %time%

:done
echo IDLE > %SENTINEL%
echo.
echo ============================================================
echo  BATCH C COMPLETE: %date% %time%
echo  Results in: %LOGDIR%
echo  Queue log: %QLOG%
echo ============================================================
pause
