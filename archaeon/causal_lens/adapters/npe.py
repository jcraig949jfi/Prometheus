"""NPE adapter (Nestor Z80xAtlas, Cycle-9 engine roles/Nestor/campaigns/z80atlas-verify-2026-09-22). READ-ONLY on NPE.

Why a replay: per-run lineage files are not on disk (runs/ gitignored; the launch drive F: is not mounted). run_cell is deterministic
from (cell, seed) (world.py:88), so the H2 RESERVOIR arms (full lineage retained, material tags on, P-11 on every pair-tape event) are
replayed EXACTLY as frozen in MANIFEST_FROZEN.json. The engine is not edited: a Runner SUBCLASS observes three things the engine
computes but does not keep, and changes nothing it computes:
  (1) founders: every _place() with pid None before the first epoch (oid, anc, implant flag);
  (2) pair-tape births: which body was overwritten (the victim's oid BEFORE the in-place rename, world.py:877), its anc before;
  (3) private-slot births: bytes written vs the slot pre-image, and residue bytes (unchanged, non-zero) -- the engine computes
      wrote_bytes (world.py:676) but stores it only folded into repro_span.

BLINDNESS: native verdict fields (`causal`, `causal_pred`, p11 `pass`, `pass_literal`, `C2`, `C4`, `C5`, `draws_passed`) are never read
by the lens rules below; they are returned as the NATIVE reading. The lens uses only execution-level measurements
(p11 diagnostics donor_authored_share_ordinary / donor_last_wrote_share_ordinary / n_directed_ordinary, which are provenance counts
from the live tape's `prov` arrays) and the observed placements. Frozen before any NPE adjudication (ADJUDICATION_C9, VERDICTs,
CAMPAIGN_REPORT outcomes) was read.

LENS RULES (frozen here):
  Founders: HU per founder (native anc). Origin: implant under ACTUAL_GENOME -> TRANSPLANT; implant under RANDOM_MATCHED -> RANDOM_INIT
    (random bytes; placement is an intervention, recorded as a property); invaders -> INSERTED_SEED; seeding RANDOM -> RANDOM_INIT;
    seeding SEEDED_* -> INSERTED_SEED.
  Pair-tape birth (the victim half now matches the donor): executor = the DONOR if donor_authored_share >= 0.5 (it wrote the directed
    bytes, by provenance), NOT_IDENTIFIABLE if the share is missing; executed material = both programs ran (shares not recorded);
    contributors = donor HU if donor_authored_share >= 0.5, else NOT_IDENTIFIABLE; host = the VICTIM BODY (it supplied the location,
    and its own code ran on the shared tape); resulting HU = donor HU (AMPLIFICATION+HOSTING) when contributors resolve, else NI.
  Private-slot birth (ALLOC/BIRTH): executor = the BIRTH caller. Written bytes have no authorship record -> contributors
    NOT_IDENTIFIABLE at material level; APPROXIMATE continuation of the caller's HU only if wrote >= len/2 AND fidelity >= 0.9 AND the
    write policy is private (basis DERIVED, granularity genome). Residue (unchanged non-zero pre-image bytes) is material of an unknown
    prior occupant.
  Spontaneous(HU) from ancestry only (NO if any inserted/transplanted ancestor).
"""
from __future__ import annotations

import sys
from pathlib import Path

Z2 = Path(__file__).resolve().parents[3] / "roles/Nestor/campaigns/z80atlas-verify-2026-09-22"


def _engine():
    if str(Z2) not in sys.path: sys.path.insert(0, str(Z2))
    import world as W                                           # noqa: E402  (NPE's own module)
    return W


def observed_runner_class():
    W = _engine()

    class Obs(W.Runner):
        def __init__(self, *a, **k):
            self._obs_founders = []; self._obs_pair = []; self._obs_priv = []; self._obs_births_started = False
            super().__init__(*a, **k)

        def _place(self, genome, anc, pid=None, niche=0):
            o = super()._place(genome, anc, pid, niche)
            if o is not None and pid is None and not self._obs_births_started:
                self._obs_founders.append({"oid": o.oid, "anc": anc, "implant": bool(self.implant) and len(self._obs_founders) == 0, "niche": niche})
            return o

        def _pair_interact(self, i, a, b):
            self._obs_births_started = True
            pre = {id(a): (a.oid, a.anc, a.slot), id(b): (b.oid, b.anc, b.slot)}; n0 = len(self.lineage)
            super()._pair_interact(i, a, b)
            for e in self.lineage[n0:]:
                if e.get("kind") != "birth": continue
                body = a if a.oid == e["child"] else (b if b.oid == e["child"] else None)
                if body is None: continue
                old = pre[id(body)]; donor = b if body is a else a
                self._obs_pair.append({"child": e["child"], "victim_old_oid": old[0], "victim_anc_before": old[1], "victim_slot": old[2],
                                       "donor_oid": pre[id(donor)][0], "donor_anc": pre[id(donor)][1], "epoch": self.epoch})

        def _on_birth(self, o, ctx, dst, cnt, partial):
            self._obs_births_started = True
            p = self.pending.get(o.oid); info = None
            if p is not None:
                slot, size, pre = p; n = max(W.MIN_LEN, min(cnt if partial else size, self.slot_size)) if hasattr(W, "MIN_LEN") else size
                cur = bytes(self.mem[slot:slot + n])
                info = {"caller": o.oid, "caller_anc": o.anc, "wrote": sum(1 for k in range(n) if cur[k] != pre[k]),
                        "residue": sum(1 for k in range(n) if cur[k] == pre[k] and cur[k] != 0), "n": n}
            n0 = len(self.lineage); ok = super()._on_birth(o, ctx, dst, cnt, partial)
            if info is not None and ok:
                for e in self.lineage[n0:]:
                    if e.get("kind") == "birth": info["child"] = e["child"]; self._obs_priv.append(info)
            return ok

    return Obs


def replay(cell: dict, seed: int, tier: str, kwargs: dict) -> dict:
    Obs = observed_runner_class()
    kw = dict(kwargs); kw.pop("implant_source", None); hx = kw.pop("implant_hex", None)      # exactly as run_campaign.py:86-90
    if hx: kw["implant_bytes"] = bytes.fromhex(hx)
    r = Obs(cell, seed, tier=tier, **kw)
    agg = r.run()
    return {"summary": agg, "lineage": list(r.lineage), "founders": r._obs_founders, "pair": r._obs_pair, "priv": r._obs_priv,
            "implant": getattr(r, "implant", None), "invaders": r.invaders, "seeding": cell.get("seeding"), "write_policy": cell.get("world")}


NATIVE_KEYS = ("causal", "causal_pred")
NATIVE_P11 = ("pass", "pass_literal", "C2", "C4", "C5", "draws_passed")
MEAS_P11 = ("donor_authored_share_ordinary", "donor_last_wrote_share_ordinary", "n_directed_ordinary", "fid_init_ordinary",
            "fid_donor_disabled_ordinary")


def lens(rec: dict) -> dict:
    """Frozen lens rules over one replay record. Returns per-event lens readings (+ native readings kept apart)."""
    hu, origin, parents = {}, {}, {}
    for f in rec["founders"]:
        h = "anc%d" % f["anc"]; hu[f["oid"]] = h
        if f["implant"]: origin[h] = "TRANSPLANT" if rec["implant"] == "ACTUAL_GENOME" else "RANDOM_INIT"
        elif f["anc"] < (rec["invaders"] or 0): origin[h] = "INSERTED_SEED"
        else: origin[h] = "RANDOM_INIT" if rec["seeding"] == "RANDOM" else "INSERTED_SEED"
    pair = {p["child"]: p for p in rec["pair"]}; priv = {p["child"]: p for p in rec["priv"]}
    NI = "NOT_IDENTIFIABLE"; out = []
    for e in rec["lineage"]:
        if e.get("kind") != "birth": continue
        c = e["child"]; nat = {k: e.get(k) for k in NATIVE_KEYS}
        if "p11" in e: nat.update({"p11_" + k: e["p11"].get(k) for k in NATIVE_P11})
        if c in pair:
            p = pair[c]; share = (e.get("p11") or {}).get("donor_authored_share_ordinary")
            dhu = hu.get(p["donor_oid"], NI); vhu = hu.get(p["victim_old_oid"], NI)
            if share is None: ex, contrib, res = NI, NI, NI
            elif share >= 0.5: ex, contrib, res = "org%d" % p["donor_oid"], [dhu], dhu
            else: ex, contrib, res = NI, NI, NI
            hu[c] = res
            out.append({"child": c, "kind": "PAIR_OVERWRITE", "executor": ex, "contributors": contrib, "host": "body:%d" % p["victim_old_oid"],
                        "resulting_hu": res, "victim_hu_before": vhu, "donor_hu": dhu, "native_parent_is_donor": e["parent"] == p["donor_oid"],
                        "native_entity_continuity": "RENAMED_IN_PLACE", "donor_authored_share": share,
                        "donor_last_wrote_share": (e.get("p11") or {}).get("donor_last_wrote_share_ordinary"),
                        "fid_donor_disabled": (e.get("p11") or {}).get("fid_donor_disabled_ordinary"),
                        "types": ["REPRODUCTION", "AMPLIFICATION", "HOSTING"] if res != NI else ["UNCLASSIFIED"], "native": nat})
        elif c in priv:
            p = priv[c]; chu = hu.get(p["caller"], NI); fid = e.get("fidelity") or 0.0
            approx = p["wrote"] >= p["n"] / 2 and fid >= 0.9 and rec["write_policy"] != "PAIR_TAPE"
            res = chu if approx else NI; hu[c] = res
            out.append({"child": c, "kind": "PRIVATE_SLOT", "executor": "org%d" % p["caller"], "contributors": NI, "host": "NONE",
                        "resulting_hu": res, "resulting_hu_basis": "DERIVED/APPROXIMATE" if approx else None, "wrote": p["wrote"], "residue": p["residue"],
                        "types": ["REPRODUCTION"] if approx else ["UNCLASSIFIED"], "native": nat})
        else:
            hu[c] = NI
            out.append({"child": c, "kind": "UNOBSERVED", "executor": NI, "contributors": NI, "resulting_hu": NI, "types": ["UNCLASSIFIED"], "native": nat})

    def spont(h):
        if h == NI or h is None: return NI
        o = origin.get(h)
        return "NO" if o in ("TRANSPLANT", "INSERTED_SEED") else ("YES" if o else NI)
    for ev in out: ev["lens_spontaneous"] = spont(ev["resulting_hu"])
    return {"events": out, "hu_origin": origin, "founders": len(rec["founders"])}
