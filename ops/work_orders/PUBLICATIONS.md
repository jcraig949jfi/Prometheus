# Master Work Order publication register

Maintained by Cyclops (registrar, MWO-0001 s2). One row per published MWO. Append-only.
This register records publication facts only. The order text lives in the archive file and is
never edited.

mwo_id   | archive path                                  | sha256 (LF bytes = git blob)                                      | publication commit                       | published_utc        | broadcast
MWO-0001 | ops/work_orders/archive/MWO-0001_2026-09-28.md | 007054adfdb1e6d78157f73c017e653983de9f93f21d835361e74d3f139b88f3 | 7e4c09f2ca8eae4a3a019dc43b3054e08bec3e77 | 2026-09-28 (see git) | comms #914 (to *)

Verify: git show origin/main:<archive path> | sha256sum ; CURRENT.md must hash identically while that
MWO is current.
Publication note (MWO-0001): the archive path was caught by the blanket "archive/" rule in .gitignore.
The same commit added "!ops/work_orders/archive/". The order text was not touched.

MWO-0002 | ops/work_orders/archive/MWO-0002_2026-09-29.md | 6f5a6a8bd3cfc977cda4fbfbc7131dc13ed73b6ecd5c71814a4bb7c9f9f43685 | 89512068ff07f0bab6953a36313d550167340722 | 2026-09-29T06:56:14Z | comms #961 (to *) | publishing seat: Aporia
Publication note (MWO-0002): two-commit protocol (MWO-0002 s2). P = 89512068f holds only CURRENT.md and the archive
copy; this row, the broadcast id and the publisher's WORK_STATE are in the separate record commit R. Publishing
seat Aporia by explicit operator custody designation for this publication only.
