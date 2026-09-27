#!/usr/bin/env bash
# TH-006 node-local verification of C-001/E-001/T-001 (BEE r038751) on a Linux node.
#
#   node_check.sh CANONICAL_REPO COMMIT PACK_SHA256 WORKDIR
#
# Builds WORKDIR from Git objects only (git archive; the canonical checkout is
# read, never modified), replays T-001 and verifies it against the committed
# pack with NO network (unshare -n) and isolated Python (-I), logs every file
# access, runs the adversarial controls, prints timings, then deletes WORKDIR
# and checks it is gone. Needs: git, python3 >= 3.8, GNU time, passwordless sudo
# (for unshare -n only).
set -euo pipefail
REPO=$1; COMMIT=$2; PACK_SHA=$3; W=$4
HARNESS_GIT=16fc6c2a
TRACED_GIT=98a28dd39f5ccccec6d3a2531cbfcfed238a61aa
T=roles/Odysseus/th006
[ -e "$W" ] && { echo "refusing: $W exists" >&2; exit 2; }
mkdir -p "$W/harness" "$W/tools"
g() { git -C "$REPO" "$@"; }
g archive "$HARNESS_GIT" prometheus/z80atlas | tar -x -C "$W/harness"
g archive "$TRACED_GIT" roles/Bellerophon/forensics_2026-09-23/tools/traced_replay.py \
    roles/Bellerophon/forensics_2026-09-23/tools/load.py | tar -x --strip-components=4 -C "$W/tools"
mkdir -p "$W/tmp_x"
g archive "$COMMIT" archaeon/causal_lens/tools_bee/codeprov_replay.py $T/tools \
    $T/pack/r038751.pack.json ops/campaigns/C-001/E-001/inputs/r038751.config.json \
    archaeon/causal_lens/out_v02/B6_PROBE_r038751.json | tar -x -C "$W/tmp_x"
cp "$W/tmp_x/archaeon/causal_lens/tools_bee/codeprov_replay.py" "$W/tools/"
cp "$W/tmp_x/$T/tools/"*.py "$W/tools/"
cp "$W/tmp_x/$T/pack/r038751.pack.json" "$W/pack.json"
cp "$W/tmp_x/ops/campaigns/C-001/E-001/inputs/r038751.config.json" "$W/"
cp "$W/tmp_x/archaeon/causal_lens/out_v02/B6_PROBE_r038751.json" "$W/published.json"
rm -rf "$W/tmp_x"

echo "== inputs"
echo "commit $(g rev-parse "$COMMIT")"
sha() { sha256sum "$1" | cut -c1-64; }
lf16() { tr -d '\r' < "$1" | sha256sum | cut -c1-16; }
echo "config sha256_16 $(sha "$W/r038751.config.json" | cut -c1-16)   (recipe: aaca26e1834bf17a)"
echo "traced_replay sha256_lf_16 $(lf16 "$W/tools/traced_replay.py")   (recipe: fcb280d0bca5ca9a)"
echo "pack sha256 $(sha "$W/pack.json")"
echo "expected    $PACK_SHA"
[ "$(sha "$W/pack.json")" = "$PACK_SHA" ] || { echo "pack sha mismatch" >&2; exit 3; }

ISO=(sudo -n unshare -n -- sudo -n -u "$(id -un)" env -i PATH=/usr/bin:/bin HOME="$W" LANG=C.UTF-8)
cd "$W"
echo "== network inside the sandbox (expect only lo)"
"${ISO[@]}" python3 -I -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(('192.168.1.202', 5432)); print('ROUTE EXISTS (bad)')
except OSError as e:
    print('no route:', e.strerror)"

echo "== replay"
"${ISO[@]}" /usr/bin/time -f "replay wall %e s, peak RSS %M KB" \
    python3 -I tools/audit_run.py audit_replay.json tools/codeprov_replay.py r038751 out.json \
    --config r038751.config.json --harness harness
echo "== verify"
set +e
"${ISO[@]}" /usr/bin/time -f "verify wall %e s, peak RSS %M KB" \
    python3 -I tools/audit_run.py audit_verify.json tools/th006_pack.py verify \
    --pack pack.json --pack-sha256 "$PACK_SHA" --replay out.json --published published.json
VERIFY=$?
set -e
echo "verify exit $VERIFY"
echo "== file accesses outside $W and the Python stdlib"
python3 -I tools/audit_run.py --report "$W" audit_replay.json audit_verify.json || true
echo "== adversarial controls on the real specimen"
"${ISO[@]}" /usr/bin/time -f "cheats wall %e s, peak RSS %M KB" \
    python3 -I tools/real_cheats.py out.json pack.json "$PACK_SHA" published.json
echo "== platform"
python3 -I -c "import platform,sys; print(platform.platform(), sys.version.split()[0])"
cd /
rm -rf "$W"
[ ! -e "$W" ] && echo "cleanup: $W removed"
pgrep -f "tools/(codeprov_replay|th006_pack|real_cheats|audit_run)\.py" >/dev/null && echo "cleanup: PROCESS LEFT" || echo "cleanup: no task process running"
exit $VERIFY
