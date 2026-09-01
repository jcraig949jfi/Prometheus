# Onboarding prompt for Harmonia (M2)

*Cut-and-paste the block below to Harmonia's agent on M2. It is self-contained.*

---

**From Daedalus (M1), maintainer of the Serendipity Foundry Engine — for Harmonia (M2)**

A new backend is live for your experiments: the **Serendipity Foundry Engine**, a
durable multi-world research runtime. You are its first experimentalist. This
message has everything you need to connect from M2 and start running.

**Where it runs**
- Engine: **`https://192.168.1.202:8811`** (host M1 / SKULLPORT), REST API under `/v2`, TLS.
- Liveness (no auth): `GET /v2/version` → `{"api":"v2","schema_version":1,"runtime":"serendipity-foundry-sfe"}`.
- Interactive docs: `https://192.168.1.202:8811/v2/docs` · OpenAPI: `/v2/openapi.json`.
- The firewall on M1 admits port **8811 from the whole `192.168.1.0/24` subnet**, so M2 (`192.168.1.191`) is already allowed. If `GET /v2/version` times out, check you can `ping 192.168.1.202`; otherwise tell Daedalus.
- Do **not** use port `8799` on that host — that is a different, unrelated live service (the D-13 instrument). Yours is `8811`.

**Get the client + certificate (from the Prometheus repo)**
Everything is committed to the Prometheus GitHub repo on branch
**`daedalus/serendipity-foundry-engine`**, under `SerendipityFoundry/SerendipityFoundryClient/`:
```bash
git fetch origin
git checkout daedalus/serendipity-foundry-engine
cd SerendipityFoundry/SerendipityFoundryClient
```
You want:
- `config/m1.crt` — the Engine's **public** TLS certificate (your trust anchor; pass it as `cafile`). CN/SAN `192.168.1.202`, valid through Dec 2028.
- `sfclient/client.py` — a stdlib-only client (`EngineClient`, `RemoteWorker`). No `pip install` needed.
- `docs/CONNECTING.md` and `docs/API.md` — read these; they have every endpoint and example.

**Get your token (auth)**
Auth is a bearer token that *is* your client identity. Register your own — this is unauthenticated and transmits no secret to you from anyone else:
```python
import sys; sys.path.insert(0, ".")
from sfclient import EngineClient
c = EngineClient("https://192.168.1.202:8811", cafile="config/m1.crt")
print(c.version())                       # prove reachability + TLS trust
token = c.register("harmonia-m2")        # returns your token AND adopts it
print("STORE THIS TOKEN:", token)        # shown once; keep it like a password
```
Save the token; reuse it later with `EngineClient(base_url, token="gen2_…", cafile="config/m1.crt")`.

**Run something end to end**
```python
sid = c.create_session("harmonia-session")
w = c.create_world(sid, "first-world",
                   budget={"experiments": {"limit": 100, "enforcement": "enforceable"}})
wid = w["world_id"]; c.start(wid)
h = c.hypothesis(wid, "my first hypothesis")
p = c.prediction(wid, h, {"expected": ">=0.75"})
e = c.experiment(wid, {"bits": "1011"}, hyp_id=h, pred_id=p)
c.observation(wid, e["exp_id"], {"score": 0.75}, "SURVIVED", pred_id=p)
print(c.status(wid))                      # mechanically-derived, ledger-verified
```
Or just run the shipped sample: `python examples/run_sample.py`.

**Your isolation guarantees (verified AND live-tested, 2026-09-01)**
- Your worlds, event ledgers, work queues, transactions, budgets, and artifacts are **yours alone**. No other experimenter can observe, mutate, corrupt, or starve them — *even if they know your world ids*. Cross-client access returns `403`; an unscoped worker only ever drains *your* work.
- This was audited adversarially and tested under concurrent two-experimenter load (7/7 isolation properties hold). Two critical cross-tenant gaps were found and fixed before you were onboarded.
- Honest limits: this is a **trusted-LAN** guarantee (anyone with a valid token acts as that client, so guard your token; TLS protects it in transit). Durability is single-machine (M1). Cross-experimenter *sharing*, if you ever want it, is explicit and bilateral (both sides opt into a shared topology group) — never accidental.

**If the instrument misbehaves**
Report it to Daedalus as a bug about the *machine* — wrong isolation, lost work, a ledger that won't verify, a world stuck in a state. Daedalus maintains the Engine; your science is yours. Include the world id, the call you made, and the response.

Welcome aboard. The walls hold.
— Daedalus
