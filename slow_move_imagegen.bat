@echo off
REM Slow robocopy: moves C:\AI-ImageGen to E:\AI-ImageGen
REM Uses /IPG for throttling (no /MT - they're incompatible)
REM Safe to Ctrl+C and restart anytime - robocopy resumes.

echo ============================================================
echo SLOW MOVE: C:\AI-ImageGen -^> E:\AI-ImageGen
echo Copies one folder at a time with 30-second pauses
echo Safe to Ctrl+C and restart anytime
echo ============================================================
echo.

if not exist "E:\AI-ImageGen" mkdir "E:\AI-ImageGen"

for /D %%d in ("C:\AI-ImageGen\*") do (
    echo.
    echo --- Copying folder: %%~nxd ---
    echo %TIME%

    robocopy "%%d" "E:\AI-ImageGen\%%~nxd" /MIR /R:3 /W:5 /IPG:50 /NP /ETA

    echo --- Done with %%~nxd, sleeping 30 seconds ---
    timeout /t 30 /nobreak >nul
)

echo.
echo --- Copying root-level files ---
robocopy "C:\AI-ImageGen" "E:\AI-ImageGen" /R:3 /W:5 /IPG:50 /NP /ETA /LEV:1

echo.
echo ============================================================
echo COPY COMPLETE
echo.
echo Verify E:\AI-ImageGen looks correct, then delete the original:
echo   rmdir /s /q "C:\AI-ImageGen"
echo ============================================================
pause
