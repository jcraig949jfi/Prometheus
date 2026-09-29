MWO-0002 revision 1 at commit:

ed71a292d9b7e8ba177636a80c753995e97ece8e

is APPROVED FOR PUBLICATION.

The approved text is the candidate at:

roles/Aporia/proposals/MWO-0002_CANDIDATE.md

with exactly these three mechanical changes and no others:

1. Remove the entire opening candidate-warning paragraph:
    CANDIDATE -- NOT AUTHORITATIVE. This file is a proposal for operator review. It is not the current Master Work Order. No seat may act on it until an approved text is published at ops/work_orders/CURRENT.md.
2. Replace:
    Date: [set at approval] America/New_York
    with:
    Date: 2026-09-29 America/New_York
3. Replace:
    END MWO-0002 (CANDIDATE)
    with:
    END MWO-0002

No other wording, whitespace-sensitive content, policy, assignment, roster rule, census criterion, or scientific restriction is to be changed.

Aporia is explicitly designated as the publishing seat for MWO-0002. This approval is the custody authorization required by MWO-0001 §2 and by MWO-0002 §2.

Publish using the approved two-phase protocol:

Phase A — publication commit P

* write the approved text byte-identically with LF endings to ops/work_orders/CURRENT.md and the immutable MWO-0002 archive path;
* commit only those canonical MWO files;
* push P to origin/main;
* verify the two committed blobs are identical and record their SHA-256.

MWO-0002 becomes authoritative at P.

Phase B — notification and record commit R

* send the one fleet-wide broadcast referencing P;
* append the MWO-0002 row to ops/work_orders/PUBLICATIONS.md;
* update Aporia’s WORK_STATE using P as mwo_commit;
* commit and push those records as R;
* verify R on origin/main.

After publication, Aporia returns to HOLD/advisory. Authoring and publishing MWO-0002 confer no continuing steward, coordinator, scheduling, or adjudication authority.

Return the publication commit P, committed-blob SHA-256, broadcast ID, and record commit R.

---
Operator follow-up answer (AskUserQuestion, before Phase A), on the blind-lane exposure of the program name in s2a:
"Publish as approved".
