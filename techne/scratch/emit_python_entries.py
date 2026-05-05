"""Emit new entries as Python source ready to paste into _mahler_data.py."""
import json

with open("F:/Prometheus/techne/scratch/extended_entries.json") as f:
    entries = json.load(f)

# Group by source family for readability
by_family = {}
for e in entries:
    src = e["source"]
    # Family key: anything before the first " x "
    fam = src.split(" x ")[0] if " x " in src else src
    by_family.setdefault(fam, []).append(e)

lines = []
for fam, es in by_family.items():
    lines.append(f"    # ----- {fam} ({len(es)} entries) -----")
    for e in es:
        lines.append("    {")
        lines.append(f"        \"degree\": {e['degree']},")
        lines.append(f"        \"coeffs\": {e['coeffs']},")
        lines.append(f"        \"mahler_measure\": {repr(e['mahler_measure'])},")
        lines.append(f"        \"name\": \"{e['name']}\",")
        lines.append(f"        \"salem_class\": {e['salem_class']},")
        lines.append(f"        \"is_smyth_extremal\": {e['is_smyth_extremal']},")
        lines.append(f"        \"lehmer_witness\": False,")
        lines.append(f"        \"degree_minimum\": {e['degree_minimum']},")
        lines.append(f"        \"source\": \"{e['source']}\",")
        lines.append("    },")
    lines.append("")

with open("F:/Prometheus/techne/scratch/extended_entries.py", "w") as f:
    f.write("\n".join(lines))

print(f"Emitted {len(entries)} entries to extended_entries.py "
      f"({len(lines)} lines)")
