"""RB-2: does the full T4 score of the WITNESS artifact (Q3 under T4) agree
with the census-side family_profile verdict? Seeded sample of 80 draws
(40 profile-admissible, 40 profile-rejected, widened inits). Forensic."""
import json, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rb2_common as C
C.worker_init()
rows = json.loads((C.HERE / "RB2_CENSUS_ROWS.json").read_text())["rows"]
rng = random.Random(C.SEED_LABEL + "/q3check")
adm = [r for r in rows if r["profile_WIDE"]["admissible"]]
rej = [r for r in rows if not r["profile_WIDE"]["admissible"]]
pick = rng.sample(adm, 40) + rng.sample(rej, 40)
agree, dis = 0, []
for k, r in enumerate(pick):
    name = C.letter_name("rbq", [k, r["body"]])
    prov = C.a17.Prov({name: (r["body"], r["final"], r["init_WIDE"])})
    q = C.t4_qualifies(prov, name, ("fold", r["init_WIDE"], r["body"], r["final"]))
    if q == r["profile_WIDE"]["admissible"]:
        agree += 1
    else:
        dis.append([r["init_WIDE"], r["body"], r["final"], r["profile_WIDE"]["admissible"], q])
out = {"n": len(pick), "agree": agree, "disagreements": dis}
(C.HERE / "RB2_T4_Q3CHECK.json").write_text(json.dumps(out, indent=1))
print(out)
