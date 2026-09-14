# Consumer death 2026-09-13 18:12 local, relaunch 2026-09-14 06:05 local

Instance m1-1bb9a189 (boot pass). Measured, not inferred, except where marked.

## What was found at boot (2026-09-14 10:03Z)

    STATUS.md said     alive, pid 26164 at fb7aa5bed
    tasklist 26164     no such process
    heartbeat          vivarium@m1 age_s 42691 at 10:03:27Z -> last beat ~22:12Z 09-13
                       (18:12 EDT); build.code.base_sha fb7aa5bed; started_at 2026-09-12 17:44Z
    consumer log       last line 2026-09-13T18:27:33Z (row 88471869 EXECUTED, scope 623);
                       idle ticks are not logged, so the log cannot date the death
    var dir            no park-vivarium@m1.json, no stop flag
    scheduler task     VivariumConsumer Last Result -1073741510 = 0xC000013A
                       (STATUS_CONTROL_C_EXIT: console closed / Ctrl-C), Last Run 09-12 13:44:18
    host boot          2026-09-11 13:33:56 (no reboot)
    queue              queued 3 (created 09-13 18:27:30, 22:42:11, 09-14 02:57:10 UTC),
                       stranded 0

## Cause (strong coincidence, not a trace)

Windows Application log, same minute as the last heartbeat:

    2026-09-13 18:12:07  Application Error 1000: Faulting application WindowsTerminal.exe
                         1.24.2607.10001, module Windows.UI.Xaml.dll, exception 0xc00001ad
    2026-09-13 18:12:10  Windows Error Reporting 1001: MoAppCrash
                         Microsoft.WindowsTerminal_1.24.11911.0_x64

The task is "Interactive only"; on Windows 11 with Windows Terminal as the
default terminal, the launched .cmd is hosted in a WT window. A WT crash closes
the console, every console child gets CTRL_CLOSE, exit 0xC000013A. Nothing in
the logs names pid 26164 as WT's child, so this is the explanation that fits
every measured fact (minute, exit code, no park, no log line), not a proof.

C5 ("durable home ... so no chat session is its parent") removed the chat
session as parent and left a GUI app as parent. Same defect class, one level up.

## Why nobody noticed for 11.9 h

Rule 10 parks a LIVE process that is idle too long; a dead process cannot park.
MONITORS.md declares "15 min without a heartbeat while no row is current", but
no loop reads that threshold and posts. The only detector was a seat booting.

## Relaunch

    task action   BEFORE  F:\Prometheus-data\vivarium\vivarium_consumer.cmd
                  AFTER   C:\Windows\System32\conhost.exe F:\Prometheus-data\vivarium\vivarium_consumer.cmd
    started       2026-09-14 06:05:29 local, python pid 13460
    process tree  python 13460 <- cmd.exe 15900 <- conhost.exe 22268  (no WindowsTerminal)
    worktree      F:/Prometheus-worktrees/vivarium-consumer, clean, fb7aa5bed
                  (no commits under vivarium/ between fb7aa5bed and origin/main 6d72d1d19)
    heartbeat     alive, age 1.7 s, base_sha fb7aa5bed629daa3d9b300a829b2146d0f270003
    drained       ad1dd374 EXECUTED 10:05:33Z (2.50 s), 8b380a58 EXECUTED 10:05:33Z (0.42 s),
                  95dc53b4 EXECUTED 10:05:34Z (0.30 s); scope reconcile added 3 -> 626
    after         queued 0, stranded 0, completed 575, failed 79, cancelled 492

The conhost action removes the WT coupling; the console window can still be
closed by hand, and a logoff still ends an interactive-only task. Backlog C11.
