@echo off
REM ============================================================
REM Overnight Battery Expansion Run
REM
REM 1. Validate new trap generators (syntax + smoke test)
REM 2. Run full v3 library against expanded battery (105 categories)
REM 3. Compute new metrics (fallback rate, epistemic honesty, tier split)
REM 4. Trigger Coeus rebuild with expanded data
REM 5. Generate comparison report
REM
REM Expected runtime: 2-4 hours depending on library size
REM ============================================================

echo ============================================================
echo  Overnight Battery Expansion Run
echo  Started: %date% %time%
echo ============================================================
echo.

cd /d "F:\Prometheus\agents\hephaestus\src"

REM Step 1: Validate generators
echo [1/5] Validating trap generators...
python -c "from trap_generator import generate_trap_battery; b = generate_trap_battery(n_per_category=1, seed=99); print(f'Base generators: {len(b)} traps from {len(set(t[\"category\"] for t in b))} categories')"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Base trap generator failed
    exit /b 1
)

python -c "from trap_generator_extended import generate_full_battery; b = generate_full_battery(n_per_category=1, seed=99); print(f'Full battery: {len(b)} traps from {len(set(t[\"category\"] for t in b))} categories')"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Extended trap generator failed
    exit /b 1
)
echo [OK] Generators validated
echo.

REM Step 2: Run expanded battery against all v3 tools
echo [2/5] Running expanded battery against v3 library...
python run_expanded_battery.py
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Battery run failed
    exit /b 1
)
echo [OK] Battery complete
echo.

REM Step 3: Trigger Coeus rebuild
echo [3/5] Triggering Coeus rebuild...
cd /d "F:\Prometheus\agents\coeus\src"
python coeus.py
cd /d "F:\Prometheus\agents\hephaestus\src"
echo [OK] Coeus rebuilt
echo.

REM Step 4: Run novelty scoring on v3
echo [4/5] Running novelty scoring...
python novelty_scorer.py --update-ledger --quiet
echo [OK] Novelty scores updated
echo.

REM Step 5: Generate report
echo [5/5] Generating report...
python -c "
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

report = Path('../forge_v3/expanded_battery_report.json')
if report.exists():
    data = json.loads(report.read_text(encoding='utf-8'))
    print(f'Tools evaluated: {data.get(\"total_tools\", \"?\")}')
    print(f'Categories: {data.get(\"total_categories\", \"?\")}')
    print(f'Tier A median acc: {data.get(\"tier_a_median_acc\", \"?\")}'  )
    print(f'Tier B median acc: {data.get(\"tier_b_median_acc\", \"?\")}')
    print(f'Median fallback rate: {data.get(\"median_fallback_rate\", \"?\")}')
else:
    print('Report not found - check run_expanded_battery.py output')
"

echo.
echo ============================================================
echo  Overnight Battery Expansion Complete
echo  Finished: %date% %time%
echo ============================================================
