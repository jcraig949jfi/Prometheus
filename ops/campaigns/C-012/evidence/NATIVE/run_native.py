"""C-012-T007: the first deterministic native-world epochs through the PostgreSQL path (OP-NF2), after T004 qualified
the path. Production Moonshot schema `moonshot` (created here if absent; idempotent), namespace "native", the CANONICAL
Fabric queue, frozen Fabric v0.2 workers on ubu001/ubu002 (the T003 driver's node functions, reused unchanged),
publisher/validator/coordinator on M2. Plumbing, not science: wforge worlds under the stateless affordable-seeded
policy (moonshot.native.wforge v1; F09's path never exercised), no organism, no survival search.

    python run_native.py stage --approved-sha SHA                 # deployment, BEFORE the window
    python run_native.py run --approved-sha SHA --out DIR [--world-seeds 1,5,8] [--ticks 8] [--epochs 4]
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO))
_s = importlib.util.spec_from_file_location("run_two_node", HERE.parent / "TWO_NODE" / "run_two_node.py")
TN = importlib.util.module_from_spec(_s)
_s.loader.exec_module(TN)

from moonshot.epoch import canonical as C  # noqa: E402
from moonshot.epoch import model  # noqa: E402
from moonshot.epoch import native_wforge as NW  # noqa: E402

SCHEMA, NAMESPACE = "moonshot", "native"
PRINCIPAL, CAMPAIGN, ACTOR = "Themis", "C-012", "Themis[m2-0e9b1ed2]"
TN.SCHEMA = SCHEMA                # the reused audit checks every moonshot-worker claim against THIS schema


def one_chain(co, approved, out, world_seed, ticks, epochs):
    from wforge import GRAMMAR_VERSION
    from wforge.genome import de_novo
    from wforge.world import expand
    genome = de_novo(GRAMMAR_VERSION, world_seed)
    mech = expand(genome)
    p = NW.genesis_params(genome, episode_seed=0, ticks_per_epoch=ticks, policy_seed=world_seed)
    cid = "NW{}-E0".format(world_seed)
    g = model.make_genesis(cid, epochs=epochs, params=p, approved_code_sha=approved,
                           initial_checkpoint=NW.initial_checkpoint(p), runtime=NW.NATIVE_WFORGE_V1)
    co.create_chain(g, namespace=NAMESPACE)
    rec = {"chain_id": cid, "world_id": p["world_id"], "genome": p["genome"], "episode_seed": 0,
           "ticks_per_epoch": ticks, "epochs": epochs, "horizon": mech.horizon, "n_slots": mech.n_slots,
           "delay": mech.delay, "stoch_rate": mech.stoch_rate, "corrupt_rate": mech.corrupt_rate,
           "obs_delay": mech.obs_delay, "wforge_world_sha256": p["wforge_world_sha256"],
           "genesis_sha256": C.sha256_hex(g.bytes), "steps": []}
    S, fab = TN.fabric()
    while co.reader.head(cid)["state"] == "OPEN":
        t = co.dispatch(cid)[0]
        done = TN.wait_task(S, fab, t["task_id"], timeout=900)
        rec["steps"].append({"epoch_index": t["epoch_index"], "task_id": t["task_id"], "state": done["state"],
                             "attempts": TN.timing(done), "published": co.publish_ready()})
    rec["head"] = co.reader.head(cid)
    rec["validation"] = co.validate(cid)
    receipt = co.receipt(cid)
    (out / "RECEIPT_{}.json".format(cid)).write_bytes(C.canonical_bytes(receipt["receipt"]))
    rec["receipt_sha256"] = receipt["sha256"]
    # the reference: the same world in one process, no Fabric, no database -- the published chain must equal it
    ref = model.replay_chain(g, epochs)
    rec["equals_reference_replay"] = [x["epoch_digest"] for x in co.reader.lineage(cid)] == \
        [r.epoch_digest for r in ref]
    return rec


def run(approved, out, world_seeds, ticks, epochs):
    from moonshot.nf import coordinator as K
    from moonshot.nf import pg
    NW._wforge()                                  # puts wforge on sys.path
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rec = {"schema": SCHEMA, "namespace": NAMESPACE, "approved_code_sha": approved, "started_at": TN.now(),
           "chains": []}
    rec["preflight_before"] = TN.preflight(approved)
    if rec["preflight_before"]["tasks_by_state"].get("submitted") or rec["preflight_before"]["running_attempts"]:
        raise SystemExit("canonical queue not empty: another seat's work could be claimed -- not starting")
    admin = pg.connect()
    pg.init_schema(admin, SCHEMA)                 # the production schema; idempotent
    admin.close()
    co = K.Coordinator(SCHEMA, principal=PRINCIPAL, campaign=CAMPAIGN, actor=ACTOR)
    TN.workers("start")
    try:
        for seed in world_seeds:
            rec["chains"].append(one_chain(co, approved, out, seed, ticks, epochs))
    finally:
        TN.workers("stop")
    rec["preflight_after"] = TN.preflight(approved)
    rec["audit"] = TN.audit(rec["started_at"])
    rec["ended_at"] = TN.now()
    (out / "RUN.json").write_text(json.dumps(rec, indent=1, default=str, sort_keys=True) + "\n", encoding="utf-8",
                                  newline="\n")
    co.close()
    print(json.dumps([{k: c[k] for k in ("chain_id", "world_id", "validation", "receipt_sha256",
                                          "equals_reference_replay")} for c in rec["chains"]], indent=1, default=str))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stage")
    s.add_argument("--approved-sha", required=True)
    r = sub.add_parser("run")
    r.add_argument("--approved-sha", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--world-seeds", default="1,5,8")
    r.add_argument("--ticks", type=int, default=8)
    r.add_argument("--epochs", type=int, default=4)
    a = ap.parse_args()
    if a.cmd == "stage":
        TN.stage(a.approved_sha, None)
    else:
        run(a.approved_sha, a.out, [int(x) for x in a.world_seeds.split(",")], a.ticks, a.epochs)


if __name__ == "__main__":
    main()
