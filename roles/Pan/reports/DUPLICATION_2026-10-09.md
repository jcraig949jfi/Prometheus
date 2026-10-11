# How much of the program's text is a copy (PAN-32)

Currency: 2026-10-09T15:41Z (date -u). Command: `python -m pan dupes` (pan/dupes.py),
catalog at 943b3c96d. Table pan.chunk_dup (chunk -> canonical chunk, cluster size).

Method: exact duplicates after lower-casing and whitespace normalisation, at chunk
level (chunks of >= 200 characters), across different git artifacts. The canonical
member of a cluster is the chunk from the earliest-committed file. Near-duplicates
(paraphrased quotation) are NOT counted here; search handles those at query time
(canonical-first collapse). ORACLE: exactly one canonical per cluster -- held.

## Numbers

    chunks considered (>= 200 chars, git)     330,251
    chunks in a duplicate cluster              64,778  in 17,834 clusters
    copies (members that are not canonical)    46,944  = 14.2 percent of chunks
    characters in copies                    61,606,228  = 11.8 percent of characters
    copies in clusters of size >= 50           14,274  (template boilerplate)

    copies by kind         chunks     chars
      code                 25,351  40,804,802
      doc                  17,914  15,770,257
      data                  1,064   1,510,901
      receipt                 374   1,037,215
      prompt                1,530     841,342
      result                  382     790,772
      prereg                  179     366,116

    copies by seat         chunks     chars       code copies by top dir   chunks
      Hephaestus           30,066  38,148,890       agents                 19,650
      Theseus               4,377   7,099,684       roles                   2,665
      (no seat by path)     4,703   5,232,914       forge                   1,300
      Ananke                2,388   2,415,892       apollo                    510
      Lexis                   844   2,127,922
      Archaeon                826   1,880,127

Largest clusters are one generated-report template ("### Scores | Metric | Score |
... Reasoning ... Metacognition ...") repeated up to 2,076 times across
agents/hephaestus/humanreadable/*.md.

## Readings

- About one chunk in seven is a verbatim copy of text in another file; most of it
  is generated material (Hephaestus reports and code), not seats quoting each other.
- Boilerplate clusters are retrieval noise: a query that matches the template
  matches thousands of files equally. If retrieval work reopens, down-weighting
  chunks in clusters of size >= 50 is the cheapest lever this measurement offers
  (not applied: retrieval tuning is stopped, RETRIEVAL_VERDICTS_2026-10-09.md).
- Storage: the copies are 61.6 MB of text in pan.chunk; deduplicating chunk storage
  would save about 12 percent of that table -- not worth a schema change today.
