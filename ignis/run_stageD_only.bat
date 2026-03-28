@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM  STAGE D ONLY — CMA-ES evolution on corpus-trained seed
REM  Restart after crash. Stages A-C already complete.
REM  Estimated: 4-6 hours on GPU, longer if EvoTorch falls back to CPU
REM ============================================================================

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo ============================================================================
echo  STAGE D: CMA-ES on corpus-trained seed — %date% %time%
echo  Evolving on fine-tuned model. Comparing to SR=0.417 on base model.
echo  Reducing to 200 generations (was 500) to complete in reasonable time.
echo ============================================================================

if exist "results\corpus_first\stageB_finetune\ft_model" (
    python src\evolve_1_5b.py ^
        --model results\corpus_first\stageB_finetune\ft_model ^
        --device cuda ^
        --n-generations 200 ^
        --epsilon 3.0 ^
        --layer 23 ^
        --popsize 32 ^
        --stdev-init 0.05 ^
        --output-dir results\corpus_first\stageD_evolve_L23
    if errorlevel 1 (
        echo [FAIL] Stage D failed
    ) else (
        echo [OK] Stage D complete
    )
) else (
    echo [ERROR] Fine-tuned model not found at results\corpus_first\stageB_finetune\ft_model
)

echo.
echo  Stage D ended: %date% %time%

REM Run final eval if Stage D succeeded
if exist "results\corpus_first\stageD_evolve_L23\best_genome_1_5b.pt" (
    echo.
    echo ============================================================================
    echo  STAGE E: Final eval — %date% %time%
    echo ============================================================================
    python src\eval_v2.py ^
        --model results\corpus_first\stageB_finetune\ft_model ^
        --device cuda ^
        --genome results\corpus_first\stageD_evolve_L23\best_genome_1_5b.pt ^
        --output-dir results\corpus_first\stageE_final_eval ^
        --skip-logit-lens
    if errorlevel 1 (
        echo [FAIL] Stage E failed
    ) else (
        echo [OK] Stage E complete
    )
)

echo.
echo ============================================================================
echo  DONE — %date% %time%
echo  Check results\corpus_first\stageD_evolve_L23\ for evolution log
echo  Check results\corpus_first\stageE_final_eval\ for final comparison
echo ============================================================================
pause
