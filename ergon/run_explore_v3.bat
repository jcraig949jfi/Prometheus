@echo off
REM ================================================================
REM  ERGON EXPLORER v3 — 23 domains, 4.76M objects, 529 pairs
REM  Includes: knots_eng (Mahler+PCA), knots_topo (hyperbolic vol)
REM  F0 honest battery: object-identity permutation null
REM  Run: double-click this file
REM ================================================================
echo.
echo  ============================================================
echo   ERGON EXPLORER v3 — with F0 honest battery
echo   Started: %date% %time%
echo   Domains: 23 (core + extended + fingerprints + engineered)
echo   New: knots_eng (Mahler, roots of unity, PCA)
echo        knots_topo (hyperbolic volumes from SnapPy)
echo        artin_ade (ADE/Dynkin classification)
echo  ============================================================
echo.

cd /d F:\Prometheus\ergon

echo [1/2] Starting explorer (tensor pre-built)...
echo   Generations: 5000
echo   Per generation: 20 hypotheses
echo   F0 object-identity null: ON (honest battery)
echo.

python -u autonomous_explorer.py ^
    --generations 5000 ^
    --per-gen 20 ^
    --seed %random% ^
    --log-interval 50 ^
    --checkpoint-interval 500

echo.
echo  ============================================================
echo   EXPLORER COMPLETE: %date% %time%
echo   Check: ergon\logs\ and ergon\results\
echo  ============================================================
pause
