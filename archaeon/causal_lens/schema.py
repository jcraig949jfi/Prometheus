"""Causal-lineage graph (CAUSAL_LINEAGE_CONTRACT v0.1): data model, validator, invariant checks I1-I12, and engine-neutral queries.

Pure Python, no imports from any engine (portability requirement). A graph is JSON-serialisable:
  nodes  {id: {"kind": KIND, ...attrs}}
  edges  [[src, REL, dst, {attrs}]]
Transformation nodes carry "types" (event types) and "fields" {name: {"value": ..., "basis": BASIS, "granularity": G, "source": str}}.
Tri-valued properties live on any node under "props" {name: {"value": YES|NO|NOT_IDENTIFIABLE, "basis": BASIS}}.
"""
from __future__ import annotations

import json
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Set

YES, NO, NI = "YES", "NO", "NOT_IDENTIFIABLE"
NONE, NA, NONE_FOUND = "NONE", "NOT_APPLICABLE", "NONE_FOUND"
TRI = {YES, NO, NI}

KINDS = {"MATERIAL", "ENTITY", "EXECUTION", "TRANSFORMATION", "HU", "ENV"}
RELS = {  # rel: (allowed src kinds, allowed dst kinds)
    "performed_by": ({"EXECUTION"}, {"ENTITY"}),
    "governed_by": ({"EXECUTION"}, {"MATERIAL"}),
    "produced": ({"TRANSFORMATION"}, {"MATERIAL", "ENTITY", "HU"}),
    "copies_from": ({"MATERIAL"}, {"MATERIAL"}),               # stored as child -> source
    "contributes_material": ({"MATERIAL"}, {"MATERIAL", "HU"}), # stored as source -> child
    "mutates_from": ({"MATERIAL"}, {"MATERIAL"}),               # new -> old
    "recombines_with": ({"MATERIAL"}, {"MATERIAL"}),
    "hosts": ({"ENTITY"}, {"TRANSFORMATION"}),
    "transports": ({"ENTITY", "ENV"}, {"MATERIAL"}),
    "enables": ({"ENV"}, {"TRANSFORMATION"}),
    "member_of": ({"MATERIAL"}, {"HU"}),
    "via": ({"TRANSFORMATION"}, {"EXECUTION"}),
    "owns": ({"ENTITY"}, {"MATERIAL"}),                          # the entity carries this material (at the time of the event)
    "consumes": ({"TRANSFORMATION"}, {"MATERIAL", "ENTITY"}),    # input state of a transformation (not a contribution claim)
    "labelled_parent": ({"ENTITY"}, {"ENTITY"}),                 # native parent pointer, verbatim; NEVER read as heredity (I11)
}
EVENT_TYPES = {"ORIGINATION", "REPRODUCTION", "AMPLIFICATION", "MUTATION", "RECOMBINATION", "TRANSFER", "HOSTING", "MIGRATION",
               "ESTABLISHMENT", "EXTINCTION", "DEPENDENCY_ACQUISITION", "DEPENDENCY_LOSS", "UNCLASSIFIED"}
ORIGINS = {"RANDOM_INIT", "RANDOM_INFLOW", "INSERTED_SEED", "TRANSPLANT", "MUTATION", "RECOMBINATION", "COPY", "COMPUTED", "UNKNOWN"}
INSERTED = {"INSERTED_SEED", "TRANSPLANT"}
BASES = {"TRACE", "REPLAY", "NATIVE_RECORD", "DERIVED", "DECLARED"}
GRAN = {"bit": 0, "byte": 1, "segment": 2, "genome": 3, "entity": 4, "population": 5}
FIELDS = {"material_origin", "executor", "executed_material", "child_contributors", "host", "resulting_hu", "env_dependencies"}
HERITABLE_EDGES = ("copies_from", "contributes_material")      # the ONLY edges ancestry may follow (I11: labelled_parent excluded)


class ContractViolation(Exception):
    pass


class Graph:
    def __init__(self, engine: str, material_granularity: str, meta: Optional[dict] = None):
        assert material_granularity in GRAN, material_granularity
        self.engine = engine; self.gran = material_granularity; self.meta = meta or {}
        self.nodes: Dict[str, dict] = {}; self.edges: List[list] = []
        self._out = defaultdict(list); self._in = defaultdict(list)

    # ---------------------------------------------------------------- construction
    def node(self, nid: str, kind: str, **attrs) -> str:
        if kind not in KINDS: raise ContractViolation("unknown node kind %r" % kind)
        if nid in self.nodes:
            if self.nodes[nid]["kind"] != kind: raise ContractViolation("node %s re-declared as %s" % (nid, kind))
            self.nodes[nid].update(attrs); return nid
        self.nodes[nid] = {"kind": kind, **attrs}; return nid

    def edge(self, src: str, rel: str, dst: str, **attrs):
        if rel not in RELS: raise ContractViolation("unknown relation %r" % rel)
        self.edges.append([src, rel, dst, attrs]); self._out[(src, rel)].append(dst); self._in[(dst, rel)].append(src)

    def event(self, tid: str, types: Iterable[str], **fields) -> str:
        ts = sorted(set(types)); bad = set(ts) - EVENT_TYPES
        if bad: raise ContractViolation("unknown event types %s" % bad)
        self.node(tid, "TRANSFORMATION", types=ts, fields={})
        for k, v in fields.items(): self.field(tid, k, **v)
        return tid

    def field(self, tid: str, name: str, value, basis: str, granularity: Optional[str] = None, source: str = "", native_count: Optional[int] = None):
        """native_count: how many contributors the native record lists (lets I6 catch truncation)."""
        if name not in FIELDS: raise ContractViolation("unknown field %r" % name)
        f = {"value": value, "basis": basis, "granularity": granularity, "source": source}
        if native_count is not None: f["native_count"] = native_count
        self.nodes[tid]["fields"][name] = f

    def prop(self, nid: str, name: str, value: str, basis: str, source: str = ""):
        self.nodes[nid].setdefault("props", {})[name] = {"value": value, "basis": basis, "source": source}

    # ---------------------------------------------------------------- navigation
    def out(self, n, rel): return self._out.get((n, rel), [])
    def inn(self, n, rel): return self._in.get((n, rel), [])
    def of_kind(self, k): return [n for n, a in self.nodes.items() if a["kind"] == k]

    def to_json(self) -> dict:
        return {"schema": "prometheus.causal_lineage.v0.1", "engine": self.engine, "material_granularity": self.gran, "meta": self.meta,
                "nodes": self.nodes, "edges": self.edges}

    @classmethod
    def from_json(cls, d: dict) -> "Graph":
        g = cls(d["engine"], d["material_granularity"], d.get("meta"))
        for nid, a in d["nodes"].items(): g.nodes[nid] = a
        for s, r, t, at in d["edges"]: g.edge(s, r, t, **at)
        return g

    # ---------------------------------------------------------------- queries (engine-neutral; ancestry follows HERITABLE_EDGES only)
    def sources(self, m: str) -> List[str]:
        """Direct heritable sources of material m."""
        return list(dict.fromkeys(self.out(m, "copies_from") + [s for s in self.inn(m, "contributes_material") if self.nodes[s]["kind"] == "MATERIAL"]))

    def ancestors(self, m: str) -> Set[str]:
        seen: Set[str] = set(); st = [m]
        while st:
            x = st.pop()
            for s in self.sources(x):            # mutates_from is NOT followed: a mutation is new material, not a copy of the old value (I5)
                if s not in seen: seen.add(s); st.append(s)
        return seen

    def origins(self, m: str) -> Set[str]:
        """Origin classes of m: its own declared origin plus every heritable ancestor's (I4)."""
        out = set()
        for x in {m} | self.ancestors(m):
            o = self.nodes[x].get("origin")
            if o: out.add(o)
        return out

    def hu_members(self, hu: str) -> List[str]:
        return self.inn(hu, "member_of")

    def hu_origins(self, hu: str) -> Set[str]:
        out = set()
        for m in self.hu_members(hu): out |= self.origins(m)
        return out

    def hu_of(self, m: str) -> Optional[str]:
        h = self.out(m, "member_of"); return h[0] if h else None

    def contributors_hu(self, tid: str) -> Set[str]:
        """HUs that contributed heritable material to the outputs of transformation tid (by edges, not by fields)."""
        out = set()
        for p in self.out(tid, "produced"):
            if self.nodes[p]["kind"] != "MATERIAL": continue
            for s in self.sources(p):
                h = self.hu_of(s)
                if h: out.add(h)
        return out

    def establishments(self) -> Set[str]:
        """I8: establishments counted per HU (labels sharing one HU count once)."""
        out = set()
        for t in self.of_kind("TRANSFORMATION"):
            if "ESTABLISHMENT" in self.nodes[t]["types"]:
                v = self.nodes[t]["fields"].get("resulting_hu", {}).get("value")
                if isinstance(v, str) and v in self.nodes and self.nodes[v]["kind"] == "HU": out.add(v)
        return out

    # ---------------------------------------------------------------- validation
    def check(self) -> List[str]:
        """All contract violations (empty = conformant)."""
        v: List[str] = []
        n = self.nodes
        for s, r, t, _ in self.edges:
            if s not in n or t not in n: v.append("E0 dangling edge %s -%s-> %s" % (s, r, t)); continue
            sk, dk = RELS[r]
            if n[s]["kind"] not in sk or n[t]["kind"] not in dk: v.append("E1 %s edge %s(%s)->%s(%s)" % (r, s, n[s]["kind"], t, n[t]["kind"]))
        for nid, a in n.items():
            for pname, p in a.get("props", {}).items():
                if p["value"] not in TRI: v.append("I10 %s.%s non-tri value %r (booleans must be YES/NO/NOT_IDENTIFIABLE)" % (nid, pname, p["value"]))
                if p["basis"] not in BASES: v.append("B0 %s.%s basis %r" % (nid, pname, p["basis"]))
            if a["kind"] == "MATERIAL" and a.get("origin") and a["origin"] not in ORIGINS: v.append("O0 %s origin %r" % (nid, a["origin"]))
            if a["kind"] != "TRANSFORMATION": continue
            for fname, f in a["fields"].items():
                if f["basis"] not in BASES: v.append("B1 %s.%s basis %r" % (nid, fname, f["basis"]))
                if f["value"] is False or f["value"] is None: v.append("I10 %s.%s value %r: say NONE / NOT_IDENTIFIABLE / NOT_APPLICABLE" % (nid, fname, f["value"]))
                # I12 / I10 false precision: claim granularity cannot be finer than the basis granularity
                bg = f.get("granularity"); src = f.get("source", "")
                if fname == "child_contributors" and isinstance(f["value"], list) and src.startswith("parent_id") and self.gran in ("bit", "byte", "segment"):
                    v.append("I10 %s child_contributors from %s at %s granularity (parent ids are not material provenance)" % (nid, src, self.gran))
                if bg and bg in GRAN and GRAN[bg] > GRAN[self.gran] and fname in ("child_contributors", "material_origin") and f["basis"] in ("TRACE",):
                    v.append("I12 %s.%s TRACE basis at %s coarser than declared material granularity %s" % (nid, fname, bg, self.gran))
            v += self._check_event(nid, a)
        v += self._check_hus()
        return v

    def _check_event(self, t: str, a: dict) -> List[str]:
        v = []; ty = set(a["types"]); f = a["fields"]; n = self.nodes
        prod = self.out(t, "produced"); prod_hu = [p for p in prod if n[p]["kind"] == "HU"]
        # I9: amplification/reproduction never create an HU; origination always does
        if prod_hu and not ({"ORIGINATION"} & ty): v.append("I9 %s creates HU %s without ORIGINATION (types %s)" % (t, prod_hu, sorted(ty)))
        if "ORIGINATION" in ty and not prod_hu: v.append("I9 %s ORIGINATION without a new HU" % t)
        if "ORIGINATION" in ty and ({"AMPLIFICATION", "REPRODUCTION"} & ty): v.append("I9 %s is both ORIGINATION and %s" % (t, sorted({"AMPLIFICATION", "REPRODUCTION"} & ty)))
        # I2 / I3: executor or host appear as contributors only through material edges
        edge_hus = self.contributors_hu(t)
        cc = f.get("child_contributors", {}).get("value")
        if isinstance(cc, list):
            for c in cc:
                ref = c["ref"] if isinstance(c, dict) else c
                if ref not in n: v.append("E2 %s contributor %s unknown" % (t, ref)); continue
                k = n[ref]["kind"]
                if k == "ENTITY": v.append("I2/I3 %s names ENTITY %s as a contributor (contributors are materials or HUs)" % (t, ref))
                elif k == "HU" and ref not in edge_hus: v.append("I2/I3 %s claims HU %s contributed but no heritable edge supports it" % (t, ref))
                elif k == "MATERIAL" and not any(ref in self.sources(p) for p in prod if n[p]["kind"] == "MATERIAL"):
                    v.append("I2/I3 %s claims material %s contributed but no heritable edge supports it" % (t, ref))
            nat = f.get("child_contributors", {}).get("native_count")
            if nat is not None and len(cc) < nat: v.append("I6 %s truncates %d native contributors to %d" % (t, nat, len(cc)))
        # I5: mutation outputs link mutates_from
        if "MUTATION" in ty:
            mats = [p for p in prod if n[p]["kind"] == "MATERIAL"]
            if mats and not any(self.out(p, "mutates_from") for p in mats): v.append("I5 %s MUTATION output lacks mutates_from" % t)
        # I7: transfer keeps donor ancestry
        if "TRANSFER" in ty:
            for p in prod:
                if n[p]["kind"] != "MATERIAL": continue
                if not self.sources(p): v.append("I7 %s TRANSFER output %s has no copies_from/contributes edge to a donor" % (t, p))
        # I4: an output's declared origin must be inherited, unless this transformation originates / mutates / computes it
        for p in prod:
            if n[p]["kind"] != "MATERIAL" or not n[p].get("origin"): continue
            o = n[p]["origin"]; anc = set()
            for s in self.sources(p): anc |= self.origins(s)
            if o in ("MUTATION", "COMPUTED", "RECOMBINATION", "COPY", "UNKNOWN"): continue
            if o == "TRANSPLANT" and "TRANSFER" in ty: continue                  # I7: transplant is LAYERED on donor ancestry (kept via sources)
            if self.sources(p) and o not in anc and not ({"ORIGINATION"} & ty):
                v.append("I4 %s output %s declares origin %s not carried by its sources %s" % (t, p, o, sorted(anc)))
        return v

    def _check_hus(self) -> List[str]:
        v = []
        for h in self.of_kind("HU"):
            p = self.nodes[h].get("props", {}).get("spontaneous")
            if p and p["value"] == YES and (self.hu_origins(h) & INSERTED):
                v.append("I1 HU %s spontaneous=YES but carries inserted/transplanted ancestry %s" % (h, sorted(self.hu_origins(h) & INSERTED)))
        # I8: two ESTABLISHMENT events for one HU are one establishment -- flag duplicates so counters cannot double-count
        seen = defaultdict(list)
        for t in self.of_kind("TRANSFORMATION"):
            if "ESTABLISHMENT" in self.nodes[t]["types"]:
                seen[self.nodes[t]["fields"].get("resulting_hu", {}).get("value")].append(t)
        for h, ts in seen.items():
            if len(ts) > 1: v.append("I8 HU %s has %d ESTABLISHMENT events (count once)" % (h, len(ts)))
        return v

    def assert_ok(self):
        v = self.check()
        if v: raise ContractViolation("\n".join(v))


def spontaneous(g: Graph, hu: str) -> str:
    """Tri-valued: is this HU of spontaneous (non-inserted) origin? Derived from material ancestry, never from labels."""
    o = g.hu_origins(hu)
    if not o or o == {"UNKNOWN"}: return NI
    if o & INSERTED: return NO
    if "UNKNOWN" in o: return NI
    return YES


def dump(g: Graph, path: str):
    with open(path, "w", encoding="utf-8", newline="\n") as fh: json.dump(g.to_json(), fh, indent=1, sort_keys=True)
