@echo off
set PYTHON=C:\Users\James\AppData\Local\Programs\Python\Python312\python.exe

echo ============================================================
echo   APOLLO v2_d — Gradient Recovery
echo   %date% %time%
echo   Island: beta-v2d
echo   Source: src_v2d\   Output: run_v2d\
echo   Fixes: curriculum + annealing + AOS accuracy reward
echo ============================================================

cd /d C:\Prometheus\apollo-v2

echo [preflight] Checking GPU...
%PYTHON% -c "import torch; print(f'  GPU: {torch.cuda.get_device_name(0)} ({torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB)')"

echo [preflight] Checking config...
%PYTHON% -c "import yaml; c=yaml.safe_load(open('configs/config_v2d.yaml'))['apollo']; print(f'  Strategy: {c[\"instance_name\"]}')"

echo [preflight] Checking shared pool...
%PYTHON% -c "import yaml; c=yaml.safe_load(open('configs/config_v2d.yaml'))['apollo']; from pathlib import Path; p=Path(c['shared_pool']); print(f'  Pool: {p} (exists={p.exists()})')"

echo [preflight] Checking fastapi/uvicorn...
%PYTHON% -m pip install fastapi uvicorn --quiet 2>nul
%PYTHON% -c "import fastapi, uvicorn; print('  fastapi + uvicorn: OK')"

echo [preflight] All checks passed.
echo ============================================================
echo   Logs:        run_v2d\logs\
echo   Checkpoints: run_v2d\checkpoints\
echo   Shared Pool: \\SKULLPORT\skullport_shared\apollo_pool
echo   LLM Server:  localhost:8800 (auto-managed)
echo   Stop: Ctrl+C
echo ============================================================

%PYTHON% src_v2d\apollo.py --config configs\config_v2d.yaml

echo ============================================================
echo   Apollo v2_d stopped.
echo ============================================================
pause
