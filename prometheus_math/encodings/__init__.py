"""prometheus_math.encodings — capability-gap encoding primitives.

Per the 2026-05-07 contract-change window: 6 design docs landed for the
substrate's hunt-list capability gaps (Maass form, tropical curve, p-adic
L-function, Galois cohomology, large-cardinal consistency, motivic
period). Of those 6, T-2026-05-07-T023 (Maass form) ships a minimal impl
in this dispatch via :class:`OperatorOutputSequence`. The other 5 land
as design docs only; impl is deferred to future contract-change windows.

Per HARD-5: each encoding is structured around (object, operator-output)
pairs and operator-derived structural partitions, NOT human discipline
labels. Discipline metadata lives in ``notes`` fields, never in chart
coordinates.
"""
from prometheus_math.encodings.maass_form_hecke import (
    OperatorOutputSequence,
    SerializedMpf,
)

__all__ = [
    "OperatorOutputSequence",
    "SerializedMpf",
]
