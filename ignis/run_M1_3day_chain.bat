@echo off
REM ============================================================
REM M1 3-DAY CHAIN — Run after Batch E finishes
REM
REM Phase 1: Llama corpus-first results (ft model already exists!)
REM Phase 2: v3 steered experiments (3 architectures)
REM Phase 3: Pythia corpus-first (now fixed)
REM Phase 4: Qwen-0.5B corpus-first
REM Phase 5: Gap fill
REM
REM Total estimated: ~30h
REM Card should not idle. KILL_QUEUE to abort.
REM ============================================================

setlocal
set QLOG=results\queue_log.jsonl
set SENTINEL=CURRENT_JOB.txt

echo ============================================================
echo  M1 3-DAY CHAIN
echo  Started: %date% %time%
echo ============================================================

REM ════════════════════════════════════════════════════════════
REM PHASE 1: Llama FT results (~4h)
REM The D1 corpus-first actually SUCCEEDED — ft_model exists at
REM results\batch_D_llama\D1_corpus_first\stageB_finetune\ft_model
REM It crashed on a Unicode print, not on training. Use it now.
REM ════════════════════════════════════════════════════════════

set LLAMA_FT=results\batch_D_llama\D1_corpus_first\stageB_finetune\ft_model
set P1DIR=results\M1_chain\P1_llama_ft

if not exist results\M1_chain mkdir results\M1_chain
if not exist %P1DIR% mkdir %P1DIR%

REM ── P1a: Transfer raw genomes to Llama ft ───────────────────

if exist KILL_QUEUE goto :done

echo P1a: Transfer raw Llama genomes to ft model > %SENTINEL%
echo {"job":"P1a_llama_ft_transfer","status":"started","time":"%date% %time%"} >> %QLOG%
echo [P1a] Raw L4+L8+L12 on Llama ft model — Started: %date% %time%

python src\multilayer_eval.py ^
    --model %LLAMA_FT% ^
    --device cuda ^
    --output-dir %P1DIR%\transfer ^
    --genomes ^
        L4=results\batch_D_fallback\D1_llama_L4\best_genome_1_5b.pt ^
        L8=results\batch_C_llama\C2_llama_L8\best_genome_1_5b.pt ^
        L12=results\batch_C_llama\C3_llama_L12\best_genome_1_5b.pt ^
    --epsilon-scales 0.5 1.0 1.5 2.0 ^
    > %P1DIR%\transfer_stdout.log 2>&1

echo {"job":"P1a_llama_ft_transfer","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%

REM ── P1b: Evolve L4 on Llama ft ─────────────────────────────

if exist KILL_QUEUE goto :done

echo P1b: Evolve L4 on Llama ft (300 gen) > %SENTINEL%
echo {"job":"P1b_llama_ft_L4","status":"started","time":"%date% %time%"} >> %QLOG%
echo [P1b] Llama ft-native L4 — Started: %date% %time%

python src\evolve_1_5b.py ^
    --model %LLAMA_FT% ^
    --device cuda ^
    --output-dir %P1DIR%\evolve_L4 ^
    --layer 4 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    > %P1DIR%\evolve_L4_stdout.log 2>&1

echo {"job":"P1b_llama_ft_L4","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%

REM ── P1c: Llama ft ghost trap ────────────────────────────────

if exist KILL_QUEUE goto :done

echo P1c: Llama ft ghost trap > %SENTINEL%
echo {"job":"P1c_llama_ft_ghost","status":"started","time":"%date% %time%"} >> %QLOG%

python src\ghost_trap_analysis.py ^
    --model %LLAMA_FT% ^
    --device cuda ^
    --output-dir %P1DIR%\ghost ^
    --epsilon-scale 1.0 ^
    --genomes ^
        L4=results\batch_D_fallback\D1_llama_L4\best_genome_1_5b.pt ^
        L8=results\batch_C_llama\C2_llama_L8\best_genome_1_5b.pt ^
    > %P1DIR%\ghost_stdout.log 2>&1

echo {"job":"P1c_llama_ft_ghost","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%

REM ════════════════════════════════════════════════════════════
REM PHASE 2: v3 steered experiments (~2h)
REM Can steering flip the HARDER traps?
REM ════════════════════════════════════════════════════════════

set P2DIR=results\M1_chain\P2_v3_steered
if not exist %P2DIR% mkdir %P2DIR%

REM ── P2a: Qwen 1.5B ft — v3 with winning combo ─────────────

if exist KILL_QUEUE goto :done

echo P2a: Qwen ft v3 steered (L19+L20+L21 x1.5) > %SENTINEL%
echo {"job":"P2a_qwen_v3_steered","status":"started","time":"%date% %time%"} >> %QLOG%
echo [P2a] v3 battery + winning combo on Qwen ft — Started: %date% %time%

python src\v3_baseline_eval.py ^
    --model results\corpus_first\stageB_finetune\ft_model ^
    --device cuda ^
    --output-dir %P2DIR%\qwen_ft ^
    > %P2DIR%\qwen_ft_stdout.log 2>&1

echo {"job":"P2a_qwen_v3_steered","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%

REM ── P2b: Pythia — v3 evolve L16 (300 gen) ──────────────────
REM Evolve directly against v3 traps? No — v3_baseline_eval doesn't
REM do evolution. We need to evolve on v2 (which fitness.py uses)
REM and then TEST on v3. Let's just baseline the ft models on v3.

REM ── P2c: Llama ft — v3 baseline ────────────────────────────

if exist KILL_QUEUE goto :done

echo P2c: Llama ft v3 baseline > %SENTINEL%
echo {"job":"P2c_llama_ft_v3","status":"started","time":"%date% %time%"} >> %QLOG%

python src\v3_baseline_eval.py ^
    --model %LLAMA_FT% ^
    --device cuda ^
    --output-dir %P2DIR%\llama_ft ^
    > %P2DIR%\llama_ft_stdout.log 2>&1

echo {"job":"P2c_llama_ft_v3","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%

REM ════════════════════════════════════════════════════════════
REM PHASE 3: Pythia corpus-first retry (~8h)
REM loop_closure.py now fixed for GPT-NeoX layer access + Unicode
REM ════════════════════════════════════════════════════════════

set P3DIR=results\M1_chain\P3_pythia_cf
if not exist %P3DIR% mkdir %P3DIR%

if exist KILL_QUEUE goto :done

echo P3: Pythia corpus-first (fixed loop_closure) > %SENTINEL%
echo {"job":"P3_pythia_corpus_first","status":"started","time":"%date% %time%"} >> %QLOG%
echo [P3] Pythia corpus-first retry — loop_closure fixed — Started: %date% %time%

python src\corpus_first.py ^
    --model EleutherAI/pythia-1.4b ^
    --device cuda ^
    --n-generations 300 ^
    --output-dir %P3DIR% ^
    > %P3DIR%\stdout.log 2>&1

set P3_EXIT=%ERRORLEVEL%
echo {"job":"P3_pythia_corpus_first","status":"finished","exit_code":%P3_EXIT%,"time":"%date% %time%"} >> %QLOG%

REM If Pythia ft model exists, do transfer test
set PYTHIA_FT=%P3DIR%\stageB_finetune\ft_model
if exist %PYTHIA_FT%\config.json (
    echo P3b: Pythia ft transfer test > %SENTINEL%
    echo {"job":"P3b_pythia_ft_transfer","status":"started","time":"%date% %time%"} >> %QLOG%

    python src\multilayer_eval.py ^
        --model %PYTHIA_FT% ^
        --device cuda ^
        --output-dir %P3DIR%\transfer ^
        --genomes ^
            L8=results\batch_A\A3_pythia_L8\best_genome_1_5b.pt ^
            L10=results\batch_A\A3_pythia_L10\best_genome_1_5b.pt ^
            L16=results\batch_A\A3_pythia_L16\best_genome_1_5b.pt ^
        --epsilon-scales 0.5 1.0 1.5 ^
        > %P3DIR%\transfer_stdout.log 2>&1

    echo {"job":"P3b_pythia_ft_transfer","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%

    REM Ghost trap on Pythia ft
    echo P3c: Pythia ft ghost trap > %SENTINEL%
    echo {"job":"P3c_pythia_ft_ghost","status":"started","time":"%date% %time%"} >> %QLOG%

    python src\ghost_trap_analysis.py ^
        --model %PYTHIA_FT% ^
        --device cuda ^
        --output-dir %P3DIR%\ghost ^
        --epsilon-scale 1.0 ^
        --genomes ^
            L16=results\batch_A\A3_pythia_L16\best_genome_1_5b.pt ^
        > %P3DIR%\ghost_stdout.log 2>&1

    echo {"job":"P3c_pythia_ft_ghost","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%

    REM v3 on Pythia ft
    echo P3d: Pythia ft v3 baseline > %SENTINEL%
    echo {"job":"P3d_pythia_ft_v3","status":"started","time":"%date% %time%"} >> %QLOG%

    python src\v3_baseline_eval.py ^
        --model %PYTHIA_FT% ^
        --device cuda ^
        --output-dir %P3DIR%\v3 ^
        > %P3DIR%\v3_stdout.log 2>&1

    echo {"job":"P3d_pythia_ft_v3","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%
)

REM ════════════════════════════════════════════════════════════
REM PHASE 4: Qwen-0.5B corpus-first (~6h)
REM loop_closure works on Qwen. Fill the small-scale ft cell.
REM ════════════════════════════════════════════════════════════

set P4DIR=results\M1_chain\P4_qwen05_cf
if not exist %P4DIR% mkdir %P4DIR%

if exist KILL_QUEUE goto :done

echo P4: Qwen-0.5B corpus-first > %SENTINEL%
echo {"job":"P4_qwen05_corpus_first","status":"started","time":"%date% %time%"} >> %QLOG%
echo [P4] Qwen-0.5B corpus-first — Started: %date% %time%

python src\corpus_first.py ^
    --model Qwen/Qwen2.5-0.5B-Instruct ^
    --device cuda ^
    --n-generations 300 ^
    --output-dir %P4DIR% ^
    > %P4DIR%\stdout.log 2>&1

echo {"job":"P4_qwen05_corpus_first","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%

REM If 0.5B ft model exists, transfer test
set Q05_FT=%P4DIR%\stageB_finetune\ft_model
if exist %Q05_FT%\config.json (
    echo P4b: Qwen-0.5B ft transfer > %SENTINEL%
    echo {"job":"P4b_qwen05_ft_transfer","status":"started","time":"%date% %time%"} >> %QLOG%

    python src\multilayer_eval.py ^
        --model %Q05_FT% ^
        --device cuda ^
        --output-dir %P4DIR%\transfer ^
        --genomes ^
            L10=%P4DIR%\stageD_evolve\best_genome_1_5b.pt ^
        --epsilon-scales 0.5 1.0 1.5 2.0 ^
        > %P4DIR%\transfer_stdout.log 2>&1

    echo {"job":"P4b_qwen05_ft_transfer","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%
)

REM ════════════════════════════════════════════════════════════
REM PHASE 5: Llama corpus-first retry (now fixed) (~8h)
REM ════════════════════════════════════════════════════════════

set P5DIR=results\M1_chain\P5_llama_cf_retry
if not exist %P5DIR% mkdir %P5DIR%

if exist KILL_QUEUE goto :done

echo P5: Llama corpus-first retry (fixed) > %SENTINEL%
echo {"job":"P5_llama_corpus_first","status":"started","time":"%date% %time%"} >> %QLOG%
echo [P5] Llama corpus-first with fixed loop_closure — Started: %date% %time%

python src\corpus_first.py ^
    --model meta-llama/Llama-3.2-1B ^
    --device cuda ^
    --n-generations 300 ^
    --output-dir %P5DIR% ^
    > %P5DIR%\stdout.log 2>&1

echo {"job":"P5_llama_corpus_first","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%

REM If Llama ft produced, do full characterization
set LLAMA_FT2=%P5DIR%\stageB_finetune\ft_model
if exist %LLAMA_FT2%\config.json (
    echo P5b: Llama ft2 transfer > %SENTINEL%
    echo {"job":"P5b_llama_ft2_transfer","status":"started","time":"%date% %time%"} >> %QLOG%

    python src\multilayer_eval.py ^
        --model %LLAMA_FT2% ^
        --device cuda ^
        --output-dir %P5DIR%\transfer ^
        --genomes ^
            L4=results\batch_D_fallback\D1_llama_L4\best_genome_1_5b.pt ^
            L8=results\batch_C_llama\C2_llama_L8\best_genome_1_5b.pt ^
            L12=results\batch_C_llama\C3_llama_L12\best_genome_1_5b.pt ^
        --epsilon-scales 0.5 1.0 1.5 2.0 ^
        > %P5DIR%\transfer_stdout.log 2>&1

    echo {"job":"P5b_llama_ft2_transfer","status":"finished","exit_code":%ERRORLEVEL%,"time":"%date% %time%"} >> %QLOG%
)

:done
echo IDLE > %SENTINEL%
echo.
echo ============================================================
echo  M1 3-DAY CHAIN COMPLETE: %date% %time%
echo  Results in: results\M1_chain\
echo  Queue log: %QLOG%
echo ============================================================
pause
