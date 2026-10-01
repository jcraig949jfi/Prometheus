Revise the MWO-0002 candidate once, then return it for approval.

Your candidate at 7c84a44b481496f715b7b3a4319aa01df27eacd5 is accepted in substance, with the following rulings and one required protocol repair.

1. Publisher

Designate Aporia as the publishing seat for MWO-0002.

This is an explicit operator custody change under MWO-0001 section 2.

The architectural rule prospectively is:

* any assigned capable seat may AUTHOR a candidate;
* only operator-approved text may become authoritative;
* any seat designated in the approval may PUBLISH that approved MWO;
* publication authority lasts only for that publication and creates no steward/coordinator authority.

Aporia remains otherwise HOLD/advisory after publication.

2. Repair the publication protocol

The candidate’s current publication sequence is circular: the publication commit SHA does not exist until the publication commit is created, and the broadcast ID does not exist until after the broadcast.

Replace it with an explicit two-commit protocol.

Phase A — publication commit P

1. Write the approved text verbatim and byte-identically, LF-normalized, to:
    * ops/work_orders/CURRENT.md
    * the immutable archive path.
2. Commit those canonical MWO files. Call this commit P, the publication commit.
3. Push P to origin/main.
4. Verify both committed blobs from origin/main and compute their identical SHA-256.

At this point the MWO is published and authoritative.

Phase B — notification and publication record

5. Send one fleet-wide comms broadcast containing:
    * MWO ID;
    * publication commit P;
    * archive path;
    * committed-blob SHA-256;
    * fetch origin/main:ops/work_orders/CURRENT.md and adopt.
6. Append the publication record to ops/work_orders/PUBLICATIONS.md, including:
    * MWO ID;
    * archive path;
    * blob SHA-256;
    * publication commit P;
    * publication UTC time;
    * broadcast ID;
    * publishing seat.
7. Update the publishing seat’s WORK_STATE using P as mwo_commit.
8. Commit and push these records as a separate record commit R.
9. Verify R is on origin/main, then the registrar function ends.

Never require P to contain its own SHA or a future broadcast ID.

3. Census roster

Keep the Git-derived roster exactly as drafted.

Do not wake dormant or parked seats solely to file census paperwork.

A seat that does not become live during the census may be classified centrally as NOT_LIVE, not as a migration failure.

4. Seat instructions

Keep MWO-0001 scientific assignments carried forward by reference, as drafted.

Do not refresh all seat sections from a point-in-time snapshot.

The explicitly restated safeguards in your candidate are sufficient.

5. Stale ops/README.md

Do not repair the stale pilot banner before or during the census.

Keep it listed as known migration friction. MWO-0001/MWO-0002 govern where it conflicts.

Whether seats are confused by that stale lower-authority document is useful evidence for the migration census.

A later MWO may retire or correct it.

6. SI requests #603 and #608

Mark the held Selective Irreversibility steward-era freeze requests #603 and #608 CANCELED / SUPERSEDED AS COORDINATION REQUESTS.

Reason: the stewardship/sign-off mechanism that generated them was superseded by direct operator + central-MWO coordination.

This cancellation does not reject, validate, or otherwise adjudicate the underlying scientific ideas. Any still-useful scientific question may be proposed again through the current Thread/Campaign/MWO process.

Do not resurrect Aporia/Cyclops stewardship.

7. Everything else

Retain the candidate’s substantive census design:

* one small migration JSON per live seat;
* updated WORK_STATE;
* no required comms ACK/report;
* reports may remain on seat branches;
* YES claims require evidence pointers;
* central coordination, not seats, makes MIGRATED/PARTIAL classifications;
* explicitly measure how MWO-0001 and MWO-0002 were discovered;
* measure identifier drift rather than repairing it during the census;
* real scientific/custody/operator gates count as successful migration when represented correctly;
* Fabric limitations are migration evidence, not automatic seat failure;
* no science launch, spend, reveal, privilege expansion, promexec, or Fabric feature work.

Update the candidate and author note, commit and push the revision, and return the new candidate commit SHA and SHA-256.

Do not publish yet.
