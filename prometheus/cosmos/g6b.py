"""Run the preregistered G6b (roles/Cosmos/campaigns/c0b/PREREG.md amendment B1) on a campaign store.

  python -m prometheus.cosmos.g6b <campaign_out_dir>
"""
import json
import sys
from pathlib import Path

from prometheus.cosmos import broker
from prometheus.cosmos.campaign0 import COMMITMENT
from prometheus.cosmos.store import Store


def main(out):
    out = Path(out)
    st = Store(out / "store")
    frozen = [l for l in st.laws() if l["freeze_hash"]]
    assert len(frozen) == 1, "expected exactly one frozen law"
    res = broker.intervene_fresh(st, frozen[0]["law_id"], COMMITMENT)
    (out / "G6b_intervention.json").write_text(json.dumps(res, indent=1, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1))
    print("receipt chain ok:", st.receipts.verify() is None)


if __name__ == "__main__":
    main(sys.argv[1])
