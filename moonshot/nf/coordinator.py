"""The Moonshot coordinator over Fabric (C-012-T003; contract s3). STUB: RED."""
MODULE = "moonshot.epoch.fabric_exec"


class CoordinatorError(Exception):
    pass


class Coordinator:
    def __init__(self, schema="moonshot", *, principal="Themis", campaign="C-012", actor="Themis"):
        raise NotImplementedError("C-012-T003")
