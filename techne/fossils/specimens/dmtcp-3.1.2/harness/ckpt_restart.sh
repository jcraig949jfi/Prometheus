#!/bin/bash
# Techne harness: DMTCP checkpoint -> kill -> restart. args: <dmtcp bin dir> <build dir>
set -u
BIN=$1; B=$2; cd $B; rm -f ckpt_*.dmtcp dmtcp_restart_script* counter.out restart.out
export PATH=$BIN:$PATH
dmtcp_coordinator --daemon --exit-on-last -p 7779 -q >/dev/null 2>&1 || true
sleep 1
dmtcp_launch -p 7779 ./counter > counter.out 2>&1 &
LP=$!
sleep 5.5
dmtcp_command -p 7779 -c >/dev/null 2>&1 || dmtcp_command -p 7779 --checkpoint
sleep 2
LAST=$(grep -o '[0-9]*' counter.out | tail -1)
kill -9 $LP 2>/dev/null; sleep 1; pkill -9 -f '^./counter' 2>/dev/null; pkill -9 counter 2>/dev/null
echo "last count before kill = $LAST"
ls ckpt_counter_*.dmtcp | head -1 || { echo "NO CHECKPOINT IMAGE"; exit 1; }
dmtcp_coordinator --daemon --exit-on-last -p 7780 -q >/dev/null 2>&1 || true
sleep 1
dmtcp_restart -p 7780 ckpt_counter_*.dmtcp > restart.out 2>&1 &
RP=$!
sleep 4
kill -9 $RP 2>/dev/null; pkill -9 -f dmtcp_restart 2>/dev/null; pkill -9 counter 2>/dev/null
FIRST=$(grep -o 'count [0-9]*' restart.out | head -1 | grep -o '[0-9]*')
echo "first count after restart = ${FIRST:-none}"
echo "restart output head:"; head -4 restart.out
if [ -n "${FIRST:-}" ] && [ "$FIRST" -ge 4 ]; then echo "RESTART OK (continued from the checkpoint, not from 1)"; else echo "RESTART FAILED"; exit 1; fi
