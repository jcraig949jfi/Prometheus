@echo off
REM ============================================================
REM Dead-Signal Trap Diagnostic
REM
REM Three traps produce 0.0 margin because target/anti tokens
REM share the same first BPE token. This diagnoses all traps
REM and tests alternative phrasings.
REM
REM Expected runtime: ~2 minutes (no evolution, just forward passes)
REM ============================================================

echo ============================================================
echo  DEAD-SIGNAL TRAP DIAGNOSTIC
echo  Started: %date% %time%
echo ============================================================

python src\dead_signal_diagnostic.py ^
    --model results\corpus_first\stageB_finetune\ft_model ^
    --device cuda

echo.
echo  Finished: %date% %time%
pause
