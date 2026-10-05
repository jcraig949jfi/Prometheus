import glob, hashlib, json, os, collections, subprocess, sys
D = r"C:/Prometheus-data/aether/V2B/TEST-3/native"
PIN = r"C:/Prometheus-worktrees/aether-v2b-t3"
def h(r):
    body = json.dumps({k: v for k, v in r.items() if k not in ("wall_seconds", "result_sha256")}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode()).hexdigest()
rows, bad = [], []
for p in sorted(glob.glob(os.path.join(D, "t3_*.json"))):
    r = json.load(open(p, encoding="utf-8"))
    ok = h(r) == r["result_sha256"]
    if not ok: bad.append(p)
    rows.append((os.path.basename(p), r, ok))
print("units", len(rows), "hash_ok", sum(o for _, _, o in rows), "bad", bad)
dup = json.load(open(os.path.join(D, "dup_T3-P1-mob_r1x1e0-won-s4.json"), encoding="utf-8"))
orig = json.load(open(os.path.join(D, "t3_T3-P1-mob_r1x1e0-won-s4.json"), encoding="utf-8"))
print("determinism dup", "MATCH" if dup["result_sha256"] == orig["result_sha256"] else "MISMATCH", orig["result_sha256"])
per = collections.defaultdict(list)
for name, r, _ in rows:
    if r.get("instrument") == "aeth_mobility":
        key = "%s/warmup-%s" % (r["variant"], r.get("warmup_arm", "on"))
        per[key].append(r)
law_class = {}
for k in sorted(per):
    rs = sorted(per[k], key=lambda r: r["seed_index"])
    cs = [r["p1_class"] for r in rs]
    top, n = collections.Counter(cs).most_common(1)[0]
    law_class[k] = top if n >= 3 else "MIXED"
    print("%-26s %-20s %s" % (k, law_class[k], cs))
    for r in rs:
        print("   s%d tl=%.4f rev=%.3f cnt=%.3f act=%.3f chain=%.3f res=%.3f %s" % (r["seed_index"], r["turnover_late"], r["revisit_share"], r["counter_share"], r["active_site_share"], r["chain_share"], r["residue_share"], r["result_sha256"][:12]))
M = "ENDOGENOUSLY_MOBILE"
c = lambda l: law_class.get(l + "/warmup-on")
both = c("mob_r1x1e0") == M and c("mob_r1x1e1") == M
single = [l for l in ("mob_r0x1e0", "mob_r0x1e1", "mob_r1x0e0", "mob_r1x0e1") if c(l) == M]
one = (c("mob_r1x1e0") == M) != (c("mob_r1x1e1") == M)
if single: prim = "MOBILITY_WITHOUT_INTERACTION -> PARTIAL"
elif both: prim = "INTERACTION_MOBILITY_SUPPORTED -> MECHANISM_SUPPORTED"
elif not (c("mob_r1x1e0") == M or c("mob_r1x1e1") == M): prim = "NO_EFFECT"
else: prim = "PARTIAL"
print("PRIMARY:", prim, "single-switch mobile:", single)
q4 = law_class.get("v1/warmup-off")
print("Q4: v1 warm-up OFF =", q4, "->", "SUPPORTED" if q4 == "FROZEN" else "NOT SUPPORTED")
out = subprocess.run([sys.executable, "Aether/observatory/aeth_prov_reduce.py", D], cwd=PIN, capture_output=True, text=True)
red = json.loads(out.stdout)
for k, v in red["laws"].items():
    print("P3 %-12s far=%.3f P4=%.3f P5=%.3f P6=%.3f alive=%.3f n=%d seeds=%s" % (k, v["P3_far"], v["P4_transformed"], v["P5_composed"], v["P6_deep"], v["alive"], v["origins"], v["seeds"]))
json.dump({"law_class": law_class, "primary": prim, "q4": q4, "p3": red, "hash_bad": bad,
           "determinism": dup["result_sha256"] == orig["result_sha256"]},
          open(os.path.join(D, "..", "VERIFY.json"), "w"), indent=1, sort_keys=True)
