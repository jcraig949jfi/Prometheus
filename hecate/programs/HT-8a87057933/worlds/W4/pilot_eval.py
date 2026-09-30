import json
import sys
import crit

ATTEMPT = int(sys.argv[1]) if len(sys.argv) > 1 else 1
rows = crit.load("pilot_rows.jsonl")
ce = crit.pooled(crit.load("ce_reference_rows.jsonl")["CE_REFERENCE"])
nt = crit.pooled(rows["NULL_TWIN"])
pc = crit.pooled(rows["POSITIVE_CONTROL"])
ch = crit.pooled(rows["CHEAT"])
cpc, cch, cnt = crit.criterion(pc, ce, nt), crit.criterion(ch, ce, nt), crit.criterion(nt, ce, nt)
out = dict(positive_meets_success=cpc["meets_success"], cheat_detected=cch["meets_success"],
           null_twin_meets_success=cnt["meets_success"],
           pilot_pass=bool(cpc["meets_success"] and cch["meets_success"] and not cnt["meets_success"]),
           stats=dict(CE_REFERENCE=ce, POSITIVE_CONTROL=dict(pc, criterion=cpc),
                      CHEAT=dict(ch, criterion=cch), NULL_TWIN=dict(nt, criterion=cnt),
                      null_twin_meets_a_and_b=bool(cnt["a"] and cnt["b"]),
                      note="null twin part (c) is its own reference (ratio 1.0): see NOTES ambiguity 2"),
           attempt=ATTEMPT)
with open("PILOT.json", "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
