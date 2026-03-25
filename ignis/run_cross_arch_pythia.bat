@echo off
REM ============================================================================
REM  IGNIS CROSS-ARCHITECTURE — Pythia-1B-deduped (GPT-NeoX architecture)
REM  Full diagnostic suite on a non-Qwen model family
REM ============================================================================

echo ============================================================================
echo  IGNIS CROSS-ARCHITECTURE — Pythia-1B-deduped
echo  Architecture: GPT-NeoX (completely different from Qwen)
echo  16 layers, d_model=2048, 8 heads
echo ============================================================================
echo.

set PYTHON=python
set SRC=%~dp0src
set MODEL=EleutherAI/pythia-1b-deduped

echo [%time%] Job 1: Logit lens backward pass
%PYTHON% "%SRC%\logit_lens_backward.py" --model %MODEL% --device cuda --output-dir "%SRC%\results\ignis\pythia_1b" --skip-preflight
echo [%time%] Job 1 complete
echo.

echo [%time%] Job 2: Ejection decomposition
%PYTHON% "%SRC%\ejection_decompose.py" --model %MODEL% --device cuda --output-dir "%SRC%\results\ignis\ejection_pythia_1b" --skip-preflight
echo [%time%] Job 2 complete
echo.

echo [%time%] Job 3: v_proj diagnostic
%PYTHON% "%SRC%\vproj_diagnostic.py" --model %MODEL% --device cuda --output-dir "%SRC%\results\ignis\vproj_pythia_1b"
echo [%time%] Job 3 complete
echo.

echo [%time%] Job 4: Eval v2 (full battery)
%PYTHON% "%SRC%\eval_v2.py" --model %MODEL% --device cuda --output-dir "%SRC%\results\ignis\eval_v2_pythia_1b_full" --skip-logit-lens
echo [%time%] Job 4 complete
echo.

echo [%time%] Job 5: Basin escape histogram (layer 12 = 75%% depth)
%PYTHON% "%SRC%\basin_escape_histogram.py" --model %MODEL% --device cuda --output-dir "%SRC%\results\ignis\basin_pythia_1b" --layer 12 --trap "Overtake" --n-directions 50
echo [%time%] Job 5 complete
echo.

echo ============================================================================
echo  CROSS-ARCHITECTURE COMPLETE — Pythia-1B-deduped
echo  Results in: ignis\src\results\ignis\pythia_1b\
echo              ignis\src\results\ignis\ejection_pythia_1b\
echo              ignis\src\results\ignis\vproj_pythia_1b\
echo              ignis\src\results\ignis\eval_v2_pythia_1b_full\
echo              ignis\src\results\ignis\basin_pythia_1b\
echo ============================================================================
