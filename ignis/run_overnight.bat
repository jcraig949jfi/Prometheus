@echo off
REM ============================================================================
REM  IGNIS OVERNIGHT RUN — Cross-Architecture Universality Test
REM  March 24-25, 2026
REM
REM  Tests whether the ejection mechanism exists in Llama and Gemma,
REM  not just Qwen/SmolLM2. If it does, the finding is universal.
REM
REM  Estimated runtime: 6-8 hours
REM  Fire and forget. Check results in the morning.
REM ============================================================================

echo ============================================================================
echo  IGNIS OVERNIGHT RUN
echo  Cross-Architecture Universality Test
echo  Llama-3.2-1B + Gemma-3-1B
echo ============================================================================
echo.

set PYTHON=python
set SRC=%~dp0src
set PYTHONIOENCODING=utf-8

REM ── Job 1: Llama-3.2-1B Logit Lens (find L*) ─────────────────────────────
echo [%time%] Job 1: Llama-3.2-1B logit lens backward pass
%PYTHON% "%SRC%\logit_lens_backward.py" --model meta-llama/Llama-3.2-1B-Instruct --device cuda --output-dir "%SRC%\results\ignis\llama_1b" --skip-preflight
echo [%time%] Job 1 complete
echo.

REM ── Job 2: Llama-3.2-1B Ejection Decompose ────────────────────────────────
echo [%time%] Job 2: Llama-3.2-1B ejection decomposition
%PYTHON% "%SRC%\ejection_decompose.py" --model meta-llama/Llama-3.2-1B-Instruct --device cuda --output-dir "%SRC%\results\ignis\ejection_llama_1b" --skip-preflight
echo [%time%] Job 2 complete
echo.

REM ── Job 3: Llama-3.2-1B v_proj Diagnostic ─────────────────────────────────
echo [%time%] Job 3: Llama-3.2-1B v_proj diagnostic (early vs late, attn vs MLP)
%PYTHON% "%SRC%\vproj_diagnostic.py" --model meta-llama/Llama-3.2-1B-Instruct --device cuda --output-dir "%SRC%\results\ignis\vproj_llama_1b"
echo [%time%] Job 3 complete
echo.

REM ── Job 4: Llama Base vs Instruct ─────────────────────────────────────────
echo [%time%] Job 4: Llama-3.2-1B base vs instruct
%PYTHON% "%SRC%\base_vs_instruct.py" --base-model meta-llama/Llama-3.2-1B --instruct-model meta-llama/Llama-3.2-1B-Instruct --device cuda --output-dir "%SRC%\results\ignis\base_vs_instruct_llama_1b"
echo [%time%] Job 4 complete
echo.

REM ── Job 5: Llama Eval v2 ──────────────────────────────────────────────────
echo [%time%] Job 5: Llama-3.2-1B eval v2 (66 traps, 7 pillars)
%PYTHON% "%SRC%\eval_v2.py" --model meta-llama/Llama-3.2-1B-Instruct --device cuda --output-dir "%SRC%\results\ignis\eval_v2_llama_1b" --skip-logit-lens
echo [%time%] Job 5 complete
echo.

REM ── Job 6: Llama Basin Escape Histogram ────────────────────────────────────
echo [%time%] Job 6: Llama-3.2-1B basin escape histogram
%PYTHON% "%SRC%\basin_escape_histogram.py" --model meta-llama/Llama-3.2-1B-Instruct --device cuda --output-dir "%SRC%\results\ignis\basin_llama_1b" --layer 12 --trap "Overtake" --n-directions 50
echo [%time%] Job 6 complete
echo.

REM ── Job 7: Gemma-3-1B Logit Lens ──────────────────────────────────────────
echo [%time%] Job 7: Gemma-3-1B logit lens backward pass
%PYTHON% "%SRC%\logit_lens_backward.py" --model google/gemma-3-1b-it --device cuda --output-dir "%SRC%\results\ignis\gemma_1b" --skip-preflight
echo [%time%] Job 7 complete
echo.

REM ── Job 8: Gemma-3-1B Ejection Decompose ──────────────────────────────────
echo [%time%] Job 8: Gemma-3-1B ejection decomposition
%PYTHON% "%SRC%\ejection_decompose.py" --model google/gemma-3-1b-it --device cuda --output-dir "%SRC%\results\ignis\ejection_gemma_1b" --skip-preflight
echo [%time%] Job 8 complete
echo.

REM ── Job 9: Gemma-3-1B v_proj Diagnostic ───────────────────────────────────
echo [%time%] Job 9: Gemma-3-1B v_proj diagnostic
%PYTHON% "%SRC%\vproj_diagnostic.py" --model google/gemma-3-1b-it --device cuda --output-dir "%SRC%\results\ignis\vproj_gemma_1b"
echo [%time%] Job 9 complete
echo.

REM ── Job 10: Gemma Eval v2 ─────────────────────────────────────────────────
echo [%time%] Job 10: Gemma-3-1B eval v2 (66 traps, 7 pillars)
%PYTHON% "%SRC%\eval_v2.py" --model google/gemma-3-1b-it --device cuda --output-dir "%SRC%\results\ignis\eval_v2_gemma_1b" --skip-logit-lens
echo [%time%] Job 10 complete
echo.

echo ============================================================================
echo  IGNIS OVERNIGHT RUN COMPLETE
echo  Check results in:
echo    ignis\src\results\ignis\llama_1b\
echo    ignis\src\results\ignis\ejection_llama_1b\
echo    ignis\src\results\ignis\vproj_llama_1b\
echo    ignis\src\results\ignis\base_vs_instruct_llama_1b\
echo    ignis\src\results\ignis\eval_v2_llama_1b\
echo    ignis\src\results\ignis\basin_llama_1b\
echo    ignis\src\results\ignis\gemma_1b\
echo    ignis\src\results\ignis\ejection_gemma_1b\
echo    ignis\src\results\ignis\vproj_gemma_1b\
echo    ignis\src\results\ignis\eval_v2_gemma_1b\
echo ============================================================================
