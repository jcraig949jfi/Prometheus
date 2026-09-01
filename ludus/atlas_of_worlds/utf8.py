"""Force UTF-8 on stdout/stderr. Windows consoles default to cp1252, which
cannot encode most of this atlas (Senet, mahjong, pachisi, weiqi, ...)."""
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
