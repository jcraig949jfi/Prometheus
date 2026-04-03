@echo off
REM ============================================================
REM BATCH D FALLBACK — Llama corpus-first failed (loop_closure
REM doesn't handle non-Qwen models). Running alternative high-
REM value experiments instead.
REM
REM D1: Llama L4 evolution (early layer, 25%% depth)  ~3h
REM D2: Llama L4+L8+L12 combo                         ~30m
REM D3: Qwen ft L22+L19 combo (ft-native genomes)     ~30m
REM D4: Qwen v3 battery with winning combo             ~5m
REM D5: Pythia v3 battery with L16 genome              ~5m
REM
REM Total estimated: ~4h
REM ============================================================

setlocal
set LOGDIR=results\batch_D_fallback
set QLOG=results\queue_log.jsonl
set SENTINEL=CURRENT_JOB.txt

if not exist %LOGDIR% mkdir %LOGDIR%

echo ============================================================
echo  BATCH D FALLBACK
echo  Corpus-first failed on Llama. Running alternatives.
echo  Started: %date% %time%
echo ============================================================

REM ── D1: Llama L4 Evolution ─────────────────────────────────
REM We have L8 (50%%) and L12 (75%%). L4 (25%%) tests whether
REM early layers work on raw Llama like they did on raw Qwen.

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo D1: Llama L4 Evolution (300 gen, 25%% depth) > %SENTINEL%
echo {"job":"D1_llama_L4","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [D1] Llama L4 — early layer (25%% of 16 layers)
echo [D1] Does early injection work on raw Llama?
echo [D1] Started: %date% %time%
echo.

python src\evolve_1_5b.py ^
    --model meta-llama/Llama-3.2-1B ^
    --device cuda ^
    --output-dir %LOGDIR%\D1_llama_L4 ^
    --layer 4 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    > %LOGDIR%\D1_llama_L4_stdout.log 2>&1

set D1_EXIT=%ERRORLEVEL%
echo {"job":"D1_llama_L4","status":"finished","exit_code":%D1_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [D1] Finished (exit=%D1_EXIT%): %date% %time%

REM ── D2: Llama 3-Layer Combo ─────────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo D2: Llama L4+L8+L12 Combo > %SENTINEL%
echo {"job":"D2_llama_3layer_combo","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [D2] Llama 3-layer combo — does adding early layer help?
echo [D2] Started: %date% %time%
echo.

python src\multilayer_eval.py ^
    --model meta-llama/Llama-3.2-1B ^
    --device cuda ^
    --output-dir %LOGDIR%\D2_llama_combo ^
    --genomes ^
        L4=%LOGDIR%\D1_llama_L4\best_genome_1_5b.pt ^
        L8=results\batch_C_llama\C2_llama_L8\best_genome_1_5b.pt ^
        L12=results\batch_C_llama\C3_llama_L12\best_genome_1_5b.pt ^
    --epsilon-scales 0.5 1.0 1.5 2.0 ^
    > %LOGDIR%\D2_llama_combo_stdout.log 2>&1

set D2_EXIT=%ERRORLEVEL%
echo {"job":"D2_llama_3layer_combo","status":"finished","exit_code":%D2_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [D2] Finished (exit=%D2_EXIT%): %date% %time%

REM ── D3: Qwen FT L22+L19 Combo (ft-native genomes) ─────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo D3: Qwen FT L22+L19 Combo (ft-native genomes) > %SENTINEL%
echo {"job":"D3_qwen_ft_combo","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [D3] Testing ft-native L19 + ft-native L22 on Qwen ft model
echo [D3] L19 found Finish Before 3rd. L22 found Siblings. Together?
echo [D3] Started: %date% %time%
echo.

python src\multilayer_eval.py ^
    --model results\corpus_first\stageB_finetune\ft_model ^
    --device cuda ^
    --output-dir %LOGDIR%\D3_qwen_ft_combo ^
    --genomes ^
        L19_ft=results\batch_B\B3_qwen_ft_L19\best_genome_1_5b.pt ^
        L22_ft=results\batch_B\B2_qwen_ft_L22\best_genome_1_5b.pt ^
        L19_raw=results\layer_sweep\L19\best_genome_1_5b.pt ^
        L20_raw=results\layer_sweep\L20\best_genome_1_5b.pt ^
        L21_raw=results\batch4_followup\stage2_L21\best_genome_1_5b.pt ^
    --epsilon-scales 0.5 1.0 1.5 ^
    > %LOGDIR%\D3_qwen_ft_combo_stdout.log 2>&1

set D3_EXIT=%ERRORLEVEL%
echo {"job":"D3_qwen_ft_combo","status":"finished","exit_code":%D3_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [D3] Finished (exit=%D3_EXIT%): %date% %time%

REM ── D4: Qwen v3 Battery with Winning Combo ─────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo D4: Qwen v3 Battery + Steering > %SENTINEL%
echo {"job":"D4_qwen_v3_steered","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [D4] Can the L19+L20+L21 winning combo flip v3 traps too?
echo [D4] Started: %date% %time%
echo.

python src\stability_test.py ^
    --model results\corpus_first\stageB_finetune\ft_model ^
    --device cuda ^
    --output-dir %LOGDIR%\D4_qwen_v3 ^
    --n-runs 1 ^
    --epsilon-scale 1.5 ^
    > %LOGDIR%\D4_qwen_v3_stdout.log 2>&1

set D4_EXIT=%ERRORLEVEL%
echo {"job":"D4_qwen_v3_steered","status":"finished","exit_code":%D4_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [D4] Finished (exit=%D4_EXIT%): %date% %time%

:done
echo IDLE > %SENTINEL%
echo.
echo ============================================================
echo  BATCH D FALLBACK COMPLETE: %date% %time%
echo  Results in: %LOGDIR%
echo  Queue log: %QLOG%
echo ============================================================
pause
