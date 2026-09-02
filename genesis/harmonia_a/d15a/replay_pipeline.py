#!/usr/bin/env python
"""D15-A deterministic warrant-feature pipeline (amendment A3).
Reconstructs a decision's exact epistemic inputs from the ENGINE ONLY:
world ledger + KnowledgeSet at seq. No client caches, no ambient state.
Prints sha256 of the canonical feature vector + the decision.
Usage: replay_pipeline.py <world_id> <seq>"""

import hashlib
import json
import sys

CLIENT = r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryClient"
sys.path.insert(0, CLIENT)
from sfclient.client import EngineClient

PIPELINE_VERSION = "warrant-features-v1"


def main():
    wid, seq = sys.argv[1], int(sys.argv[2])
    tok = open(r"C:\ZeusD-var\harmonia\sfe_token.txt").read().strip()
    c = EngineClient("https://192.168.1.202:8811", token=tok,
                     cafile=CLIENT + r"\config\m1.crt", timeout=60.0)
    evs = [e for e in c.events(wid, limit=500)
           if (e.get("seq") or e.get("world_index", 0)) is not None]
    # legal frontier: events with global seq <= decision seq
    def gseq(e):
        return e.get("seq") if e.get("seq") is not None else -1
    evs = sorted(evs, key=gseq)
    legal = [e for e in evs if gseq(e) <= seq]
    ks = c.knowledge_set(wid, seq=seq)
    feats = dict(
        pipeline=PIPELINE_VERSION,
        n_events=len(legal),
        n_observations=sum(1 for e in legal
                           if e["event_type"] == "OBSERVATION_RECORDED"),
        n_experiments=sum(1 for e in legal
                          if e["event_type"] == "EXPERIMENT_COMMITTED"),
        n_failures=sum(1 for e in legal
                       if e["event_type"] == "FAILURE_RECORDED"),
        n_artifacts_available=ks["available_count"],
        artifact_ids=sorted(x["artifact_id"] for x in ks["available"]),
        last_event_type=legal[-1]["event_type"] if legal else None)
    # frozen deterministic warrant rule (illustrative for the gate)
    if feats["n_observations"] == 0:
        decision = "OBSERVE_MORE"
    elif feats["n_failures"] > feats["n_observations"]:
        decision = "SYNTHESIZE"
    else:
        decision = "SEARCH_MORE"
    vec = json.dumps(dict(feats=feats, decision=decision),
                     sort_keys=True)
    print(hashlib.sha256(vec.encode()).hexdigest() + ":" + decision)


if __name__ == "__main__":
    main()
