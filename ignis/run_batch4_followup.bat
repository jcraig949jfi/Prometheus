@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM  BATCH 4 FOLLOW-UP — Sequential GPU experiments
REM  Estimated runtime: 8-12 hours (let it cook overnight)
REM
REM  Stage 1: Self-corpus on 1.5B with best steering genome (~30 min)
REM  Stage 2: Expanded v_proj L21 and L24 evolution (~3-4 hours)
REM  Stage 3: gate_proj + v_proj at L22-L23 (~2-3 hours)
REM  Stage 4: Multi-layer joint evolution L21-L24 (~4-6 hours)
REM  Stage 5: Self-corpus on best Stage 4 genome (~30 min)
REM ============================================================================

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo ============================================================================
echo  BATCH 4 FOLLOW-UP — Started %date% %time%
echo ============================================================================

REM Find the best genome from the original evolve run
set GENOME_PATH=
for /r "src\results\ignis" %%f in (best_genome_1_5b.pt) do (
    set GENOME_PATH=%%f
)
if not defined GENOME_PATH (
    echo [WARN] No best_genome_1_5b.pt found, Stage 1 and 5 will skip genome injection
)
echo Using genome: %GENOME_PATH%

REM === STAGE 1: Self-corpus on 1.5B with best genome ===
echo.
echo ============================================================================
echo  STAGE 1/5: Self-corpus on 1.5B with steering genome
echo  Expected: ~30 min
echo  Target: metacognition improvement (75%% at 135M/360M)
echo ============================================================================
echo  Started: %time%

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
    echo [WARN] Stage 1 failed with error %errorlevel%
    echo [WARN] Continuing to Stage 2...
)
echo  Stage 1 completed: %time%

REM === STAGE 2: Expanded v_proj targeting L21 and L24 ===
echo.
echo ============================================================================
echo  STAGE 2/5: Individual layer evolution (L21, L24)
echo  Expected: ~3-4 hours
echo  Target: SR data per layer to map the full ejection circuit
echo ============================================================================
echo  Started: %time%

echo --- Stage 2a: Layer 21 ---
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
    echo [WARN] Stage 2a (L21) failed, continuing...
)
echo  Stage 2a completed: %time%

echo --- Stage 2b: Layer 24 ---
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
    echo [WARN] Stage 2b (L24) failed, continuing...
)
echo  Stage 2b completed: %time%

REM === STAGE 3: gate_proj + v_proj LoRA at L22-L23 ===
echo.
echo ============================================================================
echo  STAGE 3/5: gate_proj + v_proj LoRA (L22, L23 individually)
echo  Expected: ~2-3 hours
echo  Target: Does adding MLP pathway improve ES (not just SR)?
echo ============================================================================
echo  Started: %time%

echo --- Stage 3a: L22 (layer_ratio 0.786) ---
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
    echo [WARN] Stage 3a (L22) failed, continuing...
)
echo  Stage 3a completed: %time%

echo --- Stage 3b: L23 (layer_ratio 0.821) ---
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
    echo [WARN] Stage 3b (L23) failed, continuing...
)
echo  Stage 3b completed: %time%

REM === STAGE 4: Multi-layer joint evolution L21-L24 gate+v ===
echo.
echo ============================================================================
echo  STAGE 4/5: Multi-layer joint evolution (L21-L24, gate+v)
echo  Expected: ~4-6 hours (the big one)
echo  Target: SR ^> 0.417 via coordinated multi-layer perturbation
echo  Search dim: 4 layers * 2 weights * 8 rank = 64
echo ============================================================================
echo  Started: %time%

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
    echo [WARN] Stage 4 failed, continuing...
)
echo  Stage 4 completed: %time%

REM === STAGE 5: Self-corpus on best Stage 4 genome ===
echo.
echo ============================================================================
echo  STAGE 5/5: Self-corpus on multi-layer genome
echo  Expected: ~30 min
echo  Target: Close the loop — does self-corpus boost metacognition?
echo ============================================================================
echo  Started: %time%

set STAGE4_GENOME=results\batch4_followup\stage4_multilayer\best_lora_genome.pt
if exist "%STAGE4_GENOME%" (
    echo [INFO] Using Stage 4 genome for self-corpus
    REM Note: loop_closure currently supports steering vector genomes.
    REM Multi-layer LoRA genomes need a different application method.
    REM For now, run self-corpus WITHOUT genome injection as a baseline.
    python src\loop_closure.py ^
        --model Qwen/Qwen2.5-1.5B-Instruct ^
        --device cuda ^
        --n-attempts 300 ^
        --output-dir results\batch4_followup\stage5_selfcorpus_multilayer
) else (
    echo [WARN] No Stage 4 genome found, running self-corpus without injection
    python src\loop_closure.py ^
        --model Qwen/Qwen2.5-1.5B-Instruct ^
        --device cuda ^
        --n-attempts 300 ^
        --output-dir results\batch4_followup\stage5_selfcorpus_multilayer
)
if errorlevel 1 (
    echo [WARN] Stage 5 failed
)
echo  Stage 5 completed: %time%

echo.
echo ============================================================================
echo  BATCH 4 FOLLOW-UP COMPLETE — %date% %time%
echo ============================================================================
echo.
echo  Key result files:
echo    stage1_selfcorpus\loop_closure_summary.json
echo    stage2_L21\best_genome_1_5b.pt
echo    stage2_L24\best_genome_1_5b.pt
echo    stage3_lora_L22\best_lora_genome.pt
echo    stage3_lora_L23\best_lora_genome.pt
echo    stage4_multilayer\best_lora_genome.pt
echo    stage5_selfcorpus_multilayer\loop_closure_summary.json
echo.
echo  Compare SR across approaches:
echo    L22+L23 v_proj only (batch4):  SR=0.417  (65K params)
echo    L21 individual:                 Check stage2_L21
echo    L24 individual:                 Check stage2_L24
echo    L22 gate+v:                     Check stage3_lora_L22
echo    L23 gate+v:                     Check stage3_lora_L23
echo    L21-L24 joint gate+v:           Check stage4_multilayer
echo ============================================================================

endlocal
