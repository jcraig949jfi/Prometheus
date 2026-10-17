"""Write ROBUST01's fixed plans (deterministic; rerunning reproduces the frozen files byte for byte).

    python r01_make_plans.py

Plans are run by REACH01's flight driver (argv[0] is relative to Aether/V2B/REACH01):
    python ../REACH01/reach_flight.py PLAN OUTDIR --jobs 2 --wall-cap S --drain --deadline ISO
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "C:/Prometheus-data/aether_robust01"
REACH01 = os.path.abspath(os.path.join(HERE, "..", "REACH01")).replace(os.sep, "/")
RUN = "../ROBUST01/r01_run.py"


def write(name, plan):
    with open(os.path.join(HERE, name), "w", newline="\n") as f:
        json.dump(plan, f, indent=1)
        f.write("\n")


def main():
    write("plan_s0.json", [
        {"id": "S0_%s" % law, "argv": ["../ROBUST01/r01_stage0.py", "--law", law, "--out", "{out}"],
         "out": "%s/S0/STAGE0_%s.json" % (DATA, law)} for law in ("contest", "fold")])

    search, certify = [], []
    for s in range(40):
        for arm in "CA":
            out = "%s/S1/search/G1_%s_s%d.json" % (DATA, arm, s)
            search.append({"id": "S1_G1_%s_s%d" % (arm, s),
                           "argv": [RUN, "{out}", "R3/r3_frontier.py", "--geom", "G1", "--arm", arm, "--op", "XOR",
                                    "--seed", str(s), "--batches", "20", "--out", "{out}"], "out": out})
            certify.append({"id": "S1_cert_G1_%s_s%d" % (arm, s),
                            "argv": [RUN, "{out}", "R3/r3_certify_run.py", out, "{out}"],
                            "out": out[:-5] + "_cert.json"})
    write("plan_s1_search.json", search)
    write("plan_s1_certify.json", certify)

    s2a = []
    for s in range(8):
        for arm in "NSUP":
            s2a.append({"id": "S2A_%s_s%d" % (arm, s),
                        "argv": [RUN, "{out}", "R4/r4_accum.py", "--arm", arm, "--seed", str(s),
                                 "--component", REACH01 + "/R4/component_planted.json", "--batches", "20",
                                 "--out", "{out}"],
                        "out": "%s/S2A/search/%s_s%d.json" % (DATA, arm, s)})
    write("plan_s2a_search.json", s2a)
    write("plan_s2a_reduce.json", [
        {"id": "S2A_reduce",
         "argv": [RUN, "{out}", "R4/r4_reduce.py", "%s/S2A/search" % DATA, "--rules", REACH01 + "/R4/RULES.json",
                  "--component", REACH01 + "/R4/component_planted.json",
                  "--transplant", "%s/S0/transplant_task1_fold.json" % DATA, "--out", "{out}"],
         "out": "%s/S2A/REDUCTION_S2A.json" % DATA}])


if __name__ == "__main__":
    main()
