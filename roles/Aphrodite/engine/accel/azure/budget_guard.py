"""Budget guard for the Azure canary. Refuses (exit 3) if the worst-case cost
exceeds the cap. Worst case = the resource group lives for the full
MAX_MINUTES hard ceiling, billed in WHOLE hours (conservative; Azure bills VMs
per minute), times a safety factor, plus a fixed overhead.

    python budget_guard.py azure.env
"""
import math
import sys
from pathlib import Path


def load(path):
    cfg = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip()
    return cfg


def estimate(cfg):
    hourly = (float(cfg["VM_PRICE_PER_HOUR"]) + float(cfg["DISK_PRICE_PER_HOUR"])
              + float(cfg["IP_PRICE_PER_HOUR"]))
    billed_hours = math.ceil(int(cfg["MAX_MINUTES"]) / 60)
    worst = hourly * billed_hours * float(cfg["SAFETY_FACTOR"]) + float(cfg["FIXED_OVERHEAD_USD"])
    cap = float(cfg["BUDGET_CAP_USD"])
    max_hours = math.floor((cap - float(cfg["FIXED_OVERHEAD_USD"]))
                           / (hourly * float(cfg["SAFETY_FACTOR"])))
    return hourly, billed_hours, worst, cap, max_hours


def main(argv):
    cfg = load(argv[1] if len(argv) > 1 else Path(__file__).with_name("azure.env"))
    hourly, billed, worst, cap, max_hours = estimate(cfg)
    print("[budget] %s @ $%.4f/h all-in; hard ceiling %s min -> billed %d h; "
          "worst case $%.2f (cap $%.2f); max whole hours under cap = %d"
          % (cfg["VM_SIZE"], hourly, cfg["MAX_MINUTES"], billed, worst, cap, max_hours))
    if cap > 3.00:
        print("[budget] REFUSE: cap above the operator's $3 per-provider ceiling")
        return 3
    if worst > cap:
        print("[budget] REFUSE: worst-case estimate exceeds cap")
        return 3
    print("[budget] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
