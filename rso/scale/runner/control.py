"""The uninterrupted control (C-013-T022): every chain replayed from its genesis in one process with Moonshot's
transport-free reference, moonshot.epoch.model.replay_chain (model.py:146-153). It reads only RUN_MANIFEST.json,
GENESIS.json and the genesis checkpoint object -- never HEAD, the lineage or the events -- so it cannot inherit
anything the interrupted run did."""
import time

from rso.scale.runner import account as A
from rso.scale.runner import engine as E
from rso.scale.runner import run as RUN
from rso.scale.runner import worker as W


def control(run_dir):
    m, mid = RUN.load_manifest(run_dir)
    engine = E.get_engine(m["engine"]["runtime"])
    chains, rows = {}, []
    c0 = time.process_time()
    for p in m["partitions"]:
        g = RUN.genesis(run_dir, p["chain_id"])
        out = W.M.replay_chain(g, m["epochs"], runner=W.moonshot_runtime(engine))
        final = engine.digest(engine.load_state(p["params"], out[-1].checkpoint))
        chains[p["chain_id"]] = {"head_epoch_digest": out[-1].epoch_digest, "final_state_digest": final,
                                 "epoch_digests": [r.epoch_digest for r in out]}
        rows.append({"chain_id": p["chain_id"], "head_epoch_digest": out[-1].epoch_digest,
                     "final_state_digest": final})
    return {"manifest_id": mid, "run_digest": A.run_digest(mid, rows), "chains": chains,
            "cpu_s": round(time.process_time() - c0, 6)}
