"""Contract v0.3 (E-001 / T-005): the B6 repair. v0.2 is frozen and untouched; v0.3 = v0.2 + three-referent governance.

Measured basis (ops/campaigns/C-001/E-001/T-004_RESULT.md): "which code governed the copy" has three referents that diverge
differently per substrate:
  WHO    the executing context / body that performed the write        NPE prov / prov_lit; BEE writer; Archaeon executor
  WHERE  the location of the executing instruction                    BEE pc < L; Archaeon exec_foreign; NPE tape half
  WHAT   the MATERIAL of the executing instruction (its provenance)   Archaeon taint labels (native); BEE and NPE only by FULL replay
Divergence measured: BEE WHERE != WHAT (27,083/28,163 location-foreign births own-material, r038751); NPE WHO != WHAT (26.4% of
directed writes); Archaeon WHERE != WHAT in 28% of block-15 hosting births.

v0.3 rules:
  fields  write_governing, execution_share           = WHAT only (unchanged meaning from v0.2, now enforced)
          code_location_share                        = WHERE (new)
          context_authorship                         = WHO (new)
  each of the four carries `referent` in {WHO, WHERE, WHAT} and must match its field.
  J21  no governance field may be filled from another referent: a WHAT field whose referent/source is WHO or WHERE is rejected;
       if an engine records only WHO or WHERE, write_governing / execution_share must be NOT_IDENTIFIABLE (or absent).
  J22  autonomy suffixes follow the referent: AUTONOMY_WRITE / AUTONOMY_EXEC are WHAT claims; location-based and context-based
       variants must be named AUTONOMY_WRITE_LOCATION / AUTONOMY_WRITE_CONTEXT (never the bare WHAT names).
Limit: J21 is enforced on the declared `referent` and on source wording (pc, location, prov, context, region). An adapter that
mis-declares its referent can pass; the regression tests in test_causal_lens_v03.py check the four real adapters' declarations.
"""
from __future__ import annotations

from typing import List

from archaeon.causal_lens import schema_v02 as V2
from archaeon.causal_lens.schema_v02 import *  # noqa: F401,F403  (v0.2 vocabulary re-exported)

REFERENT_OF = {"write_governing": "WHAT", "execution_share": "WHAT", "code_location_share": "WHERE", "context_authorship": "WHO"}
FIELDS_V03 = set(V2.FIELDS) | {"code_location_share", "context_authorship"}   # v0.2's set is NOT mutated
import re
_WHERE_RE = re.compile(r"\bpc\s*[<>]|\blocation\b|\bregion\b|\baddress\b")
_WHO_RE = re.compile(r"\bprov(_lit)?\b|\bcontext\b|\bthread\b|\bwriter id\b|\bexecutor id\b")   # word-bounded: "provenance" is not "prov"


class Graph(V2.Graph):
    def field(self, tid, name, value, basis, granularity=None, source="", **extra):
        if name not in FIELDS_V03: raise V2.ContractViolation("unknown field %r" % name)
        self.nodes[tid]["fields"][name] = {"value": value, "basis": basis, "granularity": granularity, "source": source, **extra}

    def event(self, tid, types, **fields):
        ts = sorted(set(types)); bad = set(ts) - V2.EVENT_TYPES
        if bad: raise V2.ContractViolation("unknown event types %s" % bad)
        self.node(tid, "TRANSFORMATION", types=ts, fields={})
        for k, v in fields.items(): self.field(tid, k, **v)
        return tid

    def check(self) -> List[str]:
        v = super().check()
        for t in self.of_kind("TRANSFORMATION"):
            f = self.nodes[t]["fields"]
            for name, want in REFERENT_OF.items():
                fd = f.get(name)
                if not fd: continue
                ref = fd.get("referent")
                if ref is None: v.append("J21 %s.%s has no declared referent (%s)" % (t, name, want)); continue
                if ref != want: v.append("J21 %s.%s is a %s field filled from a %s reading" % (t, name, want, ref)); continue
                if want == "WHAT" and fd["value"] not in (V2.NI, V2.NA, V2.NONE):
                    src = str(fd.get("source", "")).lower()
                    if _WHERE_RE.search(src): v.append("J21 %s.%s WHAT value sourced from a location reading" % (t, name))
                    if _WHO_RE.search(src): v.append("J21 %s.%s WHAT value sourced from a context/executor reading" % (t, name))
            for pname, p in self.nodes[t].get("props", {}).items():
                if pname in ("autonomy_write", "autonomy_exec") and p.get("referent") not in (None, "WHAT"):
                    v.append("J22 %s.%s is a WHAT name carrying a %s reading" % (t, pname, p.get("referent")))
        return v

    @classmethod
    def from_json(cls, d: dict) -> "Graph":
        g = cls(d["engine"], d["granularity"], d.get("rules"), d.get("meta"))
        for nid, a in d["nodes"].items(): g.nodes[nid] = a
        for s, r, t, at in d["edges"]: g.edge(s, r, t, **at)
        return g
