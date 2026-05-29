@echo off
REM Background build script for mathlib4 + lean-repl bridge project.
REM Runs in two phases: clone mathlib4, then `lake exe cache get` + `lake build`.
REM Total expected time: 15-45 min (cache get is the bulk; pre-built oleans).

setlocal enabledelayedexpansion
set "PATH=%USERPROFILE%\.elan\bin;%PATH%"

set "ROOT=F:\Prometheus\external_deps"
set "MATHLIB_DIR=%ROOT%\mathlib4"
set "BRIDGE_DIR=%ROOT%\mathlib_repl"

echo === [build_mathlib_repl] %DATE% %TIME% ===

REM ----- Phase 1: clone mathlib4 -----
if exist "%MATHLIB_DIR%\.git" (
    echo [phase1] mathlib4 already cloned at %MATHLIB_DIR%
) else (
    echo [phase1] cloning mathlib4 ...
    git clone --depth 1 https://github.com/leanprover-community/mathlib4 "%MATHLIB_DIR%"
    if errorlevel 1 (
        echo [phase1] clone failed
        exit /b 1
    )
)

echo --- mathlib4 lean-toolchain ---
type "%MATHLIB_DIR%\lean-toolchain"

REM ----- Phase 2: read mathlib4 toolchain, build bridge project -----
for /f "usebackq tokens=*" %%i in ("%MATHLIB_DIR%\lean-toolchain") do (
    set "MATHLIB_TOOLCHAIN=%%i"
)
echo [phase2] mathlib4 toolchain: !MATHLIB_TOOLCHAIN!

REM ----- Phase 3: build mathlib4 oleans via cache -----
cd /d "%MATHLIB_DIR%"
echo [phase3] elan show ...
elan show
echo [phase3] lake exe cache get (downloads pre-built oleans) ...
lake exe cache get
if errorlevel 1 (
    echo [phase3] cache get failed
    exit /b 2
)
echo [phase3] lake build (verifies oleans align) ...
lake build
if errorlevel 1 (
    echo [phase3] lake build failed
    exit /b 3
)

echo === [build_mathlib_repl] DONE %DATE% %TIME% ===
exit /b 0
