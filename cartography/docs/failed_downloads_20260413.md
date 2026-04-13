# Failed Downloads — Need Manual Browser Download
## 2026-04-13

### Gaia DR3 (Stellar parameters)
- **What:** 1.8B stars with Teff, logg, metallicity, radius, distance
- **Why failed:** TAP query returns HTTP 400 — needs proper ADQL client or astroquery
- **Manual URL:** https://gea.esac.esa.int/archive/ → ADQL query interface
- **Query:** `SELECT TOP 50000 source_id, ra, dec, parallax, pmra, pmdec, phot_g_mean_mag, bp_rp, teff_gspphot, logg_gspphot, mh_gspphot, radius_gspphot, distance_gspphot FROM gaiadr3.gaia_source WHERE phot_g_mean_mag < 12 AND teff_gspphot IS NOT NULL ORDER BY phot_g_mean_mag`
- **Format:** CSV download from the query interface
- **Save to:** `F:\Prometheus\cartography\physics\data\gaia\gaia_bright_50k.csv`
- **Alternative:** `pip install astroquery` then use `from astroquery.gaia import Gaia`

### House of Graphs (Graph theory)
- **What:** Database of "interesting" graphs with invariants
- **Why failed:** API pagination returns empty on list endpoint
- **Manual URL:** https://houseofgraphs.org/meta-directory
- **What to get:** Download graph collections linked from the meta-directory
- **Format:** graph6 format (compact text encoding of adjacency matrices)
- **Save to:** `F:\Prometheus\cartography\physics\data\graphs\`

### PubChem (Molecular properties)
- **What:** 119M compounds with computed descriptors (MW, logP, HBD, HBA, TPSA, etc.)
- **Why failed:** REST API 400 error on batch property queries, CSV batching had parsing issues
- **Manual URL:** https://pubchem.ncbi.nlm.nih.gov/classification/#hid=72 → Download → CSV
- **Alternative:** FTP bulk at ftp://ftp.ncbi.nlm.nih.gov/pubchem/Compound/Extras/
- **What to get:** `CID-Property` file — has all computed descriptors for all compounds
- **Save to:** `F:\Prometheus\cartography\physics\data\pubchem\`

### ChEMBL (Bioactivity)
- **What:** 2.5M compounds with IC50, Ki, molecular properties
- **Why failed:** REST API timeout on molecule endpoint
- **Manual URL:** https://www.ebi.ac.uk/chembl/ → Downloads → SQLite or CSV
- **Direct:** https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/
- **What to get:** `chembl_33_sqlite.tar.gz` (~4GB compressed)
- **Save to:** `F:\Prometheus\cartography\physics\data\chembl\`

### OQMD (Quantum materials)
- **What:** 1.4M materials with DFT formation energies, band gaps, volumes
- **Why failed:** REST API returned empty results (format may have changed)
- **Manual URL:** https://oqmd.org/download → Full database download
- **What to get:** MySQL or SQLite dump
- **Save to:** `F:\Prometheus\cartography\physics\data\oqmd\`

### HITRAN (Molecular spectroscopy)
- **What:** Line-by-line molecular absorption database
- **Why failed:** API endpoint didn't return data (may need authentication)
- **Manual URL:** https://hitran.org/ → Data Access → Line-by-line
- **What to get:** Water (H2O) lines, 0-10000 cm⁻¹, all transitions
- **Format:** CSV or .par format
- **Save to:** `F:\Prometheus\cartography\physics\data\hitran\`

### PDB (Protein structures)
- **What:** 252K protein structures with resolution, molecular weight, atom count
- **Why failed:** GraphQL query syntax error, REST API too slow per-entry
- **Manual URL:** https://www.rcsb.org/docs/search-and-fetch → Custom Report
- **What to get:** Custom report with: PDB ID, resolution, MW, atom count, polymer count, experiment type, space group
- **Format:** CSV download
- **Alternative:** https://data.rcsb.org/rest/v1/holdings/current/entry_ids gives all IDs, then batch fetch
- **Save to:** `F:\Prometheus\cartography\physics\data\pdb\`

---

## Successfully Downloaded (for reference)

| Dataset | Objects | Size | Location |
|---------|---------|------|----------|
| QM9 | 134K | 294 MB | physics/data/qm9/ |
| 3-manifolds | 224K | 14 MB | physics/data/snappy_manifolds.csv |
| Exoplanets | 6.2K | 694 KB | physics/data/exoplanets/ |
| Kepler planets | 2.8K | 362 KB | physics/data/kepler/ |
| Pulsars | 4.4K | 5.3 MB | physics/data/pulsars/ |
| GW events | 219 | 13 KB | physics/data/gravitational_waves/ |
| Nuclear masses | 3.6K | 462 KB | physics/data/nuclear/ |
| Earthquakes M4+ | 95K | 18 MB | physics/data/earthquakes_full/ |
| SDSS stars | 50K | 5 MB | physics/data/sdss/ |
| UniProt proteins | 575K | 284 MB | physics/data/uniprot/ |
| Error Correction Zoo | 1,069 codes | 10 MB | physics/data/codes/eczoo_data/ |
| Materials Project | 10K | 4.4 MB | physics/data/materials_project_10k.json |
| Superconductors | 4K + 41K | 92 MB | physics/data/superconductors/ |
| NIST spectra | 99 elements | 7.5 MB | physics/data/nist_asd/ |
| Particles | 225 | 44 KB | physics/data/pdg/ |
| CODATA constants | 286 | 59 KB | physics/data/codata/ |
| Basis sets | 776 | 276 MB | physics/data/basis_sets/ |

## LMFDB (pulling from devmirror.lmfdb.xyz)

| Table | Rows | Size | Status |
|-------|------|------|--------|
| g2c_curves | 66K | 40 MB | DONE, in Postgres |
| artin_reps | 798K | 445 MB | DONE, in Postgres |
| mf_newforms | 1.1M | 8 GB | DONE, in Postgres |
| ec_curvedata | 3.8M | 1.8 GB | DONE, in Postgres |
| lfunc_lfunctions | 24.2M | ~350 GB | 20M/24.2M (83%) |

All completed files also on Z:\ for M2.

---

## Additional Databases Found (need manual or special download)

### Tier 1: Highest value
- **OQMD** (1.4M materials) — https://oqmd.org/download/ — 21 GB SQL dump
- **JARVIS-DFT** (40K materials) — https://jarvis.nist.gov/ — Figshare JSON
- **HEPData** (138K tables) — https://www.hepdata.net/ — REST API
- **Topological Materials DB** (96K) — https://topologicalquantumchemistry.com/
- **CERN Open Data** — https://opendata.cern.ch/ — derived datasets

### Tier 2: Specialized
- **SuperBand** (2.5K superconductors) — https://www.superband.work/
- **TopoMat** (16.7K 2D materials) — https://www.materialscloud.org/discover/topomat
- **MAGNDATA** (2K magnetic structures) — https://www.cryst.ehu.es/magndata/
- **C2DB** (4K 2D materials) — https://c2db.fysik.dtu.dk/
- **NOMAD** (millions of entries) — https://nomad-lab.eu/
- **Blinkverse FRBs** — https://blinkverse.alkaidos.cn
- **SB9 binary stars** (5K) — https://sb9.astro.ulb.ac.be/
- **AAVSO variable stars** (2M) — https://vsx.aavso.org/

### Tier 3: Networks/connectomes
- **SNAP networks** (50+ graphs) — https://snap.stanford.edu/data/
- **C. elegans connectome** (302 neurons) — https://www.wormwiring.org/
- **GRAND gene networks** (12.5K) — https://grand.networkmedicine.org
- **Network Repository** (thousands) — https://networkrepository.com/

### Tier 4: Earth/climate
- **OpenMindat** (6K minerals) — https://api.mindat.org/
- **RRUFF minerals** — https://www.rruff.net/about/download-data/
- **IGRF-14 geomagnetic field** — https://www.ngdc.noaa.gov/IAGA/vmod/igrf.html
- **Auger cosmic rays** (81K) — https://opendata.auger.org/
- **CRDB cosmic ray flux** — https://lpsc.in2p3.fr/crdb/

### Just Downloaded
- UCI Superconductivity: 21K entries, 81 features — DONE
- Fermi GRBs: 4.3K bursts with spectral params — DONE
- SDSS galaxies: 50K — DONE
- SDSS quasars: 50K — DONE
- Kepler planets: 2.8K extended — DONE
