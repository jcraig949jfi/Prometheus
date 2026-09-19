# atlas/ -- the Prometheus experiment index (seat: roles/Atlas)

A two-tier relational index of every experiment the engines ran (SFE,
NPE, Archaeon's frontier scheduler, Vivarium; more as they appear), in
schema `atlas` on the M1 store. Pointers, not copies. Read-only against
every engine. Design: roles/Atlas/MODEL.md. Sources: roles/Atlas/SOURCES.md.

    python -m atlas migrate
    python -m atlas harvest all        # reference commits archaeon_campaigns frontier npe vivarium pew local_files
    python -m atlas comb               # the recomb rules -> atlas.signal
    python -m atlas report --out <file>
    python -m atlas status
    python -m pytest -q atlas/tests

Useful views/functions: atlas.v_manifest, atlas.v_edge_dangling,
atlas.v_local_only, atlas.v_coverage, atlas.v_shape_inventory,
atlas.v_measurement_names, atlas.descendants(type,key), atlas.ancestors(type,key).
