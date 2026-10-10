# Host relaunch entry (C-013-T025, roadmap P-3)

    python -m rso.scale.runner relaunch <run_dir>          # run from a git WORKTREE of the repo, never the canonical checkout

One command, safe to fire forever. It decides from the run directory alone (`relaunch.py`): every chain COMPLETE ->
`COMPLETE`; a chain HALTED -> `HALTED` (exit 4, waits for a resolver); a live supervisor -> `RUNNING`; the last supervisor
stopped BLOCKED / CAP_REFUSED -> `BLOCKED` (exit 5, an operator's explicit `launch` re-arms it); otherwise it starts a
detached supervisor (`LAUNCHED`), which resumes from the last verified head (s3.8). Exit 0 for COMPLETE / RUNNING /
LAUNCHED. Idempotent: the check and launch run under `<run>/supervisor/.relaunch.lock` and return only once the new
supervisor is live, and `acquire_supervisor` is the second guard, so overlapping fires start one supervisor. Each fire is
one row in `<run>/supervisor/relaunch.jsonl`. The computation stays at supervisor + one worker (two processes).

## Tested with a SIMULATED scheduler only

`sched_sim.py` invokes the entry on a timer (a subprocess per fire, the command line below). Its fire test kills the
supervisor and the worker mid-epoch, then nothing but the timer acts: fire 1 LAUNCHED, fires 2-6 RUNNING, then COMPLETE;
digest == control (`evidence/RELAUNCH_FIRE_RESULT_T025.json`). **No OS scheduler task, service or timer was installed on
any host.** Installing one is the operator's decision (C-013 escalation-2 response); the commands below are written down
and were NOT run. Use the absolute path of a worktree and of the run directory.

## Install (operator, if and when wanted) -- NOT RUN

Windows Task Scheduler, every 5 minutes, as the current user (schtasks has no start-in directory, hence the `cd /d` wrapper):

    schtasks /Create /TN "Prometheus\relaunch-<runname>" /SC MINUTE /MO 5 /F ^
      /TR "cmd /c cd /d C:\Prometheus-worktrees\<worktree> && python -m rso.scale.runner relaunch C:\Prometheus-runs\<runname>"
    schtasks /Delete /TN "Prometheus\relaunch-<runname>" /F          :: remove it when the run is done

Linux systemd user timer (`~/.config/systemd/user/prom-relaunch@.service` and `.timer`):

    # prom-relaunch.service
    [Service]
    Type=oneshot
    WorkingDirectory=/home/<user>/Prometheus-worktrees/<worktree>
    ExecStart=/usr/bin/python3 -m rso.scale.runner relaunch /home/<user>/Prometheus-runs/<runname>
    # prom-relaunch.timer
    [Timer]
    OnBootSec=2min
    OnUnitActiveSec=5min
    [Install]
    WantedBy=timers.target

    systemctl --user daemon-reload && systemctl --user enable --now prom-relaunch.timer
    systemctl --user disable --now prom-relaunch.timer            # remove when the run is done

The supervisor is spawned detached (`supervisor.py` launch_detached), so the scheduler's job object / cgroup ending does
not take the run with it. After a reboot the timer's next fire resumes the run; a COMPLETE run makes every later fire a
no-op, so removing the timer is housekeeping, not a safety need.
