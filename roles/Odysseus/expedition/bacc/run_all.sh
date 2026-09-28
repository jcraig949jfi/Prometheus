#!/bin/sh
# bacc full run: sequential substrates, 4 procs each. Logs wall per substrate.
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
python3 test_bacc.py > run_log.txt 2>&1
for s in z80 rbn wse; do
  /usr/bin/time -f "$s wall %e s" -a -o run_times.txt python3 sub_$s.py >> run_log.txt 2>&1
done
echo DONE >> run_log.txt
