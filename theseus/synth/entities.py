"""ENTITIES and GENEALOGY.

Entity (charter shape, JSON on disk):
  id, generation, ancestry (sorted ids of ALL ancestors), origin
  ("human" | "synthetic" | "control" | "known"; an evolved lens is
  origin "synthetic" with kind "lens"), executableRepresentation
  (genome, or a Tyche lens genome for kind="lens"), behavioralFingerprint,
  lensDependencies, parentIds (ORDERED: collisions are noncommutative),
  metadata, plus Theseus bookkeeping: kind, lane, state (decision state),
  born_step.

origin "control" and "known" entities never enter the synthetic genealogy
as parents unless a control explicitly says so; they are separate roots.

Genealogical rulers (charter "GENEALOGICAL NOVELTY"), all exact:
  generation            1 + max parent generation (G0 = 0)
  min_depth_to_g0       shortest parent-path to any origin=human ancestor
                        (None when no human ancestor exists)
  mean_ancestry_depth   mean over all ancestors of their shortest distance
  raw_human_rule_frac   fraction of the genome's rules copied UNCHANGED from
                        a G0 genome (rule provenance "G0:*")
  parent_synth_frac     fraction of immediate parents with origin synthetic
  grandparents_synth    True when every grandparent is synthetic
  n_g0_ancestors, ancestral_diversity (distinct G0 roots / all G0)
None of these is conceptual novelty; they are one axis.
"""

from __future__ import annotations

from collections import deque

DECISION_STATES = ("UNTOUCHED", "ALIVE", "DARK", "NOVEL_NICHE", "REPLICATING",
                   "TRANSFER", "INTERPRET", "FOSSIL", "PARK")


class Registry:
    def __init__(self):
        self.E = {}
        self._depth_cache = {}

    def add(self, e):
        assert e["id"] not in self.E, e["id"]
        for p in e.get("parentIds", []):
            assert p in self.E, f"unknown parent {p}"
        anc = set()
        for p in e.get("parentIds", []):
            anc.add(p)
            anc |= set(self.E[p]["ancestry"])
        e["ancestry"] = sorted(anc)
        pg = [self.E[p]["generation"] for p in e.get("parentIds", [])]
        e["generation"] = 1 + max(pg) if pg else e.get("generation", 0)
        e.setdefault("state", "UNTOUCHED")
        e.setdefault("lensDependencies", [])
        self.E[e["id"]] = e
        return e

    def __getitem__(self, k):
        return self.E[k]

    def __contains__(self, k):
        return k in self.E

    def values(self):
        return self.E.values()

    # ---------------------------------------------------------------- rulers

    def min_depth_to_g0(self, eid):
        if eid in self._depth_cache:
            return self._depth_cache[eid]
        seen = {eid: 0}
        q = deque([eid])
        best = None
        while q:
            x = q.popleft()
            if self.E[x]["origin"] == "human":
                best = seen[x]
                break
            for p in self.E[x].get("parentIds", []):
                if p not in seen:
                    seen[p] = seen[x] + 1
                    q.append(p)
        self._depth_cache[eid] = best
        return best

    def ancestor_depths(self, eid):
        seen = {eid: 0}
        q = deque([eid])
        while q:
            x = q.popleft()
            for p in self.E[x].get("parentIds", []):
                if p not in seen:
                    seen[p] = seen[x] + 1
                    q.append(p)
        seen.pop(eid)
        return seen

    def genealogy(self, eid, n_g0_total=None):
        e = self.E[eid]
        parents = e.get("parentIds", [])
        depths = self.ancestor_depths(eid)
        g0 = [a for a in e["ancestry"] if self.E[a]["origin"] == "human"]
        rules = e["executableRepresentation"].get("rules", []) if e.get("kind") != "lens" else []
        raw = sum(1 for r in rules if str(r.get("prov", "")).startswith("G0:"))
        gps = [gp for p in parents for gp in self.E[p].get("parentIds", [])]
        return {
            "generation": e["generation"],
            "min_depth_to_g0": self.min_depth_to_g0(eid),
            "mean_ancestry_depth": (sum(depths.values()) / len(depths)) if depths else 0.0,
            "raw_human_rule_frac": (raw / len(rules)) if rules else 0.0,
            "parent_synth_frac": (sum(self.E[p]["origin"] == "synthetic" for p in parents) / len(parents)) if parents else 0.0,
            "grandparents_synth": bool(gps) and all(self.E[g]["origin"] == "synthetic" for g in gps),
            "has_direct_human_parent": any(self.E[p]["origin"] == "human" for p in parents),
            "n_g0_ancestors": len(g0),
            "ancestral_diversity": (len(g0) / n_g0_total) if n_g0_total else None,
            "n_ancestors": len(e["ancestry"]),
        }


# ------------------------------------------------------------------ lanes

LANES = ("G0", "SHALLOW", "DEEP", "VERY_DEEP")
DEEP_MIN_GEN = 5


def eligible(reg, eid, lane):
    """May entity eid serve as a parent in this lane?"""
    e = reg[eid]
    if e["origin"] in ("control", "known"):
        return False
    if lane == "G0":
        return True
    if lane == "SHALLOW":
        return True  # the lane's constraint is on the parent SET (>= half synthetic)
    if e["origin"] == "human":
        return False
    if lane == "DEEP":
        return e["generation"] >= DEEP_MIN_GEN or e.get("kind") == "lens"
    if lane == "VERY_DEEP":
        if e.get("kind") == "lens":
            return True
        if e["generation"] < DEEP_MIN_GEN:
            return False
        ps = e.get("parentIds", [])
        return bool(ps) and all(reg[p]["origin"] == "synthetic"
                                and all(reg[g]["origin"] == "synthetic" for g in reg[p].get("parentIds", []))
                                for p in ps)
    raise ValueError(lane)


def parent_set_ok(reg, pids, lane):
    if lane == "SHALLOW":
        return sum(reg[p]["origin"] != "human" for p in pids) * 2 >= len(pids)
    if lane in ("DEEP", "VERY_DEEP"):
        return all(reg[p]["origin"] != "human" for p in pids)
    return True
