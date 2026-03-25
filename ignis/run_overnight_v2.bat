@echo off
REM ============================================================================
REM  IGNIS OVERNIGHT RUN v2 — Gemma + Qwen cross-architecture
REM  Llama is gated (needs Meta approval). Using open-access models only.
REM ============================================================================

echo ============================================================================
echo  IGNIS OVERNIGHT RUN v2
echo  Gemma-3-1B + Qwen2.5-0.5B (open access models)
echo ============================================================================
echo.

set PYTHON=python
set SRC=%~dp0src
set PYTHONIOENCODING=utf-8

REM ── Gemma-3-1B Suite ───────────────────────────────────────────────────────

echo [%time%] Job 1: Gemma-3-1B logit lens
%PYTHON% "%SRC%\logit_lens_backward.py" --model google/gemma-3-1b-it --device cuda --output-dir "%SRC%\results\ignis\gemma_1b" --skip-preflight
echo [%time%] Job 1 complete
echo.

echo [%time%] Job 2: Gemma-3-1B ejection decompose
%PYTHON% "%SRC%\ejection_decompose.py" --model google/gemma-3-1b-it --device cuda --output-dir "%SRC%\results\ignis\ejection_gemma_1b" --skip-preflight
echo [%time%] Job 2 complete
echo.

echo [%time%] Job 3: Gemma-3-1B v_proj diagnostic
%PYTHON% "%SRC%\vproj_diagnostic.py" --model google/gemma-3-1b-it --device cuda --output-dir "%SRC%\results\ignis\vproj_gemma_1b"
echo [%time%] Job 3 complete
echo.

echo [%time%] Job 4: Gemma-3-1B eval v2
%PYTHON% "%SRC%\eval_v2.py" --model google/gemma-3-1b-it --device cuda --output-dir "%SRC%\results\ignis\eval_v2_gemma_1b" --skip-logit-lens
echo [%time%] Job 4 complete
echo.

echo [%time%] Job 5: Gemma-3-1B basin escape
%PYTHON% "%SRC%\basin_escape_histogram.py" --model google/gemma-3-1b-it --device cuda --output-dir "%SRC%\results\ignis\basin_gemma_1b" --layer 20 --trap "Overtake" --n-directions 50
echo [%time%] Job 5 complete
echo.

REM ── Qwen2.5-0.5B Suite (smallest Qwen, tests scale floor) ─────────────────

echo [%time%] Job 6: Qwen2.5-0.5B logit lens
%PYTHON% "%SRC%\logit_lens_backward.py" --model Qwen/Qwen2.5-0.5B-Instruct --device cuda --output-dir "%SRC%\results\ignis\qwen_05b" --skip-preflight
echo [%time%] Job 6 complete
echo.

echo [%time%] Job 7: Qwen2.5-0.5B ejection decompose
%PYTHON% "%SRC%\ejection_decompose.py" --model Qwen/Qwen2.5-0.5B-Instruct --device cuda --output-dir "%SRC%\results\ignis\ejection_qwen_05b" --skip-preflight
echo [%time%] Job 7 complete
echo.

echo [%time%] Job 8: Qwen2.5-0.5B v_proj diagnostic
%PYTHON% "%SRC%\vproj_diagnostic.py" --model Qwen/Qwen2.5-0.5B-Instruct --device cuda --output-dir "%SRC%\results\ignis\vproj_qwen_05b"
echo [%time%] Job 8 complete
echo.

echo [%time%] Job 9: Qwen2.5-0.5B base vs instruct
%PYTHON% "%SRC%\base_vs_instruct.py" --base-model Qwen/Qwen2.5-0.5B --instruct-model Qwen/Qwen2.5-0.5B-Instruct --device cuda --output-dir "%SRC%\results\ignis\base_vs_instruct_qwen_05b"
echo [%time%] Job 9 complete
echo.

echo [%time%] Job 10: Qwen2.5-0.5B eval v2
%PYTHON% "%SRC%\eval_v2.py" --model Qwen/Qwen2.5-0.5B-Instruct --device cuda --output-dir "%SRC%\results\ignis\eval_v2_qwen_05b" --skip-logit-lens
echo [%time%] Job 10 complete
echo.

echo [%time%] Job 11: Qwen2.5-0.5B basin escape
%PYTHON% "%SRC%\basin_escape_histogram.py" --model Qwen/Qwen2.5-0.5B-Instruct --device cuda --output-dir "%SRC%\results\ignis\basin_qwen_05b" --layer 18 --trap "Overtake" --n-directions 50
echo [%time%] Job 11 complete
echo.

echo ============================================================================
echo  IGNIS OVERNIGHT RUN v2 COMPLETE
echo  Results in: ignis\src\results\ignis\gemma_1b\
echo              ignis\src\results\ignis\qwen_05b\
echo ============================================================================
