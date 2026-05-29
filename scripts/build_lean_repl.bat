@echo off
cd /d F:\Prometheus\external_deps\repl
set "PATH=%USERPROFILE%\.elan\bin;%PATH%"
echo --- toolchain required ---
type lean-toolchain
echo --- elan show ---
elan show
echo --- lake build (this can take several minutes for first run) ---
lake build
echo --- exit code %ERRORLEVEL% ---
