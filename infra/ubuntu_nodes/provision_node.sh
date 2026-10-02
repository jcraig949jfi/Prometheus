#!/bin/bash
# Turn a freshly autoinstalled machine (hostname ubu-new, our SSH keys, passwordless sudo) into a swarm node.
# Run from ELSA or M2 (Git Bash is fine):   bash provision_node.sh <ip> <hostname>     e.g.  bash provision_node.sh 192.168.1.178 ubu004
#
# Steps: rename -> ubuntu_server_setup.sh -> clone/pull repo + git identity -> GitHub token -> reboot if needed ->
#        inventory, compared with ubu001 if reachable.
# GitHub token (never printed): C:\autoinstall_secrets\tokens\<hostname>.txt if present (deleted after use),
# else C:\autoinstall_secrets\tokens\shared.txt (kept, reused by every node), else the step is skipped.
set -u
IP=${1:?usage: provision_node.sh <ip> <hostname>}
NAME=${2:?usage: provision_node.sh <ip> <hostname>}
HERE=$(cd "$(dirname "$0")" && pwd)
TOKDIR=/c/autoinstall_secrets/tokens
REPO=https://github.com/jcraig949jfi/Prometheus.git
H=jcraig@$IP
SSH="ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new"
step() { echo; echo "=== $(date +%H:%M:%S) $*"; }
die() { echo "FAILED: $*"; exit 1; }

case "$NAME" in ubu[0-9][0-9][0-9]) ;; *) die "hostname must look like ubuNNN";; esac

step "0 reach $IP"
ssh-keygen -R "$IP" >/dev/null 2>&1          # a reinstalled machine has a new host key
$SSH $H true || die "can't SSH to $H with this machine's key"
$SSH $H 'sudo -n true' || die "no passwordless sudo on $H"
$SSH $H 'echo "now: $(hostname), $(. /etc/os-release; echo $PRETTY_NAME), $(nproc) threads, $(free -h | awk "/Mem:/{print \$2}") RAM, $(df -h / | awk "NR==2{print \$2}") root"'

step "1 hostname -> $NAME"
$SSH $H "sudo hostnamectl set-hostname $NAME && sudo sed -i 's/^127\.0\.1\.1.*/127.0.1.1 $NAME/' /etc/hosts && grep -q '^127.0.1.1' /etc/hosts || echo '127.0.1.1 $NAME' | sudo tee -a /etc/hosts >/dev/null; hostname"

step "2 ubuntu_server_setup.sh (disk, updates, lid, Wi-Fi power save, Claude Code, battery, linger; ~5-15 min)"
tr -d '\r' < "$HERE/ubuntu_server_setup.sh" | $SSH $H 'cat > /tmp/ubuntu_server_setup.sh'
$SSH $H 'sudo bash /tmp/ubuntu_server_setup.sh > /tmp/prom_setup.log 2>&1; echo "setup exit=$?"; grep -E "^=== |REBOOT|thresholds|skipped|failed|Claude Code\)" /tmp/prom_setup.log | sed "s/^/  /"'

step "3 repo + git identity"
$SSH $H "git config --global user.name 'James Craig ($NAME)'; git config --global user.email jcraig@jfi.ai; git config --global pull.ff only
  if [ -d ~/Prometheus/.git ]; then git -C ~/Prometheus pull -q && echo pulled; else git clone -q $REPO ~/Prometheus && echo cloned; fi
  git -C ~/Prometheus log -1 --format='  HEAD %h %cs'"

step "4 GitHub token"
TOK=""
[ -f "$TOKDIR/$NAME.txt" ] && TOK="$TOKDIR/$NAME.txt"
[ -z "$TOK" ] && [ -f "$TOKDIR/shared.txt" ] && TOK="$TOKDIR/shared.txt"
if [ -z "$TOK" ]; then
  echo "  no token file ($TOKDIR/$NAME.txt or shared.txt): skipped. Pull works without one; push doesn't."
else
  echo "  using $(basename "$TOK")"
  $SSH $H 'umask 077; cat > /tmp/.ghtok' < "$TOK"
  $SSH $H 'tr -d "\r\n\t " < /tmp/.ghtok | gh auth login --with-token --hostname github.com; rc=$?; shred -u /tmp/.ghtok; gh auth setup-git
    gh auth status 2>&1 | grep -o "Logged in to github.com account [a-z0-9]*" | sed "s/^/  /"
    cd ~/Prometheus && git push --dry-run origin HEAD:refs/heads/probe-$(hostname)-push-check >/dev/null 2>&1 && echo "  push dry-run OK" || echo "  push dry-run FAILED"; exit $rc' \
    && { [ "$(basename "$TOK")" = "$NAME.txt" ] && rm -f "$TOK" && echo "  per-node token file deleted from this machine"; true; }
fi

step "5 reboot if needed"
if $SSH $H '[ -f /var/run/reboot-required ]'; then
  $SSH $H 'sudo systemctl reboot' 2>/dev/null; sleep 30
  for i in $(seq 1 40); do $SSH $H true 2>/dev/null && break; sleep 10; done
  $SSH $H 'echo "  back: $(uname -r), $(uptime -p)"' || die "didn't come back after reboot"
else
  echo "  not needed"
fi

step "6 inventory"
tr -d '\r' < "$HERE/node_inventory.sh" > /tmp/node_inventory.$$
$SSH $H 'bash -s' < /tmp/node_inventory.$$ > /tmp/inv_new.$$ 2>&1
if $SSH jcraig@192.168.1.218 true 2>/dev/null; then
  $SSH jcraig@192.168.1.218 'bash -s' < /tmp/node_inventory.$$ > /tmp/inv_ref.$$ 2>&1
  echo "  key                  | $NAME | ubu001 (reference)   (! = differs)"
  # These are expected to differ per machine:
  SKIP='^(hostname|model|uptime|ram|disk_root|net|temp_max_C|battery_pct|git_user|authorized_keys|ssh_keys_own|repo_head|repo_behind|tmux_sessions|rc_services|rc_enabled|user_units|scripts_home|claude|claude_logged_in|claude_env_file|wifi_ps_svc|failed_units)='
  join -t= -a1 <(sort /tmp/inv_new.$$) <(sort /tmp/inv_ref.$$) | while IFS='=' read -r k a b; do
    if printf '%s=\n' "$k" | grep -Eq "$SKIP"; then flag=" "; else [ "$a" = "$b" ] && flag=" " || flag="!"; fi
    printf '%s %-20s | %s | %s\n' "$flag" "$k" "${a:0:45}" "${b:0:45}"
  done
else
  sed 's/^/  /' /tmp/inv_new.$$
fi
rm -f /tmp/node_inventory.$$ /tmp/inv_new.$$ /tmp/inv_ref.$$

step "DONE: $NAME at $IP. Still manual: Claude login (ssh $H, then claude), DHCP reservation, machine log entry."
