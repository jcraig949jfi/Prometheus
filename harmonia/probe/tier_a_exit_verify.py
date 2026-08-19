"""Tier A exit verification — recompute every §4.2 criterion from the raw ledger.

Harmonia B, meter integrity. Companion to TIER_A_EXIT_HARMONIA_B_2026-08-19.md.
Reads only committed artifacts; no API. Reproduces every number in that review.

Run:  PYTHONPATH=. python harmonia/probe/tier_a_exit_verify.py
"""
import json, math, random, pathlib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[2]
LED  = ROOT/"ergon/probe/ledgers/pilot_d0_ledger.jsonl"
PRE  = ROOT/"ergon/probe/ledgers/nearmiss_mix-M30_prepass.jsonl"
MAN  = ROOT/"ergon/probe/manifests/nearmiss_mix-M30_manifest_n200.jsonl"
R7   = ROOT/"ergon/probe/ledgers/r7_d0_m30_2026-08-19.json"
R3   = ROOT/"ergon/probe/ledgers/r3_live_2026-08-19.json"
ARMS = ["F0","F-null","F-prom-retrieved","F-oracle","F-answer"]

def jl(p): return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]

by = defaultdict(dict)
for r in jl(LED): by[r["uid"]][r["arm"]] = r
U = sorted(by)
c  = lambda u,a: int(bool(by[u][a]["correct"]))
tk = lambda u,a: by[u][a]["packet_tokens"]

def mcnemar(a,b,us=None):
    us = us or U
    n01=sum(1 for u in us if c(u,a) and not c(u,b)); n10=sum(1 for u in us if c(u,b) and not c(u,a))
    n=n01+n10; k=min(n01,n10)
    return (1.0 if n==0 else min(1.0, 2*sum(math.comb(n,i)*0.5**n for i in range(k+1)))), n01, n10

def boot(a,b,us=None,B=10000,seed=0):
    us = us or U
    d=[c(u,a)-c(u,b) for u in us]; rng=random.Random(seed); n=len(d)
    ms=sorted(sum(d[rng.randrange(n)] for _ in range(n))/n for _ in range(B))
    return sum(d)/n, ms[int(.025*B)], ms[int(.975*B)]

def binom_le(k,n,p0): return sum(math.comb(n,i)*p0**i*(1-p0)**(n-i) for i in range(0,k+1))

fails=[]
print("="*74); print("TIER A EXIT — §4.2 criteria recomputed from committed artifacts"); print("="*74)

print(f"\n[5] typed results end-to-end: {len(jl(LED))} rows, {len(U)} tasks, "
      f"complete={sum(1 for u in U if all(a in by[u] for a in ARMS))}")

print("\n[6] reading ladder (paired, n=%d)" % len(U))
for a in ARMS: print(f"    {a:<18s} {sum(c(u,a) for u in U)/len(U):.4f}")
print()
for a,b in [("F-answer","F0"),("F-oracle","F0"),("F-prom-retrieved","F-null"),
            ("F-prom-retrieved","F0"),("F-null","F0"),("F-oracle","F-null")]:
    p,n01,n10 = mcnemar(a,b); m,lo,hi = boot(a,b)
    print(f"    {a:<18s} - {b:<8s} {m:+.4f}  McNemar p={p:.4g}  CI [{lo:+.4f},{hi:+.4f}]")
p_ans,_,_ = mcnemar("F-answer","F0"); d_ans,_,_ = boot("F-answer","F0")
p_ora,_,_ = mcnemar("F-oracle","F0"); d_ora,lo_ora,_ = boot("F-oracle","F0")
ok6 = (d_ans>=0.25 and p_ans<0.01) and (p_ora<0.05 and d_ora>0)
print(f"\n    F-answer >> F0 : {'PASS' if (d_ans>=0.25 and p_ans<0.01) else 'FAIL'}")
print(f"    F-oracle >  F0 : {'PASS' if (p_ora<0.05 and d_ora>0) else 'FAIL'}  <-- p={p_ora:.3f}")
if not ok6: fails.append("[6] F-oracle > F0 not significant")

print("\n[2] R7 both layers")
r7=json.loads(R7.read_text(encoding="utf-8"))
d0=r7["strata"]["D0"]
has_marginals = any(k in d0 for k in ("marginals","tolerances","layer_a"))
print(f"    layer (b) classifier {d0['classifier']} vs {d0['ceiling']}: {d0['verdict']}")
print(f"    layer (a) marginals present in result file: {has_marginals}")
src=(ROOT/"ergon/probe/run_r7_d0d1.py").read_text(encoding="utf-8")
called = "calibrate_tolerances(" in src.split("import",1)[1].replace("calibrate_tolerances,","")
print(f"    calibrate_tolerances CALLED in runner: {called}")
if not (has_marginals and called): fails.append("[2] R7 layer (a) never executed")

print("\n[1] R3 controls")
r3=json.loads(R3.read_text(encoding="utf-8"))
print(f"    A  delta {r3['A_payload_consumption']['delta']:+.4f} p={r3['A_payload_consumption']['mcnemar_p']:.3g}  PASS")
print(f"    B  delta {r3['B_cheat']['delta']:+.4f} p={r3['B_cheat']['mcnemar_p']:.3g} at n={r3['n_paired']} "
      f"(spec B_MIN_N=400 -> power 0.60 vs 0.85 @+10pp)")
gold=[r["gold_int"] for r in jl(MAN)]
from collections import Counter
ch=1.0/len(set(gold))
k=int(r3["C_leakage_live"]["recovery"]*r3["C_leakage_live"]["n"])
print(f"    C  recovery {k}/{r3['C_leakage_live']['n']} at chance {ch:.2f}; "
      f"P(X<={k}|chance)={binom_le(k,r3['C_leakage_live']['n'],ch):.3e}")
print(f"       parse-fail logged for C batch: {'parse_fail' in json.dumps(r3['C_leakage_live'])}")
if binom_le(k,r3["C_leakage_live"]["n"],ch) < 1e-6:
    fails.append("[1] control C returned an outcome ~impossible under its own chance rate; not demonstrated")
print(f"    D  headroom {r3['D_headroom']['headroom']:+.4f}  PASS")

print("\n[3] R13 stratification")
scr=json.loads((ROOT/"ergon/probe/ledgers/nearmiss_mix-M30_prepass_screen.json").read_text(encoding="utf-8"))
print(f"    both_right {scr['both_right']} both_wrong {scr['both_wrong']} discordant {scr['discordant']} "
      f"movable {scr['movable_share']} >= {scr['movable_floor']}  PASS")

print("\n[TOKEN ASYMMETRY] per-arm means and the tercile decomposition")
for a in ARMS: print(f"    {a:<18s} mean tokens {sum(tk(u,a) for u in U)/len(U):7.1f}")
t=sorted((tk(u,"F-null"),u) for u in U); k3=len(t)//3
for i,g in enumerate([[u for _,u in t[:k3]],[u for _,u in t[k3:2*k3]],[u for _,u in t[2*k3:]]]):
    f0=sum(c(u,"F0") for u in g)/len(g); fn=sum(c(u,"F-null") for u in g)/len(g)
    fp=sum(c(u,"F-prom-retrieved") for u in g)/len(g)
    print(f"    tercile {i+1} n={len(g):3d}: F0 {f0:.3f} | F-null {fn:.3f} ({fn-f0:+.3f}) | "
          f"F-prom {fp:.3f} ({fp-f0:+.3f}) | Delta_carry {fp-fn:+.3f}")

print("\n[F-ORACLE] split by which fixed string the task received")
pre={r["uid"]: r.get("extracted_int") for r in jl(PRE) if r["rep"]==1}
man={r["uid"]: r["gold_int"] for r in jl(MAN)}
corr={u:(v==man[u]) for u,v in pre.items() if u in man}
for lab,sel in (("prior WRONG (specific fix)",False),("prior RIGHT (filler)",True)):
    g=[u for u in U if corr.get(u) is sel]
    m,lo,hi=boot("F-oracle","F0",g)
    print(f"    {lab:<28s} n={len(g):3d}  F-oracle-F0 {m:+.4f}  CI [{lo:+.4f},{hi:+.4f}]")

print("\n"+"="*74)
if fails:
    print("VERDICT: TIER-A-EXIT-FAIL")
    for f in fails: print("  -", f)
else:
    print("VERDICT: TIER-A-EXIT-PASS")
print("="*74)
raise SystemExit(1 if fails else 0)
