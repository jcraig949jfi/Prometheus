#!/bin/bash
# Block R runner (amendment 1): <= 2 rbroad at once; kills its process tree on exit.
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
export PYTHONPATH=.
C=tyche/runs/v2_blockR
cleanup() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -like '*tyche.v2.run_v2*' -or \$_.CommandLine -like '*tyche.v2.history_v2*' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force -ErrorAction SilentlyContinue }"; }
trap cleanup EXIT INT TERM
one() {
  local out=$C/$1_$(echo $2 | tr ':' '-')_s$3
  python -m tyche.v2.run_v2 --harsh $1 --worlds $2 --coal PAIRS --chem GRAFT --gens 50 --switch 20 --seed $3 --out $out --workers $4 --tag $1-$2-s$3 > /dev/null 2>&1
  rc=$?
  python -m tyche.v2.history_v2 $out --workers 2 > /dev/null 2>&1
  echo "FINISHED $out rc=$rc"
}
one STRICT rbroad 1 9 & one LEX rbroad 1 9 & wait
one RES rbroad 1 9 & one STRICT rbroad 2 9 & wait
one LEX rbroad 2 9 & one RES rbroad 2 9 & wait
for s in 1 2; do for h in STRICT LEX RES; do one $h rrelated $s 4 & done; done; wait
for s in 1 2; do for h in STRICT LEX RES; do for r in R1 R2 R3 R4; do one $h rsolo:$r $s 2 & done; wait; done; done
python -m tyche.v2.report_v2 $C > /dev/null 2>&1; echo "REPORT rc=$?"
echo ALL_DONE
