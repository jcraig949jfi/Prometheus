"""Class (h): world-run records without genome bytes.

Incident (W2-34): no C-A3 run saved genomes or registers -- every runaway/takeover record stores tag counts or
frequencies, never bytes. Five Wave-2 questions were blocked by it (C-CORE 34/49, H1 re-score, run 52, 0008, W2-17
morph genotypes). Recommendation: store final and periodic genome bytes plus registers (256 x 64 B per checkpoint).

``check_stores_genomes(records, genome_len=None)``: walks every JSON value AND key of each record for genome bytes:
a hex string of exactly 2*L hex digits (L = `genome_len`, or any L in 16..512 when None), a list of >= 16 ints in
0..255 under a key that names bytes/genome, or a key named genome/genomes/implant_hex. Registers are recognised as
a list of 8 ints under a key named regs/registers.

Verdicts
    NO_GENOMES        no record carries genome bytes (the instrument gap)
    NO_REGISTERS      genomes stored but no registers, when `require_registers` (carried-register worlds)
    OK                genome bytes found (details: where, and whether registers were found)
    NOT_VERIFIED      no records, or none could be parsed
"""
from __future__ import annotations

import gzip
import json
import pathlib
import re
from typing import Any, Dict, Iterable, List, Optional

from . import CheckResult, NOT_VERIFIED, OK

NAME = "stores_genomes"
HEX = re.compile(r"^[0-9a-fA-F]+$")
GENOME_KEYS = re.compile(r"^(genome|genomes|genome_hex|implant_hex|g_hex|final_genome|dg|bytes_hex)$")
REG_KEYS = re.compile(r"^(regs|registers|reg_state)$")


def _is_genome_hex(s: str, L: Optional[int]) -> bool:
    if not HEX.match(s) or len(s) % 2:
        return False
    n = len(s) // 2
    if isinstance(L, (tuple, list, set, frozenset)):
        return n in L
    return n == L if L else 16 <= n <= 512


def _walk(x: Any, path: str, L: Optional[int], hits: List[str], regs: List[str], depth=0):
    if depth > 12:
        return
    if isinstance(x, dict):
        for k, v in x.items():
            ks = str(k)
            if _is_genome_hex(ks, L) and len(hits) < 200:
                hits.append(path + "/<key>")
            if GENOME_KEYS.match(ks) and v:
                hits.append(path + "/" + ks)
            if REG_KEYS.match(ks) and isinstance(v, list) and len(v) == 8:
                regs.append(path + "/" + ks)
            _walk(v, path + "/" + ks, L, hits, regs, depth + 1)
    elif isinstance(x, list):
        for i, v in enumerate(x[:64]):
            _walk(v, path + "[%d]" % i, L, hits, regs, depth + 1)
    elif isinstance(x, str):
        if _is_genome_hex(x, L):
            hits.append(path)


def load_records(paths: Iterable[pathlib.Path], limit: int = 40) -> List[Any]:
    out = []
    for p in list(paths)[:limit]:
        p = pathlib.Path(p)
        try:
            if p.suffix == ".gz":
                out.append(json.load(gzip.open(p, "rt")))
            elif p.suffix == ".jsonl":
                out.append([json.loads(l) for l in p.read_text().splitlines()[:200] if l.strip()])
            else:
                out.append(json.loads(p.read_text()))
        except (OSError, ValueError):
            continue
    return out


def check_stores_genomes(records: List[Any], genome_len: Optional[int] = None,
                         require_registers: bool = False) -> CheckResult:
    if not records:
        return CheckResult(NAME, NOT_VERIFIED, "no parseable records")
    hits: List[str] = []
    regs: List[str] = []
    for i, r in enumerate(records):
        _walk(r, "rec%d" % i, genome_len, hits, regs)
    details = {"n_records": len(records), "genome_sites": hits[:10], "n_genome_sites": len(hits),
               "register_sites": regs[:5], "n_register_sites": len(regs)}
    if not hits:
        return CheckResult(NAME, "NO_GENOMES",
                           "%d records carry no genome bytes: any later question about which bytes did it is blocked "
                           "(W2-34); store final + periodic genomes and registers" % len(records), details)
    if require_registers and not regs:
        return CheckResult(NAME, "NO_REGISTERS", "genomes stored but no registers, in a carried-register world", details)
    return CheckResult(NAME, OK, "genome bytes stored (%d sites)%s" % (len(hits), "" if regs else "; registers absent"),
                       details)
