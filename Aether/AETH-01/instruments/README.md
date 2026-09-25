# AETH-01 optimization-round instruments

Currency: 2026-09-22. These are the scripts that produced every number in
`../GPU_MEMORY_OPTIMIZATION_01_2026-09-22.md`. They are committed because
a verdict whose rows cannot be regenerated is an assertion (base role
s2), not because they are part of the kernel. Nothing here is imported by
`aeth01.v1`, by the canary, or by the pod.

They run off-GPU, on the NumPy backend, from a seat worktree:

    python Aether/AETH-01/instruments/<script>.py <repo-root> [args]

| script | what it answers |
|:-------|:----------------|
| `measure_peak.py` | peak per-tick allocation, bytes/site, of the current reference kernel |
| `digest_gate.py` | does this kernel reproduce the eight A40 digests frozen in `RUNPOD_SCALE_RECEIPT_2026-09-22.md`? |
| `adversarial.py` | 464 domain-extreme cases, a candidate variant against the reference |
| `diff_and_measure.py` | 400 randomized cases plus a peak-memory comparison, variant against reference |
| `timing.py` | seconds per tick, one kernel against another |

`measure_peak.py` and `digest_gate.py` stand alone. The other three
compare TWO kernels, so they need something to compare against: the
reference file is the current kernel, and an older one is recovered from
git rather than kept as a copy that can drift, e.g.

    git show 251bc987e:Aether/test/reference/gpu_aeth01.py > /tmp/before.py
    python Aether/AETH-01/instruments/timing.py /tmp/before.py \
        Aether/test/reference/gpu_aeth01.py

where `251bc987e` is the pre-optimization commit.

`measure_peak.py` and the committed regression guard
(`Aether/test/test_aeth01_memory_footprint.py`) both verify FIRST that
tracemalloc can see NumPy's allocations at all. Without that check a
broken measurement reports zero bytes and every ceiling passes, which is
the exact shape of instrument this program keeps finding in its own
graveyard.

The fast, always-on subset of this evidence lives in
`Aether/test/test_aeth01_memory_footprint.py` and runs in the normal
suite. These scripts are the slow tail: sizes up to 2048, full
variant-against-variant comparison, and timing.
