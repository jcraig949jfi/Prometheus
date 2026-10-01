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

MWO-0003 | ops/work_orders/archive/MWO-0003_2026-09-29.md | 74dffcaef363cda5c65ab783046e3da83f6811a40b0b4f84b7916ec5a4c0f10b | 624a686ea066f971a83231e3b3528f9a29d41deb | 2026-09-29T11:14:53Z | comms #987 (to *) | publishing seat: Aporia

MWO-0004 | ops/work_orders/archive/MWO-0004_2026-09-29.md | 925660b2d2be53af2ee4195391e484d9649bbd4ee828cd60432ce2f0903a99df | 25a486d4494ad56a1ccba2c3fcefa3f462609a14 | 2026-09-29T11:42:53Z | comms #988 (to *) | publishing seat: Aporia

CWO-2026-09-30 | ops/fleet/CWO_2026-09-30_FLEET_ACTIVATION.md | ab93f64684d94771350848d2aef5d518f9045e1f8b79ba7834e419c83aba7b7e | (this commit) | 2026-09-30 | comms broadcast | executor: Aporia (operator CWO; supplements MWO-0004, CURRENT.md unchanged)
CWO-2026-09-30B | ops/fleet/CWO_2026-09-30B_FINISH_IN_PLACE.md | e62cb5ee986d78758ef9912642da1975ee32c715a091088de210d22d803000b9 | (this commit) | 2026-09-30 | comms broadcast | executor: Aporia (operator CWO; supplements MWO-0004; supersedes CWO-2026-09-30 auto-promotion)
CWO-2026-09-30C | ops/fleet/CWO_2026-09-30C_FINISH_SURFACE_DISPATCH.md | edc4792d30a7829709f1eb392ead55c092f47139c760879556ef17408c867e6c | (this commit) | 2026-09-30 | comms broadcast | executor: Aporia (operator CWO; governing fleet-operating order; supersedes conflicting CWO-2026-09-30/-30B text)
