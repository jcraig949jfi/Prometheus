# 08 - PERMANENT RECORD: THE AVIDA V0.1 CORRECTION

Preserved because it is a concrete Prometheus failure specimen, not as a
general methodological essay.

    ORIGINAL CLAIM (V0.1)
        Seven lineage genomes (pd 3, 60, 84, 94, 101, 103, 106) were damaged by
        PDF extraction/transcription loss. Diagnosis offered: "the extractor
        dropped bolded mutation glyphs". Two independent extractors (pypdf and
        pdfplumber) agreed byte-for-byte, including reproducing the same seven
        underscores, which was cited as evidence that the loss was real and in
        the PDF text layer.

    CORRECTION (final bounded pass)
        ZERO were damaged. Recovering the 2003-06-08 capture of
        case-study/lineage.html yielded the legend verbatim:
            "point mutations are printed in red, insertions in green;
             deletions are marked by blue asterisks"
        The blue asterisk is a DOCUMENTED DELETION MARKER. The PDF text layer
        rendered it as an underscore. Nothing was lost.

    CONSEQUENCES
        1. The evaluator-based lineage-repair justification is WITHDRAWN. One of
           the three stated reasons for building a 2003 binary evaporated.
        2. Those seven genomes are each ONE INSTRUCTION SHORTER than V0
           recorded; the marker occupies a display column and is not an
           instruction. Five now read len = prev-1 (clean deletion), two read
           len = prev (deletion plus compensating insertion, consistent with
           independent 0.05 divide-insert / divide-delete rates).
        3. pd 101, a frozen checkpoint, was declared BLOCKED on a defect that
           did not exist.
        4. Transcription status UPGRADED to validated: 105 of 105 undamaged
           rows agree EXACTLY across two independent PRIMARY renderings.

    THE SPECIFIC LESSON
        Two independent extractors agreeing establishes REPRODUCIBILITY, not
        SEMANTIC CORRECTNESS. Both were faithfully reproducing a source
        notation that the analyst had not read. The agreement was cited AS
        EVIDENCE FOR the damage hypothesis, when it was equally consistent with
        -- and in fact caused by -- correct transcription of a symbol whose
        meaning was documented in a file that had not yet been fetched.

    WHAT WOULD HAVE CAUGHT IT EARLIER
        Reading the source legend before diagnosing the source. The legend was
        in an object listed on the site index from the first capture in 2003.

    EVIDENCE PRESERVED
        genome_display retains the original rendering verbatim; genome holds
        the corrected instruction sequence; deletion_marker_positions records
        where the markers were. The erroneous parse is preserved in
        lineage_of_descent.jsonl alongside the corrected
        lineage_of_descent_corrected.jsonl. Nothing was overwritten.
