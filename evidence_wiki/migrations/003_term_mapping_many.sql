-- A single source term may legitimately map to more than one canonical term
-- (a source sentence can describe two mechanisms). Make the mapping
-- many-to-many; each row still records who mapped it and how.
ALTER TABLE ew.term_mappings DROP CONSTRAINT IF EXISTS term_mappings_pkey;
ALTER TABLE ew.term_mappings ADD PRIMARY KEY (dimension, source_term, term_id, ontology_version);
