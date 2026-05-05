"""Write the new _mahler_data.py with original 21 entries + 157 extensions."""

# Read the current header / table-prefix from the existing file.
with open("F:/Prometheus/prometheus_math/databases/_mahler_data.py", "r") as f:
    src = f.read()

# Read the new entries block (already a sequence of dict literals,
# indented at 4 spaces, ready to drop inside MAHLER_TABLE = [ ... ].
with open("F:/Prometheus/techne/scratch/extended_entries.py", "r") as f:
    extended_block = f.read()

# We want to insert the extended block just BEFORE the closing "]" of
# the MAHLER_TABLE list literal, but AFTER all existing entries.
#
# The existing file's closing of MAHLER_TABLE is the line "]" right
# before the post-table comment block.  We split on that.
marker = "MAHLER_TABLE: list[dict] = ["
assert marker in src, "marker not found"

# Find closing bracket of the list.  The file structure has:
#     MAHLER_TABLE: list[dict] = [
#         { ... }
#         ...
#         { ... },
#     ]
#
# followed by post-table comment + MAHLER_TABLE[1]["mahler_measure"] = ...
# patches.
# We need the FIRST "]" that closes the list.  Use a stack-based scan.

start = src.index(marker) + len(marker)
depth = 1  # inside [
i = start
while i < len(src) and depth > 0:
    c = src[i]
    if c == "[":
        depth += 1
    elif c == "]":
        depth -= 1
    i += 1
close_idx = i  # one past the closing ]

# Insert extended_block just before the closing ].
# The closing ] is at index close_idx - 1.
# The character before it should be a newline + the closing bracket.
# We splice in the new entries.
prefix = src[:close_idx - 1]   # up to but not including the "]"
suffix = src[close_idx - 1:]   # starting from "]"

# Add a trailing newline + the new block + nothing extra at end of prefix.
# prefix ends with the last entry's trailing newline.  Append a section
# header comment + the block.

# Strip trailing whitespace in prefix.
prefix = prefix.rstrip() + "\n"

new_section = (
    "\n"
    "    # ====================================================================\n"
    "    # === Phase 1 extension (2026-04-22): 157 deterministically-verified\n"
    "    # === entries from Smyth Pisot family, Pisot x^n - x^(n-1) - 1 family,\n"
    "    # === Lehmer-x-cyclotomic, Smyth-extremal x cyclotomic, Salem-x-cyclotomic\n"
    "    # === extensions, Tribonacci/Golden x cyclotomic, and small cyclotomics.\n"
    "    # === Every entry's mahler_measure was computed via\n"
    "    # === techne.lib.mahler_measure.mahler_measure and (for closed-form\n"
    "    # === families like Lehmer x Phi_k) cross-checked against the\n"
    "    # === literature value to better than 1e-9.\n"
    "    # ====================================================================\n\n"
)

new_src = prefix + new_section + extended_block + suffix

with open("F:/Prometheus/prometheus_math/databases/_mahler_data.py", "w") as f:
    f.write(new_src)

print("Wrote new _mahler_data.py")
print(f"  Original src length: {len(src)} chars")
print(f"  New src length:      {len(new_src)} chars")
