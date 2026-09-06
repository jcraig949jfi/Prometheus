"""Rehearse the exact migration M2 would take: schema 4 -> 6, on M2's build.

I have only ever exercised 5 -> 6. M2 runs 0fd24e0f3 / schema 4, so its path is
4 -> 5 -> 6 and it has never been run end to end. This builds a schema-4 ledger
with M2's OWN engine source, populates it with representative data, then opens
it with the v6 build and checks that nothing was lost, nothing was back-filled,
and the pre-existing sessions land as LEGACY rather than silently bound.
"""
import io
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile

WT = ("C:/Users/jcrai/AppData/Local/Temp/claude/F--SerendipityD/"
      "1abf2828-fed8-4e30-a8e2-7e51465690a5/scratchpad/daedwt2")
M2_BUILD = "0fd24e0f3"          # what M2 is running right now
REL = "SerendipityFoundry/SerendipityFoundryEngine"
OK, BAD = [], []


def check(name, cond, detail=""):
    (OK if cond else BAD).append(name)
    print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name,
                           "" if cond else "\n         " + str(detail)))


tmp = tempfile.mkdtemp()
# --- lay down M2's actual engine source -----------------------------------
tar = os.path.join(tmp, "m2.tar")
with open(tar, "wb") as fh:
    fh.write(subprocess.run(
        ["git", "archive", M2_BUILD, REL + "/sfe"],
        cwd=WT, capture_output=True).stdout)
subprocess.run(["tar", "-xf", tar, "-C", tmp], capture_output=True)
m2eng = os.path.join(tmp, REL.replace("/", os.sep))
db = os.path.join(tmp, "m2sim.db")

build = os.path.join(tmp, "build_v4.py")
io.open(build, "w", encoding="utf-8", newline="\n").write("""
import sys, json
sys.path.insert(0, %r)
from sfe.store import SCHEMA_VERSION
from sfe.runtime import Foundry
print("   M2 build SCHEMA_VERSION =", SCHEMA_VERSION)
f = Foundry(%r)
c = f.create_client("m2-sim")
s = f.create_session(c, "pre-affinity-session")
out = {"client": c, "session": s, "worlds": [], "exps": [], "obs": [], "work": []}
for i in range(3):
    w = f.create_world(s, "w%%d" %% i)["world_id"]
    f.start_world(w, c)
    out["worlds"].append(w)
    h = f.propose_hypothesis(w, "h%%d" %% i, client_id=c)
    hid = h["hyp_id"] if isinstance(h, dict) else h
    e = f.create_experiment(w, {"arm": i}, client_id=c, hyp_id=hid, enqueue=True)
    out["exps"].append(e["exp_id"]); out["work"].append(e["work_id"])
    o = f.record_observation(w, e["exp_id"], {"v": i}, "SURVIVED", client_id=c)
    out["obs"].append(o["obs_id"] if isinstance(o, dict) else o)
    f.create_artifact(w, "blob", b"payload-%%d" %% i, client_id=c)
f.close()
print(json.dumps(out))
""" % (m2eng, db))
r = subprocess.run([sys.executable, build], capture_output=True, text=True,
                   cwd=m2eng)
if r.returncode != 0:
    print(r.stdout)
    print(r.stderr[-2500:])
    sys.exit("could not build a schema-4 ledger with M2's source")
lines = [l for l in r.stdout.strip().split("\n") if l.strip()]
print(lines[0])
seed = json.loads(lines[-1])

cx = sqlite3.connect(db)
before = {t: cx.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0]
          for t in ("worlds", "events", "experiments", "observations",
                    "artifacts", "work_items", "sessions", "hypotheses")}
v4 = cx.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0]
head_before = cx.execute(
    "SELECT world_id, head_hash, next_index FROM worlds ORDER BY world_id"
).fetchall()
cx.close()
print("   built schema-%s ledger: %s" % (v4, before))
print()

shutil.copy(db, db + ".preupgrade")

# --- now open it with the v6 build ----------------------------------------
print("MIGRATION 4 -> 6 USING THE v6 BUILD")
up = os.path.join(tmp, "upgrade.py")
io.open(up, "w", encoding="utf-8", newline="\n").write("""
import sys
sys.path.insert(0, %r)
from sfe.store import SCHEMA_VERSION
from sfe.runtime import Foundry
print("   v6 build SCHEMA_VERSION =", SCHEMA_VERSION)
f = Foundry(%r)
print("   engine_instance_id minted:", f.engine_instance_id())
f.close()
""" % (os.path.join(WT, REL), db))
r = subprocess.run([sys.executable, up], capture_output=True, text=True,
                   cwd=os.path.join(WT, REL))
print(r.stdout.rstrip() or r.stderr[-1500:])
check("migration 4 -> 6 completes without error", r.returncode == 0,
      r.stderr[-600:])
print()

cx = sqlite3.connect(db)
after = {t: cx.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0]
         for t in before}
v6 = cx.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0]

check("schema_version is now 6", v6 == "6", v6)
check("no scientific row was lost or added", after == before,
      "before=%s\n         after =%s" % (before, after))
head_after = cx.execute(
    "SELECT world_id, head_hash, next_index FROM worlds ORDER BY world_id"
).fetchall()
check("every world's head_hash and index are untouched",
      head_after == head_before)

new_tables = {r[0] for r in cx.execute(
    "SELECT name FROM sqlite_master WHERE type='table'")}
check("v6 containers created", {"families", "family_members", "claims"}
      <= new_tables)
check("v6 containers are EMPTY (nothing invented)",
      all(cx.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0] == 0
          for t in ("families", "family_members", "claims")))

att = cx.execute("SELECT COUNT(*) FROM work_items WHERE "
                 "executed_config_hash IS NOT NULL OR entry_state_hash IS NOT "
                 "NULL OR player_identity_hash IS NOT NULL OR "
                 "measurement_identity_hash IS NOT NULL").fetchone()[0]
check("NO attestation was back-filled", att == 0, "%d rows attested" % att)
ana = cx.execute("SELECT COUNT(*) FROM experiments WHERE source_set_hash "
                 "IS NOT NULL").fetchone()[0]
check("NO analysis was back-filled", ana == 0)

# the v5 session-affinity migration is the interesting one for M2
cols = {r[1] for r in cx.execute("PRAGMA table_info(sessions)")}
check("v5 session columns present", {"key_hash", "engine_instance_id",
                                     "affinity_mode"} <= cols, sorted(cols))
rows = cx.execute("SELECT affinity_mode, key_hash, engine_instance_id "
                  "FROM sessions").fetchall()
check("pre-existing sessions land as LEGACY with NO binding",
      all(r[0] == "LEGACY" and r[1] is None and r[2] is None for r in rows),
      rows)
eid = cx.execute("SELECT value FROM meta WHERE key='engine_instance_id'"
                 ).fetchone()
check("M2 would mint its OWN engine_instance_id", eid is not None
      and eid[0].startswith("eng_")
      and eid[0] != "eng_8a37a5d305969034d488c43e",
      eid[0] if eid else None)
cx.close()

# --- and the rollback direction -------------------------------------------
print()
print("ROLLBACK: can M2's CURRENT build reopen the migrated ledger?")
rb = os.path.join(tmp, "rollback.py")
io.open(rb, "w", encoding="utf-8", newline="\n").write("""
import sys
sys.path.insert(0, %r)
from sfe.store import Store
try:
    Store(%r).initialize()
    print("   OPENED IT")
except Exception as e:
    print("   REFUSED:", str(e)[:110])
""" % (m2eng, db))
r = subprocess.run([sys.executable, rb], capture_output=True, text=True,
                   cwd=m2eng)
print(r.stdout.rstrip())
check("a code-only rollback is REFUSED, loudly", "REFUSED" in r.stdout,
      r.stdout)

print()
print("%d passed, %d failed" % (len(OK), len(BAD)))
if BAD:
    print("FAILED:", BAD)
sys.exit(1 if BAD else 0)
