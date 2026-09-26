"""BEE adapter (Bellerophon z80atlas): traced per-birth logs -> canonical causal accounts (contract v0.1). READ-ONLY on BEE.

Source records (BEE forensics, traced_replay.py `births` rows, one per endogenous birth; C:/Users/James/z80atlas_forensics_2026-09-23_local/births/):
  0 tick  1 writer_id  2 child_id  3 mechanism  4 fid_writer_post  5 fid_target  6 material  7 n_window_writes  8 copied_from_own
  9 by_own_code  10 bytes_changed_vs_prior  11 is_sr  12 sr_depth  13 own_steps  14 win_steps  15 other_steps  16 variant  17 fid_pre
  18 is_sr_postonly  19 into_empty
Run config (C:/Users/James/z80atlas_campaign_2026-09-19/runs/<rid>/config.json): cells, config.init, init_tapes, config.representation.
Founders (frozen BEE world._init_population, harness 16fc6c2a): n_fill = cells//2 organisms, ids 1..n_fill in fill order; if init_tapes:
ids 1..max(1,n_fill//4) are TRANSPLANT; elif init is SEEDED_*: ids 1..max(1,n_fill//8) are INSERTED_SEED; all others RANDOM_INIT.

BLINDNESS: the adapter NEVER reads the native verdict columns 6 (material, a resemblance heuristic), 11 is_sr, 12 sr_depth, 16 variant,
17 fid_pre, 18 is_sr_postonly. They are returned separately as the NATIVE reading for the differential. Frozen before any BEE native
adjudication (SPECIMEN_LEDGER, TRACED_* lists, summaries, flags) was read.

LENS RULES (frozen here):
  material parts of a child window (L bytes):
    OWN      = copied_from_own          bytes written by copy ops whose source address < L (the writer's own tape)     basis TRACE
    RETAINED = L - n_window_writes      bytes never written this execution -> the prior occupant's bytes stay put     basis TRACE (write set)
               (into_empty: the prior is zeros -> constant, no contributor)
    OTHER    = n_window_writes - OWN    written bytes whose source is not persisted (window-to-window copy, computed,
                                        input) -> NO contributor claimed (abstain)
  HU continuation: the child continues the writer's HU if OWN >= L/2; the prior occupant's HU if RETAINED >= L/2 and the cell was
    occupied; ORIGINATION (new HU, contributors = writer and/or occupant HUs with > 0 bytes) if neither source reaches L/2 AND OTHER < L/2;
    NOT_IDENTIFIABLE if OTHER >= L/2 (the majority of the child has an unpersisted source: claiming an origination would be false precision).
  executor = writer (its context ran; TRACE). executed material shares: own_steps -> writer material, win_steps -> occupant/partner
    material, other_steps -> unattributed.
  host = the writer when the child continues ANOTHER HU (writer supplied execution + the write), NONE otherwise.
  AUTONOMOUS (lens self-reproduction) = continues the writer's HU AND own_steps > win_steps + other_steps.
  DECOUPLED = continues the writer's HU but the writer mostly executed the partner/occupant's code (win_steps > own_steps): the
    executed material and the heritable material come from different entities.
  CAPTURE (lens) = continues the occupant's HU (the writer acted, the occupant's material persisted).
  An organism whose birth is not in the log (EXTERNAL / pollination spawns are not traced) has HU NOT_IDENTIFIABLE, and so do its children.
  Establishment: NOT_IDENTIFIABLE from births logs (no death / end-of-run membership in the rows).
"""
from __future__ import annotations

import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Optional

from archaeon.causal_lens.schema import Graph, NONE, NI

BIRTHS = Path(r"C:\Users\James\z80atlas_forensics_2026-09-23_local\births")
RUNS = Path(r"C:\Users\James\z80atlas_campaign_2026-09-19\runs")
NATIVE_COLS = {"material": 6, "is_sr": 11, "sr_depth": 12, "variant": 16, "fid_pre": 17, "is_sr_postonly": 18}


def founders(cfg: dict) -> Dict[int, str]:
    n = cfg["cells"]; n_fill = max(1, n // 2); init = cfg["config"].get("init", "RANDOM"); it = cfg.get("init_tapes") or cfg["config"].get("init_tapes") or []
    out = {}
    for k in range(n_fill):
        oid = k + 1
        if it and k < max(1, n_fill // 4): out[oid] = "TRANSPLANT"
        elif str(init).startswith("SEEDED") and k < max(1, n_fill // 8): out[oid] = "INSERTED_SEED"
        else: out[oid] = "RANDOM_INIT"
    return out


def L_of(cfg: dict) -> int:
    rep = cfg["config"].get("representation", "Z80_64")
    return 32 if "32" in str(rep) else 64


def rows(rid: str):
    with gzip.open(BIRTHS / (rid + ".jsonl.gz"), "rt") as fh:
        for line in fh:
            line = line.strip()
            if line: yield json.loads(line)


class Pass:
    """One pass over a run's births: HU assignment, per-event lens classification, optional canonical graph."""
    def __init__(self, cfg: dict, want_graph: bool = False, graph_limit: int = 5000):
        self.L = L_of(cfg); self.found = founders(cfg); self.hu: Dict[int, object] = {}   # org id -> HU id | NI
        self.hu_origin: Dict[object, str] = {}; self.hu_parents: Dict[object, list] = {}
        for oid, o in self.found.items(): self.hu[oid] = "root%d" % oid; self.hu_origin["root%d" % oid] = o
        self.occupant_of_child: Dict[int, Optional[int]] = {}
        self.cell_occ: Dict[int, int] = {}
        self.n_orig = 0; self.counts = Counter(); self.events = []
        self.g = Graph("bee.z80atlas", "segment", {"L": self.L}) if want_graph else None; self.glimit = graph_limit
        if self.g is not None:
            for h, o in self.hu_origin.items():
                self.g.node("hu:" + h, "HU"); self.g.node("found:" + h, "MATERIAL", origin=o); self.g.edge("found:" + h, "member_of", "hu:" + h)

    def hu_of(self, oid): return self.hu.get(oid, NI)

    def step(self, r: list, occupant: Optional[int] = None) -> dict:
        """occupant: id of the organism overwritten (None if unknown or empty). BEE births rows do not carry `replaced`; the adapter
        receives it only when a caller reconstructs it. Without it, RETAINED bytes have an unidentified owner (NI)."""
        L = self.L; tick, w, c, mech = r[0], r[1], r[2], r[3]
        nw, own, byown, into_empty = r[7], r[8], r[9], r[19]
        own_s, win_s, oth_s = r[13], r[14], r[15]
        retained = 0 if into_empty else L - nw; other = nw - own
        whu = self.hu_of(w); ohu = self.hu_of(occupant) if occupant is not None else NI
        if own >= L / 2: res, how = whu, "WRITER"
        elif retained >= L / 2: res, how = (ohu, "OCCUPANT")
        elif other >= L / 2: res, how = NI, "UNRESOLVED"
        else:
            contrib = ([whu] if own else []) + ([ohu] if retained else [])
            if any(x == NI for x in contrib): res, how = NI, "UNRESOLVED_CONTRIB"
            else:
                self.n_orig += 1; res = "orig%d" % self.n_orig; how = "ORIGINATION"
                self.hu_parents[res] = contrib
                self.hu_origin[res] = "INSERTED" if any(self._inserted(x) for x in contrib) else ("UNKNOWN" if not contrib else "DERIVED")
        self.hu[c] = res
        cls = {"WRITER": "AUTONOMOUS" if own_s > win_s + oth_s else ("DECOUPLED" if win_s > own_s else "WRITER_MIXED_EXEC"),
               "OCCUPANT": "CAPTURE", "ORIGINATION": "ORIGINATION", "UNRESOLVED": "UNRESOLVED", "UNRESOLVED_CONTRIB": "UNRESOLVED"}[how]
        self.counts[cls] += 1; self.counts["births"] += 1
        ev = {"tick": tick, "writer": w, "child": c, "mech": mech, "lens_class": cls, "lens_hu": res, "writer_hu": whu,
              "lens_spontaneous": self.spont(res) if res != NI else NI, "own": own, "retained": retained, "other": other,
              "exec_own_share": round(own_s / max(1, own_s + win_s + oth_s), 3)}
        if self.g is not None and len(self.g.nodes) < self.glimit * 12: self._emit(r, ev, occupant)
        return ev

    def _inserted(self, h) -> bool:
        seen = set(); st = [h]
        while st:
            x = st.pop()
            if x in seen or x == NI: continue
            seen.add(x); o = self.hu_origin.get(x)
            if o in ("INSERTED_SEED", "TRANSPLANT", "INSERTED"): return True
            st += self.hu_parents.get(x, [])
        return False

    def spont(self, h) -> str:
        """Tri-valued spontaneity of an HU from ancestry: NO if any inserted ancestor; NI if an unresolved ancestor; else YES."""
        seen = set(); st = [h]; unk = False
        while st:
            x = st.pop()
            if x in seen: continue
            seen.add(x)
            if x == NI: unk = True; continue
            o = self.hu_origin.get(x)
            if o in ("INSERTED_SEED", "TRANSPLANT", "INSERTED"): return "NO"
            st += self.hu_parents.get(x, [])
        return NI if unk else "YES"

    def _emit(self, r, ev, occupant):
        g = self.g; t = "b%d" % ev["child"]; L = self.L
        wm = "m:%d" % ev["writer"]; g.node("org:%d" % ev["writer"], "ENTITY"); g.node(wm, "MATERIAL"); g.edge("org:%d" % ev["writer"], "owns", wm)
        whu = ev["writer_hu"]
        if whu != NI:
            g.node("hu:" + whu, "HU"); g.edge(wm, "member_of", "hu:" + whu)
            if ("found:" + whu) in g.nodes and not g.out(wm, "copies_from"): g.edge(wm, "copies_from", "found:" + whu, basis="DERIVED")
        g.node("x:" + t, "EXECUTION"); g.edge("x:" + t, "performed_by", "org:%d" % ev["writer"]); g.edge("x:" + t, "governed_by", wm, share=ev["exec_own_share"])
        types = {"AUTONOMOUS": ["REPRODUCTION"], "DECOUPLED": ["REPRODUCTION", "HOSTING"], "WRITER_MIXED_EXEC": ["REPRODUCTION"],
                 "CAPTURE": ["REPRODUCTION", "AMPLIFICATION", "HOSTING"], "ORIGINATION": ["ORIGINATION"], "UNRESOLVED": ["UNCLASSIFIED"]}[ev["lens_class"]]
        g.event(t, types); g.edge(t, "via", "x:" + t)
        g.field(t, "executor", "org:%d" % ev["writer"], "TRACE", "entity")
        host = "org:%d" % ev["writer"] if ev["lens_class"] == "CAPTURE" else NONE
        g.field(t, "host", host, "DERIVED", "entity")
        if host != NONE: g.edge(host, "hosts", t)
        g.node("org:%d" % ev["child"], "ENTITY"); g.edge("org:%d" % ev["child"], "labelled_parent", "org:%d" % ev["writer"])
        contrib = []
        if ev["own"]:
            p = t + ":own"; g.node(p, "MATERIAL", share=ev["own"] / L); g.edge(p, "copies_from", wm); g.edge(t, "produced", p)
            if whu != NI: contrib.append("hu:" + whu)
        if ev["other"]:
            p = t + ":other"; g.node(p, "MATERIAL", share=ev["other"] / L, note="written, source not persisted"); g.edge(t, "produced", p)
        if ev["retained"]:
            p = t + ":retained"; g.node(p, "MATERIAL", share=ev["retained"] / L, note="prior occupant bytes (owner not in the birth row)"); g.edge(t, "produced", p)
        res = ev["lens_hu"]
        if res != NI:
            g.node("hu:" + res, "HU")
            if ev["lens_class"] == "ORIGINATION": g.edge(t, "produced", "hu:" + res)
            for p in g.out(t, "produced"):
                if g.nodes[p]["kind"] == "MATERIAL": g.edge(p, "member_of", "hu:" + res)
        g.field(t, "child_contributors", contrib if (contrib and not ev["other"] and not ev["retained"]) else NI, "TRACE", "segment",
                source="copied_from_own count; retained/other owners not persisted")
        g.field(t, "resulting_hu", ("hu:" + res) if res != NI else NI, "DERIVED", "genome")


def native_of(r: list) -> dict:
    return {k: r[i] for k, i in NATIVE_COLS.items()}


def run(rid: str, want_graph=False, graph_limit=5000, max_rows=None) -> dict:
    cfg = json.loads((RUNS / rid / "config.json").read_text(encoding="utf-8"))
    p = Pass(cfg, want_graph, graph_limit); diff = Counter(); first_auto = None; first_native_sr = None; n = 0
    for r in rows(rid):
        ev = p.step(r); nat = native_of(r); n += 1
        diff[(ev["lens_class"], nat["material"], int(nat["is_sr"]))] += 1
        if first_auto is None and ev["lens_class"] == "AUTONOMOUS": first_auto = ev
        if first_native_sr is None and nat["is_sr"]: first_native_sr = {"tick": r[0], "writer": r[1], "child": r[2], "lens": ev}
        if max_rows and n >= max_rows: break
    return {"rid": rid, "init": cfg["config"].get("init"), "init_tapes": bool(cfg.get("init_tapes")), "L": p.L, "births": n,
            "lens_counts": dict(p.counts), "joint_lens_native": {"%s|%s|sr%d" % k: v for k, v in diff.items()},
            "first_autonomous": first_auto, "first_native_sr": first_native_sr, "graph": p.g}
