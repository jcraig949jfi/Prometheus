#!/bin/bash
# Add an unprivileged, resource-capped side-project user to one ubu node.
# Run ON the node as jcraig (needs sudo):  bash add_mind_user.sh <username> "<ssh public key line>"
# Removes cleanly with:  sudo loginctl terminate-user <u>; sudo userdel -r <u>; sudo rm -rf /etc/systemd/system/user-<uid>.slice.d
set -euo pipefail
U="$1"; KEY="$2"
case "$KEY" in ssh-ed25519\ *|ssh-rsa\ *|ecdsa-sha2-*) ;; *) echo "not an SSH public key"; exit 1;; esac

id "$U" >/dev/null 2>&1 || sudo useradd --create-home --shell /bin/bash --comment "side project (not pantheon), no sudo" "$U"
sudo chmod 750 "/home/$U"
sudo chmod 750 /home/jcraig                     # jcraig's tokens stay unreadable to the side-project user
sudo install -d -m 700 -o "$U" -g "$U" "/home/$U/.ssh"
echo "$KEY" | sudo tee "/home/$U/.ssh/authorized_keys" >/dev/null
sudo chown "$U:$U" "/home/$U/.ssh/authorized_keys"; sudo chmod 600 "/home/$U/.ssh/authorized_keys"
sudo loginctl enable-linger "$U"                 # its user services may run without a login

# Caps: half the CPU threads, 40% of RAM, so fleet workers and seats are never starved.
UID_=$(id -u "$U"); CPUS=$(nproc); Q=$(( CPUS * 50 ))
sudo mkdir -p "/etc/systemd/system/user-${UID_}.slice.d"
printf '[Slice]\nCPUQuota=%d%%\nMemoryMax=40%%\nTasksMax=2048\n' "$Q" | sudo tee "/etc/systemd/system/user-${UID_}.slice.d/50-side-project-limits.conf" >/dev/null
sudo systemctl daemon-reload
echo "$(hostname): user $U uid $UID_ ready; CPUQuota=${Q}% of ${CPUS} threads, MemoryMax=40%"
