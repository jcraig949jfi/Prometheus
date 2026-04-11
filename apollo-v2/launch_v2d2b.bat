@echo off
set PYTHON=C:\Users\James\AppData\Local\Programs\Python\Python312\python.exe

echo ============================================================
echo   APOLLO v2_d2b — 50/50 Qwen+DeepSeek (Replica B)
echo   %date% %time%
echo   Island: beta-v2d2b
echo ============================================================

cd /d C:\Prometheus\apollo-v2

%PYTHON% src_v2d\apollo.py --config configs\config_v2d2b.yaml

echo ============================================================
echo   Apollo v2_d2b stopped.
echo ============================================================
pause
