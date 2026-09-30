#!/bin/sh
# Install the promexec execution boundary on a Linux node (operator ruling 2026-09-28). Run with sudo. Idempotent.
#   sudo sh fabric/promexec/install.sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
[ "$(id -u)" = 0 ] || { echo "run with sudo" >&2; exit 1; }
CALLER=${SUDO_USER:?run via sudo from the fabric worker account}
SDV=$(systemctl --version | awk 'NR==1{print $2}')
[ "$SDV" -ge 247 ] || { echo "systemd $SDV < 247: ProtectProc=/ProcSubset= unsupported; round-2 broker refuses to install" >&2; exit 1; }
echo "== execution user promexec (system, no login, no groups, no password)"
id promexec >/dev/null 2>&1 || useradd --system --user-group --home-dir /var/lib/promexec --no-create-home --shell /usr/sbin/nologin promexec
passwd -l promexec >/dev/null 2>&1 || true
echo "   groups: $(id -Gn promexec)"
echo "== run area /var/lib/promexec/runs (root 0711: promexec may enter its own run dir, not list others)"
install -d -o root -g root -m 0755 /var/lib/promexec
install -d -o root -g root -m 0711 /var/lib/promexec/runs
echo "== execution python /opt/promexec/py (root-owned, read-only to promexec) with numpy + scipy"
if [ ! -x /opt/promexec/py/bin/python ]; then
  install -d -o root -g root -m 0755 /opt/promexec
  python3 -m venv /opt/promexec/py
  /opt/promexec/py/bin/pip install -q --only-binary=:all: numpy scipy
fi
chown -R root:root /opt/promexec; chmod -R go-w /opt/promexec
/opt/promexec/py/bin/python -m pip list --format=freeze 2>/dev/null | grep -iE '^(numpy|scipy)=='
echo "== broker /usr/local/sbin/promexec-run (root:root 0755, a COPY: the repo file is not what sudo runs)"
install -o root -g root -m 0755 "$HERE/broker.py" /usr/local/sbin/promexec-run
sha256sum /usr/local/sbin/promexec-run
echo "== sudoers: $CALLER may run exactly the broker, nothing else via this rule"
printf '%s ALL=(root) NOPASSWD: /usr/local/sbin/promexec-run\n' "$CALLER" > /etc/sudoers.d/promexec.tmp
visudo -cf /etc/sudoers.d/promexec.tmp >/dev/null && install -o root -g root -m 0440 /etc/sudoers.d/promexec.tmp /etc/sudoers.d/promexec
rm -f /etc/sudoers.d/promexec.tmp
echo "== stale run directories from the round-1 layout (root-owned area; none expected)"
ls -A /var/lib/promexec/runs | head -5
echo "== checks"
sudo -u promexec sudo -n true 2>/dev/null && echo "WARNING: promexec can sudo" || echo "   promexec has no sudo (promexec -> sudo refused)"
sudo -u promexec test -r /home/$CALLER 2>/dev/null && echo "WARNING: promexec can read /home/$CALLER" || echo "   promexec cannot read /home/$CALLER"
echo "done"
