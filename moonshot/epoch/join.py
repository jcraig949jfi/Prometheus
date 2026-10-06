"""D5: node auto-join without auto-authorization (CONTRACT s8; design v0.3 N3/N7; C-008-T005)."""


class JoinRefused(Exception):
    """The node may not join: dirty checkout, unapproved code, or a missing prerequisite."""


class AncestryOracle:
    def __init__(self, code_dir, approval_ref):
        self.code_dir, self.approval_ref = code_dir, approval_ref

    def __call__(self, sha) -> bool:
        raise NotImplementedError("C-008-T005")


def node_store(remote, *, namespace, layout, local_dir, node_id):
    raise NotImplementedError("C-008-T005")


def join(remote, *, namespace, layout, code_dir, approval_ref="origin/main", node_id=None, workers=1, duration_s,
         data_dir, leases=True, ttl=60, host_label=None) -> dict:
    raise NotImplementedError("C-008-T005")
