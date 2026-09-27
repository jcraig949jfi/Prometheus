#!/bin/bash
# Post-install setup for Ubuntu servers (written for the ThinkPad X1 Carbons, 2026-09-25).
# Needs: network up, jcraig with passwordless sudo. Runbook: ubuntu_server_install_runbook.md section 8.
# Run from M2:  scp ubuntu_server_setup.sh jcraig@<ip>:/tmp/ && ssh jcraig@<ip> "sudo nohup bash /tmp/ubuntu_server_setup.sh > /tmp/prom_setup.log 2>&1 < /dev/null &"
set -u
export DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a
step() { echo "=== $(date -u +%FT%TZ) $*"; }

step "1 extend root LV to full disk (installer default uses only 100 GB)"
lvextend -r -l +100%FREE /dev/ubuntu-vg/ubuntu-lv || echo "lvextend: nothing to do or failed"
df -h / | tail -1

step "2 apt update + full-upgrade"
apt-get update -q
apt-get -y -q -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold full-upgrade
apt-get -y -q install iw git curl htop tmux
apt-get -y -q autoremove

step "3 lid switch -> ignore"
mkdir -p /etc/systemd/logind.conf.d
printf '[Login]\nHandleLidSwitch=ignore\nHandleLidSwitchExternalPower=ignore\nHandleLidSwitchDocked=ignore\n' \
  > /etc/systemd/logind.conf.d/10-server-lid.conf
systemctl kill -s HUP systemd-logind

step "4 wifi power save off (driver option + service after wifi connects; a udev rule alone did NOT survive reboot)"
echo "options iwlmvm power_scheme=1" > /etc/modprobe.d/iwlwifi-powersave-off.conf
for d in /sys/class/net/wl*; do
  [ -e "$d" ] || continue
  n=$(basename "$d")
  printf '%s\n' \
    '[Unit]' \
    "Description=Turn off Wi-Fi power saving on $n" \
    "After=netplan-wpa-$n.service network-online.target" \
    'Wants=network-online.target' \
    '' \
    '[Service]' \
    'Type=oneshot' \
    'ExecStartPre=/bin/sleep 5' \
    "ExecStart=/usr/sbin/iw dev $n set power_save off" \
    'RemainAfterExit=yes' \
    '' \
    '[Install]' \
    'WantedBy=multi-user.target' > "/etc/systemd/system/wifi-powersave-off-$n.service"
  systemctl daemon-reload
  systemctl enable -q --now "wifi-powersave-off-$n.service"
  iw dev "$n" get power_save
done

step "5 Claude Code for jcraig"
sudo -u jcraig -H bash -lc 'curl -fsSL https://claude.ai/install.sh | bash' || echo "claude install failed"
sudo -u jcraig -H bash -lc '~/.local/bin/claude --version' || true

step "6 battery charge limits 75/80 (laptops only; skipped if no BAT0 thresholds)"
if [ -w /sys/class/power_supply/BAT0/charge_control_end_threshold ]; then
  printf '%s\n' \
    '[Unit]' \
    'Description=Battery charge limits (start 75%, stop 80%) for always-plugged server' \
    '' \
    '[Service]' \
    'Type=oneshot' \
    'ExecStart=/bin/sh -c "echo 75 > /sys/class/power_supply/BAT0/charge_control_start_threshold; echo 80 > /sys/class/power_supply/BAT0/charge_control_end_threshold"' \
    'RemainAfterExit=yes' \
    '' \
    '[Install]' \
    'WantedBy=multi-user.target' > /etc/systemd/system/battery-charge-limit.service
  systemctl daemon-reload
  systemctl enable -q --now battery-charge-limit.service
  echo "thresholds: start=$(cat /sys/class/power_supply/BAT0/charge_control_start_threshold) stop=$(cat /sys/class/power_supply/BAT0/charge_control_end_threshold)"
else
  echo "no battery thresholds; skipped"
fi

step "7 linger for jcraig (user services start at boot without a login)"
loginctl enable-linger jcraig
loginctl show-user jcraig -p Linger

step "8 reboot needed?"
[ -f /var/run/reboot-required ] && echo REBOOT_REQUIRED || echo NO_REBOOT_NEEDED
step DONE
