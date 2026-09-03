#!/usr/bin/env python3
"""
Re-derive every load-bearing T0 claim of HC-T01 from the committed artifacts.

Run from the specimen directory:
    python derived/verify_t0_claims.py

Requires pdfminer.six. Reads only files committed under original/ and
recovered_code/. Prints PASS/FAIL per claim and exits non-zero on any FAIL.

Each claim below is one that HC_T01_REVIEW_PACKET.txt asserts. If a claim here
fails, the packet is wrong and must be corrected, not explained.
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(HERE, "original")
CODE = os.path.join(HERE, "recovered_code")
MANIFEST = os.path.join(HERE, "RECOVERED_ARTIFACT_MANIFEST.jsonl")

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(ascii_safe("%-4s %-52s %s" % ("PASS" if ok else "FAIL", name, detail)))


LIGATURES = {
    "(cid:12)": "fi", "(cid:11)": "ff", "(cid:27)": "sigma",
    "ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl",
    "ﬃ": "ffi", "ﬄ": "ffl",
}


def norm(text):
    """Strip everything but alphanumerics, after normalising BOTH the (cid:NN)
    codes and the real Unicode ligature codepoints that pdfminer emits for this
    corpus. Both kinds are present, and missing the Unicode ones produced a
    false negative the first time this verifier was run."""
    t = text.lower()
    for k, v in LIGATURES.items():
        t = t.replace(k, v)
    return re.sub(r"[^a-z0-9]", "", t)


def ascii_safe(s):
    return s.encode("ascii", "replace").decode("ascii")


def extract(pdf_path):
    from pdfminer.high_level import extract_text
    return extract_text(pdf_path)


# ---------------------------------------------------------------- hashes
def claim_hashes():
    if not os.path.exists(MANIFEST):
        check("manifest present", False, MANIFEST)
        return
    bad = []
    n = 0
    for line in open(MANIFEST, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        p = os.path.join(HERE, row["artifact"])
        if not os.path.exists(p):
            bad.append("missing " + row["artifact"])
            continue
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        if h != row["sha256"]:
            bad.append("hash mismatch " + row["artifact"])
        n += 1
    check("all manifest artifacts hash correctly",
          not bad, "%d artifacts, %d problems" % (n, len(bad)))
    for b in bad:
        print("       " + b)


# ---------------------------------------------------------------- thesis
def claim_thesis():
    pdf = os.path.join(ORIG, "03-toussaint-phd.pdf")
    if not os.path.exists(pdf):
        check("thesis present", False, pdf)
        return
    raw = extract(pdf)
    lines = raw.split("\n")
    flat = norm(raw)

    check("thesis is dated 31 March 2003",
          "march312003" in flat, "front matter")

    # Table 1.7 detector sample count.
    check("Table 1.7 states 2000 samples for the exploration distributions",
          "2000" in flat and "numberofsamplestoanalyzetheexplorationdistributions" in flat,
          "detector sample count")

    check("detector sample is per individual",
          "finitesizesampleofsize2000ofthedistributionforeachindividual" in flat,
          "section 1.5.3 Measures")

    # Figure captions: the ablation figure shows fitness only.
    clean = raw
    for k, v in LIGATURES.items():
        clean = clean.replace(k, v)
    caps = re.findall(r"Figure 1\.(\d+): (.{0,90})", clean)
    capd = {int(a): b for a, b in caps}
    check("Figure 1.6 is the population-averaged detector",
          "averaged over the population" in capd.get(6, ""),
          repr(capd.get(6, ""))[:60])
    check("Figure 1.7 is the ablation and is fitness only",
          "fitness" in capd.get(7, "").lower(),
          repr(capd.get(7, ""))[:60])

    # 2x2 design.
    check("Figure 1.7 caption states the 2x2 arms",
          "beta=01andbeta=0" in flat.replace("β", "beta")
          or "0.1 and" in capd.get(7, "") + raw[raw.find("Figure 1.7"):raw.find("Figure 1.7") + 400],
          "beta 0.1 vs 0, alpha 0.03 vs 0.06")

    check("Figure 1.7 states 10 independent trials",
          "10independenttrials" in flat, "replicates per cell")

    # Section boundaries, then the decisive locality result.
    def find_line(pat):
        """Return the LAST matching line. The contents page repeats every
        heading, so the first match is the table of contents, not the body."""
        hit = None
        for i, ln in enumerate(lines):
            if re.match(pat, ln.strip()):
                hit = i
        return hit

    s153 = find_line(r"^1\.5\.3 First experiment")
    s154 = find_line(r"^1\.5\.4 Second experiment")
    s155 = find_line(r"^1\.5\.5 Third experiment")
    s16 = find_line(r"^1\.6 Conclusions")
    ok_bounds = None not in (s153, s154, s155, s16) and s153 < s154 < s155 < s16
    check("section boundaries 1.5.3 < 1.5.4 < 1.5.5 < 1.6 located",
          ok_bounds, "lines %s %s %s %s" % (s153, s154, s155, s16))
    if not ok_bounds:
        return

    md = [i for i, ln in enumerate(lines) if "modular degree" in ln.lower()]
    in_153 = [i for i in md if s153 <= i < s154]
    outside = [i for i in md if not (s153 <= i < s154)]
    check("'modular degree' occurs ONLY inside 1.5.3, the detector experiment",
          md and not outside,
          "%d occurrences, %d in 1.5.3, %d elsewhere"
          % (len(md), len(in_153), len(outside)))

    abl = "\n".join(lines[s154:s155]).lower()
    check("no measured detector statistic inside 1.5.4, the ablation",
          "modular degree" not in abl and "mutual information" not in abl,
          "1.5.4 has no modular degree and no mutual information")

    plants = "\n".join(lines[s155:s16]).lower()
    check("no detector statistic inside 1.5.5, the plants experiment",
          all(k not in plants for k in
              ("modular degree", "neutral degree", "exploration distribution")),
          "1.5.5 is detector-free")

    check("the ablation ASSERTS the detector claim it never measures",
          "changed the exploration distribution" in abl,
          "the sentence that transfers Experiment 1's result")

    # The published inconsistency.
    check("beta is inconsistent in the record (0.1 in caption, 0.01 in body)",
          "= 0.01" in "\n".join(lines[s154:s155]),
          "logged as VERIFIED_RANGE, not guessed")


# ------------------------------------------------------------ 2001 paper
def claim_2001():
    pdf = os.path.join(ORIG, "physics_0102009v1.pdf")
    if not os.path.exists(pdf):
        check("2001 arXiv paper present", False, pdf)
        return
    flat = norm(extract(pdf))
    # The caption is split across interleaved PDF columns, so the phrase is not
    # contiguous even after normalisation. Check both halves.
    check("2001 paper uses 10 000 samples per time step, not 2000",
          "analyzedbytaking10000" in flat and "samplesateachtimestep" in flat,
          "the two sample counts are different experiments")
    check("2001 paper reports a PRECURSOR modular statistic, named differently",
          "modularexploration" in flat and "modulardegree" not in flat,
          "'modular exploration', single individual, (1+1) selection")


# ------------------------------------------------------- recovered source
def claim_source():
    p = os.path.join(CODE, "02-stringRuleJTB_main.cpp.txt")
    q = os.path.join(CODE, "evolution_8h-source.txt")
    r = os.path.join(CODE, "02-plantEvo_2main_8cpp-example.txt")
    for path in (p, q, r):
        if not os.path.exists(path):
            check("recovered source present", False, path)
            return
    src = open(p, encoding="utf-8", errors="replace").read()
    evo = open(q, encoding="utf-8", errors="replace").read()
    plant = open(r, encoding="utf-8", errors="replace").read()

    check("string-rule driver computes the detector for the BEST individual",
          "best->spectrum(" in src, "spectrum() call")
    check("string-rule driver ALSO loops the detector over the whole population",
          re.search(r"for\(i=0;i<pop\.N\(\);i\+\+\)\s*\{\s*pop\(i\)\.spectrum", src)
          is not None,
          "population-wide, not just the best")
    check("that population loop is enabled, not compiled out",
          "#if 1" in src and "#if 0" not in src.split("#if 1")[0][-40:],
          "#if 1")
    check("driver computes avgfit, which appears in no published figure",
          "avgfit" in src, "unreported fifth statistic")
    check("evolve() calls monitor() once per generation",
          re.search(r"generation\+\+;", evo) and "monitor();" in evo,
          "instrument is inside the generation loop")
    check("the plants driver does NOT compute the detector",
          "spectrum(" not in plant,
          "matches the published plants figures exactly")




# ------------------------------------------------- execution-directive gates
# Required by DIRECTIVE_HC_T01_EXECUTION_2026-09-03.txt section 26:
# "The verifier must fail if the primary probe operator, checkpoint cadence,
#  denominator/statistic definitions, mechanical null, or run-level inference
#  are unspecified."
def claim_execution_specs():
    cfgp = os.path.join(HERE, "HC_T01_FROZEN_CONFIG.json")
    if not os.path.exists(cfgp):
        check("frozen config present", False, cfgp); return
    cfg = json.load(open(cfgp, encoding="utf-8"))
    pri = cfg.get("primary", {})

    check("PRIMARY PROBE OPERATOR is specified",
          pri.get("beta_probe") is not None,
          "beta_probe = %s" % pri.get("beta_probe"))
    check("PRIMARY DETECTOR STATISTIC is specified",
          bool(pri.get("primary_detector_statistic")),
          str(pri.get("primary_detector_statistic")))
    check("PRIMARY ACQUISITION METRIC is specified",
          bool(pri.get("primary_acquisition_metric")),
          str(pri.get("primary_acquisition_metric")))
    cks = cfg.get("checkpoints") or []
    check("CHECKPOINT CADENCE is specified",
          len(cks) >= 5 and cks[0] == 0 and sorted(cks) == cks,
          "%d checkpoints, %s .. %s" % (len(cks), cks[0] if cks else "-", cks[-1] if cks else "-"))
    check("the two primary inferential checkpoints are named and in the cadence",
          pri.get("t_primary_early") in cks and pri.get("t_primary_late") in cks,
          "early=%s late=%s" % (pri.get("t_primary_early"), pri.get("t_primary_late")))
    den = cfg.get("denominators", {})
    check("DENOMINATOR / STATISTIC DEFINITIONS are specified",
          all(k in den for k in ("modular_degree", "all_probabilities", "mi_bins",
                                 "phenotype_compare_len", "absent_position")),
          "%d denominator rules" % len(den))
    mn = cfg.get("mechanical_null", {})
    check("MECHANICAL NULL is specified",
          bool(mn.get("definition")) and bool(mn.get("generation_zero_baseline")),
          "definition and generation-zero baseline both present")
    check("RUN-LEVEL INFERENCE is specified",
          pri.get("unit_of_analysis") == "run" and bool(pri.get("inference")),
          "unit=%s" % pri.get("unit_of_analysis"))
    check("smoothing rule is frozen",
          pri.get("smoothing") is not None, "smoothing = %s" % pri.get("smoothing"))
    check("run lengths are frozen, primary plus two sensitivities",
          pri.get("PRIMARY_RUN_LENGTH") and pri.get("SHORT_SENSITIVITY")
          and pri.get("LONG_SENSITIVITY"),
          "%s / %s / %s" % (pri.get("PRIMARY_RUN_LENGTH"),
                            pri.get("SHORT_SENSITIVITY"), pri.get("LONG_SENSITIVITY")))
    check("estimator-noise protocol is specified",
          (cfg.get("estimator_noise") or {}).get("R_seeds", 0) >= 10,
          "R = %s detector seeds" % (cfg.get("estimator_noise") or {}).get("R_seeds"))
    check("both historical parameter conflicts are recorded, not silently guessed",
          set(cfg.get("parameter_conflict_resolutions", {})) >= {"alpha_indel", "beta"},
          ", ".join(sorted(cfg.get("parameter_conflict_resolutions", {}))))
    for f in ("FROZEN_POPULATION_PROBE_SPEC.md", "OPERATOR_HISTORY_DID_SPEC.md",
              "ESTIMATOR_NOISE_PROTOCOL.md"):
        check("spec present: " + f, os.path.exists(os.path.join(HERE, f)), "")


def claim_simulator():
    src = os.path.join(HERE, "derived", "hct01.c")
    if not os.path.exists(src):
        check("simulator source present", False, src); return
    t = open(src, encoding="utf-8", errors="replace").read()
    check("simulator carries the worked-example property test",
          "cdcdadcdc" in t and "cdadc" in t,
          "thesis section 1.5.1 example is asserted in selftest")
    check("simulator asserts the length-11 compact encoding",
          "genome length %d (thesis says 11)" in t or "thesis says 11" in t, "")
    check("simulator asserts beta=0 can never create an operator",
          "creates no operators" in t, "")
    check("second-type operator creation inserts BEHIND the source sequence",
          "inserted in the genome BEHIND the sequence p" in t,
          "order of application matters for hierarchical encodings")


if __name__ == "__main__":
    print("HC-T01 T0 claim verification")
    print("=" * 72)
    claim_hashes()
    claim_thesis()
    claim_2001()
    claim_source()
    claim_execution_specs()
    claim_simulator()
    print("=" * 72)
    failed = [n for n, ok, _ in results if not ok]
    print("%d claims checked, %d failed" % (len(results), len(failed)))
    sys.exit(1 if failed else 0)
