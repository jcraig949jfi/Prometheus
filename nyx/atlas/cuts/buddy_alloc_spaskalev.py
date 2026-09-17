"""Cut: buddy-alloc-spaskalev (Spaskalev's single-header buddy allocator; ancestry-aware, Stage A DEEP; SOURCE_READ on M3;
position 31 of the 2026-09-17 NOT_CUT order). Read: buddy_alloc.h buddy_malloc 771-808, buddy_free 907-935, depth_for_size
1112-1128, the tree encoding (struct buddy_tree 1381-1400, status/mark/release/update_parent_chain 1756-1813), find_free
1814-1861, virtual slots 1203-1253. NOT read: realloc, the walk/reserve/resize paths, the bitset helpers, tests.c (2,763 lines).
Nothing ran (C; no compiler on M3).
"""
from nyx.atlas.author import Cut

H = "vault:buddy-alloc-spaskalev/upstream/tree/buddy_alloc.h"
c = Cut("buddy-alloc-spaskalev", mode="ANCESTRY_AWARE", inspected=["buddy_alloc.h 771-808, 907-935, 1112-1128, 1381-1400, 1756-1861, 1203-1253"],
        evidence=[("SOURCE_READ", H + ":771-808"), ("SOURCE_READ", H + ":907-935"), ("SOURCE_READ", H + ":1756-1861"), ("SOURCE_READ", H + ":1203-1253")],
        note="a buddy allocator whose free/used state is a complete binary tree of small integers packed in a bitset: each node stores the largest free order beneath it (0 = fully used, depth-relative), so allocation is a root-to-leaf descent comparing two children and release is an upward recomputation that stops as soon as a parent's value is unchanged")

tree = c.organ("tree_of_largest_free_order_per_node_packed_in_a_bitset_with_upward_recompute_that_stops_when_unchanged", human_name="buddy_tree_mark / buddy_tree_release / update_parent_chain (1761-1813); the node encoding (internal_position: local_offset = bits per node at that depth)", status="ACCEPTED",
    mechanism="each tree node holds a number: 0 for fully free at its own size, its depth-relative maximum for fully used, otherwise the largest free block order below it; marking a node writes its max value, releasing writes 0; either then walks to the root: parent = (either child nonzero) * (min(children) + 1); the walk returns early the first time a parent already holds that value, so most updates touch O(1) nodes",
    input="a tree position", output="an updated tree", state="the bitset (ceil(log2 size) levels of nodes, node width growing by one bit per level toward the root)", update="per alloc/free",
    assumptions=["a node's summary (largest free order below) is enough to route an allocation without visiting the leaves; the early stop is sound because a parent's value depends only on its two children"],
    fitness_value_in_ancestor="alloc and free are O(depth) with a memory overhead of a few bits per block rather than a free list per order", failure_landscape="by reading: an allocation of a size much smaller than the alignment still costs the full descent; coalescing is implicit (a parent reads 0 when both children read 0), so there is no explicit buddy-merge step to get wrong",
    human_prior="Knowlton 1965 / Knuth's buddy system, usually implemented with per-order free lists; the packed-tree encoding is this author's", evidence_ref=H + ":1756-1813", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the buddy_tree_* functions",
    coverage={"input_topology": "TREE", "output_topology": "TREE", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE", "resource_dependence": "MEMORY"})

find = c.organ("root_to_leaf_descent_that_prefers_the_busier_child_that_still_fits_to_keep_large_blocks_whole", human_name="buddy_tree_find_free (1814-1861)", status="ACCEPTED",
    mechanism="starting at the root with target_status = depth-1, refuse if the root's summary exceeds the target; at each level compare the left child's value against the target: if the left cannot fit go right, if the right cannot fit go left, else read the right child's value and go left when left is equal or more busy than right (prefer the busier side), or left when right is completely empty; the descent ends at the target depth without a search",
    input="a target depth", output="a position or INVALID_POS", state="none beyond the tree", update="per alloc", assumptions=["packing new allocations into already-fragmented subtrees preserves fully-free subtrees for large requests (a best-fit heuristic by summary value)"],
    fitness_value_in_ancestor="O(depth) allocation with a fragmentation-avoiding choice at every level for free", failure_landscape="UNKNOWN by run; the README claims low fragmentation, not measured here", evidence_ref=H + ":1814-1861", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="buddy_tree_find_free",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE", "order_sensitivity": "SENSITIVE"})

virt = c.organ("non_power_of_two_arena_by_pre_marking_the_missing_tail_as_virtual_used_slots", human_name="buddy_toggle_virtual_slots (1203-1253); buddy_virtual_slots (1138-1146)", status="ACCEPTED",
    mechanism="the tree is sized for the next power of two above the arena; the difference (delta) is masked by walking down the right spine, marking whole right children whenever delta exceeds half the node, until delta is exactly one node; resizing unmarks them the same way; allocation then never sees the phantom space",
    input="memory_size, alignment", output="a tree with the tail marked", state="the marked nodes", update="at init/resize", assumptions=["a power-of-two tree plus a used-marked tail is simpler than a tree of arbitrary shape"],
    fitness_value_in_ancestor="arbitrary arena sizes with the unchanged power-of-two machinery", failure_landscape="UNKNOWN by run", evidence_ref=H + ":1203-1253", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the toggle function",
    coverage={"input_topology": "SCALAR", "output_topology": "TREE", "state_amount": "LOG", "stochasticity": "DETERMINISTIC"})

c.reject("depth_for_size (1112-1128): ceiling power of two of the request and a trailing-zero count", reason="BELOW_MEANINGFUL_GRAIN", evidence=H + ":1112-1128", note="the rounding is the buddy system's definition, not a mechanism")
c.reject("buddy_realloc / reallocarray, buddy_walk, reserve_range, resize/embed/grow/shrink, change tracking, the bitset helpers, tests.c and bench.c", reason="OTHER", evidence="NOT READ; residue")
c.reject("'buddy allocator' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the summary-tree encoding, the descent policy and the virtual-tail trick are separable (dlmalloc in this atlas holds a different allocator with none of them)")

c.edge(find, tree, "feeds", note="the chosen position is marked"); c.edge(tree, find, "gates", note="node summaries route the descent"); c.edge(virt, tree, "feeds")

c.pressure("a_fixed_arena_must_serve_power_of_two_requests_with_bounded_time_per_operation_and_bounded_bookkeeping_while_keeping_large_blocks_available",
    condition="an organism allocates and frees blocks of varying sizes from a fixed arena; requests are rounded to powers of two; time per operation and metadata size are both scored; large requests must keep succeeding late in the trace", resource_or_constraint="the arena; a few bits per block of metadata",
    failure_condition="a large request fails while total free space would have sufficed (external fragmentation), or an operation costs more than O(log size)", world_punishes="free lists that scatter small allocations across free subtrees; metadata that grows with the number of live blocks", world_rewards="a summary per node and a descent that packs into busy subtrees",
    observable_consequence="largest satisfiable request after a fixed alloc/free trace, and metadata bytes, vs a naive first-fit buddy (Knuth's) on the same trace", vacuity_condition="all requests the same size", trivial_shortcuts="an arena much larger than the live set",
    cheat_control="an organism told the future trace can pack optimally (an upper bound); the naive buddy with the busier-child rule removed (go left always) must show more failures on an adversarial trace: the world must show both",
    cost_class="CPU-scale", source_evidence="buddy_tree_find_free; update_parent_chain; README's fragmentation claim", purpose="PURPOSE: memory allocation (Spaskalev 2021-)")

c.ancestry("reimplementation_of", "Knowlton 1965 / Knuth TAOCP 1 (buddy system); the packed summary tree is the author's own encoding", note="from the README and the record")
c.residue("PARTIALLY_EXPLAINED", ["realloc, walk and resize paths unread", "tests.c unread (an oracle for a Stage C run once a C compiler exists)", "nothing ran"], note="the three mechanisms that distinguish this buddy allocator from the textbook one are located")
c.save(state="DEEP")
