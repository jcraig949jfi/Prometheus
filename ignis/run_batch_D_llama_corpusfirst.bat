@echo off
REM ============================================================
REM BATCH D — Llama Corpus-First + Transfer Test
REM
REM D1: Llama corpus-first full pipeline             ~6h
REM D2: Transfer raw genomes to Llama ft model       ~30m
REM D3: Evolve L8 on Llama ft model (300 gen)        ~3h
REM D4: Llama ft multi-layer combo                   ~30m
REM D5: Llama ft ghost trap                          ~5m
REM
REM Total estimated: ~10h
REM
REM Hypothesis: Corpus-first shifts Llama's productive layers
REM earlier, like it did on Qwen. Llama's huge margins (+49 on
REM L8) suggest the residual stream is highly responsive — the
REM ft model may show even more dramatic layer shifts.
REM
REM SKIP/KILL:
REM   Create SKIP_D2 through SKIP_D5 to skip jobs
REM   Create KILL_QUEUE in ignis/ to abort
REM ============================================================

setlocal
set LOGDIR=results\batch_D_llama
set QLOG=results\queue_log.jsonl
set SENTINEL=CURRENT_JOB.txt
set MODEL=meta-llama/Llama-3.2-1B

if not exist %LOGDIR% mkdir %LOGDIR%

echo ============================================================
echo  BATCH D — LLAMA CORPUS-FIRST + TRANSFER TEST
echo  Started: %date% %time%
echo  Log: %LOGDIR%
echo ============================================================

REM ── D1: Corpus-First Full Pipeline ─────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo D1: Llama Corpus-First Full Pipeline > %SENTINEL%
echo {"job":"D1_llama_corpus_first","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [D1] Llama corpus-first — does fine-tuning shift productive layers earlier?
echo [D1] Llama L8 had +49 margins raw. What happens after corpus-first?
echo [D1] Started: %date% %time%
echo.

python src\corpus_first.py ^
    --model %MODEL% ^
    --device cuda ^
    --n-generations 300 ^
    --output-dir %LOGDIR%\D1_corpus_first ^
    > %LOGDIR%\D1_corpus_first_stdout.log 2>&1

set D1_EXIT=%ERRORLEVEL%
echo {"job":"D1_llama_corpus_first","status":"finished","exit_code":%D1_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [D1] Finished (exit=%D1_EXIT%): %date% %time%

REM Check if ft model was produced
set FT_MODEL=%LOGDIR%\D1_corpus_first\stageB_finetune\ft_model
if not exist %FT_MODEL%\config.json (
    echo [D1] No fine-tuned model found. Corpus-first may have failed.
    echo [D1] Skipping D2-D5 (all depend on ft model).
    echo {"job":"D1_llama_corpus_first","status":"no_ft_model","time":"%date% %time%"} >> %QLOG%
    goto :done
)

echo [D1] Fine-tuned model found at %FT_MODEL%

REM ── D2: Transfer Raw Genomes to FT Model ───────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_D2 (
    echo [D2] SKIP_D2 detected. Skipping.
    echo {"job":"D2_llama_transfer","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :d3
)

echo D2: Transfer Raw Llama Genomes to FT Model > %SENTINEL%
echo {"job":"D2_llama_transfer","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [D2] Testing raw L8+L12 genomes on fine-tuned Llama
echo [D2] Key question: do genomes transfer cross-model like on Qwen?
echo [D2] Started: %date% %time%
echo.

python src\multilayer_eval.py ^
    --model %FT_MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\D2_transfer ^
    --genomes ^
        L8=results\batch_C_llama\C2_llama_L8\best_genome_1_5b.pt ^
        L12=results\batch_C_llama\C3_llama_L12\best_genome_1_5b.pt ^
    --epsilon-scales 0.5 1.0 1.5 2.0 ^
    > %LOGDIR%\D2_transfer_stdout.log 2>&1

set D2_EXIT=%ERRORLEVEL%
echo {"job":"D2_llama_transfer","status":"finished","exit_code":%D2_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [D2] Finished (exit=%D2_EXIT%): %date% %time%

:d3

REM ── D3: Evolve L8 on Llama FT Model ────────────────────────
REM L8 was the star on raw Llama. Does ft-native L8 do even better?

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_D3 (
    echo [D3] SKIP_D3 detected. Skipping.
    echo {"job":"D3_llama_ft_L8","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :d4
)

echo D3: Llama FT L8 Evolution (300 gen) > %SENTINEL%
echo {"job":"D3_llama_ft_L8","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [D3] Evolve L8 on corpus-first Llama
echo [D3] Raw L8 got +49 margins. Can ft-native do better?
echo [D3] Started: %date% %time%
echo.

python src\evolve_1_5b.py ^
    --model %FT_MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\D3_llama_ft_L8 ^
    --layer 8 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    > %LOGDIR%\D3_llama_ft_L8_stdout.log 2>&1

set D3_EXIT=%ERRORLEVEL%
echo {"job":"D3_llama_ft_L8","status":"finished","exit_code":%D3_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [D3] Finished (exit=%D3_EXIT%): %date% %time%

:d4

REM ── D4: Llama FT Multi-Layer Combo ─────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_D4 (
    echo [D4] SKIP_D4 detected. Skipping.
    echo {"job":"D4_llama_ft_combo","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :d5
)

echo D4: Llama FT Multi-Layer Combo > %SENTINEL%
echo {"job":"D4_llama_ft_combo","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [D4] Combo: ft-native L8 + raw L8 + raw L12 on ft model
echo [D4] Started: %date% %time%
echo.

REM Use whatever genomes exist — ft-native L8 from D3, raw L8 and L12 from batch C
python src\multilayer_eval.py ^
    --model %FT_MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\D4_ft_combo ^
    --genomes ^
        L8_raw=results\batch_C_llama\C2_llama_L8\best_genome_1_5b.pt ^
        L12_raw=results\batch_C_llama\C3_llama_L12\best_genome_1_5b.pt ^
        L8_ft=%LOGDIR%\D3_llama_ft_L8\best_genome_1_5b.pt ^
    --epsilon-scales 0.5 1.0 1.5 ^
    > %LOGDIR%\D4_ft_combo_stdout.log 2>&1

set D4_EXIT=%ERRORLEVEL%
echo {"job":"D4_llama_ft_combo","status":"finished","exit_code":%D4_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [D4] Finished (exit=%D4_EXIT%): %date% %time%

:d5

REM ── D5: Ghost Trap on FT Model ─────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)
if exist SKIP_D5 (
    echo [D5] SKIP_D5 detected. Skipping.
    echo {"job":"D5_llama_ft_ghost","status":"skipped","time":"%date% %time%"} >> %QLOG%
    goto :done
)

echo D5: Llama FT Ghost Trap > %SENTINEL%
echo {"job":"D5_llama_ft_ghost","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [D5] Ghost trap on ft-native L8 — does corpus-first change the mechanism?
echo [D5] Started: %date% %time%
echo.

python src\ghost_trap_analysis.py ^
    --model %FT_MODEL% ^
    --device cuda ^
    --output-dir %LOGDIR%\D5_ft_ghost ^
    --epsilon-scale 1.0 ^
    --genomes ^
        L8_ft=%LOGDIR%\D3_llama_ft_L8\best_genome_1_5b.pt ^
    > %LOGDIR%\D5_ft_ghost_stdout.log 2>&1

set D5_EXIT=%ERRORLEVEL%
echo {"job":"D5_llama_ft_ghost","status":"finished","exit_code":%D5_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [D5] Finished (exit=%D5_EXIT%): %date% %time%

:done
echo IDLE > %SENTINEL%
echo.
echo ============================================================
echo  BATCH D COMPLETE: %date% %time%
echo  Results in: %LOGDIR%
echo  Queue log: %QLOG%
echo ============================================================
pause
