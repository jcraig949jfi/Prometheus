@echo off
REM ============================================================
REM  M2 BATCH — April 3: Corpus-First on Llama + Pythia
REM  Expected runtime: ~10-14 hours
REM
REM  IMPORTANT: Both Llama and Pythia already have ft_model/ from
REM  prior failed runs (crashed on Unicode delta, now fixed).
REM  corpus_first.py will detect existing ft_model and skip Stage B.
REM  This means we go straight to Stages C-E (~4-6h each model).
REM ============================================================
echo ============================================================
echo  M2 BATCH — Corpus-First: Llama + Pythia
echo  Started: %date% %time%
echo ============================================================

REM --- Llama Corpus-First (Stages C-E, ~5h) ---
REM Stage B ft_model already exists at:
REM   results\batch_D_llama\D1_corpus_first\stageB_finetune\ft_model\
REM Llama has 16 layers, --layer 8 = 50%% depth (same as best raw steering)

echo.
echo [L1] Corpus-first: Llama 1B (will skip Stage B, resume from C)
echo [L1] Started: %date% %time%
python src\corpus_first.py ^
    --model meta-llama/Llama-3.2-1B ^
    --device cuda ^
    --skip-baseline ^
    --layer 8 ^
    --n-generations 500 ^
    --output-dir results\batch_D_llama\D1_corpus_first
echo [L1] Finished (exit=%ERRORLEVEL%): %date% %time%

REM --- Pythia Corpus-First (Stages C-E, ~5h) ---
REM Stage B ft_model already exists at:
REM   results\batch_B\B4_pythia_corpus_first\stageB_finetune\ft_model\
REM Pythia has 24 layers, --layer 16 = 67%% depth (same as best raw steering)

echo.
echo [P1] Corpus-first: Pythia 1.4B (will skip Stage B, resume from C)
echo [P1] Started: %date% %time%
python src\corpus_first.py ^
    --model EleutherAI/pythia-1.4b ^
    --device cuda ^
    --skip-baseline ^
    --layer 16 ^
    --n-generations 500 ^
    --output-dir results\batch_B\B4_pythia_corpus_first
echo [P1] Finished (exit=%ERRORLEVEL%): %date% %time%

echo.
echo ============================================================
echo  M2 BATCH COMPLETE: %date% %time%
echo  Llama results: results\batch_D_llama\D1_corpus_first\
echo  Pythia results: results\batch_B\B4_pythia_corpus_first\
echo ============================================================
pause
