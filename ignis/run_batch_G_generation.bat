@echo off
REM ============================================================
REM BATCH G — Generation Validation (Risk 2)
REM
REM Logit margin flips != text changes. Round 2 showed Z=40.6
REM on logits with 0-1 generation flips. This batch runs
REM generation_check.py on the best combos across architectures
REM to test whether steering actually changes what the model SAYS.
REM
REM G1: Qwen 1.5B, v2, L19+L20+L21 best genomes       ~20m
REM G2: Llama 1B, v2, L8 genome                        ~15m
REM G3: Phi-2, v2, L12+L20 genomes                     ~20m
REM G4: Qwen 1.5B, v3, best genome (requires batch F)  ~20m
REM
REM Total estimated: ~75m
REM ============================================================

setlocal
set LOGDIR=results\batch_G
set QLOG=results\queue_log.jsonl
set SENTINEL=CURRENT_JOB.txt

if not exist %LOGDIR% mkdir %LOGDIR%

echo ============================================================
echo  BATCH G — GENERATION VALIDATION (RISK 2)
echo  Started: %date% %time%
echo ============================================================

REM ── G1: Qwen 1.5B v2 Best Genomes (L19+L20+L21) ───────────
REM These are the multilayer combo that gave 30/30 bypass on v2.

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo G1: Qwen 1.5B v2 Generation Check (L19) > %SENTINEL%
echo {"job":"G1a_qwen15_v2_L19","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [G1a] Qwen 1.5B v2 generation check — L19
echo [G1a] Started: %date% %time%
echo.

python src\generation_check.py ^
    --model Qwen/Qwen2.5-1.5B-Instruct ^
    --device cuda ^
    --output-dir %LOGDIR%\G1a_qwen15_v2_L19 ^
    --genome results\layer_sweep\batch4_followup\L19\best_genome_1_5b.pt ^
    --epsilon 3.0 ^
    --battery v2 ^
    > %LOGDIR%\G1a_qwen15_v2_L19_stdout.log 2>&1

set G1a_EXIT=%ERRORLEVEL%
echo {"job":"G1a_qwen15_v2_L19","status":"finished","exit_code":%G1a_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [G1a] Finished (exit=%G1a_EXIT%): %date% %time%

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo G1: Qwen 1.5B v2 Generation Check (L20) > %SENTINEL%
echo {"job":"G1b_qwen15_v2_L20","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [G1b] Qwen 1.5B v2 generation check — L20
echo [G1b] Started: %date% %time%
echo.

python src\generation_check.py ^
    --model Qwen/Qwen2.5-1.5B-Instruct ^
    --device cuda ^
    --output-dir %LOGDIR%\G1b_qwen15_v2_L20 ^
    --genome results\layer_sweep\batch4_followup\L20\best_genome_1_5b.pt ^
    --epsilon 3.0 ^
    --battery v2 ^
    > %LOGDIR%\G1b_qwen15_v2_L20_stdout.log 2>&1

set G1b_EXIT=%ERRORLEVEL%
echo {"job":"G1b_qwen15_v2_L20","status":"finished","exit_code":%G1b_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [G1b] Finished (exit=%G1b_EXIT%): %date% %time%

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo G1: Qwen 1.5B v2 Generation Check (L21) > %SENTINEL%
echo {"job":"G1c_qwen15_v2_L21","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [G1c] Qwen 1.5B v2 generation check — L21
echo [G1c] Started: %date% %time%
echo.

python src\generation_check.py ^
    --model Qwen/Qwen2.5-1.5B-Instruct ^
    --device cuda ^
    --output-dir %LOGDIR%\G1c_qwen15_v2_L21 ^
    --genome results\layer_sweep\batch4_followup\L21\best_genome_1_5b.pt ^
    --epsilon 3.0 ^
    --battery v2 ^
    > %LOGDIR%\G1c_qwen15_v2_L21_stdout.log 2>&1

set G1c_EXIT=%ERRORLEVEL%
echo {"job":"G1c_qwen15_v2_L21","status":"finished","exit_code":%G1c_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [G1c] Finished (exit=%G1c_EXIT%): %date% %time%

REM ── G2: Llama 1B v2 L8 Genome ─────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo G2: Llama 1B v2 Generation Check (L8) > %SENTINEL%
echo {"job":"G2_llama_v2_L8","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [G2] Llama 1B v2 generation check — L8
echo [G2] Started: %date% %time%
echo.

python src\generation_check.py ^
    --model meta-llama/Llama-3.2-1B ^
    --device cuda ^
    --output-dir %LOGDIR%\G2_llama_v2_L8 ^
    --genome results\batch_C_llama\C2_llama_L8\best_genome_1_5b.pt ^
    --epsilon 3.0 ^
    --battery v2 ^
    > %LOGDIR%\G2_llama_v2_L8_stdout.log 2>&1

set G2_EXIT=%ERRORLEVEL%
echo {"job":"G2_llama_v2_L8","status":"finished","exit_code":%G2_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [G2] Finished (exit=%G2_EXIT%): %date% %time%

REM ── G3: Phi-2 v2 L12+L20 Genomes ──────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo G3: Phi-2 v2 Generation Check (L12) > %SENTINEL%
echo {"job":"G3a_phi2_v2_L12","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [G3a] Phi-2 v2 generation check — L12
echo [G3a] Started: %date% %time%
echo.

python src\generation_check.py ^
    --model microsoft/phi-2 ^
    --device cuda ^
    --output-dir %LOGDIR%\G3a_phi2_v2_L12 ^
    --genome results\batch_phi2\P2_phi2_L12\best_genome_1_5b.pt ^
    --epsilon 3.0 ^
    --battery v2 ^
    > %LOGDIR%\G3a_phi2_v2_L12_stdout.log 2>&1

set G3a_EXIT=%ERRORLEVEL%
echo {"job":"G3a_phi2_v2_L12","status":"finished","exit_code":%G3a_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [G3a] Finished (exit=%G3a_EXIT%): %date% %time%

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo G3: Phi-2 v2 Generation Check (L20) > %SENTINEL%
echo {"job":"G3b_phi2_v2_L20","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [G3b] Phi-2 v2 generation check — L20
echo [G3b] Started: %date% %time%
echo.

python src\generation_check.py ^
    --model microsoft/phi-2 ^
    --device cuda ^
    --output-dir %LOGDIR%\G3b_phi2_v2_L20 ^
    --genome results\batch_phi2\P3_phi2_L20\best_genome_1_5b.pt ^
    --epsilon 3.0 ^
    --battery v2 ^
    > %LOGDIR%\G3b_phi2_v2_L20_stdout.log 2>&1

set G3b_EXIT=%ERRORLEVEL%
echo {"job":"G3b_phi2_v2_L20","status":"finished","exit_code":%G3b_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [G3b] Finished (exit=%G3b_EXIT%): %date% %time%

REM ── G4: Qwen 1.5B v3 Best Genome (from batch F) ───────────
REM This depends on batch F completing. Skip if genome doesn't exist.

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

if not exist results\batch_F_v3\F2_qwen15_v3_L10\best_genome_1_5b.pt (
    echo [G4] SKIPPED: batch_F_v3 genome not found yet.
    echo [G4] Run batch F first, then re-run this batch or run G4 manually.
    echo {"job":"G4_qwen15_v3","status":"skipped","reason":"genome_not_found","time":"%date% %time%"} >> %QLOG%
    goto :done
)

echo G4: Qwen 1.5B v3 Generation Check (L10) > %SENTINEL%
echo {"job":"G4_qwen15_v3_L10","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [G4] Qwen 1.5B v3 generation check — L10 (from batch F)
echo [G4] Started: %date% %time%
echo.

python src\generation_check.py ^
    --model Qwen/Qwen2.5-1.5B-Instruct ^
    --device cuda ^
    --output-dir %LOGDIR%\G4_qwen15_v3_L10 ^
    --genome results\batch_F_v3\F2_qwen15_v3_L10\best_genome_1_5b.pt ^
    --epsilon 3.0 ^
    --battery v3 ^
    > %LOGDIR%\G4_qwen15_v3_L10_stdout.log 2>&1

set G4_EXIT=%ERRORLEVEL%
echo {"job":"G4_qwen15_v3_L10","status":"finished","exit_code":%G4_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [G4] Finished (exit=%G4_EXIT%): %date% %time%

:done
echo IDLE > %SENTINEL%
echo.
echo ============================================================
echo  BATCH G COMPLETE: %date% %time%
echo  Results in: %LOGDIR%
echo  Queue log: %QLOG%
echo ============================================================
pause
