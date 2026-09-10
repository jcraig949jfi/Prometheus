#!/usr/bin/env bash
# Verify the conformance gate in all four states.  Harmonia 2026-09-10.
#
# NEVER pipe the gate and read $? -- that captures the pipe's status, a defect
# that has bitten this campaign twice. Every run below redirects instead.
#
#   usage: verify_gate_states.sh <cacert> [scratch_base]
set -u
CA="${1:?cacert path}"
SCRATCH="${2:-http://127.0.0.1:8901/v2}"
G=roles/Harmonia/contracts/conformance_check.py
NEW=roles/Harmonia/contracts/sfe_contract.json
OLD=roles/Harmonia/contracts/fixtures/sfe_contract_schema6_frozen.json

run() { timeout 200 python "$@" >/dev/null 2>&1; echo $?; }
fail=0
t() { # name expected actual
  if [ "$2" = "$3" ]; then printf '  [PASS] %-46s %s\n' "$1" "$3"
  else printf '  [FAIL] %-46s expected %s got %s\n' "$1" "$2" "$3"; fail=1; fi
}

echo "conformance gate state verification"
t "0 CONFORMANT  current contract vs live"      0 "$(run $G --contract $NEW --cacert $CA)"
t "3 INCOMPLETE  stale contract, routes undeclared" 3 "$(run $G --contract $OLD --cacert $CA)"
t "0 INCOMPLETE+declared, all routes listed"    0 "$(run $G --contract $OLD --cacert $CA \
      --consumer-routes 'GET /v2/version' 'POST /v2/worlds/{wid}/experiments')"
t "3 INCOMPLETE+declared, calls an added route" 3 "$(run $G --contract $OLD --cacert $CA \
      --consumer-routes 'POST /v2/worlds/{wid}/budget/reserve')"
t "1 DRIFT       same build, DIFFERENT ledger"  1 "$(run $G --contract $NEW --base $SCRATCH)"
t "2 UNREACHABLE"                               2 "$(run $G --contract $NEW --base http://127.0.0.1:9999/v2)"
echo
[ $fail -eq 0 ] && echo "all six states verified" || echo "VERIFICATION FAILED"
exit $fail
