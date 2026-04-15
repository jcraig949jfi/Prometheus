@echo off
REM Aporia — Full math solver battery
REM Uses Gemini (free tier) to classify and attempt all 490 math problems
REM Estimated time: ~3 hours
REM Results saved to: aporia/mathematics/solutions.jsonl
REM
REM The script is idempotent — it skips problems already in solutions.jsonl
REM So you can stop and restart without losing progress.

cd /d F:\Prometheus\aporia

echo ============================================
echo  Aporia Solver Battery — Full Run
echo  Model: Gemini 2.5 Flash (free tier)
echo  Problems: 490 math questions
echo  Output: mathematics/solutions.jsonl
echo ============================================
echo.
echo Starting in 5 seconds... (Ctrl+C to cancel)
timeout /t 5

python scripts/solve_battery.py --model gemini --delay 4

echo.
echo ============================================
echo  Battery complete!
echo  Results: mathematics/solutions.jsonl
echo ============================================
echo.

REM Generate summary
python -c "import json,collections; c=collections.Counter(); total=0; ^
with open('mathematics/solutions.jsonl','r',encoding='utf-8') as f: ^
  for line in f: ^
    e=json.loads(line); r=e.get('result',{}); cl=r.get('classification','unknown'); c[cl]+=1; total+=1; ^
print(f'Total processed: {total}'); ^
[print(f'  {k}: {v}') for k,v in c.most_common()]"

pause
