You are being assigned a program-level drafting task.

Objective

Draft the next Prometheus Master Work Order, MWO-0002, whose primary purpose is to measure and report fleet migration to the single-MWO operating model established by MWO-0001.

Do not execute or publish MWO-0002 yet.

Produce a candidate Master Work Order for operator review.

Source of truth

Begin by fetching current Git state.

Read at minimum:

* ops/work_orders/CURRENT.md
* ops/work_orders/PUBLICATIONS.md
* MWO-0001’s immutable archive copy
* fabric/README.md
* fabric/PROTOCOL.md
* fabric/FREEZE.md
* current roles/*/WORK_STATE.json files where present
* latest pushed status/report material necessary to understand migration state

Use GitHub/repository evidence as authoritative. Do not rely on old Aporia stewardship assumptions.

Architectural ruling

Master Work Order authorship is not owned by Cyclops or any particular seat.

Any capable seat may draft a proposed MWO when assigned to do so.

Distinguish:

1. AUTHORING — synthesizing repository state into a candidate common work order.
2. APPROVAL — operator + central ChatGPT coordination accepts or revises the candidate.
3. PUBLICATION — after approval, a designated seat commits the approved text to the canonical MWO paths and broadcasts the pointer.

No author may make its own candidate authoritative merely by writing it.

Aporia is the author for this candidate. It is not thereby restored as a Prometheus steward.

MWO-0002 purpose

MWO-0002 should conduct a one-cycle migration census.

Every key live seat should report whether it has successfully migrated from bespoke prompting to the common model:

Git current MWO → seat work loop → Git durable state, with comms as notification and Fabric/A2A as the execution plane.

The census should determine whether each seat:

* found and adopted MWO-0001;
* can discover subsequent MWOs without a bespoke prompt;
* maintains useful machine-readable work state;
* can identify its current authorized work;
* checks comms correctly;
* uses Fabric/A2A where appropriate;
* understands Thread → Campaign → Experiment → Task → Attempt;
* uses the canonical lease authority where relevant;
* correctly distinguishes real operator/scientific gates from routine coordination;
* has any migration blockers or legacy conventions.

Important constraints

MWO-0002 is primarily a migration census, not a new science campaign.

Carry forward MWO-0001’s existing scientific assignments, blindness rules, custody boundaries, Fabric freeze, resource restrictions, and operator gates unless there is a concrete reason to change one.

Do not:

* reveal sealed information;
* authorize gated campaigns merely for the census;
* enable promexec;
* add Fabric features;
* create a new coordinator/steward layer;
* require seats to send lengthy comms reports;
* require a merge to main merely to report status;
* wake every dormant historical seat solely for paperwork.

Prefer a small machine-readable migration report committed by each seat, plus an updated WORK_STATE.

The key empirical question should be approximately:

If the unique bootstrap prompt that pointed this seat to MWO-0001 were never sent again, could the seat now continue routine Prometheus work by fetching the current MWO, checking comms/Fabric, and reading Git state?

A true hard scientific/operator gate does not count as migration failure.

MWO portability requirement

Write MWO-0002 so that any seat could have authored it and any designated seat could publish the approved text.

Do not encode Aporia-specific or Cyclops-specific authority into the general protocol.

If a registrar role is needed for this publication, define it as a temporary function of the designated publishing seat.

Deliverable

Create a candidate document, preferably:

roles/Aporia/proposals/MWO-0002_CANDIDATE.md

Also create a short author note stating:

* Git commit/state reviewed;
* principal design choices;
* ambiguities or policy conflicts discovered;
* anything you intentionally changed from MWO-0001;
* anything requiring operator decision before publication.

Commit and push the candidate.

Do not modify ops/work_orders/CURRENT.md.

Do not broadcast MWO-0002 as authoritative.

Return the candidate commit SHA and path for operator review.

After delivering the candidate, HOLD unless current authorized Aporia work exists independently of this assignment.
