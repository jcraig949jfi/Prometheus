@echo off
set PYTHON=C:\Users\James\AppData\Local\Programs\Python\Python312\python.exe

echo ============================================================
echo   APOLLO-BETA v2 — Breadth-First Generalist
echo   %date% %time%
echo   Machine: M2 (i7-14700F, 20 cores, RTX 5060 Ti 16GB)
echo ============================================================

cd /d C:\Prometheus\apollo-v2

REM Preflight checks
echo [preflight] Checking GPU...
%PYTHON% -c "import torch; print(f'  GPU: {torch.cuda.get_device_name(0)} ({torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB)')"

echo [preflight] Checking config...
%PYTHON% -c "import yaml; c=yaml.safe_load(open('configs/config.yaml'))['apollo']; print(f'  Strategy: {c[\"instance_name\"]}')"

echo [preflight] Checking shared pool...
%PYTHON% -c "import yaml; c=yaml.safe_load(open('configs/config.yaml'))['apollo']; from pathlib import Path; p=Path(c['shared_pool']); print(f'  Pool: {p} (exists={p.exists()})')"

echo [preflight] Checking forge_primitives...
%PYTHON% -c "import sys; sys.path.insert(0,'C:/Prometheus/agents/hephaestus/src'); import forge_primitives as fp; funcs=[x for x in dir(fp) if not x.startswith('_') and callable(getattr(fp,x,None))]; print(f'  Primitives: {len(funcs)} functions')"

echo [preflight] All checks passed.
echo ============================================================

REM Launch
echo [launch] Starting Apollo-Beta (no generation limit)
echo   Logs:        C:\Prometheus\apollo-v2\logs\apollo_run.jsonl
echo   Checkpoints: C:\Prometheus\apollo-v2\checkpoints
echo   Shared Pool: \\SKULLPORT\skullport_shared\apollo_pool
echo   Stop: Ctrl+C    Resume: launch_beta.bat
echo ============================================================

%PYTHON% src\apollo.py --config configs\config.yaml

echo ============================================================
echo   Apollo-Beta stopped. Resume with: launch_beta.bat
echo ============================================================
pause
