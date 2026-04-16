# prometheus_sci — Scientific Data

**Database:** prometheus_sci  
**Host:** 192.168.1.176:5432  
**User:** postgres / prometheus  
**Access:** Read after ingestion  
**Total rows:** 854,710  

## Schema: core

| Table | Rows | Columns | Source |
|-------|------|---------|--------|
| data_source | 6 | source_id, name, origin_url, file_path, loaded_at, row_count, checksum | Provenance tracking |

## Schema: topology

| Table | Rows | Columns | Source |
|-------|------|---------|--------|
| knots | 12,965 | knot_id, name, crossing_number, determinant, alexander_coeffs, jones_coeffs, conway_coeffs, signature, source_id | cartography/knots/data/knots.json |
| polytopes | 980 | polytope_id, name, dimension, n_vertices, n_edges, n_facets, f_vector, is_simplicial, source_id | cartography/polytopes/data/polytopes.json |

## Schema: chemistry

| Table | Rows | Columns | Source |
|-------|------|---------|--------|
| qm9 | 133,885 | mol_id, smiles, homo, lumo, homo_lumo_gap, zpve, polarizability, n_atoms, source_id | cartography/chemistry/data/qm9.csv |

## Schema: physics

| Table | Rows | Columns | Source |
|-------|------|---------|--------|
| materials | 10,000 | mat_id, material_id, band_gap, formation_energy_per_atom, spacegroup_number, density, volume, nsites, source_id | cartography/physics/data/materials_project_10k.json |
| superconductors | 0 | sc_id, material_formula, tc, spacegroup, sc_class, source_id | — |
| codata | 0 | constant_id, name, value, uncertainty, unit, source_id | — |
| pdg_particles | 0 | particle_id, name, pdg_id, mass_gev, charge, spin, lifetime_s, is_stable, source_id | — |

## Schema: algebra

| Table | Rows | Columns | Source |
|-------|------|---------|--------|
| groups | 544,831 | group_id, label, order_val (NUMERIC), exponent (NUMERIC), n_conjugacy, is_abelian, is_solvable, source_id | cartography/groups/data/abstract_groups.json |
| space_groups | 230 | sg_id, number, symbol, point_group_order, crystal_system, lattice_type, is_symmorphic | cartography/spacegroups/data/space_groups.json |
| lattices | 26 | lattice_id, label, dimension, determinant, level, class_number, kissing_number, source_id | cartography/lattices/data/*.json |

**Note:** groups.order_val and exponent widened from INTEGER to NUMERIC (some group orders are 60+ digits).

## Schema: analysis

| Table | Rows | Columns | Source |
|-------|------|---------|--------|
| fungrim | 0 | formula_id, fungrim_id, formula_type, module, n_symbols, formula_text, source_id | — |
| oeis | 0 | seq_id, oeis_id, name, first_terms[], growth_rate, entropy, is_monotone, source_id | — |

## Schema: biology

| Table | Rows | Columns | Source |
|-------|------|---------|--------|
| metabolism | 0 | model_id, bigg_id, n_reactions, n_metabolites, n_genes, n_compartments, frac_reversible, source_id | — |

## Schema Creation

```bash
# Run on M1 as postgres:
psql -U postgres -f scripts/db_setup.sql
```

Full schema: `scripts/db_setup.sql`  
Migration script (M2 data): `mnemosyne/migrate_m2.py`
