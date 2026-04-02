@echo off
REM ============================================================
REM BATCH C (Llama) — Architecture Sweep: Llama-3.2-1B
REM
REM Llama-3.2-1B: 16 layers, ~2.5GB weights, ~6GB TL
REM
REM C1: Baseline eval                               ~5m
REM C2: L8 evolution (300 gen, 50%% depth)           ~3h
REM C3: L12 evolution (300 gen, 75%% depth)          ~3h
REM C4: Multi-layer combo (L8+L12)                   ~30m
REM C5: Ghost trap analysis                          ~5m
REM C6: v3 battery baseline                          ~2m
REM
REM Total estimated: ~7h
REM
REM SKIP/KILL:
REM   Create SKIP_C2 through SKIP_C6 to skip jobs
REM   Create KILL_QUEUE in ignis/ to abort
REM ============================================================

setlocal
set LOGDIR=results\batch_C_llama
set QLOG=results\queue_log.jsonl
set SENTINEL=CURRENT_JOB.txt
set MODEL=meta-llama/Llama-3.2-1B

if not exist %LOGDIR% mkdir %LOGDIR%

echo ============================================================
echo  BATCH C (LLAMA) — ARCHITECTURE SWEEP: Llama-3.2-1B
echo  Started: %date% %time%
echo  Log: %LOGDIR%
echo ============================================================

REM ── C1: Baseline ────────────────────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo C1: Llama-3.2-1B Baseline (v2 battery) > %SENTINEL%
echo {"job":"C1_llama_baseline","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [C1] Llama-3.2-1B baseline — v2 battery
echo [C1] Started: %date% %time%
echo.

python src\stability_test.py ^
    --model %MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\C1_baseline ^
    --n-runs 1 ^
    --epsilon-scale 0.0 ^
    > %LOGDIR%\C1_baseline_stdout.log 2>&1

set C1_EXIT=%ERRORLEVEL%
echo {"job":"C1_llama_baseline","status":"finished","exit_code":%C1_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [C1] Finished (exit=%C1_EXIT%): %date% %time%

REM ── C2: L8 Evolution ───────────────────────────────────────
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

echo C2: Llama L8 Evolution (300 gen, 50%% depth) > %SENTINEL%
echo {"job":"C2_llama_L8","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [C2] Llama L8 — mid-depth (50%% of 16-layer model)
echo [C2] Started: %date% %time%
echo.

python src\evolve_1_5b.py ^
    --model %MODEL% ^
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

REM ── C3: L12 Evolution ──────────────────────────────────────
REM L12 = 75%% depth.

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_C3 (
    echo [C3] SKIP_C3 detected. Skipping.
    echo {"job":"C3_llama_L12","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :c4
)

echo C3: Llama L12 Evolution (300 gen, 75%% depth) > %SENTINEL%
echo {"job":"C3_llama_L12","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [C3] Llama L12 — late layer (75%% of 16-layer model)
echo [C3] Started: %date% %time%
echo.

python src\evolve_1_5b.py ^
    --model %MODEL% ^
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

REM ── C4: Multi-Layer Combo ───────────────────────────────────

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
    --model %MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\C4_combo ^
    --genomes ^
        L8=%LOGDIR%\C2_llama_L8\best_genome_1_5b.pt ^
        L12=%LOGDIR%\C3_llama_L12\best_genome_1_5b.pt ^
    --epsilon-scales 0.5 1.0 1.5 2.0 ^
    > %LOGDIR%\C4_combo_stdout.log 2>&1

set C4_EXIT=%ERRORLEVEL%
echo {"job":"C4_llama_combo","status":"finished","exit_code":%C4_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [C4] Finished (exit=%C4_EXIT%): %date% %time%

:c5

REM ── C5: Ghost Trap ─────────────────────────────────────────

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
echo [C5] Ghost trap — bypass or amplification on Llama?
echo [C5] Started: %date% %time%
echo.

python src\ghost_trap_analysis.py ^
    --model %MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\C5_ghost ^
    --epsilon-scale 1.0 ^
    --genomes ^
        L8=%LOGDIR%\C2_llama_L8\best_genome_1_5b.pt ^
        L12=%LOGDIR%\C3_llama_L12\best_genome_1_5b.pt ^
    > %LOGDIR%\C5_ghost_stdout.log 2>&1

set C5_EXIT=%ERRORLEVEL%
echo {"job":"C5_llama_ghost","status":"finished","exit_code":%C5_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [C5] Finished (exit=%C5_EXIT%): %date% %time%

:c6

REM ── C6: v3 Battery Baseline ────────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_C6 (
    echo [C6] SKIP_C6 detected. Skipping.
    echo {"job":"C6_llama_v3","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :done
)

echo C6: Llama v3 Battery Baseline > %SENTINEL%
echo {"job":"C6_llama_v3","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [C6] v3 battery baseline on Llama — how do harder traps discriminate?
echo [C6] Started: %date% %time%
echo.

python src\v3_baseline_eval.py ^
    --model %MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\C6_v3_baseline ^
    > %LOGDIR%\C6_v3_baseline_stdout.log 2>&1

set C6_EXIT=%ERRORLEVEL%
echo {"job":"C6_llama_v3","status":"finished","exit_code":%C6_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [C6] Finished (exit=%C6_EXIT%): %date% %time%

:done
echo IDLE > %SENTINEL%
echo.
echo ============================================================
echo  BATCH C (LLAMA) COMPLETE: %date% %time%
echo  Results in: %LOGDIR%
echo  Queue log: %QLOG%
echo ============================================================
pause
