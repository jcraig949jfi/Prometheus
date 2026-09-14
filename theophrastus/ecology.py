"""The founding ecology, exactly as preregistered in
roles/Theophrastus/crucible/PREREG_FOUNDING_CRUCIBLE_2026-09-13.md.

Mechanism hexes are read from Herakles's embedded genome record and ASSERTED
against the preregistered constants, so a drift in either is a failure here
rather than a silently different experiment.
"""
from __future__ import annotations

import sys
from pathlib import Path

from .cell import (UNKNOWN, Branch, Cell, Intervention, Mechanism, Pressure,
                   Repeat, World)

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from herakles.evca import genomes as _g            # noqa: E402

PROVENANCE = "herakles/evca/genomes.py GENOMES[%r] (RECOVERED_SPECIMEN; %s)"

#: preregistered hexes; the assertion below is the drift guard
PREREG_HEX = {
    "maj": "000101170117177f0117177f177f7fff",
    "GKL": "005f005f005f005f005fff5f005fff5f",
    "exp": "0505408305c90101200b0efb94c7cff7",
    "par": "0504058705000f77037755837bffb77f",
}
for _n, _hx in PREREG_HEX.items():
    assert _g.rule_hex(_n) == _hx, ("genome %s drifted from prereg" % _n)

MECHANISMS = {n: Mechanism(n, PREREG_HEX[n],
                           PROVENANCE % (n, _g.GENOMES[n]["source"]))
              for n in PREREG_HEX}

BRANCH_EVIDENCE = ("herakles/evca/genomes.py GENOMES[*].kind and .source "
                   "(published characterisation: EvCA review Table 1 / "
                   "EvEmComp Table 1)")
BRANCHES = {
    "hand_designed": Branch("hand_designed",
                            (PREREG_HEX["maj"], PREREG_HEX["GKL"]),
                            BRANCH_EVIDENCE, relation="sibling_of:ga_evolved_1993_95"),
    "ga_evolved_1993_95": Branch("ga_evolved_1993_95",
                                 (PREREG_HEX["exp"], PREREG_HEX["par"]),
                                 BRANCH_EVIDENCE, relation="sibling_of:hand_designed"),
}
BRANCH_OF = {"maj": "hand_designed", "GKL": "hand_designed",
             "exp": "ga_evolved_1993_95", "par": "ga_evolved_1993_95"}

WORLDS = {
    "W149": World("W149", 149, 320),
    "W599": World("W599", 599, 1198),
    "W149h": World("W149h", 149, 298),
    "W599h": World("W599h", 599, 1286),
}

PRESSURES = {
    "P_iid": Pressure("P_iid", (None,), 100, "stable"),
    "P_unif": Pressure("P_unif", (0.1, 0.2, 0.3, 0.4, 0.45, 0.55, 0.6, 0.7,
                                  0.8, 0.9), 10, "stable"),
    "P_iid_T": Pressure("P_iid_T", (None,), 100, "at_T"),
}

INTERVENTIONS = {
    "NONE": Intervention("NONE", "none"),
    "REFLECT": Intervention("REFLECT", "reflect"),
}

SEED_PRIMARY = 20260913
SEED_REPLICATION = 20260914
REPEAT = Repeat(count=8, seed_derivation="sha256_index", max_seconds=600)

BUDGET_EXECUTIONS = 45
BUDGET_WALL_S = 3600


def cell(mech: str, world: str, pressure: str, intervention: str = "NONE",
         seed_root: int = SEED_PRIMARY, proposer: str = "prereg",
         rationale: str = "") -> Cell:
    return Cell(mechanism=MECHANISMS[mech], pressure=PRESSURES[pressure],
                world=WORLDS[world], branch=BRANCHES[BRANCH_OF[mech]],
                intervention=INTERVENTIONS[intervention], seed_root=seed_root,
                repeat=REPEAT,
                proposal={"proposer": proposer, "rationale": rationale,
                          "llm_generated": False})


def coverage_pass(seed_root: int = SEED_PRIMARY):
    """4 mechanisms x 2 worlds x 2 pressures, intervention NONE (16)."""
    return [cell(m, w, p, "NONE", seed_root, "prereg:coverage")
            for m in ("maj", "GKL", "exp", "par")
            for w in ("W149", "W599")
            for p in ("P_iid", "P_unif")]


def intervention_stencil(seed_root: int = SEED_PRIMARY):
    return [cell(m, "W149", "P_iid", "REFLECT", seed_root, "prereg:stencil:intervention")
            for m in ("GKL", "exp", "par", "maj")]


def resource_stencil(seed_root: int = SEED_PRIMARY):
    return [cell(m, w, "P_iid", "NONE", seed_root, "prereg:stencil:resource")
            for m in ("GKL", "exp") for w in ("W149h", "W599h")]


def exact_null_stencil(seed_root: int = SEED_PRIMARY):
    return [cell("GKL", "W149", "P_iid_T", "NONE", seed_root, "prereg:stencil:exact_null")]


def anchors(seed_root: int = SEED_REPLICATION):
    return [cell("GKL", "W149", "P_iid", "NONE", seed_root, "prereg:replication:anchor"),
            cell("exp", "W149", "P_iid", "NONE", seed_root, "prereg:replication:anchor")]
