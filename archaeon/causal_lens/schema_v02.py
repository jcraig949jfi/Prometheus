"""Causal-lineage graph, CONTRACT v0.2: data model, declared rules, validator J1-J20, engine-neutral queries.

Pure Python, no engine imports. v0.1 (schema.py) is untouched. See CAUSAL_LINEAGE_CONTRACT_v0.2.md.
"""
from __future__ import annotations

import json
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Set

YES, NO, NI = "YES", "NO", "NOT_IDENTIFIABLE"
NONE, NA, ILL, NONE_FOUND = "NONE", "NOT_APPLICABLE", "ILL_POSED", "NONE_FOUND"
TRI = {YES, NO, NI}
SPECIAL = {NONE, NA, NI, ILL, NONE_FOUND}

KINDS = {"MATERIAL", "BODY", "IDENTITY", "EXECUTION", "TRANSFORMATION", "HU", "ARCH", "ENV", "LOCATION", "CF_TEST"}
RELS = {
    "performed_by": ({"EXECUTION"}, {"BODY"}),
    "carries": ({"BODY"}, {"MATERIAL"}),
    "assigned": ({"IDENTITY"}, {"BODY"}),
    "write_governed_by": ({"EXECUTION"}, {"MATERIAL"}),
    "execution_share": ({"EXECUTION"}, {"MATERIAL", "LOCATION"}),
    "produced": ({"TRANSFORMATION"}, {"MATERIAL", "BODY", "HU", "IDENTITY"}),
    "consumes": ({"TRANSFORMATION"}, {"MATERIAL", "BODY"}),
    "copies_from": ({"MATERIAL"}, {"MATERIAL"}),
    "contributes_material": ({"MATERIAL"}, {"MATERIAL"}),
    "mutates_from": ({"MATERIAL"}, {"MATERIAL"}),
    "recombines_with": ({"MATERIAL"}, {"MATERIAL"}),
    "hosted_by": ({"TRANSFORMATION"}, {"BODY"}),
    "transports": ({"BODY", "ENV"}, {"MATERIAL"}),
    "made_in": ({"MATERIAL"}, {"LOCATION"}),
    "located_in": ({"BODY"}, {"LOCATION"}),
    "member_of": ({"MATERIAL"}, {"HU"}),
    "member_of_arch": ({"MATERIAL"}, {"ARCH"}),
    "enables": ({"ENV"}, {"TRANSFORMATION"}),
    "via": ({"TRANSFORMATION"}, {"EXECUTION"}),
    "tests": ({"CF_TEST"}, {"TRANSFORMATION"}),
    "labelled_parent": ({"IDENTITY"}, {"IDENTITY"}),
}
HERITABLE = ("copies_from", "contributes_material")
EVENT_TYPES = {"ORIGINATION", "REPRODUCTION", "AMPLIFICATION", "MUTATION", "RECOMBINATION", "TRANSFER", "HOSTING", "MIGRATION",
               "ESTABLISHMENT", "EXTINCTION", "DEPENDENCY_ACQUISITION", "DEPENDENCY_LOSS", "IDENTITY_CHANGE", "BODY_CREATION",
               "BODY_DESTRUCTION", "UNCLASSIFIED"}
ORIGINS = {"RANDOM_INIT", "RANDOM_INFLOW", "INSERTED_SEED", "TRANSPLANT", "MUTATION", "RECOMBINATION", "COPY", "COMPUTED", "UNKNOWN"}
INSERTED = {"INSERTED_SEED", "TRANSPLANT"}
BASES = {"TRACE", "REPLAY", "NATIVE_RECORD", "DERIVED", "DECLARED"}
GRAN = {"bit": 0, "byte": 1, "segment": 2, "genome": 3, "body": 4, "population": 5}
FIELDS = {"ancestry_origin", "executor_body", "executor_identity", "write_governing", "execution_share", "factual_contributors",
          "host_body", "hu_continuity", "resulting_hu", "architecture_class", "env_dependencies", "persisting_object"}
ILL_OK = {"hu_continuity", "resulting_hu", "architecture_class", "identity_continuity"}
ARCH_KINDS = {"exact", "equivalence", "behavioral", "structural"}
CF_KINDS = {"SUFFICIENCY", "NECESSITY"}


class ContractViolation(Exception):
    pass


def continuity(shares: Dict[str, object], rule: dict) -> dict:
    """Apply a declared hu_rule to factual contributor shares {hu: share | NOT_IDENTIFIABLE}.
    Returns {"hu_continuity": ref|NONE|NI|ILL_POSED, "ill_posed": justification?}. The engine-neutral heart of B1."""
    if rule.get("kind") != "MAJORITY": raise ContractViolation("unknown hu_rule %r" % rule)
    if not shares: return {"hu_continuity": NONE}
    thr = rule.get("threshold", 0.5)
    known = {h: v for h, v in shares.items() if v != NI}
    if len(known) < len(shares):                                                 # v0.2.1: unknown shares matter only if they could change the answer
        if known and max(known.values()) > thr and sum(1 for v in known.values() if v == max(known.values())) == 1:
            return {"hu_continuity": max(known, key=known.get)}                   # a strict known majority cannot be overturned
        return {"hu_continuity": NI}                                             # J6: incomplete evidence is never ILL_POSED
    best = max(shares.values()); top = [h for h, v in shares.items() if v == best]
    if best > thr and len(top) == 1: return {"hu_continuity": top[0]}
    if len(top) > 1 and best >= thr:
        return {"hu_continuity": ILL, "ill_posed": {"rule": rule, "evidence": shares, "why": "tie between %s" % sorted(top)}}
    if rule.get("no_majority", "ILL_POSED") == "ORIGINATE": return {"hu_continuity": NONE}
    return {"hu_continuity": ILL, "ill_posed": {"rule": rule, "evidence": shares, "why": "no contributor exceeds %s" % thr}}


class Graph:
    def __init__(self, engine: str, granularity: str, rules: Optional[dict] = None, meta: Optional[dict] = None):
        assert granularity in GRAN, granularity
        self.engine = engine; self.gran = granularity; self.rules = rules or {}; self.meta = meta or {}
        self.nodes: Dict[str, dict] = {}; self.edges: List[list] = []
        self._out = defaultdict(list); self._in = defaultdict(list)

    # ---------------------------------------------------------------- construction
    def node(self, nid: str, kind: str, **attrs) -> str:
        if kind not in KINDS: raise ContractViolation("unknown node kind %r" % kind)
        if nid in self.nodes:
            if self.nodes[nid]["kind"] != kind: raise ContractViolation("node %s re-declared as %s" % (nid, kind))
            self.nodes[nid].update(attrs); return nid
        self.nodes[nid] = {"kind": kind, **attrs}; return nid

    def edge(self, s: str, rel: str, t: str, **attrs):
        if rel not in RELS: raise ContractViolation("unknown relation %r" % rel)
        self.edges.append([s, rel, t, attrs]); self._out[(s, rel)].append(t); self._in[(t, rel)].append(s)

    def event(self, tid: str, types: Iterable[str], **fields) -> str:
        ts = sorted(set(types)); bad = set(ts) - EVENT_TYPES
        if bad: raise ContractViolation("unknown event types %s" % bad)
        self.node(tid, "TRANSFORMATION", types=ts, fields={})
        for k, v in fields.items(): self.field(tid, k, **v)
        return tid

    def field(self, tid: str, name: str, value, basis: str, granularity: Optional[str] = None, source: str = "", **extra):
        if name not in FIELDS: raise ContractViolation("unknown field %r" % name)
        self.nodes[tid]["fields"][name] = {"value": value, "basis": basis, "granularity": granularity, "source": source, **extra}

    def prop(self, nid: str, name: str, value, basis: str, source: str = ""):
        self.nodes[nid].setdefault("props", {})[name] = {"value": value, "basis": basis, "source": source}

    def arch(self, aid: str, kind: str, criterion: str, justification: str) -> str:
        return self.node(aid, "ARCH", arch_kind=kind, criterion=criterion, justification=justification)

    def cf_test(self, cid: str, subject: str, kind: str, intervention: Optional[dict], outcome: Optional[dict], result: str,
                basis: str = "REPLAY", on: Optional[str] = None, **extra) -> str:
        self.node(cid, "CF_TEST", subject=subject, cf_kind=kind, intervention=intervention, outcome=outcome, result=result, basis=basis, **extra)
        if on: self.edge(cid, "tests", on)
        return cid

    # ---------------------------------------------------------------- navigation / queries
    def out(self, n, rel): return self._out.get((n, rel), [])
    def inn(self, n, rel): return self._in.get((n, rel), [])
    def of_kind(self, k): return [n for n, a in self.nodes.items() if a["kind"] == k]

    def sources(self, m: str) -> List[str]:
        return list(dict.fromkeys(self.out(m, "copies_from") + self.inn(m, "contributes_material")))

    def ancestors(self, m: str) -> Set[str]:
        seen: Set[str] = set(); st = [m]
        while st:
            x = st.pop()
            for s in self.sources(x):
                if s not in seen: seen.add(s); st.append(s)
        return seen

    def origins(self, m: str) -> Set[str]:
        return {self.nodes[x]["origin"] for x in {m} | self.ancestors(m) if self.nodes[x].get("origin")}

    def hu_of(self, m: str) -> Optional[str]:
        h = self.out(m, "member_of"); return h[0] if h else None

    def hu_origins(self, hu: str) -> Set[str]:
        out = set()
        for m in self.inn(hu, "member_of"): out |= self.origins(m)
        return out

    def made_in(self, m: str) -> List[str]:
        return self.out(m, "made_in")

    def bodies_of_identity(self, i: str) -> List[str]:
        return self.out(i, "assigned")

    def identities_of_body(self, b: str) -> List[str]:
        return self.inn(b, "assigned")

    def contributors_hu(self, t: str) -> Set[str]:
        out = set()
        for p in self.out(t, "produced"):
            if self.nodes[p]["kind"] != "MATERIAL": continue
            for s in self.sources(p):
                h = self.hu_of(s)
                if h: out.add(h)
        return out

    def establishments(self) -> Dict[str, str]:
        out = {}
        for t in self.of_kind("TRANSFORMATION"):
            if "ESTABLISHMENT" in self.nodes[t]["types"]:
                v = self.nodes[t]["fields"].get("persisting_object", {}).get("value")
                if isinstance(v, str) and v in self.nodes: out[v] = self.nodes[v]["kind"]
        return out

    def cf_tests(self, t: str) -> List[dict]:
        return [dict(self.nodes[c], id=c) for c in self.inn(t, "tests")]

    def to_json(self) -> dict:
        return {"schema": "prometheus.causal_lineage.v0.2", "engine": self.engine, "granularity": self.gran, "rules": self.rules,
                "meta": self.meta, "nodes": self.nodes, "edges": self.edges}

    @classmethod
    def from_json(cls, d: dict) -> "Graph":
        g = cls(d["engine"], d["granularity"], d.get("rules"), d.get("meta"))
        for nid, a in d["nodes"].items(): g.nodes[nid] = a
        for s, r, t, at in d["edges"]: g.edge(s, r, t, **at)
        return g

    # ---------------------------------------------------------------- validation
    def check(self) -> List[str]:
        v: List[str] = []; n = self.nodes
        for s, r, t, at in self.edges:
            if s not in n or t not in n: v.append("E0 dangling %s -%s-> %s" % (s, r, t)); continue
            sk, dk = RELS[r]
            if n[s]["kind"] not in sk or n[t]["kind"] not in dk: v.append("E1 %s edge %s(%s)->%s(%s)" % (r, s, n[s]["kind"], t, n[t]["kind"]))
            if r in HERITABLE and str(at.get("basis", "")).lower() in ("location", "made_in", "niche"):
                v.append("J16 heritable edge %s->%s justified by location" % (s, t))
        for nid, a in n.items():
            for pname, p in a.get("props", {}).items():
                if pname in ("autonomous", "sufficient", "necessary"): v.append("J9/J11 %s has bare property %r" % (nid, pname))
                if p["value"] == ILL: v.append("J6 %s.%s ILL_POSED used as a boolean" % (nid, pname))
                elif p["value"] not in TRI: v.append("J18 %s.%s non-tri value %r" % (nid, pname, p["value"]))
            k = a["kind"]
            if k == "MATERIAL" and a.get("origin") and a["origin"] not in ORIGINS: v.append("O0 %s origin %r" % (nid, a["origin"]))
            if k == "ARCH":
                if a.get("arch_kind") not in ARCH_KINDS or not a.get("criterion") or not a.get("justification"):
                    v.append("A0 ARCH %s must declare kind in %s, a criterion and a justification" % (nid, sorted(ARCH_KINDS)))
                if "similar" in str(a.get("criterion", "")).lower() and a.get("arch_kind") != "structural":
                    v.append("A1 ARCH %s criterion looks like sequence similarity" % nid)
            if k == "CF_TEST":
                if a.get("cf_kind") not in CF_KINDS: v.append("J11 %s cf_kind %r" % (nid, a.get("cf_kind")))
                if not a.get("intervention") or not a["intervention"].get("name"): v.append("J11 %s has no named intervention" % nid)
                if not a.get("outcome") or not a["outcome"].get("predicate"): v.append("J11 %s has no outcome predicate" % nid)
                if a.get("result") not in TRI: v.append("J11 %s result %r not tri-valued" % (nid, a.get("result")))
            if k == "TRANSFORMATION": v += self._check_event(nid, a)
        v += self._check_global()
        return v

    def _is(self, ref, kind):
        return isinstance(ref, str) and ref in self.nodes and self.nodes[ref]["kind"] == kind

    def _check_event(self, t: str, a: dict) -> List[str]:
        v = []; f = a["fields"]; ty = set(a["types"]); n = self.nodes
        for name, fd in f.items():
            val = fd["value"]
            if fd["basis"] not in BASES: v.append("B1 %s.%s basis %r" % (t, name, fd["basis"]))
            if val is False or val is None or val is True: v.append("J18 %s.%s value %r" % (t, name, val))
            if val == ILL:
                if name not in ILL_OK: v.append("J6 %s.%s: ILL_POSED not permitted in this field" % (t, name))
                elif not fd.get("ill_posed"): v.append("J6 %s.%s: ILL_POSED without justification" % (t, name))
                else:
                    ev = fd["ill_posed"].get("evidence") or {}
                    if not ev or any(x == NI for x in ev.values()): v.append("J6 %s.%s: ILL_POSED on incomplete evidence (must be NOT_IDENTIFIABLE)" % (t, name))
        for name in ("host_body", "executor_body"):
            val = f.get(name, {}).get("value")
            if isinstance(val, str) and val not in SPECIAL and not self._is(val, "BODY"): v.append("J14 %s.%s references %s, not a BODY" % (t, name, val))
        for name in ("hu_continuity", "resulting_hu"):
            val = f.get(name, {}).get("value")
            if isinstance(val, str) and val not in SPECIAL:
                if self._is(val, "ARCH"): v.append("J17 %s.%s references an ARCH" % (t, name))
                elif not self._is(val, "HU"): v.append("E3 %s.%s references %s, not an HU" % (t, name, val))
        hc = f.get("hu_continuity", {}).get("value"); rh = f.get("resulting_hu", {}).get("value")
        created = [p for p in self.out(t, "produced") if n[p]["kind"] == "HU"]
        if hc == ILL and isinstance(rh, str) and rh not in SPECIAL and rh not in created:
            v.append("J7 %s: continuity ILL_POSED but resulting_hu names pre-existing HU %s" % (t, rh))
        if created and "ORIGINATION" not in ty: v.append("J19 %s creates HU without ORIGINATION" % t)
        if "ORIGINATION" in ty and not created and rh not in (ILL, NI, NA): v.append("J19 %s ORIGINATION without a new HU" % t)
        wg = f.get("write_governing")
        if wg and "execution_share" in str(wg.get("source", "")).lower(): v.append("J8 %s write_governing derived from execution_share" % t)
        fc = f.get("factual_contributors")
        if fc:
            if fc["basis"] == "REPLAY" and "counterfactual" in str(fc.get("source", "")).lower(): v.append("J10 %s factual_contributors from a counterfactual" % t)
            if isinstance(fc["value"], list):
                refs = [c["ref"] if isinstance(c, dict) else c for c in fc["value"]]
                edge_hus = self.contributors_hu(t)
                for r in refs:
                    if r not in n: v.append("E2 %s contributor %s unknown" % (t, r)); continue
                    kk = n[r]["kind"]
                    if kk in ("BODY", "IDENTITY"): v.append("J2/J3 %s names %s %s as a contributor" % (t, kk, r))
                    elif kk == "HU" and r not in edge_hus: v.append("J2/J3 %s claims HU %s without a heritable edge" % (t, r))
                    elif kk == "MATERIAL" and not any(r in self.sources(p) for p in self.out(t, "produced") if n[p]["kind"] == "MATERIAL"):
                        v.append("J2/J3 %s claims material %s without a heritable edge" % (t, r))
                if fc.get("native_count") is not None and len(refs) < fc["native_count"]: v.append("J5 %s truncates contributors" % t)
                if str(fc.get("source", "")).startswith("parent_id") and GRAN.get(fc.get("granularity") or self.gran, 9) < GRAN["body"]:
                    v.append("J18 %s contributors at %s granularity from parent ids" % (t, fc.get("granularity") or self.gran))
        if "ESTABLISHMENT" in ty:
            po = f.get("persisting_object", {}).get("value")
            if not (self._is(po, "HU") or self._is(po, "ARCH") or (isinstance(po, str) and f["persisting_object"].get("declared_kind"))):
                v.append("J13 %s ESTABLISHMENT without a persisting object (HU / ARCH / declared)" % t)
        if "MUTATION" in ty:
            mats = [p for p in self.out(t, "produced") if n[p]["kind"] == "MATERIAL"]
            if mats and not any(self.out(p, "mutates_from") for p in mats): v.append("J5 %s MUTATION without mutates_from" % t)
        if "TRANSFER" in ty:
            for p in self.out(t, "produced"):
                if n[p]["kind"] == "MATERIAL" and not self.sources(p): v.append("J5 %s TRANSFER output %s severed from donor" % (t, p))
        for p in self.out(t, "produced"):
            if n[p]["kind"] != "MATERIAL" or not n[p].get("origin"): continue
            o = n[p]["origin"]
            if o in ("MUTATION", "COMPUTED", "RECOMBINATION", "COPY", "UNKNOWN") or (o == "TRANSPLANT" and "TRANSFER" in ty): continue
            anc = set()
            for s in self.sources(p): anc |= self.origins(s)
            if self.sources(p) and o not in anc and "ORIGINATION" not in ty: v.append("J4 %s output %s origin %s not inherited" % (t, p, o))
        return v

    def _check_global(self) -> List[str]:
        v = []
        for h in self.of_kind("HU"):
            p = self.nodes[h].get("props", {}).get("spontaneous")
            if p and p["value"] == YES and (self.hu_origins(h) & INSERTED): v.append("J1 HU %s spontaneous=YES with inserted ancestry" % h)
        seen = defaultdict(list)
        for t in self.of_kind("TRANSFORMATION"):
            if "ESTABLISHMENT" in self.nodes[t]["types"]: seen[self.nodes[t]["fields"].get("persisting_object", {}).get("value")].append(t)
        for o, ts in seen.items():
            if len(ts) > 1: v.append("J12 %s established %d times" % (o, len(ts)))
        # J15: a BODY named as renamed (IDENTITY_CHANGE) must keep one BODY node: every IDENTITY_CHANGE consumes and produces the same BODY
        for t in self.of_kind("TRANSFORMATION"):
            if "IDENTITY_CHANGE" in self.nodes[t]["types"]:
                cb = {b for b in self.out(t, "consumes") if self.nodes[b]["kind"] == "BODY"}
                pb = {b for b in self.out(t, "produced") if self.nodes[b]["kind"] == "BODY"}
                if pb - cb: v.append("J15 %s identity change creates a new BODY %s (a rename must keep the body)" % (t, sorted(pb - cb)))
                if not cb: v.append("J15 %s identity change names no BODY" % t)
        return v

    def assert_ok(self):
        v = self.check()
        if v: raise ContractViolation("\n".join(v))


def spontaneous(g: Graph, hu: str) -> str:
    o = g.hu_origins(hu)
    if not o or o == {"UNKNOWN"}: return NI
    if o & INSERTED: return NO
    if "UNKNOWN" in o: return NI
    return YES


def dump(g: Graph, path: str):
    with open(path, "w", encoding="utf-8", newline="\n") as fh: json.dump(g.to_json(), fh, indent=1, sort_keys=True)
