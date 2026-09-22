"""Cut: dlmalloc (Doug Lea's malloc 2.8.6; ancestry-aware, Stage A COARSE; SOURCE_READ on M3; sixth of the 2026-09-17 NOT_CUT order).
The body is one 6,291-line file. Read: the design comment (1-130 vital statistics; 2200-2600 chunk representation, head/foot
bits, tree chunks, segments, malloc_state: top, dv, smallbins, treebins, binmaps), dlmalloc() 4550-4686 (the two-path algorithm),
dlfree() 4688-4795 (coalescing, top, dv, trim trigger), tmalloc_large/tmalloc_small 4440-4548, sys_trim 4301-4367. NOT read:
sys_alloc/add_segment/prepend_alloc (3946-4254), mmap_alloc, realloc/memalign/calloc/bulk_free, mspaces (5400+), the debug
checkers (3225-3534), locking. Nothing ran.
"""
from nyx.atlas.author import Cut

M = "vault:dlmalloc/upstream/malloc.c"
c = Cut("dlmalloc", mode="ANCESTRY_AWARE", inspected=["malloc.c 1-130, 2200-2600, 4301-4367, 4440-4795"],
        evidence=[("SOURCE_READ", M + ":2200-2600"), ("SOURCE_READ", M + ":4550-4795"), ("SOURCE_READ", M + ":4440-4548"), ("SOURCE_READ", M + ":4301-4367"), ("SOURCE_READ", M + ":1-130")],
        note="the famous name covers seven mechanisms with separate lives: boundary tags with in-use bits, immediate coalescing, exact-size small bins with a bitmap, size-keyed tries for large chunks, a designated victim, a wilderness chunk, "
             "and a trim policy that disables itself on failure; plus a security layer that refuses bad frees")

tag = c.organ("boundary_tags_with_in_use_bits_folded_into_the_size_word", human_name="malloc_chunk head/prev_foot; PINUSE_BIT/CINUSE_BIT (2200-2300)", status="ACCEPTED",
    mechanism="every chunk has a head word = size | flags where the two low bits (free by 8-byte alignment) say whether THIS chunk and the PREVIOUS chunk are in use; a free chunk also writes its size at its foot (the next chunk's prev_foot), so a chunk can find its predecessor only when the predecessor is free; mmapped chunks clear both bits",
    input="a chunk address", output="its size, in-use state, neighbours", state="one word per chunk (two for free chunks)", update="on every allocate/free/split/coalesce",
    assumptions=["8-byte alignment leaves the low bits free", "user data may overwrite the foot of an in-use chunk, so the foot is only trusted when the chunk is free (the head of the next chunk says so)"],
    fitness_value_in_ancestor="constant-time neighbour discovery for coalescing at one word of overhead", failure_landscape="by reading: a corrupted head propagates (next_chunk arithmetic); the optional FOOTERS check word and the address/pinuse checks exist because of it",
    human_prior="Knuth's boundary tags (1973) with the in-use-bit trick to drop the foot for allocated chunks", evidence_ref=M + ":2200-2300", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the head/foot macros",
    coverage={"input_topology": "SCALAR", "output_topology": "VECTOR", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "representation_sensitivity": "SENSITIVE"})

coal = c.organ("immediate_coalescing_on_free_with_top_and_dv_absorption", human_name="dlfree (4688-4795)", status="ACCEPTED",
    mechanism="on free: if the previous chunk is free (pinuse clear) merge backward (unlinking it from its bin unless it is dv); if the next chunk is free merge forward: if next is top, the freed chunk becomes top (and dv is cleared if it was dv; trim is considered); if next is dv, the merged chunk becomes dv; else unlink next and merge; the result is inserted into a small bin or a tree bin; large frees count down to a segment release check",
    input="a chunk", output="one larger free chunk in a bin, or a larger top/dv", state="bins, top, dv", update="per free",
    assumptions=["merging eagerly is cheaper than searching later; fragmentation is fought at free time"], fitness_value_in_ancestor="adjacent free space is never fragmented by bookkeeping; top grows back so trimming can return memory",
    failure_landscape="UNKNOWN by run; by reading: a free of a chunk adjacent to dv silently grows dv, so dv may become large and stop being a good 'recent split' hint", evidence_ref=M + ":4688-4795", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="dlfree",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "update_topology": "EVENT_DRIVEN", "resource_dependence": "MEMORY"})

sb = c.organ("exact_size_small_bins_indexed_by_size_over_8_with_a_non_empty_bitmap", human_name="smallbins / smallmap; dlmalloc small path (4581-4640)", status="ACCEPTED",
    mechanism="32 doubly linked bins, one per 8-byte size up to 256 bytes; a 32-bit map has bit i set when bin i is non-empty; a small request checks its bin and the next (the 'remainderless' fit: two bits at once), else takes the smallest non-empty larger bin found with least_bit(map & left_bits), splits it, and the remainder becomes the new dv",
    input="a padded request size nb", output="a chunk of exactly nb or nb+8, or a split with the remainder as dv", state="the bins and the map", update="per small malloc/free",
    assumptions=["small sizes dominate and repeat, so exact reuse beats searching"], fitness_value_in_ancestor="O(1) for the common case; the bitmap avoids scanning empty bins", failure_landscape="UNKNOWN by run",
    human_prior="the 256-byte small/large boundary and the 8-byte spacing", evidence_ref=M + ":2497-2520, 4581-4640", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="smallbin_at, smallmap, the small path",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "memory": "ARCHIVE", "stochasticity": "DETERMINISTIC", "resource_dependence": "MEMORY"})

tb = c.organ("size_keyed_bitwise_tries_for_large_chunks_with_best_fit_by_leftmost_walk", human_name="treebins / tmalloc_large / tmalloc_small (2380-2440, 4440-4548)", status="ACCEPTED",
    mechanism="32 tree bins, two per power of two; each bin is a trie keyed on the bits of the size below the bin's leading bit (child index = next size bit); equal sizes hang off one node as a list; best fit walks the trie following the request's bits, remembering the deepest untaken right subtree, then descends leftmost children to find the smallest chunk >= nb; if no bin fits, the next non-empty tree bin from the map is used; the chosen chunk is split and the remainder binned (or made dv for small requests)",
    input="nb", output="the best-fitting large chunk, split", state="the tries and treemap", update="per large malloc/free",
    assumptions=["large requests are rare enough that O(log range) per operation is fine; sizes in a bin differ only in low bits"], fitness_value_in_ancestor="best fit without sorting: 6-53 steps worst case (the comment's bound)",
    failure_landscape="UNKNOWN by run", human_prior="bitwise trie (a 'digital search tree') rather than a balanced tree; two bins per power of two", evidence_ref=M + ":2380-2440, 4440-4548", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="malloc_tree_chunk and the two tmalloc functions",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PERSISTENT", "memory": "ARCHIVE", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE"})

dv = c.organ("designated_victim_as_the_preferred_source_for_small_requests_without_an_exact_fit", human_name="dv / dvsize; replace_dv; dlmalloc 4648-4665", status="ACCEPTED",
    mechanism="the remainder of the most recent split for a small request is held outside the bins as dv; a small request with no exact-fit bin is served from dv if it fits (split, or exhaust); a large request uses a binned chunk only if it fits better than dv, else dv; freeing next to dv extends it",
    input="requests; splits", output="a chunk carved from dv", state="dv, dvsize", update="per split and per dv use",
    assumptions=["consecutive small requests are likely to be freed together, so carving them from one region keeps them adjacent (locality) and coalescable"], fitness_value_in_ancestor="locality for sequences of small allocations; fewer bin insertions",
    failure_landscape="UNKNOWN by run", human_prior="a single 'last remainder' hint rather than a cache per size", evidence_ref=M + ":2506-2512, 4648-4665", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="every dv reference",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "memory": "LAST_VALUE", "stochasticity": "DETERMINISTIC"})

top = c.organ("wilderness_top_chunk_grown_from_the_system_and_trimmed_back_with_self_disabling_autotrim", human_name="top / topsize; sys_trim (4301-4367); should_trim in dlfree", status="ACCEPTED",
    mechanism="the highest chunk of the active segment is never binned; requests that nothing else serves are split from it, and it is extended by sys_alloc (MORECORE preferred, MMAP otherwise); when a free makes top exceed trim_check (default 2 MB), sys_trim gives back whole granularity units above a pad via MORECORE(-extra) (only if the break is where it was left) or mremap/munmap; if a trim releases nothing, trim_check is set to infinity so the attempt is never repeated",
    input="requests; frees adjacent to top", output="memory returned to the system, or not", state="top, topsize, trim_check, segments", update="per top split; per large free",
    assumptions=["the OS break may have moved (another allocator): checked, not assumed", "repeated failed trims are worse than never trimming"], fitness_value_in_ancestor="footprint follows demand downward; a hostile OS cannot make trimming a per-free cost",
    failure_landscape="by reading: once autotrim is disabled it stays disabled for the process; the failure is remembered, never retried", human_prior="the 2 MB trim threshold and 256 KB mmap threshold are tuning; the self-disable is a policy choice recorded in one line",
    evidence_ref=M + ":2497-2505, 4301-4367, 4666-4676, 4740-4750", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="sys_trim and the top references",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "feedback": "CLOSED_LOOP", "stochasticity": "DETERMINISTIC", "resource_dependence": "MEMORY", "adaptation": "POLICY", "recovery": "NONE"})

sec = c.organ("usage_error_detection_by_address_range_in_use_bits_and_optional_footer_magic", human_name="ok_address / ok_inuse / ok_pinuse / FOOTERS / USAGE_ERROR_ACTION (dlfree RTCHECKs)", status="ACCEPTED",
    mechanism="every free checks that the address is above least_addr, that the chunk's head says in-use, and that the next chunk's pinuse bit agrees; with FOOTERS each chunk carries a per-process magic in its foot that a foreign or forged chunk will not have; a failed check aborts (default), or drops all bookkeeping and continues (PROCEED_ON_ERROR)",
    input="a pointer passed to free/realloc", output="proceed, abort, or discard-and-continue", state="least_addr, mparams.magic", update="per free",
    assumptions=["the bookkeeping words themselves are intact (the comment says so explicitly)"], fitness_value_in_ancestor="a double free or wild free is caught before it corrupts; the library never writes below its own base",
    failure_landscape="by reading: an overwrite that preserves the head bits passes; the checks are consistency checks, not integrity proofs", evidence_ref=M + ":76-115, 4705-4715, 4735, 4790", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the RTCHECK sites and the FOOTERS macros",
    coverage={"input_topology": "SCALAR", "output_topology": "DECISION", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "failure_mode": "CORRUPTS", "recovery": "EXTERNAL_RESET"})

c.reject("sys_alloc / add_segment / prepend_alloc / mmap_alloc / release_unused_segments (getting memory from the system, segment list)", reason="OTHER", evidence="NOT READ this pass (3832-4254); residue")
c.reject("realloc / memalign / calloc / bulk_free / inspect_all / mspaces / locks / the debug checkers", reason="OTHER", evidence="NOT READ (4797-6291, 3225-3534, 1887-2000); the checkers are instruments", note="mspace_* is the same machine instantiated per arena; the debug checkers are the body's own oracle and a Stage C asset")
c.reject("the compile-time option layer (#if FOOTERS, USE_LOCKS, INSECURE, HAVE_MMAP, ...)", reason="GENERIC_LANGUAGE_MECHANICS", evidence="configuration, not mechanism; the options select which organs exist")
c.reject("'malloc' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the basic algorithm comment (4552-4569) is itself a ten-step composition of the organs above")

c.edge(tag, coal, "feeds"); c.edge(coal, sb, "updates"); c.edge(coal, tb, "updates"); c.edge(coal, dv, "updates"); c.edge(coal, top, "updates"); c.edge(sb, dv, "updates", note="split remainder -> dv"); c.edge(tb, dv, "competes", note="better-fit test")
c.edge(dv, top, "competes", note="dv before top"); c.edge(top, coal, "triggers", note="should_trim"); c.edge(sec, coal, "gates"); c.edge(tag, sec, "feeds"); c.edge(sb, tb, "competes", note="tmalloc_small when no small bin fits")

c.pressure("a_stream_of_variable_sized_requests_and_releases_must_be_served_from_one_contiguous_region_under_a_footprint_and_a_latency_bound",
    condition="the world issues allocate(size)/release(ptr) in an unknown interleaving with sizes from a heavy-tailed mix; the organism owns one region it may extend or shrink at a cost; every request must be answered in bounded time",
    resource_or_constraint="footprint (high-water mark of the region), per-operation time, wasted bytes (fragmentation)", failure_condition="a request refused while enough free bytes exist (fragmentation), or per-operation time growing with the number of live blocks",
    world_punishes="both; and a footprint that never shrinks after a burst", world_rewards="an organism whose free space stays coalesced and whose common case is constant time", observable_consequence="footprint / live bytes over a trace; p99 operation time vs live block count; bytes returned to the system after a burst",
    vacuity_condition="uniform sizes (a free list suffices) or infinite memory", trivial_shortcuts="a bump allocator that never frees (footprint unbounded); a per-size free list with no coalescing (passes time, fails fragmentation on shifting size mixes)",
    cheat_control="an organism given the whole trace in advance must achieve the optimal offline packing; a bump allocator must show footprint = total allocated: if the world cannot distinguish those, it is not measuring fragmentation",
    cost_class="CPU-scale", source_evidence="malloc.c 4552-4569 (the algorithm), 2497-2560 (the state), record domain resource-management", purpose="PURPOSE: general-purpose dynamic memory allocation (Lea)")

c.pressure("a_self_tuning_policy_must_stop_retrying_an_action_the_environment_has_shown_to_be_useless",
    condition="an organism periodically attempts a maintenance action (return unused resource) whose success depends on the environment; each attempt costs; the environment may make it permanently impossible",
    resource_or_constraint="attempt cost; the benefit when it works", failure_condition="paying the cost forever with no benefit", world_punishes="repeated failed attempts", world_rewards="remembering the failure and stopping (at the cost of never benefiting if the environment changes)",
    observable_consequence="attempts after the first failure; benefit forgone if the environment later allows the action", vacuity_condition="the action always succeeds or never costs", trivial_shortcuts="never attempt",
    cheat_control="an organism told the environment's answer in advance must attempt exactly when it works; the ancestor's self-disable must show zero attempts after one failure and zero benefit after the environment relents: both must be visible",
    cost_class="CPU-scale", source_evidence="malloc.c 4361-4363 (trim_check = MAX_SIZE_T on failure)", purpose="PURPOSE: autotrim policy (dlmalloc)")

c.ancestry("algorithm_from", "Knuth boundary tags; Lea's malloc lineage 1987-2012 (the file's own history); the glibc ptmalloc family derives from earlier versions (the comment at 27-30)", note="from the source comments; not verified against the record this pass")
c.residue("PARTIALLY_EXPLAINED", ["system-memory acquisition and segment management not read (about 400 lines); realloc/memalign/mspaces not read; the bin-index arithmetic (compute_tree_index) read as a macro only", "nothing ran; the body's own debug checkers (DEBUG/FOOTERS) are an oracle for a Stage C run"],
          note="the allocate/free core is accounted for; the boundary of the cut is the malloc_state and the two exported entry points")
c.save(state="COARSE")
