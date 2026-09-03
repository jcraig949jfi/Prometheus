import os
import argparse
import numpy as np
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List
from typing import Any
import json
import re
from tqdm import tqdm
import pandas as pd

import helper

#Explore mutational neighborhood of GRN.

@dataclass
class GRNFileInfo:
    """Store parsed information from a GRN results filename."""

    iterations: int
    rules: List[int]
    seeds: List[int]
    repetition: int
    filename: str

class GRNFilenameParser:
    @staticmethod
    def parse(filename: Path) -> GRNFileInfo:
        filename_str = filename.as_posix()

        # Try the complex format first (with paired numbers)
        complex_pattern = r"stats_(\d+)_(\d+-\d+)_(\d+-\d+)_(\d+)_best_grn\.txt$"
        complex_match = re.search(complex_pattern, filename_str)

        if complex_match:
            iterations = int(complex_match.group(1))
            rules = [int(x) for x in complex_match.group(2).split("-")]
            seeds = [int(x) for x in complex_match.group(3).split("-")]
            repetition = int(complex_match.group(4))
            return GRNFileInfo(iterations, rules, seeds, repetition, filename_str)

        # Try the simple format
        simple_pattern = r"stats_(\d+)_(\d+)_(\d+)_(\d+)_best_grn\.txt$"
        simple_match = re.search(simple_pattern, filename_str)

        if simple_match:
            iterations = int(simple_match.group(1))
            rules = [int(simple_match.group(2))]
            seeds = [int(simple_match.group(3))]
            repetition = int(simple_match.group(4))
            return GRNFileInfo(iterations, rules, seeds, repetition, filename_str)

        raise ValueError(f"Unrecognized filename format: {filename}")

class JSONLogger:
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def append(self, results: Any) -> None:
        with self.filepath.open("a") as f:
            f.write(json.dumps(results) + "\n")

    def read(self) -> list:
        results = []
        with open(self.filepath) as f:
            results = [json.loads(line) for line in f]
        return results

def explore_noise(filename, seeds, rule, noise_scaling, candidate_idx, grn_size = 22, num_cells = 22, dev_steps = 22, geneid=1, nclones=1000):
    seeds = [69904,149796]
    grns = np.loadtxt(filename)
    num_grns = int(grns.shape[0] / (grn_size + 2) / grn_size)
    grns = grns.reshape(num_grns, grn_size + 2, grn_size)

    candidate = grns[candidate_idx]
    clones = np.tile(candidate, (nclones, 1, 1))
    noise = np.random.randn(*clones.shape) * noise_scaling
    clones += noise
    clones[0] = candidate
    target1, phenos1, fitnesses1 = helper.get_pop_TPF(
        clones, len(clones), num_cells, grn_size, dev_steps, geneid, rule, seeds[0], seeds[0]
    )
    target2, phenos2, fitnesses2 = helper.get_pop_TPF(
        clones, len(clones), num_cells, grn_size, dev_steps, geneid, rule, seeds[1], seeds[1]
    )
    #fitnesses = score(phenos, target)
    return [phenos1,phenos2], [target1,target2], [fitnesses1,fitnesses2]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--rule', type=int, default=30, help='List of rules')    
    parser.add_argument('--exp_type', type=str, default="variable", help="Variable or static")
    parser.add_argument('--candidate_idx', type=str, default="-1", help="Which generation to check")

    args = parser.parse_args()

    if args.exp_type == "variable":
        args.season_len = 300
    else:
        args.season_len = 100_000

    root="~/CA_GRN_results/detailed_save/"
    dir_path = Path(f"~/CA_GRN_results/detailed_save/{args.exp_type}/").expanduser()

    files = [file for file in dir_path.iterdir() if file.is_file() and file.name.startswith(f"stats_{args.season_len}_{args.rule}") and file.name.endswith("_best_grn.txt")]

    M = 0.3 #max noise
    N = 1 #number of noise levels to test
    nrows = 50 #x**2 is number of clones

    out_filename1 = os.path.expanduser(f"~/scratch/testing_noisy/stats_{args.rule}_{args.exp_type}2_{args.candidate_idx}_env1_unsorted_noise_data.jsonl")
    out_filename2 = os.path.expanduser(f"~/scratch/testing_noisy/stats_{args.rule}_{args.exp_type}2_{args.candidate_idx}_env2_unsorted_noise_data.jsonl")

    df_outfilename = os.path.expanduser(f"~/scratch/testing_noisy/stats_{args.rule}_{args.exp_type}2_{args.candidate_idx}_pheno_data.csv")

    log1 = JSONLogger(out_filename1)
    log2 = JSONLogger(out_filename2)

    df = pd.DataFrame(columns=["Pheno_dists1", "Pheno_stds1", "Pheno_dists2", "Pheno_stds2"])

    for filename in tqdm(files, position=0):
        if "149796" in filename.name:
            print(filename)
            params = GRNFilenameParser.parse(filename)
            data1 = []
            data2 = []
            noise_levels = np.linspace(0.063, M, N).tolist()
            for noise_scaling in tqdm(noise_levels, position=1, leave=False):
                phenos, target, fitnesses = explore_noise(
                    filename,
                    seeds=params.seeds,
                    noise_scaling=noise_scaling,
                    candidate_idx = int(args.candidate_idx),
                    rule=params.rules[0],
                    nclones=nrows * nrows,
                )
                #data1.append(np.sort(fitnesses[0]).tolist())
                #data2.append(np.sort(fitnesses[1]).tolist())
                if noise_scaling > 0.06 and noise_scaling < 0.065:
                    candidate_pheno1 = phenos[0][0]
                    candidate_pheno2 = phenos[1][0]
                    candidate_pheno1s = np.tile(candidate_pheno1, (nrows*nrows,1,1))
                    candidate_pheno2s = np.tile(candidate_pheno2, (nrows*nrows,1,1))
                    diffs1 = np.abs(candidate_pheno1s - phenos[0]).reshape((nrows*nrows,23*22)).sum(axis=1)[1:].mean()
                    diffs2 = np.abs(candidate_pheno2s - phenos[1]).reshape((nrows*nrows,23*22)).sum(axis=1)[1:].mean()
                    stds1 = np.std(np.array(phenos[0])[1:,:,:].reshape(nrows*nrows-1,23*22), axis=0).mean()
                    stds2 = np.std(np.array(phenos[1])[1:,:,:].reshape(nrows*nrows-1,23*22), axis=0).mean()
                    row = {
                    "Pheno_dists1": diffs1,
                    "Pheno_stds1": stds1,
                    "Pheno_dists2": diffs2,
                    "Pheno_stds2": stds2
                    }
                    # Append the row to the DataFrame
                    df = df._append(row, ignore_index=True)
                data1.append(fitnesses[0].tolist())
                data2.append(fitnesses[1].tolist())
            to_log1 = {
                "file": filename.as_posix(),
                "params": asdict(params),
                "data": data1,
                "noise_levels": noise_levels,
                "env": 0
            }
            to_log2 = {
                "file": filename.as_posix(),
                "params": asdict(params),
                "data": data2,
                "noise_levels": noise_levels,
                "env": 1
            }
            log1.append(to_log1)
            log2.append(to_log2)

    df.to_csv(df_outfilename, index=False)