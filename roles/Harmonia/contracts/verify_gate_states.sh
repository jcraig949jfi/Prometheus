#!/usr/bin/env bash
# Verify the conformance gate in all four states.  Harmonia 2026-09-10.
#
# SELF-CONTAINED: starts and verifies its own scratch engine (Daedalus's
# deploy/scratch_contract_engine.py, c817f2d68) rather than assuming one is
# running in somebody's terminal. Without it, test 5 -- the ONLY executable
# proof that a ledger change is caught -- silently degrades to state 2
# UNREACHABLE: still non-zero, but for the wrong reason, so it stops proving
# what it was written to prove.
#
# NEVER pipe the gate and read $$? -- that captures the pipe's status, a defect
# that has bitten this campaign twice. Every run below redirects instead.
#
#   usage: verify_gate_states.sh <cacert> [port]
set -u
CA="${1:?cacert path}"
PORT="${2:-8901}"
SCRATCH="http://127.0.0.1:${PORT}/v2"

G=roles/Harmonia/contracts/conformance_check.py
NEW=roles/Harmonia/contracts/sfe_contract.json
OLD=roles/Harmonia/contracts/fixtures/sfe_contract_schema6_frozen.json
ENGINE=SerendipityFoundry/SerendipityFoundryEngine/deploy/scratch_contract_engine.py

started=0
cleanup() { [ "$started" = "1" ] && { echo "  stopping the scratch engine we started"; kill "$PID" 2>/dev/null; }; }
trap cleanup EXIT

# --- the scratch engine, started if absent and VERIFIED either way ----------
if [ ! -f "$ENGINE" ]; then
  echo "ABORT: $ENGINE not found. Test 5 cannot be proved without it."; exit 4
fi
if ! python "$ENGINE" --check --port "$PORT" >/dev/null 2>&1; then
  echo "  scratch engine not up on :$PORT -- starting it"
  python "$ENGINE" --port "$PORT" >/dev/null 2>&1 &
  PID=$!; started=1
  for _ in $(seq 1 30); do
    python "$ENGINE" --check --port "$PORT" >/dev/null 2>&1 && break; sleep 1
  done
fi
# HALT rather than test against an unverified instrument. --check asserts the
# build hash MATCHES prod, the schema matches, the ledger DIFFERS, and
# registration is open. If any fails, test 5 is not testing a ledger change.
if ! python "$ENGINE" --check --port "$PORT" >/dev/null 2>&1; then
  echo "ABORT: scratch engine on :$PORT failed its own --check."
  python "$ENGINE" --check --port "$PORT" 2>&1 | sed 's/^/    /'
  echo "  Not running the states: test 5 would pass for the wrong reason."
  exit 4
fi

# DEFENCE IN DEPTH, added 2026-09-10 after Daedalus's --port bug (0f98ef1f0):
# --check accepted a port, started an engine on it, then built its check URL
# from a module constant -- so at any non-default port it silently interrogated
# 8901 and returned 0. The HALT guard above passed for the same reason the bug
# was invisible, and test 5 then hit an empty port and degraded to state 2.
#
# The lesson generalises past that one bug: a check we DELEGATE may be about a
# different target than the one our tests will hit. So assert it here, at the
# EXACT url test 5 uses, rather than trusting a report about it.
python - "$SCRATCH" "$NEW" <<'PYEOF' || exit 4
import json, sys, urllib.request
scratch, contract = sys.argv[1], sys.argv[2]
want = json.load(open(contract, encoding="utf-8"))["engine"]["engine_instance_id"]
try:
    live = json.loads(urllib.request.urlopen(scratch + "/version", timeout=10).read())
except Exception as e:                                             # noqa: BLE001
    print("ABORT: nothing answering at %s -- %r" % (scratch, e)); sys.exit(4)
got = live.get("engine_instance_id")
if got == want:
    print("ABORT: %s reports the SAME ledger as the contract (%s)." % (scratch, got))
    print("  Test 5 would pass as CONFORMANT, not DRIFT. It proves nothing.")
    sys.exit(4)
print("  test-5 target confirmed at %s: ledger %s, contract %s" % (scratch, got, want))
PYEOF
echo "  scratch engine verified on :$PORT (build matches prod, ledger differs)"

run() { timeout 200 python "$@" >/dev/null 2>&1; echo $?; }
fail=0
t() { if [ "$2" = "$3" ]; then printf '  [PASS] %-46s %s\n' "$1" "$3"
      else printf '  [FAIL] %-46s expected %s got %s\n' "$1" "$2" "$3"; fail=1; fi; }

echo "conformance gate state verification"
t "0 CONFORMANT  current contract vs live"           0 "$(run $G --contract $NEW --cacert $CA)"
t "3 INCOMPLETE  stale contract, routes undeclared"  3 "$(run $G --contract $OLD --cacert $CA)"
t "0 INCOMPLETE+declared, all routes listed"         0 "$(run $G --contract $OLD --cacert $CA \
      --consumer-routes 'GET /v2/version' 'POST /v2/worlds/{wid}/experiments')"
t "3 INCOMPLETE+declared, calls an added route"      3 "$(run $G --contract $OLD --cacert $CA \
      --consumer-routes 'POST /v2/worlds/{wid}/budget/reserve')"
t "1 DRIFT       same build, DIFFERENT ledger"       1 "$(run $G --contract $NEW --base $SCRATCH)"
t "2 UNREACHABLE"                                    2 "$(run $G --contract $NEW --base http://127.0.0.1:9999/v2)"
echo
[ $fail -eq 0 ] && echo "all six states verified" || echo "VERIFICATION FAILED"
exit $fail
