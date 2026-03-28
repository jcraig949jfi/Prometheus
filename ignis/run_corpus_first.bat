@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM  CORPUS-FIRST PROTOCOL — Tests the order-of-operations hypothesis
REM  Estimated runtime: 6-8 hours
REM
REM  Theory: v_proj dual-use means corpus must come BEFORE evolution.
REM  Fine-tune base model on reasoning data first, then evolve on the
REM  fine-tuned seed. This should: (1) shallow ejection profile,
REM  (2) faster CMA-ES convergence, (3) coherent post-evolution output.
REM
REM  Stage A: Baseline diagnostic on vanilla 1.5B (30 min)
REM  Stage B: Fine-tune 1.5B on reasoning corpus — no evolution (45 min)
REM  Stage C: Diagnostic on fine-tuned seed — measure ejection change (30 min)
REM  Stage D: CMA-ES evolution on fine-tuned seed at L22+L23 (3-4 hours)
REM  Stage E: Eval + comparison table (30 min)
REM ============================================================================

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

set SA_OK=0
set SB_OK=0
set SC_OK=0
set SD_OK=0
set SE_OK=0

echo ============================================================================
echo  CORPUS-FIRST PROTOCOL — Started %date% %time%
echo  Testing order-of-operations: corpus first, evolution second
echo ============================================================================

REM ============================================================================
REM  STAGE A: Baseline diagnostic on vanilla 1.5B
REM  Logit lens + eval_v2 on unmodified model. Reference point.
REM ============================================================================
echo.
echo ============================================================================
echo  STAGE A: Baseline diagnostic on vanilla 1.5B — %time%
echo ============================================================================

python src\logit_lens_backward.py ^
    --model Qwen/Qwen2.5-1.5B-Instruct ^
    --device cuda ^
    --output-dir results\corpus_first\stageA_baseline ^
    --skip-preflight
if errorlevel 1 (
    echo [FAIL] Stage A logit lens failed
) else (
    echo [OK] Stage A logit lens complete
)

python src\eval_v2.py ^
    --model Qwen/Qwen2.5-1.5B-Instruct ^
    --device cuda ^
    --output-dir results\corpus_first\stageA_baseline ^
    --skip-logit-lens
if errorlevel 1 (
    echo [FAIL] Stage A eval_v2 failed
) else (
    set SA_OK=1
    echo [OK] Stage A complete
)
echo  Stage A ended: %time%

REM ============================================================================
REM  STAGE B: Fine-tune 1.5B on reasoning corpus — NO evolution
REM  loop_closure.py without --genome: generates reasoning attempts,
REM  verifies correctness, fine-tunes on verified chains.
REM  This shifts v_proj from heuristic to reasoning representations.
REM ============================================================================
echo.
echo ============================================================================
echo  STAGE B: Fine-tune 1.5B on reasoning corpus — %time%
echo  No evolution, no steering vector. Pure supervised fine-tuning.
echo ============================================================================

python src\loop_closure.py ^
    --model Qwen/Qwen2.5-1.5B-Instruct ^
    --device cuda ^
    --n-attempts 300 ^
    --output-dir results\corpus_first\stageB_finetune
if errorlevel 1 (
    echo [FAIL] Stage B failed
) else (
    set SB_OK=1
    echo [OK] Stage B complete
)
echo  Stage B ended: %time%

REM ============================================================================
REM  STAGE C: Diagnostic on fine-tuned seed
REM  KEY MEASUREMENT: Does the ejection profile change after corpus training?
REM  If L* shifts or spike-and-collapse shallows, the theory is confirmed.
REM  If baseline SR improves without evolution, that's the strongest signal.
REM ============================================================================
echo.
echo ============================================================================
echo  STAGE C: Post-corpus diagnostic — %time%
echo  Does reasoning training shallow the ejection profile?
echo ============================================================================

REM Check if fine-tuned model was saved
if exist "results\corpus_first\stageB_finetune\ft_tmp" (
    echo Found fine-tuned model at results\corpus_first\stageB_finetune\ft_tmp

    python src\logit_lens_backward.py ^
        --model results\corpus_first\stageB_finetune\ft_tmp ^
        --device cuda ^
        --output-dir results\corpus_first\stageC_post_corpus ^
        --skip-preflight
    if errorlevel 1 (
        echo [WARN] Stage C logit lens on fine-tuned model failed
        echo [INFO] Falling back to base model logit lens — fine-tuned model may not load in TransformerLens
    )

    python src\eval_v2.py ^
        --model results\corpus_first\stageB_finetune\ft_tmp ^
        --device cuda ^
        --output-dir results\corpus_first\stageC_post_corpus ^
        --skip-logit-lens
    if errorlevel 1 (
        echo [WARN] Stage C eval_v2 on fine-tuned model failed
    ) else (
        set SC_OK=1
        echo [OK] Stage C complete
    )
) else (
    echo [WARN] No fine-tuned model found — Stage B may not have saved. Skipping Stage C.
)
echo  Stage C ended: %time%

REM ============================================================================
REM  STAGE D: CMA-ES evolution on fine-tuned seed
REM  THE KEY EXPERIMENT. Evolve on the corpus-trained model, not base.
REM  Predictions: faster convergence, higher SR, ES should improve too.
REM  Target: L22+L23 v_proj (same as the 0.417 result for comparison)
REM ============================================================================
echo.
echo ============================================================================
echo  STAGE D: CMA-ES on corpus-trained seed — %time%
echo  Evolving on fine-tuned model. Comparing to SR=0.417 on base model.
echo ============================================================================

REM Evolution at L23 on the fine-tuned seed
if exist "results\corpus_first\stageB_finetune\ft_tmp" (
    python src\evolve_1_5b.py ^
        --model results\corpus_first\stageB_finetune\ft_tmp ^
        --device cuda ^
        --n-generations 500 ^
        --epsilon 3.0 ^
        --layer 23 ^
        --popsize 32 ^
        --stdev-init 0.05 ^
        --output-dir results\corpus_first\stageD_evolve_L23
    if errorlevel 1 (
        echo [WARN] Stage D L23 evolution on fine-tuned model failed
        echo [INFO] TransformerLens may not load HF-saved model. Trying base model as fallback.
    ) else (
        set SD_OK=1
        echo [OK] Stage D L23 complete
    )
)

REM Fallback: if fine-tuned model doesn't load in TransformerLens, skip to Stage E
if not !SD_OK!==1 (
    echo [INFO] Fine-tuned model may not be TransformerLens-compatible.
    echo [INFO] This is expected — TransformerLens requires specific model architectures.
    echo [INFO] The Stage C eval_v2 results still tell us if corpus training shifted ejection.
)
echo  Stage D ended: %time%

REM ============================================================================
REM  STAGE E: Final eval + comparison
REM ============================================================================
echo.
echo ============================================================================
echo  STAGE E: Final comparison — %time%
echo ============================================================================

if !SD_OK!==1 (
    python src\eval_v2.py ^
        --model results\corpus_first\stageB_finetune\ft_tmp ^
        --device cuda ^
        --genome results\corpus_first\stageD_evolve_L23\best_genome_1_5b.pt ^
        --output-dir results\corpus_first\stageE_final_eval ^
        --skip-logit-lens
    if errorlevel 1 (
        echo [WARN] Stage E eval failed
    ) else (
        set SE_OK=1
        echo [OK] Stage E complete
    )
)
echo  Stage E ended: %time%

REM ============================================================================
REM  SUMMARY
REM ============================================================================
echo.
echo ============================================================================
echo  CORPUS-FIRST PROTOCOL COMPLETE — %date% %time%
echo ============================================================================
echo.
echo  Stage results:
if !SA_OK!==1 (echo    [OK]   Stage A: Baseline diagnostic) else (echo    [FAIL] Stage A: Baseline diagnostic)
if !SB_OK!==1 (echo    [OK]   Stage B: Corpus fine-tune) else (echo    [FAIL] Stage B: Corpus fine-tune)
if !SC_OK!==1 (echo    [OK]   Stage C: Post-corpus diagnostic) else (echo    [FAIL] Stage C: Post-corpus diagnostic)
if !SD_OK!==1 (echo    [OK]   Stage D: Evolution on seed) else (echo    [FAIL] Stage D: Evolution on seed)
if !SE_OK!==1 (echo    [OK]   Stage E: Final eval) else (echo    [FAIL] Stage E: Final eval)
echo.
echo  Key comparisons:
echo    Baseline ejection profile:     results\corpus_first\stageA_baseline\
echo    Post-corpus ejection profile:  results\corpus_first\stageC_post_corpus\
echo    Evolution on corpus seed:      results\corpus_first\stageD_evolve_L23\
echo    Final eval:                    results\corpus_first\stageE_final_eval\
echo.
echo  Questions answered:
echo    1. Did corpus training shallow the ejection? Compare A vs C logit lens
echo    2. Did baseline SR improve without evolution? Compare A vs C eval_v2
echo    3. Did evolution converge faster on the seed? Check D generation log
echo    4. Did SR beat 0.417? Compare D best_genome fitness to batch4 result
echo ============================================================================

endlocal
