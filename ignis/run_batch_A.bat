@echo off
REM ============================================================
REM BATCH A — Validation Suite
REM
REM A1: Stability test (10x winning combo)         ~30m
REM A2: Ghost trap analysis (mechanism type)        ~30m
REM A3: Cross-arch Pythia-1.4B evolution            ~6h
REM
REM Total estimated: ~7h
REM
REM SKIP/KILL:
REM   Create SKIP_A2 or SKIP_A3 in ignis/ to skip a job
REM   Create KILL_QUEUE in ignis/ to abort after current job
REM ============================================================

setlocal
set LOGDIR=results\batch_A
set QLOG=results\queue_log.jsonl
set SENTINEL=CURRENT_JOB.txt
set FT_MODEL=results\corpus_first\stageB_finetune\ft_model

if not exist %LOGDIR% mkdir %LOGDIR%

echo ============================================================
echo  BATCH A — VALIDATION SUITE
echo  Started: %date% %time%
echo  Log: %LOGDIR%
echo  Kill: create KILL_QUEUE to abort
echo  Skip: create SKIP_A2 or SKIP_A3 to skip jobs
echo ============================================================

REM ── A1: Stability Test ──────────────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo A1: Stability Test (10x L19+L20+L21 x1.5) > %SENTINEL%
echo {"job":"A1_stability","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [A1] Stability Test — 10 runs of winning combo
echo [A1] Started: %date% %time%
echo.

python src\stability_test.py ^
    --model %FT_MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\A1_stability ^
    --n-runs 10 ^
    > %LOGDIR%\A1_stability_stdout.log 2>&1

set A1_EXIT=%ERRORLEVEL%
echo {"job":"A1_stability","status":"finished","exit_code":%A1_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [A1] Finished (exit=%A1_EXIT%): %date% %time%

REM ── A2: Ghost Trap Analysis ─────────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_A2 (
    echo [A2] SKIP_A2 detected. Skipping ghost trap analysis.
    echo {"job":"A2_ghost","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :a3
)

echo A2: Ghost Trap Analysis (cos_with_residual, norm_ratio) > %SENTINEL%
echo {"job":"A2_ghost","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [A2] Ghost Trap Analysis — mechanistic classification
echo [A2] Started: %date% %time%
echo.

python src\ghost_trap_analysis.py ^
    --model %FT_MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\A2_ghost ^
    > %LOGDIR%\A2_ghost_stdout.log 2>&1

set A2_EXIT=%ERRORLEVEL%
echo {"job":"A2_ghost","status":"finished","exit_code":%A2_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [A2] Finished (exit=%A2_EXIT%): %date% %time%

:a3

REM ── A3: Cross-Architecture Pythia-1.4B ──────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_A3 (
    echo [A3] SKIP_A3 detected. Skipping cross-arch evolution.
    echo {"job":"A3_pythia","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :done
)

echo A3: Cross-Arch Pythia-1.4B Evolution (L10, 500 gen) > %SENTINEL%
echo {"job":"A3_pythia_L10","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [A3] Cross-Architecture — Pythia-1.4B
echo [A3] Evolving L10 (early layer, ~42%% depth for 24-layer model)
echo [A3] Started: %date% %time%
echo [A3] This will take ~2h per layer.
echo.

REM Pythia-1.4B has 24 layers. Early-layer hypothesis says L8-L12 should be productive.
REM Start with L10 (the analogue of L19 in a 28-layer model = ~42%% depth)
REM NOTE: Pythia-1.4B is ~5.6GB in fp16. TransformerLens overhead ~2x = ~11GB.
REM Should fit in 16GB with CMA-ES overhead. If OOM, try pythia-410m instead.
REM NOTE: Pythia is a BASE model (no instruct). Logit margin measurement still
REM works — we only need token preference, not instruction following.

python src\evolve_1_5b.py ^
    --model EleutherAI/pythia-1.4b ^
    --device cuda ^
    --output-dir %LOGDIR%\A3_pythia_L10 ^
    --layer 10 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    > %LOGDIR%\A3_pythia_L10_stdout.log 2>&1

set A3a_EXIT=%ERRORLEVEL%
echo {"job":"A3_pythia_L10","status":"finished","exit_code":%A3a_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [A3a] Pythia L10 finished (exit=%A3a_EXIT%): %date% %time%

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

REM Now L8 (deeper early layer)
echo A3b: Cross-Arch Pythia-1.4B Evolution (L8, 300 gen) > %SENTINEL%
echo {"job":"A3_pythia_L8","status":"started","time":"%date% %time%"} >> %QLOG%
echo [A3b] Pythia L8 — Started: %date% %time%

python src\evolve_1_5b.py ^
    --model EleutherAI/pythia-1.4b ^
    --device cuda ^
    --output-dir %LOGDIR%\A3_pythia_L8 ^
    --layer 8 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    > %LOGDIR%\A3_pythia_L8_stdout.log 2>&1

set A3b_EXIT=%ERRORLEVEL%
echo {"job":"A3_pythia_L8","status":"finished","exit_code":%A3b_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [A3b] Pythia L8 finished (exit=%A3b_EXIT%): %date% %time%

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

REM Now L16 (mid-late layer for comparison)
echo A3c: Cross-Arch Pythia-1.4B Evolution (L16, 300 gen) > %SENTINEL%
echo {"job":"A3_pythia_L16","status":"started","time":"%date% %time%"} >> %QLOG%
echo [A3c] Pythia L16 — Started: %date% %time%

python src\evolve_1_5b.py ^
    --model EleutherAI/pythia-1.4b ^
    --device cuda ^
    --output-dir %LOGDIR%\A3_pythia_L16 ^
    --layer 16 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    > %LOGDIR%\A3_pythia_L16_stdout.log 2>&1

set A3c_EXIT=%ERRORLEVEL%
echo {"job":"A3_pythia_L16","status":"finished","exit_code":%A3c_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [A3c] Pythia L16 finished (exit=%A3c_EXIT%): %date% %time%

:done
echo IDLE > %SENTINEL%
echo.
echo ============================================================
echo  BATCH A COMPLETE: %date% %time%
echo  Results in: %LOGDIR%
echo  Queue log: %QLOG%
echo ============================================================
echo.
echo Check results\queue_log.jsonl for job timing.
echo Check %LOGDIR%\*_stdout.log for per-job output.
pause
