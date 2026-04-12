@echo off
set PYTHON=C:\Users\James\AppData\Local\Programs\Python\Python312\python.exe
echo Starting LLM Server (Qwen2.5-Coder-7B-Instruct, 8-bit)...
%PYTHON% C:\Prometheus\apollo-v2\src_v2c\llm_server.py
pause
