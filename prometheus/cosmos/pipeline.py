"""The chamber: observe worlds into the graph, mine laws over lineage folds.

Universality gate: a law may be called CANDIDATE (cross-substrate) only when the
data span >= MIN_LINEAGES independent code lineages. With fewer, the best law is
reported as INSUFFICIENT_INDEPENDENCE, never as universal.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Sequence

import numpy as np

from prometheus.cosmos.contract import COORDS, Family
from prometheus.cosmos.independence import lineages
from prometheus.cosmos.miner import Miner, default_workers
from prometheus.cosmos.world import DEFAULT_EPISODES, evaluate

MIN_LINEAGES = 3


class Chamber:
    def __init__(self, families: Sequence[Family], store=None, episodes: int = DEFAULT_EPISODES,
                 campaign: str = "c0", code_sha: str = "?"):
        self.fams = {f.name: f for f in families}
        self.lineage = lineages({f.name: f.lineage for f in families})
        self.store = store
        self.episodes = episodes
        self.campaign = campaign
        self.code_sha = code_sha
        self.rows: List[Dict[str, Any]] = []
        self.n_queries = 0

    def observe(self, fam_name: str, params: Dict[str, Any], purpose: str = "sample", replicate: int = 0,
                parent: Optional[str] = None, edge_kind: Optional[str] = None, delta: Any = None,
                episodes: Optional[int] = None, keep: bool = True) -> Dict[str, Any]:
        fam = self.fams[fam_name]
        rec = evaluate(fam, params, replicate=replicate, episodes=episodes or self.episodes, campaign=self.campaign)
        self.n_queries += 1
        row = {"family": fam_name, "lineage": self.lineage[fam_name], "world_id": rec["world_id"],
               "params": params, "coords": fam.coords(params, "v1"), "coords_v2": fam.coords(params, "v2"),
               "y": int(rec["verdict"] == "PAYS"), "margin": rec["margin"], "se": rec["margin_se"],
               "acc": rec["acc"], "purpose": purpose, "replicate": replicate}
        if self.store is not None:
            self.store.add_node(rec["world_id"], fam_name, row["lineage"], params, row["coords"], row["coords_v2"], purpose)
            self.store.add_run(rec, purpose, self.code_sha)
            if parent and edge_kind:
                self.store.add_edge(parent, rec["world_id"], edge_kind, delta)
        if keep:
            self.rows.append(row)
        return row


def design(rows: Iterable[Dict[str, Any]], cmap: str = "v1"):
    rows = list(rows)
    key = "coords" if cmap == "v1" else "coords_v2"
    X = {c: np.array([r[key][c] for r in rows], float) for c in COORDS}
    y = np.array([r["y"] for r in rows], int)
    g = np.array([r["lineage"] for r in rows])
    fam = np.array([r["family"] for r in rows])
    return X, y, g, fam


def mine_rows(rows: Iterable[Dict[str, Any]], cmap: str = "v1", n_perm: int = 19, seed: int = 0,
              workers: Optional[int] = None, max_size: Optional[int] = None) -> Dict[str, Any]:
    X, y, g, fam = design(rows, cmap)
    kw = {} if max_size is None else {"max_size": max_size}
    M = Miner(X, y, g, **kw)
    res = M.mine(n_perm=n_perm, seed=seed, workers=default_workers() if workers is None else workers)
    n_lin = len(set(g.tolist()))
    res["n_lineages"] = n_lin
    res["n_families"] = len(set(fam.tolist()))
    res["cmap"] = cmap
    res["base_rate"] = float(y.mean())
    if res["verdict"] == "CANDIDATE" and n_lin < MIN_LINEAGES:
        res["verdict"] = "INSUFFICIENT_INDEPENDENCE"
        res["reason"] = "%d independent lineage(s) < %d; the law is at most lineage-local" % (n_lin, MIN_LINEAGES)
    return res
