"""PEW execution-lineage battery (session affinity + engine identity).

Charter: CHARTER_SESSION_AFFINITY_PROVENANCE_2026-09-05.txt, gates A-H.

The question every gate serves: CAN PEW PROVE WHICH EXECUTION LINEAGE PRODUCED
A PIECE OF EVIDENCE, and does it REFUSE when otherwise-valid evidence is spliced
across incompatible SFE sessions or engines?

Run from evidence_wiki/:
    python integration/lineage_battery.py
    python integration/lineage_battery.py --host 192.168.1.191 --machine M2

Gates that need a live session-affine engine are reported SKIP (never PASS)
when the engine does not issue session keys yet.
"""
import argparse
import hashlib
import json
import os
import pathlib
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request

import requests

HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

_HOSTS = {"SKULLPORT": ("192.168.1.202", "m1.crt", "M1"),
          "SPECTREX5": ("192.168.1.191", "m2.crt", "M2")}
_HOST = os.environ.get("PROM_HOST", socket.gethostname()).upper()
_ADDR, _CERT, _MACHINE = _HOSTS.get(_HOST, ("192.168.1.191", "m2.crt", "M2"))
_DEPLOY = HERE.parent / "SerendipityFoundry" / "SerendipityFoundryEngine" / "deploy"

R = []


def gate(name, ok, detail, skipped=False):
    R.append({"gate": name, "pass": bool(ok), "skipped": skipped, "detail": detail})
    print(f"[{'SKIP' if skipped else ('PASS' if ok else 'FAIL')}] {name}: {detail}")
    return bool(ok)


def fp(key):
    """Daedalus's non-secret key fingerprint (sfe/ids.py key_fingerprint)."""
    return "sfp_" + hashlib.sha256(key.encode()).hexdigest()[:16]


class Pew:
    def __init__(self, host, port, token, machine, agent):
        self.base = f"http://{host}:{port}/api/v1"
        self.h = {"Authorization": f"Bearer {token}",
                  "X-Prometheus-Machine": machine, "X-Prometheus-Agent": agent}

    def post(self, p, b):
        return requests.post(f"{self.base}/{p}", headers=self.h, json=b, timeout=90)

    def get(self, p, **q):
        return requests.get(f"{self.base}/{p}", headers=self.h, params=q, timeout=60)


class Sfe:
    """Minimal SFE client. Carries a session key when the engine issues one."""

    def __init__(self, url, ca):
        self.url, self.ctx = url.rstrip("/"), ssl.create_default_context(cafile=ca)
        self.token = self.session_key = None

    def call(self, method, path, body=None):
        d = json.dumps(body).encode() if body is not None else None
        h = {"content-type": "application/json"}
        if self.token:
            h["authorization"] = "Bearer " + self.token
        if self.session_key:
            h["X-SFE-Session"] = self.session_key
        r = urllib.request.Request(self.url + path, data=d, headers=h, method=method)
        try:
            with urllib.request.urlopen(r, context=self.ctx, timeout=25) as z:
                return z.status, json.loads(z.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode() or "{}")
            except Exception:                                     # noqa: BLE001
                return e.code, {}

    def engine_identity_via_anchor(self):
        """The engine's instance id, read from a verify-anchor reply (the only
        published surface that carries it -- /v2/version does not)."""
        st, r = self.call("POST", "/audit/verify-anchor",
                          {"world_id": "wld_x", "event_id": "evt_x",
                           "entry_hash": "sha256:" + "0" * 64})
        return (r.get("engine") or {}).get("engine_instance_id") if st == 200 else None

    def run_experiment(self, tag):
        """A real sealed run. Returns the anchor tuple + session lineage."""
        st, c = self.call("POST", "/clients", {"name": tag})
        if st != 200:
            return None
        self.token = c["token"]
        st, se = self.call("POST", "/sessions", {"name": tag})
        if st != 200:
            return None
        self.session_key = se.get("session_key")          # None on legacy engines
        sid = se["session_id"]
        st, w = self.call("POST", "/worlds", {
            "session_id": sid, "name": tag, "seed_root": 424242,
            "sharing_policy": "ISOLATED",
            "budget": {"ticks": {"limit": 9, "enforcement": "enforceable"}}})
        if st != 200:
            return None
        wid = w["world_id"]
        self.call("POST", f"/worlds/{wid}/start")
        st, h = self.call("POST", f"/worlds/{wid}/hypotheses", {"statement": "H"})
        st, x = self.call("POST", f"/worlds/{wid}/experiments",
                          {"spec": {"action": "encounter", "ticks": 8},
                           "hyp_id": h["hyp_id"], "commit": True})
        exp_id = x["exp_id"]
        st, o = self.call("POST", f"/worlds/{wid}/observations",
                          {"exp_id": exp_id, "content": {"score": 0.5},
                           "outcome": "SURVIVED"})
        obs_id = o["obs_id"]
        st, evs = self.call("GET", f"/worlds/{wid}/events")
        evs = evs["events"] if isinstance(evs, dict) else evs
        ev_id, ev_hash = o.get("event_id"), o.get("entry_hash")
        if not (ev_id and ev_hash):
            cands = [e for e in evs if (e.get("refs") or {}).get("obs_id") == obs_id]
            if len(cands) != 1:
                return None
            ev_id, ev_hash = cands[0]["event_id"], cands[0]["entry_hash"]
        seq = next((e["event_seq"] for e in evs if e["event_id"] == ev_id), None)
        wc = next(e for e in evs if e["event_type"] == "WORLD_CREATED")
        return {"world_id": wid, "exp_id": exp_id, "obs_id": obs_id,
                "event_id": ev_id, "entry_hash": ev_hash, "event_seq": seq,
                "session_id": sid, "session_key": self.session_key,
                "wc_event_id": wc["event_id"], "wc_entry_hash": wc["entry_hash"],
                "wc_seq": wc["event_seq"],
                "affinity_mode": se.get("affinity_mode"),
                "engine_instance_id": se.get("engine_instance_id")}


def fossil(tag, run, engine=None, session=None, keyfp=None, mode=None, **kw):
    b = {"encounter_id": tag, "run_id": f"{run['exp_id']}:{run['obs_id']}",
         "sfe_entry_hash": run["entry_hash"], "sfe_event_id": run["event_id"],
         "sfe_event_seq": run["event_seq"], "sfe_world_id": run["world_id"],
         "world_id": run["world_id"], "namespace": "test", "outcome": "SURVIVED",
         "producer": {"exp_id": run["exp_id"], "obs_id": run["obs_id"]}}
    if engine:
        b["sfe_engine_instance_id"] = engine
    if session:
        b["sfe_session_id"] = session
    if keyfp:
        b["sfe_session_key_fp"] = keyfp
    if mode:
        b["sfe_affinity_mode"] = mode
    b.update(kw)
    return b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8377)
    ap.add_argument("--machine", default=_MACHINE)
    ap.add_argument("--agent", default="lineage-battery")
    ap.add_argument("--sfe-url", default=os.environ.get(
        "PEW_SFE_URL", f"https://{_ADDR}:8811/v2"))
    ap.add_argument("--sfe-cacert", default=os.environ.get(
        "PEW_SFE_CACERT", str(_DEPLOY / _CERT)))
    ap.add_argument("--peer-sfe-url", default=os.environ.get("PEW_PEER_SFE_URL"))
    ap.add_argument("--peer-sfe-cacert", default=os.environ.get("PEW_PEER_SFE_CACERT"))
    a = ap.parse_args()
    cfg = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
    tok = cfg["machine_tokens"].get(a.machine) or cfg["auth_token"]
    pew = Pew(a.host, a.port, tok, a.machine, a.agent)
    stamp = int(time.time())

    sfe = Sfe(a.sfe_url, a.sfe_cacert)
    local_engine = sfe.engine_identity_via_anchor()
    run = sfe.run_experiment(f"lineage-{stamp}")
    if not run:
        gate("L0_local_run", False, "could not produce a sealed SFE run", skipped=True)
        return finish()
    engine = run.get("engine_instance_id") or local_engine
    strict = bool(run.get("session_key"))
    gate("L0_local_run", True,
         f"engine={engine} session={run['session_id']} "
         f"affinity={'STRICT' if strict else 'LEGACY (engine issues no session key)'}")

    keyfp = fp(run["session_key"]) if strict else None

    # ---- A: correct exp+obs+engine (+session when available) -> verify TRUE
    w = pew.post("fossil/encounters",
                 fossil(f"LIN-{stamp}-A", run, engine=engine,
                        session=run["session_id"] if strict else None,
                        keyfp=keyfp, mode="STRICT" if strict else "LEGACY"))
    g = pew.get(f"fossil/encounters/{f'LIN-{stamp}-A'}")
    row = g.json()["runs"][0] if g.status_code == 200 else {}
    gate("A_correct_lineage_verifies",
         w.status_code == 200 and row.get("sfe_engine_instance_id") == engine,
         f"write={w.status_code} stored_engine={row.get('sfe_engine_instance_id')} "
         f"stored_session={row.get('sfe_session_id')} "
         f"affinity={row.get('sfe_affinity_mode')}")

    # ---- F: a random session fingerprint must not look like lineage
    bogus = pew.post("fossil/encounters",
                     fossil(f"LIN-{stamp}-F", run, engine=engine,
                            session="ses_" + "f" * 24, keyfp="sfp_" + "0" * 16,
                            mode="STRICT", encounter_id=f"LIN-{stamp}-F"))
    bd = str(bogus.json().get("detail", ""))[:140] if bogus.status_code != 200 else ""
    # The invented session names a world PEW has already bound to the REAL
    # session, so the splice witness refuses it before storage. A fabricated
    # fingerprint therefore cannot buy lineage: PEW cannot verify a fingerprint
    # it did not mint, and the (engine, world) -> session witness is what
    # actually discriminates.
    gate("F_random_session_lineage_refused",
         bogus.status_code == 409 and "cross_session_splice" in bd,
         f"HTTP {bogus.status_code} {bd}")

    # ...and on a world PEW has never seen, the same fabricated fingerprint is
    # accepted but stays an UNVERIFIED producer claim -- stored, never promoted.
    fresh_run = Sfe(a.sfe_url, a.sfe_cacert).run_experiment(f"lineage-{stamp}-f2")
    if fresh_run:
        f2 = pew.post("fossil/encounters",
                      fossil(f"LIN-{stamp}-F2", fresh_run,
                             engine=engine, session=fresh_run["session_id"],
                             keyfp="sfp_" + "0" * 16, mode="STRICT"))
        g2 = pew.get(f"fossil/encounters/LIN-{stamp}-F2")
        r2 = g2.json()["runs"][0] if g2.status_code == 200 else {}
        att2 = r2.get("attestation") or {}
        gate("F2_unverifiable_fingerprint_stored_not_promoted",
             f2.status_code == 200
             and r2.get("sfe_session_key_fp") == "sfp_" + "0" * 16
             and att2.get("sfe_anchor_checks", {}).get("binds_session") is None,
             f"stored_fp={r2.get('sfe_session_key_fp')} "
             f"binds_session={att2.get('sfe_anchor_checks', {}).get('binds_session')} "
             "(None = engine does not assert it; PEW does not invent it)")

    # ---- raw session key must never be accepted
    if strict:
        leak = pew.post("fossil/encounters",
                        fossil(f"LIN-{stamp}-KEY", run, engine=engine,
                               session=run["session_id"], keyfp=run["session_key"],
                               mode="STRICT"))
        gate("K_raw_session_key_refused", leak.status_code == 422,
             f"HTTP {leak.status_code} {str(leak.json().get('detail'))[:90]}")
    else:
        leak = pew.post("fossil/encounters",
                        fossil(f"LIN-{stamp}-KEY", run, engine=engine,
                               keyfp="sfes_" + "a" * 24 + "_secrettail",
                               mode="LEGACY"))
        gate("K_raw_session_key_refused", leak.status_code == 422,
             f"synthetic key shape refused: HTTP {leak.status_code}")

    # ---- D/E: correct session but wrong exp / wrong obs -> anchor fails
    bad_exp = dict(fossil(f"LIN-{stamp}-D", run, engine=engine,
                          session=run["session_id"] if strict else None,
                          keyfp=keyfp, mode="STRICT" if strict else "LEGACY"))
    bad_exp["producer"] = {"exp_id": "exp_" + "0" * 24, "obs_id": run["obs_id"]}
    dw = pew.post("fossil/encounters", bad_exp)
    _g = pew.get(f"fossil/encounters/LIN-{stamp}-D")
    da = ((_g.json()["runs"][0].get("attestation") or {})
             if _g.status_code == 200 and _g.json().get("runs") else {})

    gate("D_wrong_exp_not_verified",
         dw.status_code == 200 and da.get("sfe_anchor_verified") is False,
         f"anchor_verified={da.get('sfe_anchor_verified')} "
         f"binds_exp_id={(da.get('sfe_anchor_checks') or {}).get('binds_exp_id')}")

    bad_obs = dict(fossil(f"LIN-{stamp}-E", run, engine=engine,
                          session=run["session_id"] if strict else None,
                          keyfp=keyfp, mode="STRICT" if strict else "LEGACY"))
    bad_obs["producer"] = {"exp_id": run["exp_id"], "obs_id": "obs_" + "0" * 24}
    ew_ = pew.post("fossil/encounters", bad_obs)
    _g = pew.get(f"fossil/encounters/LIN-{stamp}-E")
    ea = ((_g.json()["runs"][0].get("attestation") or {})
             if _g.status_code == 200 and _g.json().get("runs") else {})

    gate("E_wrong_obs_not_verified",
         ew_.status_code == 200 and ea.get("sfe_anchor_verified") is False,
         f"anchor_verified={ea.get('sfe_anchor_verified')} "
         f"binds_obs_id={(ea.get('sfe_anchor_checks') or {}).get('binds_obs_id')}")

    # ---- C: engine mismatch. A REAL anchor, but the fossil claims a different
    # engine than the one that verifies it -> must not verify.
    other_engine = "eng_" + hashlib.sha256(b"other").hexdigest()[:24]
    mism = pew.post("fossil/encounters",
                    fossil(f"LIN-{stamp}-C", run, engine=other_engine,
                           session=run["session_id"] if strict else None,
                           keyfp=keyfp, mode="STRICT" if strict else "LEGACY"))
    _g = pew.get(f"fossil/encounters/LIN-{stamp}-C")
    ca = ((_g.json()["runs"][0].get("attestation") or {})
             if _g.status_code == 200 and _g.json().get("runs") else {})
    ck = ca.get("sfe_anchor_checks") or {}
    gate("C_engine_mismatch_not_verified",
         mism.status_code == 200 and ca.get("sfe_anchor_verified") is False
         and ck.get("binds_engine_instance") is False,
         f"claimed={other_engine[:16]}.. answering={str(ck.get('answering_engine_instance'))[:16]}.. "
         f"binds_engine_instance={ck.get('binds_engine_instance')} "
         f"verified={ca.get('sfe_anchor_verified')}")

    # ---- G: legacy pre-session evidence stays legacy, never fabricated
    leg = pew.post("fossil/encounters",
                   fossil(f"LIN-{stamp}-G", run))          # no engine/session at all
    lg = pew.get(f"fossil/encounters/LIN-{stamp}-G")
    lrow = lg.json()["runs"][0] if lg.status_code == 200 else {}
    gate("G_legacy_stays_legacy",
         leg.status_code == 200 and lrow.get("sfe_affinity_mode") == "LEGACY"
         and lrow.get("sfe_session_id") is None
         and lrow.get("sfe_engine_instance_id") is None,
         f"affinity={lrow.get('sfe_affinity_mode')} session={lrow.get('sfe_session_id')} "
         "engine=None -- no binding synthesized for evidence that had none")

    # ---- strict claim without the lineage it asserts
    hollow = pew.post("fossil/encounters",
                      fossil(f"LIN-{stamp}-H0", run, mode="STRICT"))
    gate("H0_hollow_strict_claim_refused", hollow.status_code == 422,
         f"HTTP {hollow.status_code} {str(hollow.json().get('detail'))[:80]}")

    # ---- session id without its engine is not lineage
    orphan = pew.post("fossil/encounters",
                      fossil(f"LIN-{stamp}-H1", run, session="ses_" + "a" * 24))
    gate("H1_session_without_engine_refused", orphan.status_code == 422,
         f"HTTP {orphan.status_code} {str(orphan.json().get('detail'))[:80]}")

    # ---- SPLIT BRAIN: the same engine identity offering a DIFFERENT entry_hash
    # at an event_seq PEW has already witnessed. This is the cloned-database
    # case, reproduced through the public write path.
    forked = fossil(f"LIN-{stamp}-SB", run, engine=engine,
                    session=run["session_id"] if strict else None,
                    keyfp=keyfp, mode="STRICT" if strict else "LEGACY")
    forked["encounter_id"] = f"LIN-{stamp}-SB"
    forked["sfe_entry_hash"] = "sha256:" + hashlib.sha256(b"forked").hexdigest()
    forked["sfe_event_id"] = "evt_" + hashlib.sha256(b"forked").hexdigest()[:24]
    sb = pew.post("fossil/encounters", forked)
    detail = str(sb.json().get("detail", ""))[:150] if sb.status_code != 200 else ""
    gate("SB_split_brain_fork_refused",
         sb.status_code == 409 and "split_brain_ledger_fork" in detail,
         f"HTTP {sb.status_code} {detail}")

    # ---- the refused fork is itself recorded
    try:
        from ew import db as ewdb
        conn = ewdb.connect()
        with ewdb.dict_cur(conn) as cur:
            cur.execute("SELECT count(*) n FROM ew.ledger_fork_events WHERE "
                        "engine_instance_id=%s AND event_seq=%s",
                        (engine, run["event_seq"]))
            nfork = cur.fetchone()["n"]
        conn.close()
        gate("SB2_fork_event_recorded", nfork >= 1,
             f"{nfork} fork event(s) durably recorded for (engine, seq) -- a "
             "refused write still leaves the evidence that a fork was seen")
    except Exception as exc:                                      # noqa: BLE001
        gate("SB2_fork_event_recorded", False, f"needs DB access: {exc}",
             skipped=True)

    # ---- B: wrong SESSION (needs a session-affine engine)
    if strict:
        run2 = Sfe(a.sfe_url, a.sfe_cacert).run_experiment(f"lineage-{stamp}-b")
        # same world/anchor as run, but claiming run2's session: the splice
        other_sess = pew.post("fossil/encounters",
                              fossil(f"LIN-{stamp}-B", run, engine=engine,
                                     session=run2["session_id"],
                                     keyfp=fp(run2["session_key"]), mode="STRICT"))
        _gb = pew.get(f"fossil/encounters/LIN-{stamp}-B")
        ba = ((_gb.json()["runs"][0].get("attestation") or {})
              if _gb.status_code == 200 and _gb.json().get("runs") else {})
        bk = ba.get("sfe_anchor_checks") or {}
        # PEW's own splice witness must refuse it even while the engine does
        # not assert binds_session. The engine-side check remains the real fix.
        spliced = other_sess.status_code == 409 and "cross_session_splice" in             str(other_sess.json().get("detail", ""))
        gate("B_wrong_session_refused",
             spliced or bk.get("binds_session") is False,
             f"HTTP {other_sess.status_code} splice_refused={spliced} "
             f"engine_binds_session={bk.get('binds_session')} "
             f"{str(other_sess.json().get('detail',''))[:110]}")
    else:
        gate("B_wrong_session_not_verified", False,
             "engine issues no session key yet; binds_session is not assertable",
             skipped=True)

    # ---- peer engine (cross-machine splice), when a peer is reachable
    if a.peer_sfe_url and a.peer_sfe_cacert:
        peer = Sfe(a.peer_sfe_url, a.peer_sfe_cacert)
        prun = peer.run_experiment(f"lineage-{stamp}-peer")
        peng = peer.engine_identity_via_anchor()
        if prun:
            spl = pew.post("fossil/encounters",
                           fossil(f"LIN-{stamp}-PEER", prun, engine=peng))
            _gp = pew.get(f"fossil/encounters/LIN-{stamp}-PEER")
            pa = ((_gp.json()["runs"][0].get("attestation") or {})
                  if _gp.status_code == 200 and _gp.json().get("runs") else {})
            pk = pa.get("sfe_anchor_checks") or {}
            gate("P_peer_engine_anchor_not_verified",
                 pa.get("sfe_anchor_verified") is False,
                 f"anchor minted on peer engine {str(peng)[:16]}.. verified by "
                 f"local engine -> verified={pa.get('sfe_anchor_verified')} "
                 f"binds_engine_instance={pk.get('binds_engine_instance')} "
                 f"event_exists={pk.get('event_exists')}")
        else:
            gate("P_peer_engine_anchor_not_verified", False,
                 "peer engine unreachable / no run", skipped=True)
    else:
        gate("P_peer_engine_anchor_not_verified", False,
             "no --peer-sfe-url given", skipped=True)

    return finish(engine=engine, strict=strict)


def finish(**extra):
    scored = [r for r in R if not r.get("skipped")]
    out = {"ran_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "n_scored": len(scored), "n_pass": sum(r["pass"] for r in scored),
           "skipped": [r["gate"] for r in R if r.get("skipped")],
           "all_pass": bool(scored) and all(r["pass"] for r in scored),
           "gates": R, **extra}
    (HERE / "integration" / "lineage_results.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "gates"}, indent=1))
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
