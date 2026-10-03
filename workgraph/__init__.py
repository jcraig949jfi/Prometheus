"""workgraph -- the fleet's executable work-graph conventions (base role, DISTRIBUTED_WORK.md).

Task packets, leases and attempt receipts are committed JSON files under ops/campaigns/<C-id>/
(the Git-native control-plane layout, ops/initiatives/GIT_NATIVE_LAB_CONTROL_PLANE.md s4-s5).
This package only validates and reads them; Git is the store and a fast-forward push is the claim.
It is not a scheduler and it does not touch Fabric (fabric/FREEZE.md) or comms.
Standard library only.
"""
from .core import (  # noqa: F401
    LIFECYCLE, TERMINAL, TRANSITIONS, SATISFIED_DEFAULT, TASK_REQUIRED, RECEIPT_REQUIRED, ESCALATION_HEADERS,
    load_campaigns, load_tasks, validate_campaign, validate_task, validate_receipt, validate_escalation,
    can_transition, ready_for, transition, capability, validate_all,
)
