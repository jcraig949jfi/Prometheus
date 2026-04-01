@echo off
REM ============================================================
REM BATCH B — Revised per Aletheia review
REM
REM B1: Pythia multi-layer combo (L8+L10+L16)      ~1h
REM B2: Qwen ft model L22 evolution (500 gen)       ~4h
REM B3: Qwen ft model L19 evolution (500 gen)       ~4h
REM B4: Pythia corpus-first full pipeline            ~8h  (overnight)
REM
REM Total estimated: ~17h
REM
REM B1 answers additivity vs superadditivity on 2nd architecture.
REM B2 targets the specific channels: Finish Before 3rd (25%%
REM    crossing) and Siblings (9%%) at L22 on corpus-first model.
REM B3 evolves L19 natively on ft model for stronger margins.
REM B4 is confirmatory — tests if fine-tuning shifts Pythia's
REM    productive layers earlier. Overnight priority.
REM
REM SKIP/KILL:
REM   Create SKIP_B2, SKIP_B3, SKIP_B4 in ignis/ to skip a job
REM   Create KILL_QUEUE in ignis/ to abort after current job
REM ============================================================

setlocal
set LOGDIR=results\batch_B
set QLOG=results\queue_log.jsonl
set SENTINEL=CURRENT_JOB.txt
set FT_MODEL=results\corpus_first\stageB_finetune\ft_model

if not exist %LOGDIR% mkdir %LOGDIR%

echo ============================================================
echo  BATCH B — STRENGTHENING + CROSS-ARCH DEEPENING
echo  Started: %date% %time%
echo  Log: %LOGDIR%
echo  Kill: create KILL_QUEUE to abort
echo  Skip: create SKIP_B2, SKIP_B3, SKIP_B4 to skip jobs
echo ============================================================

REM ── B1: Pythia Multi-Layer Combo ────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo B1: Pythia Multi-Layer Combo (L8+L10+L16, all subsets) > %SENTINEL%
echo {"job":"B1_pythia_combo","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [B1] Pythia Multi-Layer Combo
echo [B1] Question: additive or superadditive? Does L8+L10+L16 beat 27/30?
echo [B1] Started: %date% %time%
echo.

python src\multilayer_eval.py ^
    --model EleutherAI/pythia-1.4b ^
    --device cuda ^
    --output-dir %LOGDIR%\B1_pythia_combo ^
    --genomes ^
        L8=results\batch_A\A3_pythia_L8\best_genome_1_5b.pt ^
        L10=results\batch_A\A3_pythia_L10\best_genome_1_5b.pt ^
        L16=results\batch_A\A3_pythia_L16\best_genome_1_5b.pt ^
    --epsilon-scales 0.5 1.0 1.5 2.0 ^
    > %LOGDIR%\B1_pythia_combo_stdout.log 2>&1

set B1_EXIT=%ERRORLEVEL%
echo {"job":"B1_pythia_combo","status":"finished","exit_code":%B1_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [B1] Finished (exit=%B1_EXIT%): %date% %time%

REM ── B2: Qwen FT Model L22 Evolution ────────────────────────
REM Target: Finish Before 3rd (25%% crossing) and Siblings (9%%)
REM L22 is the broad suppressor — on raw model it got 8 flips
REM but 3 breaks. On ft model, breaks should be eliminated.

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_B2 (
    echo [B2] SKIP_B2 detected. Skipping.
    echo {"job":"B2_qwen_ft_L22","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :b3
)

echo B2: Qwen FT L22 Evolution (500 gen) — targeting new channels > %SENTINEL%
echo {"job":"B2_qwen_ft_L22","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [B2] Evolve L22 on corpus-first model
echo [B2] L22 was the broad suppressor on raw model (8 flips, 3 breaks).
echo [B2] On ft model, v_proj dual-use is resolved — expect flips without breaks.
echo [B2] Specific targets: Finish Before 3rd, Siblings channels.
echo [B2] Started: %date% %time%
echo.

python src\evolve_1_5b.py ^
    --model %FT_MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\B2_qwen_ft_L22 ^
    --layer 22 ^
    --epsilon 3.0 ^
    --n-generations 500 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    > %LOGDIR%\B2_qwen_ft_L22_stdout.log 2>&1

set B2_EXIT=%ERRORLEVEL%
echo {"job":"B2_qwen_ft_L22","status":"finished","exit_code":%B2_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [B2] Finished (exit=%B2_EXIT%): %date% %time%

:b3

REM ── B3: Qwen FT Model L19 Evolution ────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_B3 (
    echo [B3] SKIP_B3 detected. Skipping.
    echo {"job":"B3_qwen_ft_L19","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :b4
)

echo B3: Qwen FT L19 Evolution (500 gen) — ft-native genome > %SENTINEL%
echo {"job":"B3_qwen_ft_L19","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [B3] Evolve L19 directly on corpus-first model
echo [B3] Raw-model L19 transferred well, but ft-native should strengthen margins
echo [B3] Started: %date% %time%
echo.

python src\evolve_1_5b.py ^
    --model %FT_MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\B3_qwen_ft_L19 ^
    --layer 19 ^
    --epsilon 3.0 ^
    --n-generations 500 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    > %LOGDIR%\B3_qwen_ft_L19_stdout.log 2>&1

set B3_EXIT=%ERRORLEVEL%
echo {"job":"B3_qwen_ft_L19","status":"finished","exit_code":%B3_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [B3] Finished (exit=%B3_EXIT%): %date% %time%

:b4

REM ── B4: Pythia Corpus-First (Overnight) ─────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_B4 (
    echo [B4] SKIP_B4 detected. Skipping.
    echo {"job":"B4_pythia_corpus_first","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :done
)

echo B4: Pythia Corpus-First Full Pipeline (overnight) > %SENTINEL%
echo {"job":"B4_pythia_corpus_first","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [B4] Pythia corpus-first — confirmatory, lowest priority
echo [B4] Does fine-tuning shift Pythia productive layers earlier?
echo [B4] Started: %date% %time%
echo.

python src\corpus_first.py ^
    --model EleutherAI/pythia-1.4b ^
    --device cuda ^
    --n-generations 300 ^
    --output-dir %LOGDIR%\B4_pythia_corpus_first ^
    > %LOGDIR%\B4_pythia_corpus_first_stdout.log 2>&1

set B4_EXIT=%ERRORLEVEL%
echo {"job":"B4_pythia_corpus_first","status":"finished","exit_code":%B4_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [B4] Finished (exit=%B4_EXIT%): %date% %time%

:done
echo IDLE > %SENTINEL%
echo.
echo ============================================================
echo  BATCH B COMPLETE: %date% %time%
echo  Results in: %LOGDIR%
echo  Queue log: %QLOG%
echo ============================================================
echo.
echo Check results\queue_log.jsonl for job timing.
echo Check %LOGDIR%\*_stdout.log for per-job output.
pause
