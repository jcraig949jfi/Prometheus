@echo off
REM ============================================================
REM BATCH F — M1 Overnight: Qwen 1.5B v3 Evolution Pipeline
REM
REM Hypothesis: Are harder (v3) traps also bypassable via
REM             activation-space steering?
REM
REM F1: v3 baseline (sanity check, already have 16/30)     ~5m
REM F2: L10 evolution vs v3 (500 gen, 42%% depth)         ~5h
REM F3: L23 evolution vs v3 (500 gen, 82%% depth)         ~5h
REM F4: Multi-layer combo (L10+L23) on v3                  ~30m
REM F5: Ghost trap analysis on v3 best combo               ~15m
REM
REM Total estimated: ~11h
REM
REM SKIP/KILL:
REM   Create SKIP_F2 through SKIP_F5 to skip jobs
REM   Create KILL_QUEUE in ignis/ to abort
REM ============================================================

setlocal
set LOGDIR=results\batch_F_v3
set QLOG=results\queue_log.jsonl
set SENTINEL=CURRENT_JOB.txt
set MODEL=Qwen/Qwen2.5-1.5B-Instruct

if not exist %LOGDIR% mkdir %LOGDIR%

echo ============================================================
echo  BATCH F — M1 OVERNIGHT: Qwen 1.5B v3 Evolution
echo  Started: %date% %time%
echo  Log: %LOGDIR%
echo  Hypothesis: v3 traps bypassable via steering?
echo ============================================================

REM ── F1: v3 Baseline ────────────────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo F1: Qwen 1.5B v3 Baseline > %SENTINEL%
echo {"job":"F1_qwen15_v3_baseline","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [F1] Qwen 1.5B v3 baseline (sanity check)
echo [F1] Started: %date% %time%

python src\stability_test.py ^
    --model %MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\F1_v3_baseline ^
    --n-runs 1 ^
    --epsilon-scale 0.0 ^
    --battery v3 ^
    > %LOGDIR%\F1_v3_baseline_stdout.log 2>&1

set F1_EXIT=%ERRORLEVEL%
echo {"job":"F1_qwen15_v3_baseline","status":"finished","exit_code":%F1_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [F1] Finished (exit=%F1_EXIT%): %date% %time%

REM ── F2: L10 Evolution vs v3 ────────────────────────────────
REM L10 = 42%% depth. Early injection. Tests if shallow layers
REM can steer harder multi-step traps.

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_F2 (
    echo [F2] SKIP_F2 detected, skipping.
    goto :f3
)

echo F2: Qwen 1.5B L10 v3 Evolution (500 gen) > %SENTINEL%
echo {"job":"F2_qwen15_v3_L10","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [F2] Qwen 1.5B L10 v3 evolution — 500 gen
echo [F2] Started: %date% %time%

python src\evolve_1_5b.py ^
    --model %MODEL% ^
    --device cuda ^
    --layer 10 ^
    --epsilon 3.0 ^
    --n-generations 500 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    --battery v3 ^
    --output-dir %LOGDIR%\F2_qwen15_v3_L10 ^
    > %LOGDIR%\F2_qwen15_v3_L10_stdout.log 2>&1

set F2_EXIT=%ERRORLEVEL%
echo {"job":"F2_qwen15_v3_L10","status":"finished","exit_code":%F2_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [F2] Finished (exit=%F2_EXIT%): %date% %time%

REM ── F3: L23 Evolution vs v3 ────────────────────────────────
REM L23 = 82%% depth. Late injection. Original Qwen sweet spot.

:f3
if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_F3 (
    echo [F3] SKIP_F3 detected, skipping.
    goto :f4
)

echo F3: Qwen 1.5B L23 v3 Evolution (500 gen) > %SENTINEL%
echo {"job":"F3_qwen15_v3_L23","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [F3] Qwen 1.5B L23 v3 evolution — 500 gen
echo [F3] Started: %date% %time%

python src\evolve_1_5b.py ^
    --model %MODEL% ^
    --device cuda ^
    --layer 23 ^
    --epsilon 3.0 ^
    --n-generations 500 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    --battery v3 ^
    --output-dir %LOGDIR%\F3_qwen15_v3_L23 ^
    > %LOGDIR%\F3_qwen15_v3_L23_stdout.log 2>&1

set F3_EXIT=%ERRORLEVEL%
echo {"job":"F3_qwen15_v3_L23","status":"finished","exit_code":%F3_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [F3] Finished (exit=%F3_EXIT%): %date% %time%

REM ── F4: Multi-layer combo ──────────────────────────────────

:f4
if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_F4 (
    echo [F4] SKIP_F4 detected, skipping.
    goto :f5
)

echo F4: Qwen 1.5B v3 Multi-layer Combo > %SENTINEL%
echo {"job":"F4_qwen15_v3_combo","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [F4] Multi-layer combo eval (L10+L23) on v3
echo [F4] Started: %date% %time%

python src\multilayer_eval.py ^
    --model %MODEL% ^
    --device cuda ^
    --battery v3 ^
    --output-dir %LOGDIR%\F4_v3_combo ^
    --genomes ^
        L10=%LOGDIR%\F2_qwen15_v3_L10\best_genome_1_5b.pt ^
        L23=%LOGDIR%\F3_qwen15_v3_L23\best_genome_1_5b.pt ^
    --epsilon-scales 0.5 1.0 1.5 2.0 ^
    > %LOGDIR%\F4_v3_combo_stdout.log 2>&1

set F4_EXIT=%ERRORLEVEL%
echo {"job":"F4_qwen15_v3_combo","status":"finished","exit_code":%F4_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [F4] Finished (exit=%F4_EXIT%): %date% %time%

REM ── F5: Ghost trap on v3 ───────────────────────────────────

:f5
if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_F5 (
    echo [F5] SKIP_F5 detected, skipping.
    goto :done
)

echo F5: Qwen 1.5B v3 Ghost Trap Analysis > %SENTINEL%
echo {"job":"F5_qwen15_v3_ghost","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [F5] Ghost trap analysis on v3 best combo
echo [F5] Started: %date% %time%

python src\ghost_trap_analysis.py ^
    --model %MODEL% ^
    --device cuda ^
    --battery v3 ^
    --output-dir %LOGDIR%\F5_v3_ghost ^
    --genomes ^
        L10=%LOGDIR%\F2_qwen15_v3_L10\best_genome_1_5b.pt ^
        L23=%LOGDIR%\F3_qwen15_v3_L23\best_genome_1_5b.pt ^
    --epsilon-scale 1.5 ^
    > %LOGDIR%\F5_v3_ghost_stdout.log 2>&1

set F5_EXIT=%ERRORLEVEL%
echo {"job":"F5_qwen15_v3_ghost","status":"finished","exit_code":%F5_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [F5] Finished (exit=%F5_EXIT%): %date% %time%

REM ── Done ────────────────────────────────────────────────────

:done
echo IDLE > %SENTINEL%
echo.
echo ============================================================
echo  BATCH F COMPLETE: %date% %time%
echo  Results: %LOGDIR%\
echo ============================================================
pause
