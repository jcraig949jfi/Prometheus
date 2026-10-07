"""ROUTE01 reducer: PROP01 per-seed classification (route01_reduce_base, identical rules) + routing verdict.

    python route01_reduce.py UNIT_DIR --rules RULES.json --out REDUCTION.json

Verdict for RT (route1) vs L1 (reaim1) and RN (matched random-aim null), on per-seed medians:
  CONTENT_ROUTING_CAUSAL_REACH  RT >= seeds_min MULTIGENERATION seeds AND RT median ever_sites >= reach_ratio x both
                                L1 and RN AND RT median max_gen > both
  ROUTING_NO_GAIN               RT median ever_sites <= L1 median ever_sites
  ROUTING_RANDOMLIKE            otherwise, if RT median ever_sites is within [1/randomlike_band, randomlike_band] x RN's
                                and RT median max_gen <= RN median max_gen + 1
  CONTENT_ROUTING_WEAK          otherwise
"""
import io, json, os, sys, contextlib, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import route01_reduce_base as B  # noqa: E402

def main():
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("unit_dir"); ap.add_argument("--rules", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    tmp = a.out + ".base.json"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        B.main([a.unit_dir, "--candidate", "RT", "--comparators", "L1,RN", "--rules", a.rules, "--out", tmp])
    base = json.load(open(tmp)); os.remove(tmp)
    R = json.load(open(a.rules)); S = base["summary"]
    rt, l1, rn = S.get("RT"), S.get("L1"), S.get("RN")
    nm = rt["classes"].get("MULTIGENERATION", 0) if rt else 0
    if rt and l1 and rn and nm >= R["seeds_min"] and rt["median_ever_sites"] >= R["reach_ratio"] * max(1, l1["median_ever_sites"]) \
            and rt["median_ever_sites"] >= R["reach_ratio"] * max(1, rn["median_ever_sites"]) \
            and rt["median_max_gen"] > l1["median_max_gen"] and rt["median_max_gen"] > rn["median_max_gen"]:
        v = "CONTENT_ROUTING_CAUSAL_REACH"
    elif rt["median_ever_sites"] <= l1["median_ever_sites"]:
        v = "ROUTING_NO_GAIN"
    elif (rn["median_ever_sites"] / R["randomlike_band"] <= rt["median_ever_sites"] <= rn["median_ever_sites"] * R["randomlike_band"]
          and rt["median_max_gen"] <= rn["median_max_gen"] + 1):
        v = "ROUTING_RANDOMLIKE"
    else:
        v = "CONTENT_ROUTING_WEAK"
    base["routing_verdict"] = v; base["rules_sha256"] = hashlib.sha256(open(a.rules, "rb").read()).hexdigest()
    open(a.out, "w").write(json.dumps(base, indent=1))
    print(buf.getvalue()); print("ROUTING_VERDICT", v)

if __name__ == "__main__":
    main()
