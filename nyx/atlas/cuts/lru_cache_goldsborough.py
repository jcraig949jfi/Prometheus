"""Cut: lru-cache-goldsborough (Goldsborough's header-only C++ LRU cache; ancestry-aware, Stage A DEEP; SOURCE_READ on M3;
position 32 of the 2026-09-17 NOT_CUT order). Read: include/lru/internal/base-cache.hpp contains/lookup 784-850, insert 900-923,
the protected helpers 1394-1455 (names and the move-to-front / erase-lru bodies); include/lru/cache.hpp find 152-177;
include/lru/internal/last-accessed.hpp 60-130; timed-cache.hpp 200-240 (names). NOT read: the iterator classes, statistics.hpp,
the callback manager, the tests (googletest submodule). Nothing ran (C++; no compiler on M3).
"""
from nyx.atlas.author import Cut

B = "vault:lru-cache-goldsborough/upstream/tree/include/lru/internal/base-cache.hpp"; C = "vault:lru-cache-goldsborough/upstream/tree/include/lru/cache.hpp"
L = "vault:lru-cache-goldsborough/upstream/tree/include/lru/internal/last-accessed.hpp"; T = "vault:lru-cache-goldsborough/upstream/tree/include/lru/timed-cache.hpp"
c = Cut("lru-cache-goldsborough", mode="ANCESTRY_AWARE", inspected=["base-cache.hpp 784-850, 900-923, 1394-1455", "cache.hpp 152-177", "last-accessed.hpp 60-130", "timed-cache.hpp 200-240"],
        evidence=[("SOURCE_READ", B + ":784-923"), ("SOURCE_READ", B + ":1394-1455"), ("SOURCE_READ", C + ":152-177"), ("SOURCE_READ", L + ":60-130")],
        note="the textbook LRU (hash map + recency list, move-to-front on hit, pop-front on overflow) plus one mechanism of the author's: a one-entry 'last accessed' pointer checked before the hash lookup, so contains()-then-lookup() on the same key costs one hash; and a timed variant that expires entries by age on access")

lru = c.organ("hash_map_plus_recency_list_with_move_to_front_on_hit_and_evict_front_on_overflow", human_name="BaseCache::insert (900-923), Cache::find (cache.hpp 152-177), _move_to_front / _erase_lru (1394-1420)", status="ACCEPTED",
    mechanism="a std::unordered_map from key to (value, list iterator) and a std::list of keys in access order; find: map lookup, on hit splice the key's node to the back (most recent) and count a hit, on miss count a miss; insert: if present update and move to front, else emplace and append, evicting the list's front key when size exceeds capacity",
    input="keys", output="values or misses", state="the map and the list (capacity entries)", update="per access", assumptions=["recency predicts reuse (the LRU premise); the map's iterator and the list's node are both stable so the cross-references survive"],
    fitness_value_in_ancestor="O(1) expected hit, insert and evict", failure_landscape="by reading: a scan larger than the capacity evicts everything (LRU's known failure against sequential scans); no adaptivity (ARC, LIRS) anywhere in the body",
    human_prior="the standard textbook structure (e.g. Java's LinkedHashMap access order)", evidence_ref=B + ":900-923; " + C + ":152-177", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="BaseCache + Cache",
    coverage={"input_topology": "STREAM", "output_topology": "EVENT", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "memory": "WINDOW", "stochasticity": "DETERMINISTIC", "update_topology": "EVENT_DRIVEN", "failure_mode": "DEGRADES"})

last = c.organ("one_entry_last_accessed_pointer_checked_before_the_hash_lookup", human_name="Internal::LastAccessed (last-accessed.hpp); BaseCache::contains / lookup (784-850)", status="ACCEPTED",
    mechanism="every hit or insert records a raw pointer pair (key, information) of the touched map entry; contains() and lookup() first compare the requested key with that pointer by the cache's key_equal and, if equal and still valid, return without touching the map (registering a hit); erase and rehash invalidate it; the class comment explains it exists so that contains()-then-lookup() idioms pay one hash, not two",
    input="a key", output="a value or a fall-through to the map", state="two pointers and a validity flag", update="per access", assumptions=["callers repeat the same key back to back (contains then lookup, or a loop over one key)"],
    fitness_value_in_ancestor="halves the hash cost of the common two-call idiom", failure_landscape="by reading: a stale pointer after erase/rehash is the risk the validity flag exists for; the TimedCache overrides _last_accessed_is_ok to add the expiry check", evidence_ref=L + ":60-130; " + B + ":784-850", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="LastAccessed + the two front doors",
    coverage={"input_topology": "SCALAR", "output_topology": "DECISION", "state_amount": "CONSTANT", "memory": "LAST_VALUE", "stochasticity": "DETERMINISTIC"})

timed = c.organ("expiry_by_age_checked_lazily_on_access_with_a_time_to_live_per_cache", human_name="TimedCache::find / all_expired (timed-cache.hpp 200-240)", status="CANDIDATE",
    mechanism="each entry stores its insertion time; find checks the entry's age against a per-cache time_to_live before returning a hit, treating an expired entry as a miss (and erasing it); no timer or sweep: expiry is enforced only when the entry is touched", input="a key; the clock", output="a hit or a miss", state="one timestamp per entry", update="per access",
    assumptions=["expired entries are cheap to leave in place until touched"], fitness_value_in_ancestor="TTL semantics with no background work", failure_landscape="UNKNOWN by run", evidence_ref=T + ":200-240 (names and the two checks; bodies not read in full)", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="TimedCache; CANDIDATE because only the check sites were read",
    coverage={"input_topology": "SCALAR", "output_topology": "DECISION", "state_amount": "LINEAR_IN_INPUT", "resource_dependence": "TIME", "stochasticity": "DETERMINISTIC"})

c.reject("the ordered/unordered iterator classes, statistics.hpp (hit/miss counters), the callback manager, the Doxygen tree", reason="OTHER", evidence="NOT READ; residue")
c.reject("'LRU cache' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the recency structure, the last-accessed shortcut and the timed expiry are separable; the first is the textbook, the second is the author's")

c.edge(last, lru, "gates", note="short-circuits the map"); c.edge(timed, lru, "gates", note="turns a stale hit into a miss")

c.pressure("a_bounded_memory_must_answer_a_stream_of_key_lookups_with_a_hit_rate_close_to_the_offline_optimum_at_constant_cost_per_access",
    condition="an organism holds C entries; keys arrive in a stream with temporal locality; a miss costs a fetch; per-access time must not grow with C or with the stream length", resource_or_constraint="C slots; O(1) per access",
    failure_condition="hit rate far below Belady's offline optimum on locality-bearing streams, or per-access cost growing with C", world_punishes="FIFO and random eviction on reuse-heavy streams; LRU on scans larger than C", world_rewards="recency ordering; scan resistance if the world includes scans",
    observable_consequence="hit rate vs Belady's MIN on a Zipf stream, on a cyclic scan of length > C, and on their interleaving", vacuity_condition="C at least the number of distinct keys", trivial_shortcuts="a stream with no reuse (every policy scores zero)",
    cheat_control="an organism given the future (Belady) bounds the score; random eviction bounds it below on the Zipf stream; on the scan stream LRU must equal random (its known failure) so a scan-resistant organism is distinguishable: the world must show all three",
    cost_class="CPU-scale", source_evidence="cache.hpp find; base-cache.hpp insert/_erase_lru", purpose="PURPOSE: bounded caching (Goldsborough 2016)")

c.ancestry("reimplementation_of", "the LRU policy (Belady 1966 for the framing; the map+list structure is folklore)", note="from the README")
c.residue("PARTIALLY_EXPLAINED", ["iterators, statistics and callbacks unread", "TimedCache read at the check sites only", "nothing ran"], note="a small body; the author's one mechanism (last-accessed) is located and separated from the textbook")
c.save(state="DEEP")
