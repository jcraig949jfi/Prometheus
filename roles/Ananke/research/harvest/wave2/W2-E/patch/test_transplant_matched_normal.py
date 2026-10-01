"""Regression test (W2-E A7). FAILS on current prometheus/ananke/campaign.py, PASSES with
patch/transplant_matched_normal.diff. Run:
  CUDA_VISIBLE_DEVICES=-1 python -m pytest test_transplant_matched_normal.py -q            (current code: FAIL)
  CUDA_VISIBLE_DEVICES=-1 W2E_PATCHED=1 python -m pytest test_transplant_matched_normal.py -q  (patched copy: PASS)
"""
import importlib.util, os, pathlib, sys
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
ROOT = pathlib.Path(__file__).resolve().parents[7]
sys.path.insert(0, str(ROOT))
import numpy as np
import torch
torch.set_num_threads(2)
from prometheus.ananke import envs, plants
from prometheus.ananke.physics import Physics


def _campaign():
    if os.environ.get("W2E_PATCHED") == "1":
        p = pathlib.Path(__file__).with_name("campaign_patched.py")
        spec = importlib.util.spec_from_file_location("prometheus.ananke.campaign_patched", p)
        m = importlib.util.module_from_spec(spec)
        m.__package__ = "prometheus.ananke"
        sys.modules[spec.name] = m
        spec.loader.exec_module(m)
        return m
    from prometheus.ananke import campaign
    return campaign


def test_transplant_battery_has_a_matched_normal_on_its_own_seeds():
    c = _campaign()
    assert not torch.cuda.is_available()
    ph = Physics(topology="ring", n_sites=16, radius=1, dest_mode="all", lat_base=1, lat_hop=0,
                 lat_jitter=0, loss=0.0, payload_width=1, channels=1, state_dim=1, prog_len=12,
                 update_mode="sync", update_period=1).validate()
    env = envs.EnvSpec(family="RELAY", d=1, delta=4, trials=4)
    g = plants.plant("relay_flood", ph)
    spec = {"search": c.search.SearchSpec().to_dict(), "search_seed": 12345}
    res = c.transplant_battery(ph, g, env, spec, device="cpu")
    assert "normal_same_seeds" in res, "transplants have no matched baseline (unpaired comparison)"
    # the baseline must be the unmodified law on the transplant seeds
    hs = c.assays.world_seeds(c.H_int(12345, 0x7A7A), 32)
    r = c.assays.evaluate(ph, g[None], env, hs, device="cpu", graph=False)
    assert abs(res["normal_same_seeds"]["acc"] - float(r.mean()[0])) < 1e-12
