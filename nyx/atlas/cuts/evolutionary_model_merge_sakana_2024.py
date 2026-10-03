"""Cut: evolutionary-model-merge-sakana-2024 -- EVALUATION HARNESS for Sakana's evolutionarily merged models (Akiba et al. 2024); the merge search itself is NOT in the body. Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: evaluate.py 33-65; evomerge/utils.py 16-48; evomerge/models/causallm.py 14-60; evomerge/eval/ja_mgsm.py 10-67; evomerge/eval/metrics.py 8-9, 95-101; README.md 12; repository-wide grep for merge / evolutionary / CMA terms (no hits beyond the package name).
NOT read: VLM evaluators, model wrappers other than causallm, the vendored video_blip, most of the README. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('evolutionary-model-merge-sakana-2024', mode="ANCESTRY_AWARE",
        inspected=['evaluate.py 33-65', 'evomerge/utils.py 16-48', 'evomerge/models/causallm.py 14-60', 'evomerge/eval/ja_mgsm.py 10-67', 'evomerge/eval/metrics.py 8-9, 95-101', 'README.md 12', 'repository-wide grep for merge / evolutionary / CMA terms (no hits beyond the package name)'],
        evidence=[('SOURCE_READ', 'vault:evolutionary-model-merge-sakana-2024/upstream/tree/evomerge/eval/ja_mgsm.py:10-67')],
        note="ORGAN0 for the named mechanism: no merging, no evolutionary loop, no fitness-driven selection exists in the tree; what exists is an evaluator of fixed, pre-merged checkpoints. The one organ cut is the scorer [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('mgsm_ja_scoring_by_last_number_regex_with_a_language_gate', human_name='ja_mgsm.py 10-67; metrics.py 95-101', status='ACCEPTED',
    mechanism='the prediction is the last regex match of a decimal number; acc is exact equality with the answer; acc_ja also requires fastText to classify the output as Japanese with probability above 0.5; decoding is greedy',
    input='model outputs', output='accuracy', state='UNKNOWN', failure_landscape="by reading: the regex cannot span thousands separators ('1,000' becomes 0.0); the comma-stripping line is dead code",
    evidence_ref='vault:evolutionary-model-merge-sakana-2024/upstream/tree/evomerge/eval/ja_mgsm.py:10-67', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='ja_mgsm.py 10-67; metrics.py 95-101', coverage={'input_topology': 'SEQUENCE', 'output_topology': 'SCALAR', 'stochasticity': 'DETERMINISTIC'})

c.reject('the rest of the body: VLM evaluators, model wrappers other than causallm, the vendored video_blip, most of the README', reason='OTHER', evidence='NOT READ; residue')
c.reject("'evolutionary-model-merge-sakana-2024' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.reject('the evolutionary model-merge search (parameter-space and data-flow-space merging, CMA-ES over merge recipes)', reason='OTHER',
         evidence='ABSENT from the body: a repository-wide grep finds no merge, evolutionary or CMA code; the README says the repo reproduces the evaluation', note='the record already says EVALUATION ONLY; confirmed')

c.residue('CUT_INSTRUMENT_INSUFFICIENT', ['not read: VLM evaluators, model wrappers other than causallm, the vendored video_blip, most of the README', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='ORGAN0')
