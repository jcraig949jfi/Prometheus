@echo off
echo ============================================================
echo   CHARON 8-TERMINAL + EXPLORER RUNNER
echo   8 DeepSeek terminals + 1 zero-cost explorer loop
echo   Bridge trolls on duty. The Styx never sleeps.
echo ============================================================
echo.

start "" run_T1.bat
timeout /t 3 /nobreak >nul
start "" run_T2.bat
timeout /t 3 /nobreak >nul
start "" run_T3.bat
timeout /t 3 /nobreak >nul
start "" run_T4.bat
timeout /t 3 /nobreak >nul
start "" run_T5.bat
timeout /t 3 /nobreak >nul
start "" run_T6.bat
timeout /t 3 /nobreak >nul
start "" run_T7.bat
timeout /t 3 /nobreak >nul
start "" run_T8.bat
timeout /t 5 /nobreak >nul

echo.
echo   Launching zero-cost explorer loop...
start "" run_explorers.bat

echo.
echo All 8 terminals + explorer launched.
echo   T1-T4: 8 hypotheses/cycle (core domains + new datasets)
echo   T5-T8: 5 hypotheses/cycle (sleepers, shadow voids, cold cells)
echo   EXPLORER: void scan + bridge hunt + MAP-Elites + shadow tensor (0 API cost)
echo.
echo Close individual windows to stop specific terminals.
pause
