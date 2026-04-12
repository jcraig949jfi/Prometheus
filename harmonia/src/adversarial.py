"""
Adversarial Ecosystem — hunts for ways to break Harmonia's claims.

Four roles running in a loop:
  Generator: invents attacks (data, representation, structural, cross-domain, metric)
  Executor:  runs the full battery under attack conditions
  Judge:     scores damage to core invariants
  Archivist: logs and prioritizes the most damaging attacks

Runs autonomously. Produces a morning report of what almost broke.
"""
import torch
import numpy as np
import json
import time
import copy
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional
from numpy.linalg import svd, lstsq
from scipy.stats import spearmanr

from harmonia.src.domain_index import DOMAIN_LOADERS, DomainIndex
from harmonia.src.phonemes import PhonemeProjector


# ── Core measurement functions ────────────────────────────────────────

KERNEL_DOMAINS = ['elliptic_curves', 'number_fields', 'genus2']
ARITHMOS_FEAT = {'elliptic_curves': 3, 'number_fields': 3, 'genus2': 2}


def load_kernel(subsample=3000):
    """Load the 3 kernel domains into phoneme space with Arithmos residuals."""
    data = {}
    for name in KERNEL_DOMAINS:
        dom = DOMAIN_LOADERS[name]()
        proj = PhonemeProjector([dom])
        n = min(dom.n_objects, subsample)
        perm = torch.randperm(dom.n_objects)[:n]
        ph = proj.get_phonemes(0, perm).numpy()
        raw = dom.features[perm].numpy()
        M = ph[:, 0]
        target = raw[:, ARITHMOS_FEAT[name]]
        A_mat = np.vstack([M, np.ones(n)]).T
        slope, intercept = lstsq(A_mat, target, rcond=None)[0]
        arithmos = target - (slope * M + intercept)
        data[name] = {
            'ph': ph, 'raw': raw, 'M': M, 'arithmos': arithmos,
            'n': n, 'perm': perm,
        }
    return data


def measure_transfer(data, src='elliptic_curves', tgt='number_fields'):
    """Measure cross-domain Arithmos transfer via phoneme NN."""
    s, t = data[src], data[tgt]
    preds = []
    n_test = min(t['n'], 1500)
    for i in range(n_test):
        dists = np.linalg.norm(s['ph'] - t['ph'][i], axis=1)
        nearest = np.argmin(dists)
        preds.append(s['arithmos'][nearest])
    rho, _ = spearmanr(preds, t['arithmos'][:n_test])
    return rho if not np.isnan(rho) else 0.0


def measure_all(data):
    """Full measurement battery. Returns dict of metrics."""
    metrics = {}

    # Transfer rhos (3 forward directions)
    for src, tgt in [('elliptic_curves', 'number_fields'),
                      ('genus2', 'number_fields'),
                      ('elliptic_curves', 'genus2')]:
        key = f"transfer_{src[:4]}_{tgt[:4]}"
        metrics[key] = measure_transfer(data, src, tgt)

    # Megethos-Arithmos independence
    all_M = np.concatenate([d['M'] for d in data.values()])
    all_A = np.concatenate([d['arithmos'] for d in data.values()])
    rho_ma, _ = spearmanr(all_M, all_A)
    metrics['ma_independence'] = abs(rho_ma) if not np.isnan(rho_ma) else 0

    # PCA of combined phonemes
    all_ph = np.vstack([d['ph'] for d in data.values()])
    all_ph_c = all_ph - all_ph.mean(axis=0)
    if all_ph_c.shape[0] > all_ph_c.shape[1]:
        _, S, _ = svd(all_ph_c, full_matrices=False)
        explained = S**2 / (S**2).sum()
        metrics['pc1_variance'] = float(explained[0])
        metrics['eff_dim'] = float(1.0 / np.sum(explained**2))

    # Z2-only transfer (should be strong)
    data_z2 = copy.deepcopy(data)
    for name in KERNEL_DOMAINS:
        data_z2[name]['ph'] = data_z2[name]['ph'][:, 3:4]
    metrics['z2_only_transfer'] = measure_transfer(data_z2)

    return metrics


# ── Baseline ──────────────────────────────────────────────────────────

def compute_baseline(n_runs=3):
    """Compute stable baseline metrics (average of n runs)."""
    all_metrics = []
    for _ in range(n_runs):
        data = load_kernel()
        all_metrics.append(measure_all(data))
    baseline = {}
    for key in all_metrics[0]:
        vals = [m[key] for m in all_metrics]
        baseline[key] = {'mean': np.mean(vals), 'std': np.std(vals)}
    return baseline


# ── Attack Generator ──────────────────────────────────────────────────

@dataclass
class Attack:
    family: str          # data, representation, structural, cross_domain, metric
    name: str
    params: dict = field(default_factory=dict)
    description: str = ""


def generate_attack(rng=None):
    """Generate a random attack from the mutation vocabulary."""
    if rng is None:
        rng = np.random.default_rng()

    families = {
        'data': [
            ('shuffle_within_domain', lambda r: {'domain': r.choice(KERNEL_DOMAINS)}),
            ('shuffle_arithmos', lambda r: {'domain': r.choice(KERNEL_DOMAINS)}),
            ('remove_high_megethos', lambda r: {'quantile': r.uniform(0.5, 0.9)}),
            ('remove_low_megethos', lambda r: {'quantile': r.uniform(0.1, 0.5)}),
            ('inject_noise', lambda r: {'sigma': r.uniform(0.1, 2.0), 'target': r.choice(['ph', 'arithmos'])}),
            ('subsample_extreme', lambda r: {'n': int(r.uniform(100, 500))}),
        ],
        'representation': [
            ('rank_normalize', lambda r: {}),
            ('monotonic_warp', lambda r: {'power': r.uniform(0.3, 3.0)}),
            ('nonlinear_transform', lambda r: {'kind': r.choice(['exp', 'sigmoid', 'tanh', 'sqrt'])}),
            ('drop_phoneme', lambda r: {'axis': int(r.integers(0, 5))}),
            ('swap_phonemes', lambda r: {'a': int(r.integers(0, 5)), 'b': int(r.integers(0, 5))}),
        ],
        'structural': [
            ('random_grouping', lambda r: {'n_groups': int(r.integers(2, 20))}),
            ('reverse_ordering', lambda r: {'domain': r.choice(KERNEL_DOMAINS)}),
            ('duplicate_domain', lambda r: {'domain': r.choice(KERNEL_DOMAINS)}),
        ],
        'cross_domain': [
            ('swap_domains', lambda r: {'d1': 'elliptic_curves', 'd2': 'number_fields'}),
            ('merge_two_domains', lambda r: {}),
            ('drop_domain', lambda r: {'domain': r.choice(KERNEL_DOMAINS)}),
        ],
        'metric': [
            ('use_cosine_instead', lambda r: {}),
            ('use_l1_distance', lambda r: {}),
            ('scale_arithmos', lambda r: {'factor': r.uniform(0.1, 10.0)}),
        ],
    }

    family = rng.choice(list(families.keys()))
    attack_name, param_fn = families[family][rng.integers(0, len(families[family]))]
    params = param_fn(rng)

    return Attack(
        family=family,
        name=attack_name,
        params=params,
        description=f"{family}/{attack_name}({params})",
    )


# ── Attack Executor ───────────────────────────────────────────────────

def apply_attack(data, attack):
    """Apply an attack to the data and return modified copy."""
    d = copy.deepcopy(data)
    p = attack.params

    if attack.name == 'shuffle_within_domain':
        dom = p['domain']
        perm = np.random.permutation(d[dom]['n'])
        d[dom]['arithmos'] = d[dom]['arithmos'][perm]

    elif attack.name == 'shuffle_arithmos':
        dom = p['domain']
        d[dom]['arithmos'] = np.random.randn(d[dom]['n'])

    elif attack.name == 'remove_high_megethos':
        for name in KERNEL_DOMAINS:
            thresh = np.quantile(d[name]['M'], p['quantile'])
            mask = d[name]['M'] <= thresh
            for key in ['ph', 'raw', 'M', 'arithmos']:
                d[name][key] = d[name][key][mask]
            d[name]['n'] = mask.sum()

    elif attack.name == 'remove_low_megethos':
        for name in KERNEL_DOMAINS:
            thresh = np.quantile(d[name]['M'], p['quantile'])
            mask = d[name]['M'] >= thresh
            for key in ['ph', 'raw', 'M', 'arithmos']:
                d[name][key] = d[name][key][mask]
            d[name]['n'] = mask.sum()

    elif attack.name == 'inject_noise':
        for name in KERNEL_DOMAINS:
            noise = np.random.randn(*d[name][p['target']].shape) * p['sigma']
            d[name][p['target']] = d[name][p['target']] + noise

    elif attack.name == 'subsample_extreme':
        for name in KERNEL_DOMAINS:
            n = min(p['n'], d[name]['n'])
            idx = np.random.choice(d[name]['n'], n, replace=False)
            for key in ['ph', 'raw', 'M', 'arithmos']:
                d[name][key] = d[name][key][idx]
            d[name]['n'] = n

    elif attack.name == 'rank_normalize':
        for name in KERNEL_DOMAINS:
            for col in range(d[name]['ph'].shape[1]):
                order = d[name]['ph'][:, col].argsort().argsort()
                d[name]['ph'][:, col] = order / max(order.max(), 1)

    elif attack.name == 'monotonic_warp':
        power = p['power']
        for name in KERNEL_DOMAINS:
            d[name]['ph'] = np.sign(d[name]['ph']) * np.abs(d[name]['ph']) ** power

    elif attack.name == 'nonlinear_transform':
        kind = p['kind']
        for name in KERNEL_DOMAINS:
            if kind == 'exp':
                d[name]['ph'] = np.clip(np.exp(d[name]['ph']), -100, 100)
            elif kind == 'sigmoid':
                d[name]['ph'] = 1 / (1 + np.exp(-d[name]['ph']))
            elif kind == 'tanh':
                d[name]['ph'] = np.tanh(d[name]['ph'])
            elif kind == 'sqrt':
                d[name]['ph'] = np.sign(d[name]['ph']) * np.sqrt(np.abs(d[name]['ph']))

    elif attack.name == 'drop_phoneme':
        axis = p['axis']
        for name in KERNEL_DOMAINS:
            d[name]['ph'][:, axis] = 0.0

    elif attack.name == 'swap_phonemes':
        a, b = p['a'], p['b']
        for name in KERNEL_DOMAINS:
            d[name]['ph'][:, a], d[name]['ph'][:, b] = (
                d[name]['ph'][:, b].copy(), d[name]['ph'][:, a].copy())

    elif attack.name == 'reverse_ordering':
        dom = p['domain']
        d[dom]['arithmos'] = -d[dom]['arithmos']

    elif attack.name == 'duplicate_domain':
        dom = p['domain']
        d[dom + '_dup'] = copy.deepcopy(d[dom])

    elif attack.name == 'swap_domains':
        d1, d2 = p['d1'], p['d2']
        d[d1], d[d2] = d[d2], d[d1]

    elif attack.name == 'drop_domain':
        dom = p['domain']
        if dom in d and len(d) > 2:
            del d[dom]

    elif attack.name == 'scale_arithmos':
        for name in KERNEL_DOMAINS:
            if name in d:
                d[name]['arithmos'] *= p['factor']

    elif attack.name == 'use_l1_distance':
        pass  # handled in measure_transfer override

    return d


# ── Judge ─────────────────────────────────────────────────────────────

@dataclass
class DamageReport:
    attack: Attack
    metrics_before: dict
    metrics_after: dict
    damage_score: float
    damaged_metrics: list
    interesting: bool = False


def judge(baseline, metrics_after, attack):
    """Score the damage from an attack."""
    damaged = []
    total_damage = 0.0

    weights = {
        'transfer_elli_numb': 3.0,   # most important
        'transfer_genu_numb': 2.0,
        'transfer_elli_genu': 1.0,
        'ma_independence': 2.0,
        'pc1_variance': 1.0,
        'z2_only_transfer': 2.0,
    }

    for key, weight in weights.items():
        if key not in baseline or key not in metrics_after:
            continue
        base_val = baseline[key]['mean']
        after_val = metrics_after[key]
        base_std = max(baseline[key]['std'], 0.01)

        if key == 'ma_independence':
            # Want this to stay LOW; damage if it increases
            change = (after_val - base_val) / base_std
            if change > 2:
                damaged.append(f"{key}: {base_val:.3f} -> {after_val:.3f} (+{change:.1f}σ)")
                total_damage += change * weight
        else:
            # Want these to stay HIGH; damage if they decrease
            change = (base_val - after_val) / base_std
            if change > 2:
                damaged.append(f"{key}: {base_val:.3f} -> {after_val:.3f} (-{change:.1f}σ)")
                total_damage += change * weight

    # Interesting = moderate damage (not catastrophic, not zero)
    interesting = 1.0 < total_damage < 10.0

    return DamageReport(
        attack=attack,
        metrics_before={k: v['mean'] for k, v in baseline.items()},
        metrics_after=metrics_after,
        damage_score=total_damage,
        damaged_metrics=damaged,
        interesting=interesting,
    )


# ── Archivist ─────────────────────────────────────────────────────────

class Archive:
    def __init__(self, max_size=1000):
        self.reports: list[DamageReport] = []
        self.max_size = max_size

    def add(self, report):
        self.reports.append(report)
        if len(self.reports) > self.max_size:
            self.reports.sort(key=lambda r: -r.damage_score)
            self.reports = self.reports[:self.max_size]

    def top_n(self, n=10):
        return sorted(self.reports, key=lambda r: -r.damage_score)[:n]

    def interesting(self):
        return [r for r in self.reports if r.interesting]

    def by_family(self):
        families = {}
        for r in self.reports:
            fam = r.attack.family
            if fam not in families:
                families[fam] = []
            families[fam].append(r)
        return families

    def save(self, path):
        out = []
        for r in sorted(self.reports, key=lambda x: -x.damage_score)[:100]:
            out.append({
                'attack': asdict(r.attack),
                'damage_score': r.damage_score,
                'damaged_metrics': r.damaged_metrics,
                'interesting': r.interesting,
                'metrics_after': r.metrics_after,
            })
        with open(path, 'w') as f:
            json.dump(out, f, indent=2)


# ── Main Loop ─────────────────────────────────────────────────────────

def run_adversarial(n_iterations=500, report_every=50):
    """Run the adversarial ecosystem."""
    print("Computing baseline (3 runs)...")
    baseline = compute_baseline(n_runs=3)
    print("Baseline metrics:")
    for k, v in baseline.items():
        print(f"  {k:>25}: {v['mean']:.4f} ± {v['std']:.4f}")

    archive = Archive()
    rng = np.random.default_rng(42)

    print(f"\nRunning {n_iterations} adversarial attacks...")
    t0 = time.time()

    n_high_damage = 0
    n_interesting = 0

    for i in range(n_iterations):
        attack = generate_attack(rng)

        try:
            data = load_kernel(subsample=2000)
            data_attacked = apply_attack(data, attack)

            # Filter: need at least 2 domains with 50+ objects
            valid_domains = [k for k in data_attacked if isinstance(data_attacked[k], dict)
                            and 'n' in data_attacked[k] and data_attacked[k]['n'] >= 50]
            if len(valid_domains) < 2:
                continue

            metrics = measure_all(data_attacked)
            report = judge(baseline, metrics, attack)
            archive.add(report)

            if report.damage_score > 5:
                n_high_damage += 1
            if report.interesting:
                n_interesting += 1

        except Exception:
            continue

        if (i + 1) % report_every == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            print(f"  [{i+1}/{n_iterations}] {elapsed:.0f}s ({rate:.1f}/s) "
                  f"| high_damage: {n_high_damage} | interesting: {n_interesting}")

    total = time.time() - t0

    # Morning report
    print("\n" + "=" * 60)
    print("MORNING REPORT")
    print("=" * 60)
    print(f"Total attacks: {n_iterations}")
    print(f"Time: {total:.0f}s ({n_iterations/total:.1f} attacks/s)")
    print(f"High damage (>5): {n_high_damage}")
    print(f"Interesting (1-10): {n_interesting}")

    print(f"\nTop 10 most damaging attacks:")
    for r in archive.top_n(10):
        print(f"  [{r.damage_score:>6.1f}] {r.attack.description}")
        for d in r.damaged_metrics[:2]:
            print(f"          {d}")

    # Pattern detection
    print(f"\nDamage by attack family:")
    for fam, reports in archive.by_family().items():
        damages = [r.damage_score for r in reports]
        print(f"  {fam:>15}: n={len(reports)}, mean_damage={np.mean(damages):.2f}, "
              f"max={max(damages):.1f}")

    # Save
    out_path = Path(__file__).resolve().parent.parent / "results" / "adversarial_report.json"
    archive.save(out_path)
    print(f"\nSaved to {out_path}")

    return archive


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    run_adversarial(n_iterations=n)
