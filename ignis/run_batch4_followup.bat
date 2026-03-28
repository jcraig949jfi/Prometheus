@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM  BATCH 4 FOLLOW-UP — Sequential GPU experiments
REM  Estimated runtime: 10-16 hours (overnight job)
REM
REM  Stage 1: Self-corpus on 1.5B with 0.417 genome (~30 min)
REM  Stage 2: Individual L21 and L24 evolution (~3-4 hours)
REM  Stage 3: gate+v LoRA at L22, L23 individually (~2-3 hours)
REM  Stage 4: Multi-layer joint L21-L24 gate+v (~4-6 hours)
REM  Stage 5: Self-corpus on best Stage 4 genome (~30 min)
REM ============================================================================

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

set S1_OK=0
set S2A_OK=0
set S2B_OK=0
set S3A_OK=0
set S3B_OK=0
set S4_OK=0
set S5_OK=0

echo ============================================================================
echo  BATCH 4 FOLLOW-UP — Started %date% %time%
echo ============================================================================

REM --- Genome from the targeted L22+L23 evolve run ---
set GENOME_PATH=%SCRIPT_DIR%src\results\ignis\evolve_20260323_192956\best_genome_1_5b.pt
if exist "%GENOME_PATH%" (
    echo Found genome: %GENOME_PATH%
) else (
    set GENOME_PATH=
    echo [WARN] No best_genome_1_5b.pt found. Stages 1 and 5 will run without steering.
)

REM ============================================================================
REM  STAGE 1: Self-corpus on 1.5B with 0.417 genome
REM  Cheapest experiment, highest expected ROI.
REM  At 135M/360M, self-corpus pushed metacognition to 75%%.
REM  ~30 min (300 attempts + 2 epochs fine-tune + eval)
REM ============================================================================
echo.
echo ============================================================================
echo  STAGE 1/5: Self-corpus on 1.5B with steering genome — %time%
echo ============================================================================

if defined GENOME_PATH (
    python src\loop_closure.py ^
        --model Qwen/Qwen2.5-1.5B-Instruct ^
        --device cuda ^
        --n-attempts 300 ^
        --genome "%GENOME_PATH%" ^
        --output-dir results\batch4_followup\stage1_selfcorpus
) else (
    python src\loop_closure.py ^
        --model Qwen/Qwen2.5-1.5B-Instruct ^
        --device cuda ^
        --n-attempts 300 ^
        --output-dir results\batch4_followup\stage1_selfcorpus
)
if errorlevel 1 (
    echo [FAIL] Stage 1 failed with error %errorlevel%
) else (
    set S1_OK=1
    echo [OK] Stage 1 complete
)
echo  Stage 1 ended: %time%

REM ============================================================================
REM  STAGE 2: Individual layer evolution at L21 and L24
REM  Tests whether adjacent layers carry ejection redundancy.
REM  500 generations each, popsize=32.
REM ============================================================================
echo.
echo ============================================================================
echo  STAGE 2/5: Individual layer evolution (L21, L24) — %time%
echo ============================================================================

echo --- Stage 2a: Layer 21 (ratio=0.75) ---
python src\evolve_1_5b.py ^
    --model Qwen/Qwen2.5-1.5B-Instruct ^
    --device cuda ^
    --n-generations 500 ^
    --epsilon 3.0 ^
    --layer 21 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    --output-dir results\batch4_followup\stage2_L21
if errorlevel 1 (
    echo [FAIL] Stage 2a L21 failed
) else (
    set S2A_OK=1
    echo [OK] Stage 2a L21 complete
)
echo  Stage 2a ended: %time%

echo --- Stage 2b: Layer 24 (ratio=0.857) ---
python src\evolve_1_5b.py ^
    --model Qwen/Qwen2.5-1.5B-Instruct ^
    --device cuda ^
    --n-generations 500 ^
    --epsilon 3.0 ^
    --layer 24 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    --output-dir results\batch4_followup\stage2_L24
if errorlevel 1 (
    echo [FAIL] Stage 2b L24 failed
) else (
    set S2B_OK=1
    echo [OK] Stage 2b L24 complete
)
echo  Stage 2b ended: %time%

REM ============================================================================
REM  STAGE 3: gate_proj + v_proj LoRA at L22 and L23 individually
REM  Tests whether MLP is a parallel suppression pathway.
REM  If ES improves (not just SR), ejection has both attn and MLP components.
REM ============================================================================
echo.
echo ============================================================================
echo  STAGE 3/5: gate+v LoRA at L22, L23 individually — %time%
echo ============================================================================

echo --- Stage 3a: L22 only ---
python src\evolve_lora_multilayer.py ^
    --model Qwen/Qwen2.5-1.5B-Instruct ^
    --device cuda ^
    --layers 22 ^
    --rank 8 ^
    --n-generations 500 ^
    --popsize 32 ^
    --stdev-init 0.005 ^
    --output-dir results\batch4_followup\stage3_lora_L22
if errorlevel 1 (
    echo [FAIL] Stage 3a L22 gate+v failed
) else (
    set S3A_OK=1
    echo [OK] Stage 3a L22 gate+v complete
)
echo  Stage 3a ended: %time%

echo --- Stage 3b: L23 only ---
python src\evolve_lora_multilayer.py ^
    --model Qwen/Qwen2.5-1.5B-Instruct ^
    --device cuda ^
    --layers 23 ^
    --rank 8 ^
    --n-generations 500 ^
    --popsize 32 ^
    --stdev-init 0.005 ^
    --output-dir results\batch4_followup\stage3_lora_L23
if errorlevel 1 (
    echo [FAIL] Stage 3b L23 gate+v failed
) else (
    set S3B_OK=1
    echo [OK] Stage 3b L23 gate+v complete
)
echo  Stage 3b ended: %time%

REM ============================================================================
REM  STAGE 4: Multi-layer joint evolution L21-L24 gate+v
REM  THE BIG ONE. 64-dim search space. Joint optimization.
REM  750 generations, popsize=48.
REM ============================================================================
echo.
echo ============================================================================
echo  STAGE 4/5: Multi-layer joint evolution L21-L24 — %time%
echo  Search dim: 4 layers x 2 weights x 8 rank = 64
echo ============================================================================

python src\evolve_lora_multilayer.py ^
    --model Qwen/Qwen2.5-1.5B-Instruct ^
    --device cuda ^
    --layers 21,22,23,24 ^
    --rank 8 ^
    --n-generations 750 ^
    --popsize 48 ^
    --stdev-init 0.003 ^
    --output-dir results\batch4_followup\stage4_multilayer
if errorlevel 1 (
    echo [FAIL] Stage 4 failed
) else (
    set S4_OK=1
    echo [OK] Stage 4 complete
)
echo  Stage 4 ended: %time%

REM ============================================================================
REM  STAGE 5: Self-corpus on best Stage 4 genome
REM  Closes the loop. If Stage 4 beat SR=0.417, train on verified chains.
REM  Note: loop_closure.py supports steering vector genomes (from evolve_1_5b).
REM  Multi-layer genomes use a different format — run without injection for now.
REM ============================================================================
echo.
echo ============================================================================
echo  STAGE 5/5: Self-corpus on best Stage 4 result — %time%
echo ============================================================================

python src\loop_closure.py ^
    --model Qwen/Qwen2.5-1.5B-Instruct ^
    --device cuda ^
    --n-attempts 300 ^
    --output-dir results\batch4_followup\stage5_selfcorpus_multilayer
if errorlevel 1 (
    echo [FAIL] Stage 5 failed
) else (
    set S5_OK=1
    echo [OK] Stage 5 complete
)
echo  Stage 5 ended: %time%

REM ============================================================================
REM  SUMMARY
REM ============================================================================
echo.
echo ============================================================================
echo  BATCH 4 FOLLOW-UP COMPLETE — %date% %time%
echo ============================================================================
echo.
echo  Stage results:
if %S1_OK%==1 (echo    [OK]   Stage 1: Self-corpus 1.5B) else (echo    [FAIL] Stage 1: Self-corpus 1.5B)
if %S2A_OK%==1 (echo    [OK]   Stage 2a: L21 evolution) else (echo    [FAIL] Stage 2a: L21 evolution)
if %S2B_OK%==1 (echo    [OK]   Stage 2b: L24 evolution) else (echo    [FAIL] Stage 2b: L24 evolution)
if %S3A_OK%==1 (echo    [OK]   Stage 3a: L22 gate+v) else (echo    [FAIL] Stage 3a: L22 gate+v)
if %S3B_OK%==1 (echo    [OK]   Stage 3b: L23 gate+v) else (echo    [FAIL] Stage 3b: L23 gate+v)
if %S4_OK%==1 (echo    [OK]   Stage 4: L21-L24 multilayer) else (echo    [FAIL] Stage 4: L21-L24 multilayer)
if %S5_OK%==1 (echo    [OK]   Stage 5: Self-corpus multilayer) else (echo    [FAIL] Stage 5: Self-corpus multilayer)
echo.
echo  Key result files:
echo    results\batch4_followup\stage1_selfcorpus\loop_closure_summary.json
echo    results\batch4_followup\stage2_L21\best_genome_1_5b.pt
echo    results\batch4_followup\stage2_L24\best_genome_1_5b.pt
echo    results\batch4_followup\stage3_lora_L22\best_multilayer_genome.pt
echo    results\batch4_followup\stage3_lora_L23\best_multilayer_genome.pt
echo    results\batch4_followup\stage4_multilayer\best_multilayer_genome.pt
echo    results\batch4_followup\stage5_selfcorpus_multilayer\loop_closure_summary.json
echo.
echo  Compare SR across approaches:
echo    L22+L23 v_proj only (Rhea batch4): SR=0.417 (65K params)
echo    L21 steering vector:                Check stage2_L21
echo    L24 steering vector:                Check stage2_L24
echo    L22 gate+v LoRA:                    Check stage3_lora_L22
echo    L23 gate+v LoRA:                    Check stage3_lora_L23
echo    L21-L24 joint gate+v:               Check stage4_multilayer
echo ============================================================================

endlocal
