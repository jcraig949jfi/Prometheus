@echo off
set PYTHON=C:\Users\James\AppData\Local\Programs\Python\Python312\python.exe

echo ============================================================
echo   APOLLO v2_c — Full Roadmap (Shoot the Moon)
echo   %date% %time%
echo   Island: beta-v2c
echo   Source: src_v2c\   Output: run_v2c\
echo   LLM: auto-start server on localhost:8800
echo ============================================================

cd /d C:\Prometheus\apollo-v2

echo [preflight] Checking GPU...
%PYTHON% -c "import torch; print(f'  GPU: {torch.cuda.get_device_name(0)} ({torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB)')"

echo [preflight] Checking config...
%PYTHON% -c "import yaml; c=yaml.safe_load(open('configs/config_v2c.yaml'))['apollo']; print(f'  Strategy: {c[\"instance_name\"]}')"

echo [preflight] Checking shared pool...
%PYTHON% -c "import yaml; c=yaml.safe_load(open('configs/config_v2c.yaml'))['apollo']; from pathlib import Path; p=Path(c['shared_pool']); print(f'  Pool: {p} (exists={p.exists()})')"

echo [preflight] Checking fastapi/uvicorn...
%PYTHON% -m pip install fastapi uvicorn --quiet 2>nul
%PYTHON% -c "import fastapi, uvicorn; print('  fastapi + uvicorn: OK')"

echo [preflight] All checks passed.
echo ============================================================
echo   Logs:        run_v2c\logs\
echo   Checkpoints: run_v2c\checkpoints\
echo   Shared Pool: \\SKULLPORT\skullport_shared\apollo_pool
echo   LLM Server:  localhost:8800 (auto-managed)
echo   Stop: Ctrl+C
echo ============================================================

%PYTHON% src_v2c\apollo.py --config configs\config_v2c.yaml

echo ============================================================
echo   Apollo v2_c stopped.
echo ============================================================
pause
