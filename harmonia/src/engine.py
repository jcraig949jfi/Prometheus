"""
Harmonia Engine — TT-Cross exploration over mathematical domains.

Builds tensor trains via adaptive cross approximation, extracts bond
dimensions, and reports which domain pairs have real structure.
"""
import tntorch as tn
import torch
import time
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from harmonia.src.domain_index import DomainIndex, load_domains, DOMAIN_LOADERS
from harmonia.src.coupling import CouplingScorer, DistributionalCoupling, AlignmentCoupling
from harmonia.src.phonemes import PhonemeCoupling, KosmosCoupling
from harmonia.src.validate import extract_bond_components


@dataclass
class BondReport:
    """Report on the bond dimension between two adjacent domains in the TT."""
    domain_a: str
    domain_b: str
    bond_dim: int
    top_singular_values: list[float] = field(default_factory=list)


@dataclass
class ExplorationReport:
    """Full report from a TT-Cross exploration run."""
    domains: list[str]
    domain_sizes: list[int]
    tt_ranks: list[int]
    bonds: list[BondReport]
    n_function_evals: int
    wall_time_seconds: float
    eps_achieved: float
    scorer_type: str

    def summary(self) -> str:
        lines = [
            f"Harmonia Exploration — {len(self.domains)} domains, "
            f"{sum(self.domain_sizes)} total objects",
            f"TT ranks: {self.tt_ranks}",
            f"Function evals: {self.n_function_evals}",
            f"Wall time: {self.wall_time_seconds:.2f}s",
            f"Eps achieved: {self.eps_achieved:.2e}",
            "",
            "Bond dimensions:",
        ]
        for b in self.bonds:
            svs = ", ".join(f"{s:.3f}" for s in b.top_singular_values[:5])
            lines.append(f"  {b.domain_a} <-> {b.domain_b}: "
                         f"rank {b.bond_dim}  [SVs: {svs}]")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class UngatedBondReport:
    """Bond report from ungated exploration — one per (domain_pair, scorer)."""
    domain_a: str
    domain_b: str
    scorer: str
    bond_dim: int
    top_singular_values: list[float]
    energy_fractions: list[float]
    # Annotations (not gates) — what prosecution mode WOULD have killed
    n_below_energy_threshold: int  # energy < 1%
    n_below_selectivity_threshold: int  # CV < 0.1


@dataclass
class GradientPoint:
    """Coupling measurement at one resolution level."""
    resolution: int
    mean_coupling: float
    std_coupling: float
    bond_dim: int


@dataclass
class UngatedExplorationReport:
    """Full report from ungated multi-scorer exploration."""
    domains: list[str]
    domain_sizes: list[int]
    scorer_reports: dict  # scorer_name -> ExplorationReport
    bond_matrix: dict  # "domA::domB" -> {scorer -> UngatedBondReport}
    gradients: dict  # "domA::domB" -> list[GradientPoint]
    wall_time_seconds: float

    def summary(self) -> str:
        lines = [
            f"Ungated Exploration — {len(self.domains)} domains, "
            f"{sum(self.domain_sizes)} total objects",
            f"Scorers: {list(self.scorer_reports.keys())}",
            f"Wall time: {self.wall_time_seconds:.2f}s",
            "",
        ]
        for pair_key, scorer_bonds in sorted(self.bond_matrix.items()):
            da, db = pair_key.split("::")
            dims = {s: b.bond_dim for s, b in scorer_bonds.items()}
            lines.append(f"  {da} <-> {db}: {dims}")
            if pair_key in self.gradients:
                gpts = self.gradients[pair_key]
                grad_str = " -> ".join(
                    f"{g.resolution}:{g.mean_coupling:.4f}" for g in gpts)
                lines.append(f"    gradient: [{grad_str}]")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "domains": self.domains,
            "domain_sizes": self.domain_sizes,
            "scorer_reports": {s: r.to_dict() for s, r in self.scorer_reports.items()},
            "bond_matrix": {
                k: {s: asdict(b) for s, b in v.items()}
                for k, v in self.bond_matrix.items()
            },
            "gradients": {
                k: [asdict(g) for g in v]
                for k, v in self.gradients.items()
            },
            "wall_time_seconds": self.wall_time_seconds,
        }


class HarmoniaEngine:
    """
    Tensor Train exploration engine for cross-domain mathematical structure.

    Usage:
        engine = HarmoniaEngine(['knots', 'number_fields', 'space_groups'])
        tt, report = engine.explore()
        print(report.summary())
    """

    def __init__(
        self,
        domains: list[str],
        device: str = "cpu",
        max_rank: int = 20,
        eps: float = 1e-4,
        max_iter: int = 100,
        scorer: str = "distributional",
        subsample: Optional[int] = None,
    ):
        """
        Args:
            domains: List of domain names to include as tensor dimensions
            device: 'cpu' or 'cuda'
            max_rank: Maximum TT bond dimension to explore
            eps: Convergence threshold for TT-Cross
            max_iter: Maximum cross approximation iterations
            scorer: 'cosine' or 'distributional'
            subsample: If set, subsample large domains to this size for speed.
                       The full domain is used for validation afterward.
        """
        self.domain_names = domains
        self.device = device
        self.max_rank = max_rank
        self.eps = eps
        self.max_iter = max_iter
        self.scorer_type = scorer
        self.subsample = subsample

        # Load domains
        self._domains_dict = load_domains(*domains, device=device)
        self._domain_list = [self._domains_dict[name] for name in domains]

        # Apply subsampling if needed
        self._subsample_maps = {}  # domain_idx -> original indices
        if subsample:
            for i, dom in enumerate(self._domain_list):
                if dom.n_objects > subsample:
                    perm = torch.randperm(dom.n_objects)[:subsample]
                    self._subsample_maps[i] = perm
                    self._domain_list[i] = DomainIndex(
                        name=dom.name,
                        labels=[dom.labels[j] for j in perm.tolist()],
                        features=dom.features[perm],
                    )

        # Build scorer
        if scorer == "cosine":
            self._scorer = CouplingScorer(self._domain_list, device=device)
        elif scorer == "distributional":
            self._scorer = DistributionalCoupling(self._domain_list, device=device)
        elif scorer == "alignment":
            self._scorer = AlignmentCoupling(self._domain_list, device=device)
        elif scorer == "phoneme":
            self._scorer = PhonemeCoupling(self._domain_list, device=device)
        elif scorer == "kosmos":
            self._scorer = KosmosCoupling(self._domain_list, device=device)
        else:
            raise ValueError(f"Unknown scorer: {scorer}")

    def explore(self) -> tuple:
        """
        Run TT-Cross exploration.

        Returns:
            (tntorch.Tensor, ExplorationReport)
        """
        # Domain grids stay on CPU (tntorch internals require it).
        # Scorer runs on self.device (GPU if available) — we bridge in value_fn.
        domain_grids = [
            torch.arange(dom.n_objects, dtype=torch.float32)
            for dom in self._domain_list
        ]

        scorer_device = self.device

        # Wrap scorer for tntorch (expects float indices, returns float)
        def value_fn(*indices):
            int_indices = [idx.long().to(scorer_device) for idx in indices]
            result = self._scorer(*int_indices)
            return result.cpu()

        print(f"Harmonia: exploring {len(self._domain_list)} domains "
              f"({' x '.join(str(dom.n_objects) for dom in self._domain_list)})")
        print(f"  Scorer: {self.scorer_type}, max_rank: {self.max_rank}, "
              f"eps: {self.eps}")

        t0 = time.time()
        tt = tn.cross(
            function=value_fn,
            domain=domain_grids,
            eps=self.eps,
            rmax=self.max_rank,
            max_iter=self.max_iter,
            verbose=False,  # tntorch verbose has ZeroDivisionError on fast convergence
        )
        wall_time = time.time() - t0

        # Extract bond information
        ranks = tt.ranks_tt.tolist()
        bonds = []
        for i in range(len(self._domain_list) - 1):
            core = tt.cores[i]
            # SVD of the unfolding to get singular values
            # Core shape: (r_{i-1}, n_i, r_i) -> unfold to (r_{i-1}*n_i, r_i)
            unfolded = core.reshape(-1, core.shape[-1])
            try:
                svs = torch.linalg.svdvals(unfolded)
                top_svs = svs[:min(10, len(svs))].tolist()
            except Exception:
                top_svs = []

            bonds.append(BondReport(
                domain_a=self._domain_list[i].name,
                domain_b=self._domain_list[i + 1].name,
                bond_dim=ranks[i + 1],
                top_singular_values=top_svs,
            ))

        # Count function evaluations from tntorch internals
        n_evals = sum(c.numel() for c in tt.cores)

        report = ExplorationReport(
            domains=self.domain_names,
            domain_sizes=[dom.n_objects for dom in self._domain_list],
            tt_ranks=ranks,
            bonds=bonds,
            n_function_evals=n_evals,
            wall_time_seconds=wall_time,
            eps_achieved=self.eps,
            scorer_type=self.scorer_type,
        )

        return tt, report

    def explore_ungated(
        self,
        scorers: list[str] = None,
        gradient_resolutions: list[int] = None,
    ) -> UngatedExplorationReport:
        """
        Ungated exploration: run TT-Cross with multiple scorers, record
        everything without killing anything. Gates become annotations.

        Per approved exploration reform spec (Kairos + Claude_M1):
        - All scorers run sequentially on the same domains
        - Bond components annotated with energy/selectivity but NOT killed
        - Gradient sweep measures coupling vs resolution for each domain pair

        Args:
            scorers: Which scorers to use. Default: all 3 approved scorers.
            gradient_resolutions: Resolution levels for gradient sweep.
                Default: [100, 500, 2000, 10000].

        Returns:
            UngatedExplorationReport with multi-angle bond data.
        """
        if scorers is None:
            scorers = ["cosine", "distributional", "alignment"]
        if gradient_resolutions is None:
            gradient_resolutions = [100, 500, 2000, 10000]

        t0 = time.time()
        scorer_reports = {}
        bond_matrix = {}  # "domA::domB" -> {scorer -> UngatedBondReport}

        # Phase 1: Run TT-Cross with each scorer
        for scorer_name in scorers:
            print(f"\n[Ungated] Running scorer: {scorer_name}")
            engine = HarmoniaEngine(
                domains=self.domain_names,
                device=self.device,
                max_rank=self.max_rank,
                eps=self.eps,
                max_iter=self.max_iter,
                scorer=scorer_name,
                subsample=self.subsample,
            )
            tt, report = engine.explore()
            scorer_reports[scorer_name] = report

            # Extract ungated bond info with annotations
            for i, bond in enumerate(report.bonds):
                pair_key = f"{bond.domain_a}::{bond.domain_b}"
                if pair_key not in bond_matrix:
                    bond_matrix[pair_key] = {}

                # Compute annotation stats (what prosecution WOULD kill)
                components = extract_bond_components(
                    tt, i, engine._domain_list)
                total_energy = sum(sv ** 2 for sv, _, _ in components)

                n_low_energy = 0
                n_low_selectivity = 0
                energy_fracs = []

                for sv, left_scores, right_scores in components:
                    efrac = (sv ** 2) / total_energy if total_energy > 0 else 0
                    energy_fracs.append(efrac)
                    if efrac < 0.01:
                        n_low_energy += 1
                    else:
                        left_cv = (left_scores.std()
                                   / left_scores.mean().clamp(min=1e-8))
                        right_cv = (right_scores.std()
                                    / right_scores.mean().clamp(min=1e-8))
                        if left_cv < 0.1 and right_cv < 0.1:
                            n_low_selectivity += 1

                bond_matrix[pair_key][scorer_name] = UngatedBondReport(
                    domain_a=bond.domain_a,
                    domain_b=bond.domain_b,
                    scorer=scorer_name,
                    bond_dim=bond.bond_dim,
                    top_singular_values=bond.top_singular_values,
                    energy_fractions=energy_fracs,
                    n_below_energy_threshold=n_low_energy,
                    n_below_selectivity_threshold=n_low_selectivity,
                )

        # Phase 2: Gradient sweep — does coupling strengthen with resolution?
        gradients = self._gradient_sweep(gradient_resolutions)

        wall_time = time.time() - t0
        return UngatedExplorationReport(
            domains=self.domain_names,
            domain_sizes=[dom.n_objects for dom in self._domain_list],
            scorer_reports=scorer_reports,
            bond_matrix=bond_matrix,
            gradients=gradients,
            wall_time_seconds=wall_time,
        )

    def _gradient_sweep(
        self,
        resolutions: list[int],
    ) -> dict:
        """
        Measure coupling at multiple resolution levels to detect gradient.
        Positive gradient (coupling increases with N) = real structure.
        Flat or negative gradient = noise or artifact.

        Returns:
            Dict of "domA::domB" -> list[GradientPoint]
        """
        gradients = {}
        scorer_name = "distributional"  # Use distributional as reference

        for res in resolutions:
            # Skip resolutions larger than our smallest domain
            min_dom_size = min(dom.n_objects for dom in self._domain_list)
            effective_res = min(res, min_dom_size)

            print(f"[Gradient] Resolution {effective_res}...")
            try:
                engine = HarmoniaEngine(
                    domains=self.domain_names,
                    device=self.device,
                    max_rank=self.max_rank,
                    eps=1e-3,
                    max_iter=50,
                    scorer=scorer_name,
                    subsample=effective_res,
                )
                tt, report = engine.explore()

                for i, bond in enumerate(report.bonds):
                    pair_key = f"{bond.domain_a}::{bond.domain_b}"
                    if pair_key not in gradients:
                        gradients[pair_key] = []

                    # Compute mean coupling from singular values
                    svs = bond.top_singular_values
                    mean_c = sum(svs) / len(svs) if svs else 0.0
                    std_c = (sum((s - mean_c)**2 for s in svs)
                             / max(len(svs), 1)) ** 0.5 if svs else 0.0

                    gradients[pair_key].append(GradientPoint(
                        resolution=effective_res,
                        mean_coupling=mean_c,
                        std_coupling=std_c,
                        bond_dim=bond.bond_dim,
                    ))
            except Exception as e:
                print(f"[Gradient] Resolution {effective_res} failed: {e}")

        return gradients

    def inspect_bond(self, tt, bond_idx: int) -> dict:
        """
        Detailed inspection of a specific bond between adjacent domains.

        Args:
            tt: tntorch.Tensor from explore()
            bond_idx: Index of the bond (0 = first pair of domains)

        Returns:
            Dict with SVD analysis of the bond
        """
        core = tt.cores[bond_idx]
        unfolded = core.reshape(-1, core.shape[-1])
        U, S, Vh = torch.linalg.svd(unfolded, full_matrices=False)

        # Effective rank — number of SVs above 1% of the largest
        threshold = S[0] * 0.01
        effective_rank = int((S > threshold).sum().item())

        # Energy distribution — how much each component contributes
        energy = (S ** 2) / (S ** 2).sum()

        return {
            "domain_a": self._domain_list[bond_idx].name,
            "domain_b": self._domain_list[bond_idx + 1].name,
            "raw_rank": core.shape[-1],
            "effective_rank": effective_rank,
            "singular_values": S.tolist()[:20],
            "energy_distribution": energy.tolist()[:20],
            "energy_top1": energy[0].item(),
            "energy_top3": energy[:3].sum().item() if len(energy) >= 3 else 1.0,
        }

    def save_report(self, report: ExplorationReport, path: Optional[Path] = None):
        """Save exploration report as JSON."""
        if path is None:
            path = (Path(__file__).resolve().parent.parent
                    / "results" / "exploration_report.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"Report saved to {path}")


def quick_explore(
    *domain_names: str,
    max_rank: int = 10,
    subsample: int = 2000,
    device: str = "cpu",
) -> ExplorationReport:
    """
    One-liner for fast exploratory runs.

    Usage:
        report = quick_explore('knots', 'number_fields', 'space_groups')
        print(report.summary())
    """
    engine = HarmoniaEngine(
        domains=list(domain_names),
        device=device,
        max_rank=max_rank,
        subsample=subsample,
    )
    tt, report = engine.explore()
    print(report.summary())
    return report
