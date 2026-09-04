#!/usr/bin/env python
"""First Prometheus end-to-end integration: one frozen UNKNOWN Proteus
organism -> one real SFE world -> one bounded encounter -> real SFE
event anchor. Produces integration_record.json consumed by the PEW
writer. NO scoring, NO selection, NO mutation, NO phenotype claim."""

import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, r"D:\Prometheus")
sys.path.insert(0, r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryClient")
sys.path.insert(0, str(Path(__file__).parent))

from sfclient.client import EngineClient, EngineError          # noqa: E402
from proteus.foundry.vm import Player, Meter                   # noqa: E402
from proteus.foundry.prng import SplitMix64                    # noqa: E402
from proteus.foundry.lineage import checkpoint, restore        # noqa: E402
from proteus.foundry.export import encounter_identity          # noqa: E402
import adapter                                                 # noqa: E402

BASE = "https://192.168.1.202:8811"
CA = (r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryClient"
      r"\config\m1.crt")
PIN = ("sha256:5274ddbe9120ddbbd75a36965106d2efe640a3b72278e7bb97b8"
       "2e356e1fc9fc")
OUT = Path(__file__).parent

# ---- frozen encounter specification (recorded BEFORE execution) ------
ENC_SEED = 20260904
TICKS_MAX = 16
CHECKPOINT_AT_TICK = 8
N_OUT = 1
def tick_inputs(t):            # one channel carrying the tick index
    return [[t]]


def run_ticks(player, st, rng, t0, t1, meter=None):
    """Run ticks t0..t1-1; returns rows of (tick, outputs, status, ops)."""
    rows = []
    for t in range(t0, t1):
        m = Meter()
        outputs, status = player.run_tick(st, tick_inputs(t), N_OUT, rng,
                                          meter=m)
        rows.append(dict(tick=t, outputs=outputs, status=status,
                         ops=m.ops))
        if status == "halt":
            break
    return rows


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()
                          ).hexdigest()


def main():
    rec = dict(started=time.time())
    # ---- specimen ----------------------------------------------------
    sp = adapter.load_specimen()
    oid = sp["organism_id"]
    rec["organism_id"] = oid
    print("specimen:", oid[:16], "phenotype:",
          sp["entry"]["extrinsic"]["phenotype"])

    # ---- engine + world ----------------------------------------------
    tok = open(r"C:\ZeusD-var\harmonia\sfe_token.txt").read().strip()
    c = EngineClient(BASE, token=tok, cafile=CA, timeout=60.0)
    v = c.version()
    assert v["engine_source_hash"] == PIN, "engine build changed - record"
    rec["engine"] = v
    sid = c.create_session("first-prometheus-integration")
    w = c.create_world(sid, "first-integration-arena",
                       seed_root=424242,
                       budget={"experiments": {"limit": 4,
                                               "enforcement":
                                               "enforceable"}})
    wid = w["world_id"]
    c.start(wid)
    rec["session_id"] = sid
    rec["world"] = dict(world_id=wid, seed_root=424242,
                        sharing_policy="ISOLATED",
                        head_hash_at_create=w.get("head_hash"))
    print("world:", wid)

    # ---- artifact placement gate -------------------------------------
    placement = adapter.place_in_world(c, wid, sp)
    rec["placement"] = placement
    print("placement gate PASS: blob_hash == sha256:organism_id,"
          " read-back byte-equal")

    # ---- encounter identity (the SPECIFICATION) ----------------------
    enc_id = encounter_identity([oid], wid, ENC_SEED, [])
    rec["encounter"] = dict(
        encounter_id=enc_id, world_binding_id=wid, seed=ENC_SEED,
        ticks_max=TICKS_MAX, n_out=N_OUT,
        inputs_protocol="one channel [[tick_index]] per tick",
        checkpoint_at_tick=CHECKPOINT_AT_TICK, checkpoint_ids_in_spec=[])
    print("encounter_id:", enc_id[:16])

    # ---- prospective prediction BEFORE experiment commit -------------
    hyp = c.hypothesis(wid, "a frozen Proteus organism traverses "
                            "Proteus->SFE->encounter with identity "
                            "preserved and deterministic replay")
    pred = c.prediction(wid, hyp, {
        "claim": "artifact blob_hash equals sha256:organism_id; "
                 "full-run replay and checkpoint-continuation are "
                 "bit-identical",
        "organism_id": oid, "encounter_id": enc_id})
    exp = c.experiment(wid, {
        "kind": "proteus_bounded_encounter",
        "organism_id": oid, "artifact_id": placement["artifact_id"],
        "encounter": rec["encounter"]},
        hyp_id=hyp, pred_id=pred, enqueue=True)
    exp_id = exp["exp_id"]
    wk = c.claim("harmonia-m2-integration", world_id=wid)
    work_id, claim_id = wk["work_id"], wk["claim_id"]
    rec["run"] = dict(exp_id=exp_id, work_id=work_id,
                      run_id=f"{exp_id}:{work_id}",
                      hyp_id=hyp, pred_id=pred)
    print("run_id:", rec["run"]["run_id"])

    # ---- execute the bounded encounter -------------------------------
    player = Player(sp["manifest"])
    st = player.fresh_state()
    rng = SplitMix64(ENC_SEED)
    rows_a = run_ticks(player, st, rng, 0, CHECKPOINT_AT_TICK)
    rng_state_at_ckpt = rng.state          # Harmonia preserves RNG position
    snap = checkpoint(oid, st, enc_id, CHECKPOINT_AT_TICK)
    rows_b = run_ticks(player, st, rng, CHECKPOINT_AT_TICK, TICKS_MAX)
    run1 = rows_a + rows_b
    rec["execution"] = dict(
        rows=run1, statuses=[r["status"] for r in run1],
        outputs_digest=digest([r["outputs"] for r in run1]),
        ops_total=sum(r["ops"] for r in run1),
        checkpoint_id=snap["checkpoint_id"],
        rng_state_at_checkpoint=rng_state_at_ckpt)
    json.dump(snap, open(OUT / "encounter_checkpoint.json", "w"))
    print("encounter executed:", len(run1), "ticks; statuses:",
          rec["execution"]["statuses"][:4], "...")

    # ---- replay gate 1: full-run replay ------------------------------
    p2 = Player(sp["manifest"])
    st2 = p2.fresh_state()
    rng2 = SplitMix64(ENC_SEED)
    run2 = run_ticks(p2, st2, rng2, 0, TICKS_MAX)
    replay_exact = (
        [r["outputs"] for r in run1] == [r["outputs"] for r in run2]
        and [r["status"] for r in run1] == [r["status"] for r in run2]
        and [r["ops"] for r in run1] == [r["ops"] for r in run2]
        and st == st2)
    # ---- replay gate 2: restore + continuation -----------------------
    st3 = restore(snap)                    # refuses foreign runtime_hash
    rng3 = SplitMix64(ENC_SEED)
    rng3.state = rng_state_at_ckpt         # external RNG position restored
    p3 = Player(sp["manifest"])
    run3 = run_ticks(p3, st3, rng3, CHECKPOINT_AT_TICK, TICKS_MAX)
    cont_exact = (
        [r["outputs"] for r in run3] == [r["outputs"] for r in rows_b]
        and [r["status"] for r in run3] == [r["status"] for r in rows_b]
        and st3 == st)
    rec["replay_gate"] = dict(full_replay_exact=replay_exact,
                              checkpoint_continuation_exact=cont_exact,
                              checkpoint_binds_organism=(
                                  snap["organism_id"] == oid))
    print("replay gates:", rec["replay_gate"])
    if not (replay_exact and cont_exact):
        raise SystemExit("REPLAY GATE FAILED - preserve and stop")

    # ---- complete work + engine-attested observation -----------------
    c.complete(work_id, "harmonia-m2-integration", claim_id, {
        "ticks": len(run1),
        "statuses": rec["execution"]["statuses"],
        "outputs_digest": rec["execution"]["outputs_digest"],
        "ops_total": rec["execution"]["ops_total"],
        "checkpoint_id": snap["checkpoint_id"]})
    outcome = ("SURVIVED" if (replay_exact and cont_exact
                              and placement["readback_bytes_equal"])
               else "INCONCLUSIVE")
    obs = c.observation(wid, exp_id, {
        "outputs_digest": rec["execution"]["outputs_digest"],
        "statuses": rec["execution"]["statuses"],
        "identity_gate": "blob_hash==sha256:organism_id",
        "replay": rec["replay_gate"]},
        outcome, pred_id=pred, work_id=work_id)
    rec["observation"] = dict(outcome=outcome, response=obs)
    st_w = c.status(wid)
    rec["engine_attested"] = st_w.get("epistemics", {}).get(
        "observations_engine_attested")
    print("observation outcome:", outcome, "| engine-attested:",
          rec["engine_attested"])

    # ---- event anchor ------------------------------------------------
    evs = c.events(wid, limit=100)
    evs = evs["events"] if isinstance(evs, dict) else evs
    matches = [e for e in evs
               if e["event_type"] == "OBSERVATION_RECORDED"
               and (e.get("refs") or {}).get("exp_id") == exp_id]
    if len(matches) != 1:
        json.dump(dict(candidates=[{k: str(e.get(k)) for k in
                                    ("event_id", "event_type", "refs")}
                                   for e in evs]),
                  open(OUT / "anchor_ambiguity.json", "w"), indent=1)
        raise SystemExit(f"SFE_EVENT_PROVENANCE_AMBIGUOUS: "
                         f"{len(matches)} strict matches - stop before PEW")
    anchor = matches[0]
    rec["anchor"] = dict(sfe_event_id=anchor["event_id"],
                         sfe_entry_hash=anchor["entry_hash"],
                         sfe_event_seq=int(anchor["event_seq"]),
                         event_type=anchor["event_type"],
                         world_id=anchor["world_id"])
    rec["world"]["head_hash_final"] = c.status(wid).get("head_hash")
    print("anchor:", anchor["event_id"], "seq", anchor["event_seq"])

    rec["finished"] = time.time()
    json.dump(rec, open(OUT / "integration_record.json", "w"), indent=1,
              default=str)
    print("integration_record.json written")


if __name__ == "__main__":
    main()
