@echo off
REM ============================================================
REM BATCH E — Cross-Architecture Genome Transfer + 0.5B Scaling
REM
REM Pythia and Llama share d_model=2048, so their genomes are
REM dimensionally compatible. Can a genome evolved on one
REM architecture steer a completely different architecture?
REM
REM Qwen d_model=1536 — incompatible, skip.
REM
REM E1: Pythia genomes (L8,L10,L16) → Llama model      ~30m
REM E2: Llama genomes (L4,L8,L12) → Pythia model       ~30m
REM E3: Qwen-0.5B baseline (v2 + v3)                   ~5m
REM E4: Qwen-0.5B L10/L18 evolution (300 gen each)     ~4h
REM E5: Qwen-0.5B combo + ghost trap                   ~30m
REM E6: Qwen-0.5B v3 baseline                          ~2m
REM
REM Total estimated: ~6h
REM ============================================================

setlocal
set LOGDIR=results\batch_E
set QLOG=results\queue_log.jsonl
set SENTINEL=CURRENT_JOB.txt

if not exist %LOGDIR% mkdir %LOGDIR%

echo ============================================================
echo  BATCH E — CROSS-ARCH TRANSFER + 0.5B SCALING
echo  Started: %date% %time%
echo ============================================================

REM ── E1: Pythia Genomes → Llama ──────────────────────────────
REM Both d_model=2048. Layers differ (Pythia 24, Llama 16) but
REM the vectors are the same dimensionality.
REM Inject Pythia's L8,L10,L16 into Llama at matching % depths.

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo E1: Pythia Genomes on Llama Model > %SENTINEL%
echo {"job":"E1_pythia_to_llama","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [E1] Cross-arch transfer: Pythia genomes steering Llama
echo [E1] Same d_model (2048). Different architecture family.
echo [E1] Started: %date% %time%
echo.

python src\multilayer_eval.py ^
    --model meta-llama/Llama-3.2-1B ^
    --device cuda ^
    --output-dir %LOGDIR%\E1_pythia_to_llama ^
    --genomes ^
        PythiaL8=results\batch_A\A3_pythia_L8\best_genome_1_5b.pt ^
        PythiaL10=results\batch_A\A3_pythia_L10\best_genome_1_5b.pt ^
        PythiaL16=results\batch_A\A3_pythia_L16\best_genome_1_5b.pt ^
    --epsilon-scales 0.5 1.0 1.5 2.0 ^
    > %LOGDIR%\E1_pythia_to_llama_stdout.log 2>&1

set E1_EXIT=%ERRORLEVEL%
echo {"job":"E1_pythia_to_llama","status":"finished","exit_code":%E1_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [E1] Finished (exit=%E1_EXIT%): %date% %time%

REM ── E2: Llama Genomes → Pythia ──────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo E2: Llama Genomes on Pythia Model > %SENTINEL%
echo {"job":"E2_llama_to_pythia","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [E2] Cross-arch transfer: Llama genomes steering Pythia
echo [E2] Started: %date% %time%
echo.

python src\multilayer_eval.py ^
    --model EleutherAI/pythia-1.4b ^
    --device cuda ^
    --output-dir %LOGDIR%\E2_llama_to_pythia ^
    --genomes ^
        LlamaL4=results\batch_D_fallback\D1_llama_L4\best_genome_1_5b.pt ^
        LlamaL8=results\batch_C_llama\C2_llama_L8\best_genome_1_5b.pt ^
        LlamaL12=results\batch_C_llama\C3_llama_L12\best_genome_1_5b.pt ^
    --epsilon-scales 0.5 1.0 1.5 2.0 ^
    > %LOGDIR%\E2_llama_to_pythia_stdout.log 2>&1

set E2_EXIT=%ERRORLEVEL%
echo {"job":"E2_llama_to_pythia","status":"finished","exit_code":%E2_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [E2] Finished (exit=%E2_EXIT%): %date% %time%

REM ── E3: Qwen-0.5B Baseline ─────────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo E3: Qwen-0.5B v3 Baseline > %SENTINEL%
echo {"job":"E3_qwen05_v3","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [E3] Qwen-0.5B v3 battery baseline — small scale data point
echo [E3] Started: %date% %time%
echo.

python src\v3_baseline_eval.py ^
    --model Qwen/Qwen2.5-0.5B-Instruct ^
    --device cuda ^
    --output-dir %LOGDIR%\E3_qwen05_v3 ^
    > %LOGDIR%\E3_qwen05_v3_stdout.log 2>&1

set E3_EXIT=%ERRORLEVEL%
echo {"job":"E3_qwen05_v3","status":"finished","exit_code":%E3_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [E3] Finished (exit=%E3_EXIT%): %date% %time%

REM ── E4a: Qwen-0.5B L10 Evolution ───────────────────────────
REM Qwen-0.5B has 24 layers. L10 = 42%% depth.

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo E4a: Qwen-0.5B L10 Evolution (300 gen) > %SENTINEL%
echo {"job":"E4a_qwen05_L10","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [E4a] Qwen-0.5B L10 (42%% depth)
echo [E4a] Started: %date% %time%
echo.

python src\evolve_1_5b.py ^
    --model Qwen/Qwen2.5-0.5B-Instruct ^
    --device cuda ^
    --output-dir %LOGDIR%\E4a_qwen05_L10 ^
    --layer 10 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    > %LOGDIR%\E4a_qwen05_L10_stdout.log 2>&1

set E4a_EXIT=%ERRORLEVEL%
echo {"job":"E4a_qwen05_L10","status":"finished","exit_code":%E4a_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [E4a] Finished (exit=%E4a_EXIT%): %date% %time%

REM ── E4b: Qwen-0.5B L18 Evolution ───────────────────────────
REM L18 = 75%% depth.

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo E4b: Qwen-0.5B L18 Evolution (300 gen) > %SENTINEL%
echo {"job":"E4b_qwen05_L18","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [E4b] Qwen-0.5B L18 (75%% depth)
echo [E4b] Started: %date% %time%
echo.

python src\evolve_1_5b.py ^
    --model Qwen/Qwen2.5-0.5B-Instruct ^
    --device cuda ^
    --output-dir %LOGDIR%\E4b_qwen05_L18 ^
    --layer 18 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    > %LOGDIR%\E4b_qwen05_L18_stdout.log 2>&1

set E4b_EXIT=%ERRORLEVEL%
echo {"job":"E4b_qwen05_L18","status":"finished","exit_code":%E4b_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [E4b] Finished (exit=%E4b_EXIT%): %date% %time%

REM ── E5: Qwen-0.5B Combo + Ghost ────────────────────────────

if exist KILL_QUEUE (
    echo [QUEUE] KILL_QUEUE detected. Aborting.
    goto :done
)

echo E5a: Qwen-0.5B Combo > %SENTINEL%
echo {"job":"E5a_qwen05_combo","status":"started","time":"%date% %time%"} >> %QLOG%
echo.
echo [E5a] Qwen-0.5B combo L10+L18
echo [E5a] Started: %date% %time%
echo.

python src\multilayer_eval.py ^
    --model Qwen/Qwen2.5-0.5B-Instruct ^
    --device cuda ^
    --output-dir %LOGDIR%\E5a_qwen05_combo ^
    --genomes ^
        L10=%LOGDIR%\E4a_qwen05_L10\best_genome_1_5b.pt ^
        L18=%LOGDIR%\E4b_qwen05_L18\best_genome_1_5b.pt ^
    --epsilon-scales 0.5 1.0 1.5 2.0 ^
    > %LOGDIR%\E5a_qwen05_combo_stdout.log 2>&1

set E5a_EXIT=%ERRORLEVEL%
echo {"job":"E5a_qwen05_combo","status":"finished","exit_code":%E5a_EXIT%,"time":"%date% %time%"} >> %QLOG%

echo E5b: Qwen-0.5B Ghost Trap > %SENTINEL%
echo {"job":"E5b_qwen05_ghost","status":"started","time":"%date% %time%"} >> %QLOG%

python src\ghost_trap_analysis.py ^
    --model Qwen/Qwen2.5-0.5B-Instruct ^
    --device cuda ^
    --output-dir %LOGDIR%\E5b_qwen05_ghost ^
    --epsilon-scale 1.0 ^
    --genomes ^
        L10=%LOGDIR%\E4a_qwen05_L10\best_genome_1_5b.pt ^
        L18=%LOGDIR%\E4b_qwen05_L18\best_genome_1_5b.pt ^
    > %LOGDIR%\E5b_qwen05_ghost_stdout.log 2>&1

set E5b_EXIT=%ERRORLEVEL%
echo {"job":"E5b_qwen05_ghost","status":"finished","exit_code":%E5b_EXIT%,"time":"%date% %time%"} >> %QLOG%
echo [E5] Finished: %date% %time%

:done
echo IDLE > %SENTINEL%
echo.
echo ============================================================
echo  BATCH E COMPLETE: %date% %time%
echo  Results in: %LOGDIR%
echo  Queue log: %QLOG%
echo ============================================================
pause
