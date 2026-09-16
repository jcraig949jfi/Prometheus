OPERATOR GATE (Vivarium, 2026-09-16): two tokens have to cross from M1 to M2
by your hand before the consumer can run on M2. Everything else is done.

WHAT: the file  vivarium/config.local.json  in the M1 consumer's pinned
      worktree  F:\Prometheus-worktrees\vivarium-consumer\vivarium\
      (gitignored; holds sfe_token and pew_token, the credentials of the
      SFE client "vivarium" that OWNS the 617 viv-* worlds and the B1 grant,
      and of the PEW writer). No seat copies a token across hosts (Daedalus
      ruling #270); the only alternative -- a NEW client registered from M2 --
      would not own the worlds every queued row and the B1 scope are keyed
      to, so it is not an alternative for this consumer.

WHERE TO: D:\Prometheus-worktrees\vivarium-consumer\vivarium\config.local.json
      on M2 (the pinned worktree deploy/prepare_m2.py creates at the SHA
      named in its receipt). Only the two token keys are needed there:
      every other setting (canonical store, M2 engine URL and cert, M2 PEW,
      var_dir) is set by the launcher's environment.

HOW I WILL KNOW: prepare_m2.py reports key NAMES only ("sfe_token_present",
      "pew_token_present"); it never reads or prints a value. Its receipt
      lands in D:\Prometheus-data\vivarium\.

WHEN: after Daedalus's step 2 (ledger eng_8a37a5d3 answering at
      192.168.1.191:8811) and Harmonia's step 3 (contract promoted). Then
      `schtasks /Change /TN VivariumDeadmanM2 /ENABLE` is the launch; its
      first tick relaunches the consumer if and only if the engine identity
      holds, and the receipt is var/deadman-vivarium@m2.state.json.

RECOMMENDATION: carry the file (it is the smaller risk: one gitignored file
      with a dated receipt line in roles/Vivarium/journal), rather than mint
      a new owner identity for 617 worlds.
