# ops/operator_queue -- decisions only the operator can make

GLOBAL control plane (EP-GLOBAL / TH-GLOBAL-CONTROL-PLANE). Created 2026-10-03 (verbatim: roles/Achilles/prompts/2026-10-03_generic_workers/).

- priority/PRQ-<YYYYMMDD>-<Seat>-<n>.json -- one priority-elevation request per file (schema and lifecycle:
  roles/base-role/DISTRIBUTED_WORK.md s14). A seat writes REQUESTED; only the operator decides.
- PRIORITY_REQUESTS.md -- generated view (`python -m workgraph prq render`); never edited by hand.

The census email shows the open requests at its top. Git is the authority; comms carries notifications.
