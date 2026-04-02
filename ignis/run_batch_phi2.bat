@echo off
REM ============================================================
REM BATCH PHI2 — Architecture Sweep: microsoft/phi-2
REM
REM Phi-2: 32 layers, 2.7B params, ~5.5GB weights, ~12GB TL
REM TIGHT ON 16GB VRAM — if OOM, reduce popsize to 16
REM
REM P1: Baseline eval (v2 battery)                   ~5m
REM P2: L12 evolution (300 gen, 38%% depth)           ~3h
REM P3: L20 evolution (300 gen, 63%% depth)           ~3h
REM P4: L28 evolution (300 gen, 88%% depth)           ~3h
REM P5: Multi-layer combo                             ~30m
REM P6: Ghost trap analysis                           ~5m
REM P7: v3 battery baseline                           ~2m
REM
REM Total estimated: ~10h
REM
REM SKIP/KILL:
REM   Create SKIP_P3 through SKIP_P7 to skip jobs
REM   Create KILL_QUEUE in ignis/ to abort
REM ============================================================

setlocal
set LOGDIR=results\batch_phi2
set QLOG=results\queue_log.jsonl
set SENTINEL=CURRENT_JOB.txt
set MODEL=microsoft/phi-2

if not exist %LOGDIR% mkdir %LOGDIR%

echo ============================================================
echo  BATCH PHI2 — ARCHITECTURE SWEEP: microsoft/phi-2
echo  Started: %date% %time%
echo  Log: %LOGDIR%
echo  NOTE: 2.7B model is tight on 16GB VRAM.
echo  If OOM occurs, create KILL_QUEUE and re-run with popsize 16.
echo ============================================================

REM ── P1: Baseline ────────────────────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo P1: Phi-2 Baseline (v2 battery) > %SENTINEL%
echo {"job":"P1_phi2_baseline","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [P1] Phi-2 baseline — v2 battery
echo [P1] Started: %date% %time%
echo.

python src\stability_test.py ^
    --model %MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\P1_baseline ^
    --n-runs 1 ^
    --epsilon-scale 0.0 ^
    > %LOGDIR%\P1_baseline_stdout.log 2>&1

set P1_EXIT=%ERRORLEVEL%
echo {"job":"P1_phi2_baseline","status":"finished","exit_code":%P1_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [P1] Finished (exit=%P1_EXIT%): %date% %time%

if %P1_EXIT% neq 0 (
    echo [P1] FAILED — likely OOM. Phi-2 may not fit in 16GB with TransformerLens.
    echo [P1] Try reducing batch size or switch to a smaller model.
    echo {"job":"P1_phi2_baseline","status":"OOM_likely","time":"%date% %time%"} >> %QLOG%
    goto :done
)

REM ── P2: L12 Evolution ──────────────────────────────────────
REM Phi-2 has 32 layers. L12 = 38%% depth.

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo P2: Phi-2 L12 Evolution (300 gen, 38%% depth) > %SENTINEL%
echo {"job":"P2_phi2_L12","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [P2] Phi-2 L12 — early-mid (38%% of 32 layers)
echo [P2] Started: %date% %time%
echo.

python src\evolve_1_5b.py ^
    --model %MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\P2_phi2_L12 ^
    --layer 12 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 24 ^
    --stdev-init 0.05 ^
    > %LOGDIR%\P2_phi2_L12_stdout.log 2>&1

set P2_EXIT=%ERRORLEVEL%
echo {"job":"P2_phi2_L12","status":"finished","exit_code":%P2_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [P2] Finished (exit=%P2_EXIT%): %date% %time%

REM ── P3: L20 Evolution ──────────────────────────────────────
REM L20 = 63%% depth.

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_P3 (
    echo [P3] SKIP_P3 detected. Skipping.
    echo {"job":"P3_phi2_L20","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :p4
)

echo P3: Phi-2 L20 Evolution (300 gen, 63%% depth) > %SENTINEL%
echo {"job":"P3_phi2_L20","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [P3] Phi-2 L20 — mid-late (63%% of 32 layers)
echo [P3] Started: %date% %time%
echo.

python src\evolve_1_5b.py ^
    --model %MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\P3_phi2_L20 ^
    --layer 20 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 24 ^
    --stdev-init 0.05 ^
    > %LOGDIR%\P3_phi2_L20_stdout.log 2>&1

set P3_EXIT=%ERRORLEVEL%
echo {"job":"P3_phi2_L20","status":"finished","exit_code":%P3_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [P3] Finished (exit=%P3_EXIT%): %date% %time%

:p4

REM ── P4: L28 Evolution ──────────────────────────────────────
REM L28 = 88%% depth.

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_P4 (
    echo [P4] SKIP_P4 detected. Skipping.
    echo {"job":"P4_phi2_L28","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :p5
)

echo P4: Phi-2 L28 Evolution (300 gen, 88%% depth) > %SENTINEL%
echo {"job":"P4_phi2_L28","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [P4] Phi-2 L28 — late layer (88%% of 32 layers)
echo [P4] Started: %date% %time%
echo.

python src\evolve_1_5b.py ^
    --model %MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\P4_phi2_L28 ^
    --layer 28 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 24 ^
    --stdev-init 0.05 ^
    > %LOGDIR%\P4_phi2_L28_stdout.log 2>&1

set P4_EXIT=%ERRORLEVEL%
echo {"job":"P4_phi2_L28","status":"finished","exit_code":%P4_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [P4] Finished (exit=%P4_EXIT%): %date% %time%

:p5

REM ── P5: Multi-Layer Combo ───────────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_P5 (
    echo [P5] SKIP_P5 detected. Skipping.
    echo {"job":"P5_phi2_combo","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :p6
)

echo P5: Phi-2 Multi-Layer Combo > %SENTINEL%
echo {"job":"P5_phi2_combo","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [P5] Phi-2 combo — all subsets of L12+L20+L28
echo [P5] Started: %date% %time%
echo.

python src\multilayer_eval.py ^
    --model %MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\P5_combo ^
    --genomes ^
        L12=%LOGDIR%\P2_phi2_L12\best_genome_1_5b.pt ^
        L20=%LOGDIR%\P3_phi2_L20\best_genome_1_5b.pt ^
        L28=%LOGDIR%\P4_phi2_L28\best_genome_1_5b.pt ^
    --epsilon-scales 0.5 1.0 1.5 2.0 ^
    > %LOGDIR%\P5_combo_stdout.log 2>&1

set P5_EXIT=%ERRORLEVEL%
echo {"job":"P5_phi2_combo","status":"finished","exit_code":%P5_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [P5] Finished (exit=%P5_EXIT%): %date% %time%

:p6

REM ── P6: Ghost Trap ─────────────────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_P6 (
    echo [P6] SKIP_P6 detected. Skipping.
    echo {"job":"P6_phi2_ghost","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :p7
)

echo P6: Phi-2 Ghost Trap Analysis > %SENTINEL%
echo {"job":"P6_phi2_ghost","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [P6] Ghost trap on Phi-2 — bypass universal on 4th architecture?
echo [P6] Started: %date% %time%
echo.

python src\ghost_trap_analysis.py ^
    --model %MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\P6_ghost ^
    --epsilon-scale 1.0 ^
    --genomes ^
        L12=%LOGDIR%\P2_phi2_L12\best_genome_1_5b.pt ^
        L20=%LOGDIR%\P3_phi2_L20\best_genome_1_5b.pt ^
        L28=%LOGDIR%\P4_phi2_L28\best_genome_1_5b.pt ^
    > %LOGDIR%\P6_ghost_stdout.log 2>&1

set P6_EXIT=%ERRORLEVEL%
echo {"job":"P6_phi2_ghost","status":"finished","exit_code":%P6_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [P6] Finished (exit=%P6_EXIT%): %date% %time%

:p7

REM ── P7: v3 Battery Baseline ────────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_P7 (
    echo [P7] SKIP_P7 detected. Skipping.
    echo {"job":"P7_phi2_v3","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :done
)

echo P7: Phi-2 v3 Battery Baseline > %SENTINEL%
echo {"job":"P7_phi2_v3","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [P7] v3 battery on Phi-2
echo [P7] Started: %date% %time%
echo.

python src\v3_baseline_eval.py ^
    --model %MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\P7_v3_baseline ^
    > %LOGDIR%\P7_v3_baseline_stdout.log 2>&1

set P7_EXIT=%ERRORLEVEL%
echo {"job":"P7_phi2_v3","status":"finished","exit_code":%P7_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [P7] Finished (exit=%P7_EXIT%): %date% %time%

:done
echo IDLE > %SENTINEL%
echo.
echo ============================================================
echo  BATCH PHI2 COMPLETE: %date% %time%
echo  Results in: %LOGDIR%
echo  Queue log: %QLOG%
echo ============================================================
pause
