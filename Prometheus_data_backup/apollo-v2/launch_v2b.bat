@echo off
set PYTHON=C:\Users\James\AppData\Local\Programs\Python\Python312\python.exe

echo ============================================================
echo   APOLLO v2_b — NSGA-III + Stagnation Monitor
echo   %date% %time%
echo   Island: beta-v2b
echo   Source: src_v2b\   Output: run_v2b\
echo ============================================================

cd /d C:\Prometheus\apollo-v2

echo [preflight] Checking GPU...
%PYTHON% -c "import torch; print(f'  GPU: {torch.cuda.get_device_name(0)} ({torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB)')"

echo [preflight] Checking config...
%PYTHON% -c "import yaml; c=yaml.safe_load(open('configs/config_v2b.yaml'))['apollo']; print(f'  Strategy: {c[\"instance_name\"]}')"

echo [preflight] Checking shared pool...
%PYTHON% -c "import yaml; c=yaml.safe_load(open('configs/config_v2b.yaml'))['apollo']; from pathlib import Path; p=Path(c['shared_pool']); print(f'  Pool: {p} (exists={p.exists()})')"

echo [preflight] All checks passed.
echo ============================================================
echo   Logs:        run_v2b\logs\
echo   Checkpoints: run_v2b\checkpoints\
echo   Shared Pool: \\SKULLPORT\skullport_shared\apollo_pool
echo   Stop: Ctrl+C
echo ============================================================

%PYTHON% src_v2b\apollo.py --config configs\config_v2b.yaml

echo ============================================================
echo   Apollo v2_b stopped.
echo ============================================================
pause
