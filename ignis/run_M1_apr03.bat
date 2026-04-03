@echo off
REM ============================================================
REM  M1 BATCH — April 3: Generation Validation + Phi-2 Depth Sweep
REM  Expected runtime: ~14-18 hours
REM ============================================================
echo ============================================================
echo  M1 BATCH — Generation Validation + Phi-2 Depth Sweep
echo  Started: %date% %time%
echo ============================================================

REM --- PHASE 1: Generation Validation (~3h) ---
REM Tests whether logit flips translate to actual text changes.
REM This is Risk 2 (washout) — the biggest open gap in our story.

echo.
echo [G1] Generation check: Llama 1B (best genome: L8)
echo [G1] Started: %date% %time%
python src\generation_check.py ^
    --model meta-llama/Llama-3.2-1B ^
    --genome results\batch_C_llama\C2_llama_L8\best_genome_1_5b.pt ^
    --device cuda ^
    --epsilon 3.0 ^
    --output-dir results\generation_validation\llama_L8
echo [G1] Finished (exit=%ERRORLEVEL%): %date% %time%

echo.
echo [G2] Generation check: Pythia 1.4B (best genome: L16)
echo [G2] Started: %date% %time%
python src\generation_check.py ^
    --model EleutherAI/pythia-1.4b ^
    --genome results\batch_A\A3_pythia_L16\best_genome_1_5b.pt ^
    --device cuda ^
    --epsilon 3.0 ^
    --output-dir results\generation_validation\pythia_L16
echo [G2] Finished (exit=%ERRORLEVEL%): %date% %time%

echo.
echo [G3] Generation check: Qwen 0.5B (best genome: L10)
echo [G3] Started: %date% %time%
python src\generation_check.py ^
    --model Qwen/Qwen2.5-0.5B-Instruct ^
    --genome results\batch_E\E4a_qwen05_L10\best_genome_1_5b.pt ^
    --device cuda ^
    --epsilon 3.0 ^
    --output-dir results\generation_validation\qwen05_L10
echo [G3] Finished (exit=%ERRORLEVEL%): %date% %time%

echo.
echo [G4] Generation check: Phi-2 (best single-layer genome: L20)
echo [G4] Started: %date% %time%
python src\generation_check.py ^
    --model microsoft/phi-2 ^
    --genome results\batch_phi2\P3_phi2_L20\best_genome_1_5b.pt ^
    --device cuda ^
    --epsilon 3.0 ^
    --output-dir results\generation_validation\phi2_L20
echo [G4] Finished (exit=%ERRORLEVEL%): %date% %time%

echo.
echo ============================================================
echo  PHASE 1 COMPLETE (Generation Validation): %date% %time%
echo ============================================================

REM --- PHASE 2: Phi-2 Depth Curve Expansion (~12h) ---
REM We only have L12, L20, L28. Need L4, L8, L16, L24 to map the
REM full depth curve. Phi-2 single-layer results were weak (+1-2 flips)
REM — either suppression is truly distributed or we missed the sweet spot.

echo.
echo [P1] Phi-2 CMA-ES at L4 (12%% depth, 300 gen)
echo [P1] Started: %date% %time%
python src\evolve_1_5b.py ^
    --model microsoft/phi-2 ^
    --device cuda ^
    --layer 4 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    --output-dir results\batch_phi2_depth\phi2_L4
echo [P1] Finished (exit=%ERRORLEVEL%): %date% %time%

echo.
echo [P2] Phi-2 CMA-ES at L8 (25%% depth, 300 gen)
echo [P2] Started: %date% %time%
python src\evolve_1_5b.py ^
    --model microsoft/phi-2 ^
    --device cuda ^
    --layer 8 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    --output-dir results\batch_phi2_depth\phi2_L8
echo [P2] Finished (exit=%ERRORLEVEL%): %date% %time%

echo.
echo [P3] Phi-2 CMA-ES at L16 (50%% depth, 300 gen)
echo [P3] Started: %date% %time%
python src\evolve_1_5b.py ^
    --model microsoft/phi-2 ^
    --device cuda ^
    --layer 16 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    --output-dir results\batch_phi2_depth\phi2_L16
echo [P3] Finished (exit=%ERRORLEVEL%): %date% %time%

echo.
echo [P4] Phi-2 CMA-ES at L24 (75%% depth, 300 gen)
echo [P4] Started: %date% %time%
python src\evolve_1_5b.py ^
    --model microsoft/phi-2 ^
    --device cuda ^
    --layer 24 ^
    --epsilon 3.0 ^
    --n-generations 300 ^
    --popsize 32 ^
    --stdev-init 0.05 ^
    --output-dir results\batch_phi2_depth\phi2_L24
echo [P4] Finished (exit=%ERRORLEVEL%): %date% %time%

echo.
echo ============================================================
echo  M1 BATCH COMPLETE: %date% %time%
echo  Phase 1 results: results\generation_validation\
echo  Phase 2 results: results\batch_phi2_depth\
echo ============================================================
pause
