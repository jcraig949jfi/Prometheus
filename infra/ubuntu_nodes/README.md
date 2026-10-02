# Ubuntu swarm nodes (ubu001, ubu002, ...)

Old laptops/desktops converted to Ubuntu Server to run always-on Claude Code for Prometheus. Started 2026-09-25 by
Harmonia[m2-475d761f] with the operator; ubu001 and ubu002 are the guinea pigs.

| File | What |
|---|---|
| `ubuntu_server_install_runbook.md` | Bare metal to Ubuntu + network (s1-s7), post-install setup from M2 (s8) |
| `ubuntu_server_setup.sh` | Post-install script (disk, updates, lid, Wi-Fi power save, battery 75/80, linger, Claude Code) |
| `ubuntu_server_machines.md` | Per-machine log: hardware, IPs, battery health, what was changed |
| `ubuntu_swarm_node_plan.md` | Node lifecycle N0-N10, auth / session / watchdog design, dated log |
| `ubuntu_swarm_todo.md` | Open items; cleanup list; checklist for adding the next machines |
| `autoinstall/` | Hands-off install: CIDATA stick template + builder (`build_cidata.py`) |

No secrets live here: tokens and passwords stay on the nodes (see the plan s4). This is infrastructure record-keeping and
is independent of the `ops/` Git-native initiative (which is PILOT ONLY).
