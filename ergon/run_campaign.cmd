@echo off
cd /d F:\Prometheus
python ergon\probe\campaign.py >> ergon\probe\ledgers\campaign\campaign_console.log 2>&1
