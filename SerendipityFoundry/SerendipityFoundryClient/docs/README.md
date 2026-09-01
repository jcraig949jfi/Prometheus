# Serendipity Foundry Client

A thin, dependency-free client for the **Serendipity Foundry Engine** — the
durable multi-world research runtime. This package is *configuration and
documentation for connecting to an Engine*, plus a one-file Python client and
runnable examples. It contains no Engine code; it talks to a running Engine over
its `/v2` REST API.

The Engine currently runs on **M1 / SKULLPORT** at **`https://192.168.1.202:8811`**.

## What's here

```
SerendipityFoundryClient/
├── sfclient/
│   ├── __init__.py            # exports EngineClient, RemoteWorker, EngineError
│   └── client.py             # THE client — standard library only, copy anywhere
├── config/
│   ├── engine.example.json   # connection profile: base_url, cafile, token
│   └── m1.crt                # the Engine's TLS certificate (trust anchor)
├── examples/
│   ├── run_sample.py         # a full sample research session (connect + work)
│   └── run_worker.py         # a standalone remote worker for any machine
├── test_harness/
│   └── harness.py            # exercises EVERY capability against a live Engine
└── docs/
    ├── README.md             # this file
    ├── CONNECTING.md         # IP, port, tokens, keys, certs, firewall — start here
    └── API.md                # every REST endpoint + example calls
```

## 60-second start

From this machine (M1/SKULLPORT), with the Engine running:

```powershell
# 1. prove you can reach the Engine and see its identity
python examples/run_sample.py

# 2. run the full capability harness (registers its own client, drives worlds)
python test_harness/harness.py
```

Both default to `https://192.168.1.202:8811` and the bundled `config/m1.crt`.
`run_sample.py` prints the token it registers — that token *is* your credential;
store it. See **[CONNECTING.md](CONNECTING.md)** for exactly where the Engine
listens, how to get a token, and how the TLS cert is used.

## The client in three lines

```python
from sfclient import EngineClient
c = EngineClient("https://192.168.1.202:8811", cafile="config/m1.crt")
c.register("my-client")                 # → bearer token, adopted automatically
sid = c.create_session("my-session")
world = c.create_world(sid, "world-1")  # a durable, isolated experimental unit
```

`sfclient/client.py` uses only the Python standard library (`http.client`,
`ssl`, `json`). You can copy that single file to any machine and drive the
Engine with a stock Python install — no `pip install` required.

## Concepts (just enough to read the API)

- **Client** — an authenticated identity. Registering one returns a bearer
  token. A client owns everything it creates; no other client can see or touch
  it (isolation is enforced by the Engine, not the client).
- **Session** — a namespace grouping related worlds under a client.
- **World** — the durable experimental unit *and* the isolation boundary. It has
  a lifecycle (`CREATED → RUNNING ⇄ PAUSED → TERMINATED`), a per-world
  hash-chained event ledger, a resource budget, and a sharing policy.
- **Work item** — a unit of compute enqueued on a world. A **RemoteWorker**
  claims it over REST, runs a local executor, heartbeats its lease, and commits
  the result. Workers are disposable and reclaim-safe.
- **Epistemic objects** — hypotheses, predictions, experiments, observations,
  and first-class failures. The Engine enforces honest ordering (a prediction
  cannot be back-dated to "predict" a past observation).

Full walkthrough of connection details in **[CONNECTING.md](CONNECTING.md)**;
full endpoint reference with example calls in **[API.md](API.md)**.
