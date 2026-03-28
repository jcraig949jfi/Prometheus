@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM  OVERNIGHT QUEUE — Chain experiments while James works his 12-hour shift
REM
REM  Run this AFTER batch4_followup.bat finishes. Total: ~14-16 hours.
REM
REM  Block 1: Corpus-first protocol (6-8 hrs) — THE critical experiment
REM  Block 2: Cross-architecture universality (6-8 hrs) — Gemma + Qwen 0.5B
REM
REM  Usage: run_overnight_queue.bat
REM ============================================================================

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo ============================================================================
echo  OVERNIGHT QUEUE — Started %date% %time%
echo  Block 1: Corpus-first protocol
echo  Block 2: Cross-architecture universality test
echo  Estimated total: 14-16 hours
echo ============================================================================

REM ============================================================================
REM  BLOCK 1: Corpus-first protocol (order-of-operations test)
REM  This is the most scientifically important experiment in the queue.
REM ============================================================================
echo.
echo ============================================================================
echo  BLOCK 1/2: Corpus-first protocol — %time%
echo ============================================================================

call run_corpus_first.bat
echo  Block 1 ended: %time%

REM ============================================================================
REM  BLOCK 2: Cross-architecture universality test
REM  Gemma-3-1B + Qwen2.5-0.5B — is the ejection mechanism universal?
REM ============================================================================
echo.
echo ============================================================================
echo  BLOCK 2/2: Cross-architecture universality — %time%
echo ============================================================================

call run_overnight_v2.bat
echo  Block 2 ended: %time%

REM ============================================================================
REM  ALL DONE
REM ============================================================================
echo.
echo ============================================================================
echo  OVERNIGHT QUEUE COMPLETE — %date% %time%
echo.
echo  Block 1 results: results\corpus_first\
echo  Block 2 results: src\results\ignis\gemma_1b\ + src\results\ignis\qwen_05b\
echo ============================================================================

endlocal
