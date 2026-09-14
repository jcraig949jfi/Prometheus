#!/bin/bash
# Batch 06 phase 8: run the preserved SAT solvers over the shared workload, one line of raw
# behaviour per (solver, instance). No judgement of "best"; result + time + decisions/conflicts
# where the solver exposes them. Run inside prometheus-fossil-c:bookworm with the vault mounted.
# args: <vault root>  <workload dir>  <out.jsonl>
set -u
VAULT=$1; WL=$2; OUT=$3
: > "$OUT"
build_minisat() { # picosat and minisat build cheaply in this same world
  cp -r "$VAULT/minisat-2.2.0/upstream/tree/minisat" /tmp/ms 2>/dev/null
  ( cd /tmp/ms && export MROOT=/tmp/ms && make -s r >/dev/null 2>&1; find . -name 'minisat_static' -o -name 'minisat' | head -1 )
}
build_picosat() {
  cp -r "$VAULT/picosat-965/upstream/tree/picosat-965" /tmp/ps 2>/dev/null
  ( cd /tmp/ps && ./configure.sh >/dev/null 2>&1 && make -s >/dev/null 2>&1; echo /tmp/ps/picosat )
}
MS=$(build_minisat); MS=/tmp/ms/$MS
PS=$(build_picosat)
[ -x "$MS" ] || MS=$(find /tmp/ms -name 'minisat*' -type f -perm -u+x | head -1)
echo "minisat=$MS picosat=$PS" >&2
emit() { # solver instance result seconds extra
  printf '{"solver":"%s","instance":"%s","result":"%s","seconds":%s,%s}\n' "$1" "$2" "$3" "$4" "$5" >> "$OUT"
}
for cnf in "$WL"/*.cnf; do
  inst=$(basename "$cnf")
  # picosat: prints s SATISFIABLE / UNSATISFIABLE; stats to stderr
  t0=$(date +%s.%N); out=$(timeout 60 "$PS" -v "$cnf" 2>&1); rc=$?; t1=$(date +%s.%N)
  res=$(echo "$out" | grep -oE 'SATISFIABLE|UNSATISFIABLE' | head -1); [ $rc -eq 124 ] && res=TIMEOUT
  dec=$(echo "$out" | grep -oE '[0-9]+ decisions' | grep -oE '^[0-9]+'); prop=$(echo "$out" | grep -oE '[0-9]+ propagations' | grep -oE '^[0-9]+')
  emit picosat-965 "$inst" "${res:-UNKNOWN}" "$(echo "$t1 - $t0" | bc)" "\"decisions\":${dec:-null},\"propagations\":${prop:-null}"
  # minisat 2.2: prints SATISFIABLE/UNSATISFIABLE; "decisions" / "conflicts" in stats
  t0=$(date +%s.%N); out=$(timeout 60 "$MS" "$cnf" /dev/null 2>&1); rc=$?; t1=$(date +%s.%N)
  res=$(echo "$out" | grep -oE 'SATISFIABLE|UNSATISFIABLE|INDETERMINATE' | head -1); [ $rc -eq 124 ] && res=TIMEOUT
  con=$(echo "$out" | grep -iE 'conflicts' | grep -oE '[0-9]+' | head -1); dec=$(echo "$out" | grep -iE 'decisions' | grep -oE '[0-9]+' | head -1)
  emit minisat-2.2.0 "$inst" "${res:-UNKNOWN}" "$(echo "$t1 - $t0" | bc)" "\"conflicts\":${con:-null},\"decisions\":${dec:-null}"
done
echo "wrote $OUT" >&2
cat "$OUT" >&2
