"""H-IMPL regression: assays.twin_assay reach on multi-sensor families.

The twin negates sense_val[t0:t1] for EVERY sensor column (XOR: 2 sensors,
MAJ: 5), but reach is the distance of diverged sites from sensor column 0
only. A program that never emits (S0 := SENSE) therefore reports reach 6 and
beyond_hop 1.0 on MAJ and reach 3 / beyond_hop 1.0 on XOR: the other sensors'
own local divergence is read as distal transport. campaign.classify turns
this into REACH_BEYOND_HOP (C1 rows: MAJ 114/162, XOR 48/83 flagged, 59 and
46 of them with comm_delta < .02).

The legacy keys feed frozen C1 labels, so the patch ADDS reach_nearest /
beyond_hop_nearest (distance to the nearest sensor actually perturbed) and
leaves reach / beyond_hop bit-identical. FAILS on the current code (keys
absent), PASSES with patches/twin_reach_nearest_sensor.diff. CPU only.
"""
import numpy as np
import pytest
import torch

from prometheus.ananke import assays, envs, plants
from prometheus.ananke.physics import Physics

torch.set_num_threads(2)
DEV = "cpu"
PH = Physics(topology="torus", n_sites=100, radius=1, state_dim=2, payload_width=1, channels=1,
             prog_len=12, rules=1).validate()
SEEDS = assays.world_seeds(0xB0B, 8)


@pytest.mark.parametrize("fam", ["MAJ", "XOR"])
def test_silent_program_has_no_distal_reach(fam):
    g = plants.plant("sense_copy", PH)                 # never writes O.emit: no packet exists
    env = envs.EnvSpec(family=fam, d=3, delta=8, trials=12)
    tw = assays.twin_assay(PH, g[None], env, SEEDS, device=DEV)
    # legacy ruler (kept for C1): the defect
    assert tw["beyond_hop"][0] == 1.0 and tw["reach"][0] >= 3.0
    # corrected ruler: divergence never leaves the perturbed sensors
    assert tw["reach_nearest"][0] == 0.0
    assert tw["beyond_hop_nearest"][0] == 0.0


@pytest.mark.parametrize("fam", ["RELAY", "FLIP"])
def test_single_perturbed_sensor_families_agree(fam):
    """Neutrality where only column 0 is perturbed (RELAY: K=1; FLIP: the
    teacher column is silent in the cue window): nearest == legacy."""
    g = plants.plant("relay_flood", PH)
    env = envs.EnvSpec(family=fam, d=3, delta=8, trials=16 if fam == "FLIP" else 12, block=4)
    tw = assays.twin_assay(PH, g[None], env, SEEDS, device=DEV)
    assert tw["reach"][0] > 1.0                          # the relay really reaches
    np.testing.assert_array_equal(tw["reach_nearest"], tw["reach"])
    np.testing.assert_array_equal(tw["beyond_hop_nearest"], tw["beyond_hop"])
