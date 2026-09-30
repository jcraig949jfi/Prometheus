"""Apparatus for the Avida ancestry cut (operator directive 2026-09-18 s3: Nyx cuts the save / population /
ancestry mechanics; Harmonia builds the ruler). Four modules, stdlib only:

    spop.py         reads a Structured Population Save the way the fossil WRITES it, and computes the packet's
                    observables. Written from the source (Genotype::LegacySave, cPopulation::SavePopulation,
                    Output::File), never from a .spop file.
    model.py        a reference model of the retention rule the cut claims (GenotypeArbiter), driven by a toy
                    population; it writes .spop text in the fossil's format. Used for fixtures and controls only.
    strata.py       the frozen file list with CONFIG-derived flags (it opens no .spop).
    definedness.py  Harmonia rule A5: every observable is checked DEFINED on a small synthetic fixture for every
                    arm before the packet hash; plus the cheat / positive / negative controls on fixtures.
"""
