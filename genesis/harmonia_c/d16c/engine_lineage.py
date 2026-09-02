"""Engine-backed LT lineage: every epistemic act of lt.Researcher is ledgered
in an SFE world (hypothesis -> prediction -> committed experiment ->
observation -> failure), the query budget is the world's ENFORCEABLE
`experiments` budget, and the lineage's outputs are published as NATIVE
artifacts (info_kind success/failure/observation).  Synthesis worlds import
those artifacts (F10 = AVAILABLE), read them (F1 = CONSUMED, client log), and
lt.knowledge_from_artifacts builds knowledge.  The hidden-world oracle runs
client-side, so observation evidence is CLIENT_ASSERTED (recorded).
"""
import json, sys, base64
sys.path.insert(0, r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryClient")
sys.path.insert(0, r"D:\Prometheus\genesis\harmonia_c\d16c")
from sfclient.client import EngineClient, EngineError
from lt import *

BASE = "http://127.0.0.1:8899"
PIN = "sha256:5274ddbe9120ddbbd75a36965106d2efe640a3b72278e7bb97b82e356e1fc9fc"


def pinned(base=BASE):
    import urllib.request
    h = urllib.request.urlopen(base + "/v2/version").headers["x-sfe-engine-source-hash"]
    assert h == PIN, h
    return base


class KeepAliveClient(EngineClient):
    """sfclient opens a TCP connection per request; under load the OS runs out
    of ephemeral ports (WinError 10048, 16k TIME_WAIT) -- an instrument limit,
    not an engine one. One persistent connection per client instance (one
    thread per instance); reconnects once on a stale socket."""
    def __init__(self, *a, **k):
        super().__init__(*a, **k); self._keep = None

    def _req(self, method, path, body=None, *, idem_key=None):
        import http.client
        headers = {"accept": "application/json", "connection": "keep-alive"}
        if self.token: headers["authorization"] = f"Bearer {self.token}"
        if idem_key is not None: headers["Idempotency-Key"] = idem_key
        data = None
        if body is not None:
            data = json.dumps(body).encode(); headers["content-type"] = "application/json"
        for attempt in (0, 1):
            if self._keep is None:
                self._keep = http.client.HTTPConnection(self._u.hostname, self._u.port, timeout=self.timeout)
            try:
                self._keep.request(method, path, body=data, headers=headers)
                resp = self._keep.getresponse(); raw = resp.read(); status = resp.status
                break
            except (http.client.HTTPException, ConnectionError, OSError):
                try: self._keep.close()
                except Exception: pass
                self._keep = None
                if attempt: raise
        parsed = json.loads(raw) if raw else None
        if 200 <= status < 300: return parsed
        raise EngineError(status, parsed.get("detail") if isinstance(parsed, dict) else parsed)


def new_client(name, base=BASE):
    c = KeepAliveClient(base); c.register(name); return c


def oracle_of(w):
    return lambda q: (w.transition(q[1], q[2]) if q[0] == "TRANSITION" else w.admissible(q[1]))


class EngineRecorder:
    """Maps lt recorder calls onto engine calls. Raises on budget exhaustion
    (409) so the lineage stops exactly where the engine says it does."""
    def __init__(self, cli: EngineClient, wid: str):
        self.c, self.w = cli, wid
        self.n = {"hypothesis": 0, "prediction": 0, "experiment": 0, "observation": 0, "failure": 0}
        self.exhausted = False

    def __call__(self, kind, d):
        self.n[kind] += 1
        c, w = self.c, self.w
        if kind == "hypothesis":
            return c.hypothesis(w, d["statement"])
        if kind == "prediction":
            return c.prediction(w, d["hyp"], d["content"])
        if kind == "experiment":
            try:
                return c.experiment(w, {"query": d["spec"]}, hyp_id=d["hyp"], pred_id=d["pred"])["exp_id"]
            except EngineError as e:
                if e.status == 409 and "budget" in json.dumps(e.detail):
                    self.exhausted = True
                raise
        if kind == "observation":
            return c.observation(w, d["exp"], d["content"], d["outcome"], pred_id=d["pred"])
        if kind == "failure":
            return c.failure(w, failure_type=d["type"], falsifier=json.dumps(d.get("query", d.get("family"))),
                             violated=json.dumps(d.get("hypothesis", d.get("component"))),
                             reference={"component": d["component"]}, observed=d.get("result"))
        raise ValueError(kind)


def make_world(cli, session, name, budget, grp=None, policy="FULLY_SHARED", seed=None):
    r = cli.create_world(session, name, sharing_policy=policy, topology_group=grp,
                         budget={"experiments": {"limit": budget, "enforcement": "enforceable"}}, seed_root=seed)
    cli.start(r["world_id"])
    return r["world_id"]


def run_lineage(cli, wid, lt_world, settings, budget):
    """Run one researcher against the engine; publish artifacts. Returns
    (researcher, recorder, artifact_ids)."""
    rec = EngineRecorder(cli, wid)
    r = Researcher(lt_world.public(), settings, oracle_of(lt_world), rec, budget=budget + 5)  # engine is the cap
    try:
        r.run()
    except EngineError as e:
        if not rec.exhausted:
            raise
    arts = []
    for a in r.structured_artifacts() + [r.raw_artifact()]:
        ik = a["info_kind"]
        out = cli.artifact(wid, "lt", canon(a).encode(), {"info_kind": ik, "claim": a.get("claim")})
        arts.append((out["artifact_id"], ik))
    return r, rec, arts


class Synthesis:
    """A synthesis world: imports artifacts (AVAILABLE), reads them (CONSUMED),
    synthesises, answers. Keeps a read log for the CONSUMED level."""
    def __init__(self, cli, wid):
        self.c, self.w = cli, wid
        self.imported = []      # (src_world, src_aid, new_aid)
        self.read_log = []      # new_aid actually read (F1)
        self.denied = []

    def import_from(self, src_world, aids):
        for aid, ik in aids:
            try:
                r = self.c.import_artifact(self.w, src_world, aid)
                self.imported.append((src_world, aid, r["artifact_id"]))
            except EngineError as e:
                self.denied.append((src_world, aid, ik, e.status))

    def available(self):
        return self.c.knowledge_set(self.w)

    def consume(self):
        arts = []
        for _, _, new in self.imported:
            b = self.c.artifact_bytes(self.w, new); self.read_log.append(new)
            arts.append(json.loads(b))
        return arts

    def answer(self, pub, task, policy="RAW", oracle=None, verify_budget=0):
        arts = self.consume()
        K, used = knowledge_from_artifacts(pub, arts, policy, oracle=oracle, verify_budget=verify_budget)
        return K.answer(task), used
