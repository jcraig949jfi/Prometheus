@echo off
echo === Syncing new/modified files to Z:\ (SPECTREX5) ===
robocopy F:\Prometheus Z:\. /E /MT:4 /XO /XD .git node_modules __pycache__ .mypy_cache /XF *.pyc /NP
echo === Done (exit code: %ERRORLEVEL%) ===