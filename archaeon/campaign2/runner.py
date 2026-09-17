"""Campaign-2 runner: ATTEMPTS, IDEMPOTENT STEPS, RESUME and the ENGINE WRAPPER
(directive Phase A groups D, E, F, I; ledger L-012, L-013, L-009, L-001, L-002, L-010).

Attempt(experiment)      every run of a harness is an attempt with an identity
                         (C2-SFE-NN/attempts/aNN/RECEIPT.json, written after EVERY step);
                         the experiment root holds the attempt OF RECORD's receipt + rows and
                         an ATTEMPTS.json index. No renaming, ever.
Attempt.step(name, fn)   deterministic key sha(experiment, name, *parts); on a resumed attempt
                         a step whose key is in the previous attempt's receipt is REPLAYED
                         (its stored result returned, engine untouched) when its verifier says
                         the result is still valid (a world still alive, an artifact still
                         readable); otherwise it is re-executed. Engine posts that the client
                         can key (observations, failures, artifacts) carry the same key as
                         Idempotency-Key.
Engine                   the client behind ONE tracked descriptor (engine_descriptor), canonical
                         digests on both sides (digest.same), read wrappers for the routes the
                         client lacked (L-001), a session-less reader for cross-session reads
                         (D-013), and publish() that REQUIRES a maturity block for any artifact
                         kind declared as population material.
"""
from __future__ import annotations

import base64
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry.grammar import GRAMMAR_HASH               # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH              # noqa: E402

from archaeon import workspace as _ws                          # noqa: E402
from archaeon.wse import digest as D                           # noqa: E402
from archaeon.wse.engine_descriptor import engine as engine_descriptor   # noqa: E402

C2 = REPO / "archaeon" / "campaign2"
CONFIG = C2 / "config.local.json"          # gitignored (global pattern config.local.json)
CLIENT_NAME = "cmp2-archaeon"
CAMPAIGN_SEED = 20260918                   # campaign 2's own seed: its rows are independent samples beside campaign 1's
POPULATION_KINDS_PREFIX = "cmp2.pop."      # artifact kinds that can enter another population MUST carry maturity


def step_key(*parts: Any) -> str:
    return "idem:" + D.hexof(D.of_obj(list(parts)))[:32]


def _atomic_write(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


class Attempt:
    def __init__(self, experiment: str, *, root: Path = C2, resume: bool = True, dry_run: bool = False,
                 purpose: str = "", campaign_seed: int = CAMPAIGN_SEED):
        self.experiment = experiment
        self.dir = Path(root) / experiment
        attempts = self.dir / "attempts"
        attempts.mkdir(parents=True, exist_ok=True)
        existing = sorted(int(p.name[1:]) for p in attempts.glob("a[0-9][0-9]") if (p / "RECEIPT.json").exists())
        self.number = (existing[-1] + 1) if existing else 1
        self.path = attempts / ("a%02d" % self.number)
        self.path.mkdir(parents=True, exist_ok=True)
        self.dry_run = dry_run
        self.t0 = time.time()
        self.receipt: Dict[str, Any] = {
            "experiment": experiment, "attempt": self.number, "attempt_id": "%s/a%02d" % (experiment, self.number),
            "campaign": "cmp2", "campaign_seed": campaign_seed, "purpose": purpose,
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "workspace": _ws.assert_not_canonical("run " + experiment), "runtime_hash": RUNTIME_HASH, "grammar_hash": GRAMMAR_HASH,
            "engine_path": not dry_run, "engine": None if dry_run else engine_descriptor(),
            "steps": {}, "replayed": [], "worlds": {}, "artifacts": {}, "imports": {}, "records": {},
            "errors": [], "timings": {}, "typed_states": [], "disposition_candidate": None,
            "resumed_from": None, "teardown": {},
        }
        self.cache: Dict[str, dict] = {}
        if resume and existing:
            prev = json.loads((attempts / ("a%02d" % existing[-1]) / "RECEIPT.json").read_text(encoding="utf-8"))
            # a live attempt never resumes from a dry run (nothing of a dry run exists on the engine)
            if bool(prev.get("engine_path")) == (not dry_run):
                self.cache = dict(prev.get("steps", {}))
                self.receipt["resumed_from"] = existing[-1]
        self.save()

    # -- steps ---------------------------------------------------------------
    def key(self, name: str, *parts: Any) -> str:
        return step_key(self.experiment, name, *parts)

    def step(self, name: str, fn: Callable[[], Any], *, parts: tuple = (), kind: str = "local",
             verify: Optional[Callable[[Any], bool]] = None) -> Any:
        key = self.key(name, *parts)
        ent = self.cache.get(key)
        if ent is not None and not ent.get("failed"):
            try:
                ok = verify is None or bool(verify(ent["result"]))
            except Exception:                                        # noqa: BLE001
                ok = False
            if ok:
                self.receipt["steps"][key] = dict(ent, replayed=True)
                self.receipt["replayed"].append(name if not parts else "%s:%s" % (name, "/".join(str(p) for p in parts)))
                self.save()
                return ent["result"]
        t0 = time.time()
        try:
            res = fn()
        except Exception as e:                                       # noqa: BLE001
            self.receipt["steps"][key] = {"name": name, "parts": list(parts), "kind": kind, "failed": True, "error": repr(e),
                                          "replayed": False, "wall_s": round(time.time() - t0, 3)}
            self.receipt["errors"].append({"step": name, "parts": list(parts), "kind": kind, "error": repr(e)})
            self.save()
            raise
        self.receipt["steps"][key] = {"name": name, "parts": list(parts), "kind": kind, "result": res, "replayed": False,
                                      "wall_s": round(time.time() - t0, 3)}
        self.save()
        return res

    def error(self, step: str, **info: Any) -> None:
        self.receipt["errors"].append({"step": step, **info})
        self.save()

    def timing(self, name: str, t0: float) -> None:
        self.receipt["timings"][name] = round(time.time() - t0, 2)
        self.save()

    def save(self) -> None:
        _atomic_write(self.path / "RECEIPT.json", json.dumps(self.receipt, indent=1, sort_keys=True, default=str))

    def write(self, name: str, obj: Any) -> Path:
        p = self.path / name
        _atomic_write(p, json.dumps(obj, indent=1, sort_keys=True, default=str))
        return p

    def finalize(self, rows: Optional[list] = None, *, of_record: bool = True, disposition: Optional[dict] = None) -> dict:
        self.receipt["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.receipt["timings"]["total_s"] = round(time.time() - self.t0, 1)
        if disposition is not None:
            self.receipt["disposition_candidate"] = disposition
        self.save()
        if rows is not None:
            self.write("rows.json", rows)
        idx_p = self.dir / "ATTEMPTS.json"
        idx = json.loads(idx_p.read_text(encoding="utf-8")) if idx_p.exists() else {"experiment": self.experiment, "attempts": {}, "of_record": None}
        idx["attempts"][str(self.number)] = {
            "dir": "attempts/a%02d" % self.number, "started_at": self.receipt["started_at"], "finished_at": self.receipt["finished_at"],
            "engine_path": self.receipt["engine_path"], "errors": len(self.receipt["errors"]), "replayed_steps": len(self.receipt["replayed"]),
            "resumed_from": self.receipt["resumed_from"], "purpose": self.receipt["purpose"],
            "disposition_candidate": (disposition or {}).get("disposition"),
        }
        if of_record:
            idx["of_record"] = self.number
            shutil.copyfile(self.path / "RECEIPT.json", self.dir / "RECEIPT.json")
            if rows is not None:
                shutil.copyfile(self.path / "rows.json", self.dir / "rows.json")
        _atomic_write(idx_p, json.dumps(idx, indent=1, sort_keys=True))
        return idx


# ------------------------------------------------------------------ engine wrapper
class Engine:
    def __init__(self, dry_run: bool = False, config: Path = CONFIG, client_name: str = CLIENT_NAME):
        self.dry_run = dry_run
        self.c = None
        self.descriptor = None
        self._req_count = 0
        if dry_run:
            return
        from sfclient.client import EngineClient
        self.descriptor = engine_descriptor()
        cfg = json.loads(config.read_text(encoding="utf-8")) if config.exists() else {}
        self.c = EngineClient(self.descriptor["base_url"], cfg.get("token"), cafile=self.descriptor["cacert"], client_id=cfg.get("client_id"))
        if not cfg.get("token"):
            self.c.register(client_name)
            cfg = {"token": self.c.token, "client_id": self.c.client_id, "registered_at": time.time(),
                   "engine": self.descriptor["base_url"], "engine_instance_id": self.descriptor["engine_instance_id"]}
            config.write_text(json.dumps(cfg, indent=1), encoding="utf-8")
        self.client_id = self.c.client_id

    # -- lifecycle
    def version(self) -> dict:
        return self.c.version()

    def session(self, name: str) -> str:
        return self.c.create_session(name)

    def group(self, note: str) -> str:
        return self.c.create_topology_group(note)

    def world(self, session_id: str, name: str, policy: str, group: Optional[str] = None, seed_root: int = CAMPAIGN_SEED) -> dict:
        kw = {"sharing_policy": policy, "seed_root": seed_root}
        if group:
            kw["topology_group"] = group
        w = self.c.create_world(session_id, name, **kw)
        self.c.start(w["world_id"])
        return {"world_id": w["world_id"], "name": name, "policy": policy}

    def state(self, wid: str) -> str:
        return str(self.c.get_world(wid).get("state"))

    def alive(self, wid: str) -> bool:
        try:
            return self.state(wid) not in ("TERMINATED", "None")
        except Exception:                                            # noqa: BLE001
            return False

    def hypothesis(self, wid: str, statement: str) -> str:
        return self.c.hypothesis(wid, statement)

    def terminate(self, wid: str) -> str:
        self.c.terminate(wid)
        return self.state(wid)

    def terminate_all(self, worlds: Dict[str, str]) -> Dict[str, str]:
        out = {}
        for name, wid in worlds.items():
            try:
                out[name] = self.terminate(wid)
            except Exception as e:                                   # noqa: BLE001
                out[name] = "ERROR " + repr(e)
        return out

    # -- artifacts (canonical bytes, canonical digests, maturity required for population material)
    def publish(self, wid: str, kind: str, obj: Any, meta: Optional[dict] = None, *, maturity: Optional[dict] = None,
                idem_key: Optional[str] = None) -> dict:
        if kind.startswith(POPULATION_KINDS_PREFIX) and maturity is None:
            raise ValueError("artifact kind %s can enter a population and MUST carry a maturity block" % kind)
        b = D.canonical_bytes(obj)
        m = dict(meta or {})
        if maturity is not None:
            m["maturity"] = maturity
        declared = D.of_bytes(b)
        art = self.c.artifact(wid, kind, b, m, expected_blob_hash=D.hexof(declared), idem_key=idem_key)
        return {"artifact_id": D.canon(art["artifact_id"]), "blob_hash": D.canon(art.get("blob_hash")), "declared": declared,
                "bytes": len(b), "kind": kind, "hash_ok": D.same(art.get("blob_hash"), declared)}

    def fetch(self, wid: str, artifact_id: str, *, expected: Optional[str] = None, client=None) -> tuple:
        cl = client or self.c
        content = cl.artifact_content(wid, D.canon(artifact_id))
        raw = base64.b64decode(content["content_b64"])
        got = D.of_bytes(raw)
        info = {"bytes": len(raw), "digest": got, "expected": D.canon(expected), "hash_ok": D.same(got, expected) if expected else None}
        return json.loads(raw), info

    def import_fetch(self, dst_wid: str, src_wid: str, artifact_id: str, *, expected: Optional[str] = None) -> tuple:
        imp = self.c.import_artifact(dst_wid, src_wid, D.canon(artifact_id))
        obj, info = self.fetch(dst_wid, imp["artifact_id"], expected=expected)
        info["import_artifact_id"] = D.canon(imp["artifact_id"]); info["origin"] = imp.get("origin")
        return obj, info

    # -- records
    def record(self, wid: str, spec: dict, content: dict, outcome: str, *, idem_key: Optional[str] = None, hyp_id: Optional[str] = None) -> dict:
        exp = self.c.experiment(wid, spec, hyp_id=hyp_id)
        obs = self.c.observation(wid, exp["exp_id"], content, outcome, idem_key=idem_key)
        return {"exp_id": exp["exp_id"], "obs_id": obs}

    def failure(self, wid: str, failure_type: str, falsifier: str, violated: str, *, idem_key: Optional[str] = None) -> str:
        return self.c.failure(wid, failure_type=failure_type, falsifier=falsifier, violated=violated, idem_key=idem_key)

    # -- read wrappers (L-001) and the session-less reader (D-013)
    def _get(self, path: str, client=None) -> Any:
        return (client or self.c)._req("GET", path)

    def list_experiments(self, wid: str, client=None) -> list:
        return self._get("/v2/worlds/%s/experiments" % wid, client)

    def get_experiment(self, wid: str, exp_id: str, client=None) -> dict:
        return self._get("/v2/worlds/%s/experiments/%s" % (wid, exp_id), client)

    def list_observations(self, wid: str, client=None) -> list:
        return self._get("/v2/worlds/%s/observations" % wid, client)

    def list_artifacts(self, wid: str, client=None) -> list:
        """HTTP 405 on the production engine (no GET artifacts route; Phase A smoke); kept for a
        future engine, never relied on."""
        return self._get("/v2/worlds/%s/artifacts" % wid, client)

    def reader(self):
        """A client with the same token and NO session key: reads across sessions under the
        engine's advisory enforcement (campaign-1 D-013 / L-026)."""
        from sfclient.client import EngineClient
        return EngineClient(self.descriptor["base_url"], self.c.token, cafile=self.descriptor["cacert"], client_id=self.c.client_id)

    def read_campaign1(self, config: Path = REPO / "archaeon" / "campaign1" / "config.local.json"):
        """A session-less client under campaign 1's OWN principal, for artifacts campaign 1
        published (a different client id; the campaign-2 token is not that world's owner)."""
        from sfclient.client import EngineClient
        cfg = json.loads(config.read_text(encoding="utf-8"))
        return EngineClient(self.descriptor["base_url"], cfg.get("token"), cafile=self.descriptor["cacert"], client_id=cfg.get("client_id"))
