import sys
import tyche.v2.run_v2 as R

if __name__ == "__main__":
    R.CFG.update(N=16, screen_pairs=20, fit_pairs=3, screen_triples=20, fit_triples=2, drift_per_gen=3,
                 reserve_size=8, null_n=3, gens_per_epoch=2)
    sys.argv = ["x"] + sys.argv[1:]
    R.main()
