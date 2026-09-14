"""Batch 12 of the fossil harvest (2026-09-13): RAID THE LOST WORLDS -- pre-1970 bodies.

Three consecutive batches deferred pre-1970 acquisition. This one starts there.

A specimen's date is the date of the BODY, never of the idea. Every record below states which of
the charter's five body types it is, and the world it expected. Where a directory name and the
artifact disagree about a date, the ARTIFACT wins -- see cosell-eliza-bbn-lisp-1969, whose folder
is labelled 1966 while the file inside is named (and is) 1969/1972.
"""
from __future__ import annotations

from .. import record

S = []
EG = "https://raw.githubusercontent.com/jeffshrager/elizagen.org/master"


def spec(sid, **kw):
    S.append(record.skeleton(sid, **kw))


def url(u, fn):
    return {"kind": "url", "url": u, "filename": fn, "extract": False}


# ===================== 1962: Spacewar! -- a game, and an extinct machine ======================
spec("spacewar-pdp1-1962",
    canonical_name="Spacewar! 2B (25 March 1962) -- Steve Russell et al., MIT, for the DEC PDP-1",
    aliases=["Spacewar", "spacewar 2b"],
    lineage="Written in 1961-62 by Steve Russell, Martin Graetz, Wayne Wiitanen and others on MIT's PDP-1, with the starfield (Expensive Planetarium) by Peter Samson and gravity by Dan Edwards. Two ships under player control orbit a central star; thrust, rotation, torpedoes and hyperspace are computed in real time on an 18-bit machine with 4096 words of core and a Type 30 point-plotting CRT. Widely held to be the first widely distributed digital video game. The body preserved here is the AUTHENTIC 25 Mar 1962 assembly listing, not the later reconstructed-from-binary variant, which masswerk publishes separately.",
    domain=["games", "real-time", "simulation", "graphics", "interactive", "pre1970"],
    era="1962 (body: assembly source dated 25 Mar 1962)",
    version="spacewar 2b, 25 Mar 1962 (authentic source, as published by masswerk.at)",
    source_origin={"artifacts": [url("https://www.masswerk.at/spacewar/sources/spacewar_2b_25mar62.txt",
                                     "spacewar_2b_25mar62.txt")]},
    source_type="HISTORICAL_ARCHIVE_MIRROR",
    source_identity={"archive": "masswerk.at/spacewar/sources", "note": "the 25 Mar 1962 listing, "
                     "distinguished by the archive itself from the 2 Apr 62 binary reconstruction"},
    license={"spdx": "NOASSERTION", "status": "historical artifact; Spacewar was distributed freely by its authors",
             "evidence": "masswerk.at source archive; the authors placed it in the public domain by practice"},
    language=["PDP-1 macro assembly"], build_system="PDP-1 assembler (macro)",
    compiler_or_interpreter="none preserved in-vault; requires a PDP-1 assembler",
    dependencies=["a DEC PDP-1 with Type 30 CRT, or an emulator of one"],
    entry_points=["the assembled tape is loaded and started from the PDP-1 console"],
    example={"command": "assemble and run under a PDP-1 simulator with a Type 30 display",
             "input": "console test-word switches select options; two players use control boxes",
             "output": "two ships orbiting a gravitating star on a point-plotting CRT"},
    environment={"machine": "DEC PDP-1", "word_size": "18-bit", "number_representation": "one's complement",
                 "memory": "4096 words of core (typical)", "character_set": "FIODEC / concise code",
                 "os": "none -- the program owns the machine", "display": "Type 30 point-plotting CRT",
                 "storage": "paper tape", "runner": "none yet"},
    upstream_docs=["Graetz, The Origin of Spacewar, Creative Computing 1981",
                   "Computer History Museum PDP-1 restoration project documentation"],
    human_capability_summary={"built_to": "demonstrate what an interactive computer with a CRT could do, by making two human-controlled ships duel under real gravity in real time",
                              "pressure": "18-bit words, 4096 words of core, no floating point, no operating system, and a display that must be refreshed by the program itself while the game logic runs",
                              "success_means": "the simulation stays responsive and the orbits remain believable within the machine's cycle budget"},
    known_human_problem_solved="real-time interactive simulation on a machine with no OS and no spare cycles",
    human_environmental_pressure="scarce core, scarce cycles, program-refreshed display, no floating point",
    human_failure_condition="the display flickers or the game slows as object count rises; integer overflow distorts the orbits",
    behavioral_entry_point="vary the gravity constant and torpedo parameters and watch orbital stability; the computation budget is the real constraint",
    acquisition_tags=["batch12", "pre1970", "original_body", "games", "extinct_world", "outside_queue"],
    historical_disposition={
        "state": "HISTORICAL_ONLY", "failure_reasons": [],
        "superseded_by": "", "rival_of": "",
        "evidence": [{"kind": "retrospective", "ref": "Graetz, The Origin of Spacewar, Creative Computing 1981",
                      "says": "Describes Spacewar's creation on the PDP-1 at MIT and its spread to other PDP-1 "
                              "installations; the program is tied to that machine and its display."},
                     {"kind": "project_documentation", "ref": "Computer History Museum PDP-1 restoration",
                      "says": "Spacewar is demonstrated on a restored PDP-1 because the machine it requires is "
                              "no longer in ordinary existence; roughly 53 PDP-1s were built."}],
        "audit_note": "HISTORICAL_ONLY refers to the WORLD, not to a defeat: Spacewar was not out-competed, "
                      "its machine simply ceased to exist. Old is not loser; this is recorded as extinction "
                      "of an environment."},
    lineage_relations=[{"relation": "inspired_by", "to": "Bob Wyatt / E. E. Smith Lensman space opera (per Graetz)", "note": ""}])

# ===================== 1965: ELIZA, the actual body ==========================================
spec("eliza-weizenbaum-mad-slip-1965",
    canonical_name="ELIZA (1965) -- Joseph Weizenbaum's ORIGINAL MAD-SLIP implementation for CTSS on the IBM 7094",
    aliases=["ELIZA original", "MAD-SLIP ELIZA", "DOCTOR"],
    lineage="The actual program behind the 1966 CACM paper, lost for over fifty years and located by Jeff Shrager in the MIT archives in 2021 in a folder labelled COMPUTER CONVERSATIONS (1965). Written in MAD (Michigan Algorithm Decoder) using Weizenbaum's own SLIP list-processing library, running under CTSS on the IBM 7094. This is the ANCESTOR of the vault's eliza-anthay-1966, which is a modern faithful reconstruction of the same program -- so the vault now holds the original and a reconstruction of it, which can be compared.",
    domain=["conversational-ai", "natural-language", "pattern-matching", "early-ai", "list-processing", "pre1970"],
    era="1965 (body: the archival listing, folder-dated 1965; the CACM paper is 1966)",
    version="MAD-SLIP transcription + the CACM script, as released CC0 via elizagen.org",
    source_origin={"artifacts": [
        url(EG + "/1965_Weizenbaum_MAD-SLIP/MAD-SLIP_transcription.txt", "MAD-SLIP_transcription.txt"),
        url(EG + "/1965_Weizenbaum_MAD-SLIP/MAD-SLIP_translation.txt", "MAD-SLIP_translation.txt"),
        url(EG + "/1965_Weizenbaum_MAD-SLIP/1966_01_CACM_article_Eliza_script.txt", "CACM_1966_eliza_script.txt"),
        url(EG + "/1965_Weizenbaum_MAD-SLIP/ELIZA_transcription_annotated_20220216.txt", "ELIZA_transcription_annotated.txt")]},
    source_type="HISTORICAL_ARCHIVE_MIRROR",
    source_identity={"archive": "elizagen.org (Jeff Shrager), 1965_Weizenbaum_MAD-SLIP",
                     "note": "verbatim transcription of the archival listing; the photographic scan of the "
                             "original pages is published alongside it and is the primary evidence"},
    license={"spdx": "CC0-1.0", "status": "public-domain dedication",
             "evidence": "ORIGINAL_ELIZA_IN_MAD_SLIP_CC0_For_Resease in the elizagen repository"},
    language=["MAD (Michigan Algorithm Decoder)", "SLIP"],
    build_system="MAD compiler under CTSS", compiler_or_interpreter="none preserved in-vault; requires MAD + SLIP on CTSS",
    dependencies=["CTSS on an IBM 7094", "the SLIP list-processing library", "a MAD compiler"],
    entry_points=["the ELIZA driver reads a script (the DOCTOR script) and then user lines from the console"],
    example={"command": "run under CTSS with the DOCTOR script loaded",
             "input": "a typed English sentence", "output": "a transformed reply built by decomposition/reassembly rules"},
    environment={"machine": "IBM 7094", "word_size": "36-bit", "number_representation": "one's complement",
                 "character_set": "BCD (6-bit)", "os": "CTSS", "compiler": "MAD + SLIP",
                 "storage": "tape and disk under CTSS", "input_format": "console typewriter",
                 "runner": "none yet"},
    upstream_docs=["Weizenbaum, ELIZA, CACM 9(1) 1966",
                   "Weizenbaum, Symmetric List Processor (SLIP), CACM 1963",
                   "Shrager et al., ELIZA Reinterpreted (the archival recovery)"],
    human_capability_summary={"built_to": "study man-machine conversation by transforming the user's own sentences through a replaceable script of keyword rules",
                              "pressure": "a 36-bit batch/timesharing machine with a 6-bit character set, no string type, and list structure that had to be built by hand in SLIP",
                              "success_means": "the scripted transformation produces the documented dialogue; the SCRIPT, not the program, carries the personality"},
    known_human_problem_solved="scripted natural-language dialogue",
    human_environmental_pressure="no native string handling; list processing hand-built; a 6-bit character set; CTSS time limits",
    human_failure_condition="a turn matching no keyword falls through to a canned deflection; the illusion is only as wide as the script",
    behavioral_entry_point="compare the original MAD rule set against the reconstruction's behaviour on the CACM dialogue",
    acquisition_tags=["batch12", "pre1970", "original_body", "early_ai", "extinct_world", "ancestor_of_vault_fossil"],
    historical_disposition={
        "state": "HISTORICAL_ONLY", "failure_reasons": [],
        "superseded_by": "", "rival_of": "cosell-eliza-bbn-lisp-1969",
        "evidence": [{"kind": "archived_technical_discussion", "ref": "elizagen.org recovery record (Shrager, 2021)",
                      "says": "The original ELIZA source was missing for decades and was located in the MIT "
                              "archives in 2021; it had not been runnable in its own environment in the interim."},
                     {"kind": "original_paper", "ref": "Weizenbaum, CACM 9(1), 1966",
                      "says": "Describes ELIZA as running under CTSS on the IBM 7094 and written in MAD-SLIP."}],
        "audit_note": "HISTORICAL_ONLY is a statement about the WORLD (CTSS/7094/MAD/SLIP are all gone), not a "
                      "claim that ELIZA was defeated. No supersession evidence is asserted."},
    lineage_relations=[{"relation": "historical_version_of", "to": "eliza-anthay-1966",
                        "note": "the vault's eliza-anthay-1966 is a modern FAITHFUL reconstruction of THIS body; "
                                "original and reconstruction are now both held"},
                       {"relation": "shares_ancestor_with", "to": "cosell-eliza-bbn-lisp-1969",
                        "note": "independent reimplementation in a different language and world"}])

# ===================== 1969: Cosell's independent ELIZA in BBN-LISP ===========================
spec("cosell-eliza-bbn-lisp-1969",
    canonical_name="ELIZA in BBN-LISP (1969, revised 1972) -- Bernie Cosell's independent implementation at BBN",
    aliases=["Cosell ELIZA", "BBN-LISP ELIZA"],
    lineage="Bernie Cosell wrote an ELIZA independently at BBN in LISP, having read the CACM description rather than the code. A SECOND, independent organism solving the same problem in a different language and a different world -- BBN-LISP on a PDP-10 rather than MAD-SLIP on a 7094 under CTSS. Its behaviour and structure are therefore an independent answer to the same pressure, not a port.",
    domain=["conversational-ai", "natural-language", "pattern-matching", "early-ai", "lisp", "pre1970"],
    era="1969 (body: the file is dated 1969 and 1972 by its own name and content)",
    version="coselleliza1969and1972.lisp, as released via elizagen.org",
    source_origin={"artifacts": [
        url(EG + "/1966_Cosell_BBNLISP/coselleliza1969and1972.lisp", "coselleliza1969and1972.lisp"),
        url(EG + "/1966_Cosell_BBNLISP/coselleliza1969and1972.transcript", "coselleliza1969and1972.transcript")]},
    source_type="HISTORICAL_ARCHIVE_MIRROR",
    source_identity={"archive": "elizagen.org, 1966_Cosell_BBNLISP",
                     "date_discrepancy": "the DIRECTORY is labelled 1966; the FILE is named and dated 1969 and "
                                         "1972. The artifact wins: this record is dated 1969, not 1966."},
    license={"spdx": "CC-BY-like", "status": "released by the author via elizagen",
             "evidence": "ElizaLispCCLicense notice in the elizagen directory"},
    language=["BBN-LISP"], build_system="BBN-LISP interpreter",
    compiler_or_interpreter="none preserved in-vault; requires BBN-LISP (later Interlisp) on a PDP-10",
    dependencies=["BBN-LISP on a DEC PDP-10 / TENEX"],
    entry_points=["the LISP functions are loaded into BBN-LISP and driven from the REPL"],
    example={"command": "load into a BBN-LISP and call the top-level function",
             "input": "a typed English sentence", "output": "an ELIZA-style reply; a session transcript ships beside the source"},
    environment={"machine": "DEC PDP-10", "word_size": "36-bit", "number_representation": "two's complement",
                 "character_set": "ASCII/SIXBIT", "os": "TENEX (BBN)", "interpreter": "BBN-LISP",
                 "storage": "disk", "runner": "none yet"},
    upstream_docs=["Weizenbaum, ELIZA, CACM 9(1) 1966 (the description Cosell worked from)",
                   "elizagen.org Cosell materials and session transcript"],
    human_capability_summary={"built_to": "reproduce the conversational behaviour described in the CACM paper, from the description alone, in LISP",
                              "pressure": "the same illusion must be produced with list structure and no access to the original code",
                              "success_means": "a session transcript that behaves like the published dialogues"},
    known_human_problem_solved="scripted natural-language dialogue, reached independently",
    human_environmental_pressure="reconstructing behaviour from a paper rather than from source; a different machine and language",
    human_failure_condition="same class: unmatched input falls through to deflection",
    behavioral_entry_point="the shipped transcript is a behavioural record; compare its replies against the MAD-SLIP original on the same inputs",
    acquisition_tags=["batch12", "pre1970", "original_body", "early_ai", "independent_reimplementation", "extinct_world"],
    historical_disposition={
        "state": "HISTORICAL_ONLY", "failure_reasons": [],
        "superseded_by": "", "rival_of": "eliza-weizenbaum-mad-slip-1965",
        "evidence": [{"kind": "archived_technical_discussion", "ref": "elizagen.org Cosell materials",
                      "says": "Cosell's BBN-LISP ELIZA is published with its own session transcript and author "
                              "attribution; BBN-LISP and the PDP-10/TENEX world it ran in are no longer in use."}],
        "audit_note": "HISTORICAL_ONLY describes the extinct world. No claim is made that this implementation "
                      "lost to Weizenbaum's; they are independent answers, and which was 'better' is not "
                      "established by any evidence I hold."},
    lineage_relations=[{"relation": "reimplementation_of", "to": "eliza-weizenbaum-mad-slip-1965",
                        "note": "independent, from the published description rather than from the code"}])


# ===================== 1962: LISP 1.5 -- the winner whose rival left no body ==================
spec("lisp-1-5-ibm7090-1962",
    canonical_name="LISP 1.5 (1962) -- the IBM 7090 implementation, machine-readable transcription of the original assembly",
    aliases=["LISP 1.5", "lisp15"],
    lineage="McCarthy's LISP as implemented for the IBM 7090 by Hart, Levin and the MIT group, distributed with the 1962 LISP 1.5 Programmer's Manual. The body here is a machine-readable transcription of the original 7090 assembly listing (lisp15.asm, ~500 KB) together with the LISP-level sources. LISP is the branch that SURVIVED the early list-processing competition; its principal rival IPL-V (Newell, Shaw and Simon at RAND, from 1956) survives in this search only as scanned manuals, with no machine-readable body found -- an asymmetry that is itself evidence about what gets preserved.",
    domain=["programming-language", "interpreter", "list-processing", "symbolic", "early-ai", "garbage-collection", "pre1970"],
    era="1962 (body: transcription of the original 7090 assembly sources)",
    version="informatimago/lisp-1-5 machine-readable transcription of the 1962 sources",
    source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/informatimago/lisp-1-5", "commit": "HEAD"}]},
    source_type="HISTORICAL_ARCHIVE_MIRROR",
    source_identity={"repo": "github.com/informatimago/lisp-1-5",
                     "note": "Bourguignon's machine-readable transcription of the original LISP 1.5 sources; "
                             "the scanned assembly listing is included alongside as primary evidence"},
    license={"spdx": "NOASSERTION", "status": "historical transcription; see repository",
             "evidence": "repository ANNOUNCE/README"},
    language=["IBM 7090 assembly (FAP)", "LISP"], build_system="asm7090 (the repo ships a Makefile and assembler patch)",
    compiler_or_interpreter="none preserved in-vault; requires a 7090 assembler and machine/emulator",
    dependencies=["an IBM 7090/7094 or an emulator of one", "a 7090 assembler"],
    entry_points=["the assembled LISP 1.5 system reads S-expressions from cards"],
    example={"command": "assemble lisp15.asm for a 7090 and load the resulting system",
             "input": "S-expressions on punched cards", "output": "evaluated S-expressions"},
    environment={"machine": "IBM 7090/7094", "word_size": "36-bit", "number_representation": "one's complement",
                 "character_set": "BCD (6-bit)", "os": "batch monitor (FMS/IBSYS)", "assembler": "FAP-style",
                 "storage": "cards and tape", "input_format": "punched cards", "runner": "none yet"},
    upstream_docs=["McCarthy et al., LISP 1.5 Programmer's Manual, MIT Press 1962",
                   "Bobrow & Raphael, A comparison of list-processing computer languages (COMIT, IPL-V, LISP 1.5, SLIP), CACM 7(4) 1964"],
    human_capability_summary={"built_to": "evaluate symbolic expressions -- programs as data -- on a machine designed for numeric work, with automatic storage reclamation",
                              "pressure": "36-bit words, a 6-bit character set, no dynamic memory from the operating system, and symbolic structures whose lifetime the programmer could not track by hand",
                              "success_means": "eval computes the value of an S-expression and the garbage collector reclaims cells without the programmer's help"},
    known_human_problem_solved="symbolic computation and automatic storage management",
    human_environmental_pressure="fixed core, no OS memory management, numeric-oriented hardware",
    human_failure_condition="the free list exhausts and the collector cannot recover enough cells",
    behavioral_entry_point="the garbage collector and the eval/apply core are separable; cons-cell pressure is the natural perturbation",
    acquisition_tags=["batch12", "pre1970", "original_body", "language", "winner_of_pair", "extinct_world"],
    historical_disposition={
        "state": "HISTORICAL_ONLY", "failure_reasons": [],
        "superseded_by": "", "rival_of": "IPL-V (no machine-readable body located)",
        "evidence": [{"kind": "original_paper", "ref": "Bobrow & Raphael, CACM 7(4) 1964",
                      "says": "Compares COMIT, IPL-V, LISP 1.5 and SLIP as the competing list-processing "
                              "languages of the period, establishing that they were contemporaneous rivals."},
                     {"kind": "project_documentation", "ref": "Computer History Museum Software Preservation Group, LISP 1.5 family",
                      "says": "Documents the LISP 1.5 sources and their transcription as preserved historical artifacts."}],
        "audit_note": "HISTORICAL_ONLY refers to THIS 1962 body and its 7090 world. LISP as a language lineage "
                      "is emphatically still ACTIVE; no supersession is claimed. The rival IPL-V is recorded as "
                      "a rival, NOT as a defeated loser: I hold no evidence establishing why the ecosystem moved."},
    lineage_relations=[{"relation": "shares_ancestor_with", "to": "femtolisp",
                        "note": "the vault holds a modern Lisp; this is a 1962 one. Techne records the shared "
                                "domain, not equivalence"}])


def main():
    from .. import record as R
    for rec in S:
        try:
            old = R.load(rec["specimen_id"])
            for k in ("run_classification", "test_classification", "receipts", "hashes", "acquisition_date",
                      "observability", "nyx_handoff"):
                if old.get(k):
                    rec[k] = old[k]
            R.merge_artifact_pins(rec, old)
        except FileNotFoundError:
            pass
        probs = R.validate(rec)
        R.save(rec)
        print("%-36s %s" % (rec["specimen_id"], "ok" if not probs else probs))
    print(len(S), "records")


if __name__ == "__main__":
    main()
