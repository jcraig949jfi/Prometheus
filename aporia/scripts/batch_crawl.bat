@echo off
REM Aporia — Batch literature crawl (run unattended)
REM Crawls all domains with rate-limit-friendly delays.
REM Usage: batch_crawl.bat [domain] [limit]
REM   batch_crawl.bat                   -- all domains, all questions
REM   batch_crawl.bat mathematics       -- one domain
REM   batch_crawl.bat mathematics 10    -- first 10 questions

cd /d F:\Prometheus\aporia

if "%1"=="" (
    echo Crawling ALL domains...
    python scripts/crawl_literature.py --limit %2
) else (
    echo Crawling %1...
    python scripts/crawl_literature.py %1 --limit %2
)

echo.
echo Done. Check questions.jsonl files for attached papers.
pause
