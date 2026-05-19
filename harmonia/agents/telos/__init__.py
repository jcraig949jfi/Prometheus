"""Telos — stalled-specimen reviver (Harmonia child agent).

Telos patrols `D:\\Prometheus\\harmonia\\memory\\frontier_specimen_state.md`
for live_specimen F-IDs that have stalled past a tier-aging threshold,
proposes the next-leverage audit for each, and never returns a silent
tick. See `daemon.py` for implementation, `CHARTER.md` for the brief.
"""
