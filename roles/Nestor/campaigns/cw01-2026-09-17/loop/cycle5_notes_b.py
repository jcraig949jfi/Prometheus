"""Cycle-5 reconciler notes, part B: P-G08 (ruler geometry) and P-G03 (graded persistence)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-R01", "P-G08", "RECONCILER: RULER_DEPENDENT - and the dependence is diagnostic. On the same 122 programs at f .10: the Bernoulli scattered ruler gives NO length effect (slope +.04, band +-.08) and NO set effect (tops vs rest +.01); the two independent scattered variants agree (reached-only: +.02 / -.03; disable-to-NOP: -.03 / -.10, all inside bands). The EXACT-COUNT scattered ruler (round(f n) instructions) reproduces the old coordinates (length slope -.107, tops -.19, both outside bands) exactly as the contiguous window does (-.143, -.178): round(f n)/n is larger for short programs (1/5 = .20 vs 1/10 = .10 vs 2/15 = .13), so any ruler that fixes a COUNT - fixed k, contiguous windows, or rounded fractions - hits short programs harder and manufactures 'length protects' and 'selected tops are robust'. The Bernoulli ruler is corroborated by two geometry-different rulers; the count-fixing rulers are the artefact family.", True,
                      state="ACTIVE", state_reason="the ruler's own geometry is now mapped: fraction-fixing rulers agree, count-fixing rulers disagree")
    L.append_evidence("T-X15", "P-G08", "cross: under three fraction-fixing rulers the length effect and the tops' robustness advantage are absent; under two count-fixing rulers they are present. The T-X15 length coordinate is RULER-GENERATED.", True)
    L.append_evidence("T-ARCH4/M1", "P-G08", "cross: the P-D01 set effect (tops ~.20 more robust) appears only under count-fixing rulers (exact-count -.19, contiguous -.18) and not under Bernoulli (+.01), reached-only (-.03) or disable (-.10, inside band).", True)
    L.append_evidence("T-X15", "P-G03", "RECONCILER (q=1 reproduces evaluate() exactly; harness ok): carried state cannot be reduced without losing function in 112/121 programs - at q=.75 the mean reward falls .71 -> .43 and only 9 programs stay inside the band of their q=1 reward (8 with persist=all, 1 with regs); no program keeps function at q <= .5. Among the 9 programs with an eligible lower dose, scattered-deletion loss is IDENTICAL at q=.75 and q=1 (paired difference 0.000, 9 pairs). The residual correlation between persistent state words and loss at q=1 is weak (Spearman -.13, band [-.12, .17], just outside). Rule reading STATE_CORRELATED; substantive reading STATE_ENTANGLED_WITH_FUNCTION for 92 percent of programs and NO_RESIDUAL_STATE_EFFECT where a function-preserving dose exists. Carried state is not a separable robustness coordinate in this substrate.", True,
                      state="ACTIVE", state_reason="the node splits: length (ruler-generated, retired) and carried state (entangled with function, no residual effect); T-X15 becomes a record of a false coordinate unless subset persistence finds a function-preserving window")
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes B appended")


if __name__ == "__main__":
    main()
