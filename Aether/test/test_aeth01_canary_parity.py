"""Offline packaging parity, not evidence of CuPy/CUDA execution.

Imports use a CuPy-shaped stub or an explicit unavailable-module sentinel;
no real CuPy, environment configuration, credentials, or network are used.
"""

import ast
from contextlib import contextmanager
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest


TEST_ROOT = Path(__file__).resolve().parent
REFERENCE = TEST_ROOT / "reference"
CANARY = TEST_ROOT.parent / "runpod" / "aeth01_canary"
GPU_PATH = CANARY / "aeth01_gpu_kernel.py"
CPU_PATH = CANARY / "aeth01_cpu_oracle.py"

# Normalize ONLY this exact backend/warning shim, not arbitrary try blocks.
_BACKEND_SHIM = """\
try:
    import cupy as np
    BACKEND = "cupy"
except ImportError:
    import numpy as np
    BACKEND = "numpy_fallback"
    np.seterr(over="ignore")
"""


class _WithoutDocumentation(ast.NodeTransformer):
    def _body(self, node):
        if (node.body and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)):
            node.body.pop(0)
        return self.generic_visit(node)

    visit_Module = _body
    visit_ClassDef = _body
    visit_FunctionDef = _body
    visit_AsyncFunctionDef = _body

    def visit_Pass(self, node):
        return None


def _tree(path):
    return _WithoutDocumentation().visit(ast.parse(path.read_text(encoding="utf-8")))


def _dump(node):
    return ast.dump(node, include_attributes=False, indent=2)


def _gpu_physics_tree(path, *, bundled):
    tree = _tree(path)
    if bundled:
        assert _dump(tree.body.pop(0)) == _dump(ast.parse(_BACKEND_SHIM).body[0])
    else:
        assert _dump(tree.body.pop(0)) == _dump(ast.parse("import numpy as np").body[0])
        warning_call = _dump(ast.parse('np.seterr(over="ignore")').body[0])
        matches = [node for node in tree.body if _dump(node) == warning_call]
        assert len(matches) == 1
        tree.body.remove(matches[0])

        # The bundle already omits these six np.ndarray annotations. Do not
        # normalize signatures, defaults, decorators, or executable bodies.
        annotations = set()
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            for arg in node.args.args:
                if arg.annotation is not None:
                    assert _dump(arg.annotation) == _dump(ast.parse("np.ndarray").body[0].value)
                    annotations.add((node.name, arg.arg))
                    arg.annotation = None
            if node.returns is not None:
                assert _dump(node.returns) == _dump(ast.parse("np.ndarray").body[0].value)
                annotations.add((node.name, "return"))
                node.returns = None
        assert annotations == {
            ("mix64_vec", "x"), ("mix64_vec", "return"),
            ("pack_coords_vec", "row"), ("pack_coords_vec", "col"),
            ("pack_coords_vec", "return"), ("arbitration_priority_vec", "return"),
        }
    return tree


def test_cpu_all_executable_definitions_match_reference():
    # Includes every constant, class, signature, body, and serialization method;
    # there is deliberately no omitted-method allowlist.
    assert _dump(_tree(CPU_PATH)) == _dump(_tree(REFERENCE / "oracle_aeth01.py"))


def test_gpu_all_physics_bodies_and_constants_match_reference():
    assert _dump(_gpu_physics_tree(GPU_PATH, bundled=True)) == _dump(
        _gpu_physics_tree(REFERENCE / "gpu_aeth01.py", bundled=False)
    )


@contextmanager
def _offline_imports(cupy=None):
    # None blocks the import even if CuPy is installed/already imported.
    # Both successful and failing imports restore module bindings and NumPy's
    # error policy. No sys.path edits are necessary.
    with pytest.MonkeyPatch.context() as patch, np.errstate():
        patch.setitem(sys.modules, "cupy", cupy)
        yield patch


def _load_module(path, patch):
    name = f"_aeth01_parity_{path.stem}"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    patch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    return module


def test_cupy_shaped_import_without_seterr_succeeds():
    cupy = ModuleType("cupy")
    # Explicit dtype allowlist, NOT a proxy forwarding missing names to NumPy.
    for name in ("uint8", "uint64", "int64", "ndarray"):
        setattr(cupy, name, getattr(np, name))
    assert not hasattr(cupy, "seterr")
    with np.errstate(over="raise"), _offline_imports(cupy) as patch:
        errors = np.geterr()
        kernel = _load_module(GPU_PATH, patch)
        assert kernel.BACKEND == "cupy"
        assert kernel.np is cupy
        assert kernel.U64 is np.uint64
        assert int(kernel.MASK64) == (1 << 64) - 1
        assert np.geterr() == errors


def test_numpy_fallback_preserves_existing_overflow_policy():
    with np.errstate(divide="raise", over="warn", under="raise", invalid="raise"):
        with _offline_imports() as patch:
            errors = np.geterr()
            kernel = _load_module(GPU_PATH, patch)
            assert kernel.BACKEND == "numpy_fallback"
            assert kernel.np is np
            assert np.geterr() == {**errors, "over": "ignore"}
        assert np.geterr() == errors


@pytest.mark.parametrize("fail_import", [False, True])
def test_import_isolation_restores_state_even_on_failure(fail_import):
    absent = object()
    names = ("cupy", "_aeth01_parity_aeth01_gpu_kernel")
    before = {name: sys.modules.get(name, absent) for name in names}
    path_before, errors_before = list(sys.path), np.geterr()
    # Missing uint64 intentionally fails after the CuPy branch is selected.
    with _offline_imports(ModuleType("cupy") if fail_import else None) as patch:
        if fail_import:
            with pytest.raises(AttributeError, match="uint64"):
                _load_module(GPU_PATH, patch)
        else:
            _load_module(GPU_PATH, patch)
    for name in names:
        assert sys.modules.get(name, absent) is before[name]
    assert sys.path == path_before
    assert np.geterr() == errors_before


@pytest.fixture
def modules():
    with _offline_imports() as patch:
        source_cpu = _load_module(REFERENCE / "oracle_aeth01.py", patch)
        cpu = _load_module(CPU_PATH, patch)
        source_gpu = _load_module(REFERENCE / "gpu_aeth01.py", patch)
        gpu = _load_module(GPU_PATH, patch)
        assert gpu.BACKEND == "numpy_fallback"
        # Bind the fixture builder's import to our isolated source oracle, not
        # an arbitrary cached reference package. All bindings are restored.
        reference = ModuleType("reference")
        reference.__path__ = []
        reference.oracle_aeth01 = source_cpu
        patch.setitem(sys.modules, "reference", reference)
        patch.setitem(sys.modules, "reference.oracle_aeth01", source_cpu)
        scientific = _load_module(REFERENCE / "scientific_aeth01.py", patch)
        yield SimpleNamespace(cpu=cpu, gpu=gpu, source_cpu=source_cpu,
                              source_gpu=source_gpu, scientific=scientific)


def _parameters(world):
    return (world.H, world.W, world.seed, world.write_cost, world.maintenance_cost,
            world.replenish_numer, world.replenish_amount, world.mut_numer)


def _assert_trajectory(modules, world, label, steps=5):
    initial_bytes = bytes(value for row in world.grid for site in row for value in site)
    assert world.to_bytes() == initial_bytes, label
    bundled = modules.cpu.Aeth01World.from_bytes(
        *_parameters(world), data=initial_bytes, tick=world.tick
    )
    replay = modules.source_cpu.Aeth01World.from_bytes(
        *_parameters(world), data=initial_bytes, tick=world.tick
    )
    assert vars(bundled) == vars(replay) == vars(world), label
    assert bundled.to_bytes() == replay.to_bytes() == initial_bytes, label
    world = replay
    trajectories = {}
    for name in ("gpu", "source_gpu"):
        initial = np.array(world.grid, dtype=np.uint8)
        trajectories[name] = [initial[:, :, f].copy() for f in range(5)]

    for _ in range(steps):
        msg = f"{label} tick={world.tick}"
        previous = world.to_bytes()
        source_trace, bundled_trace = [], []
        source_next = world.step(trace=source_trace)
        bundled_next = bundled.step(trace=bundled_trace)
        assert vars(bundled_next) == vars(source_next), msg
        assert bundled_trace == source_trace, msg
        assert bundled_next.to_bytes() == source_next.to_bytes(), msg
        assert world.to_bytes() == bundled.to_bytes() == previous, msg
        emitted = sum(event[0] == "proposal_emitted" for event in source_trace)
        counters = {
            "activity_density": emitted / (world.H * world.W),
            "total_energy": sum(site[4] for row in source_next.grid for site in row),
        }
        for name, arrays in trajectories.items():
            # Each implementation consumes its OWN prior output, not a reset
            # from the oracle at each tick.
            output = getattr(modules, name).gpu_step(
                world.H, world.W, world.seed, world.tick, *_parameters(world)[3:], *arrays
            )
            for array in output[:5]:
                assert array.dtype == np.uint8 and array.shape == (world.H, world.W), msg
            assert np.stack(output[:5], axis=-1).tobytes() == source_next.to_bytes(), msg
            assert output[5] == counters, msg
            trajectories[name] = output[:5]
        world, bundled = source_next, bundled_next


def test_full_k3_corpus_multitick_parity(modules):
    cases = list(modules.scientific.k3_intervention_cases())
    assert cases
    for label, world in cases:
        _assert_trajectory(modules, world, label)


@pytest.mark.parametrize("grid,parameters", [
    ([[(1, 1, 0, 7, 100), (0, 0, 0, 0, 0)]], {"write_cost": 5}),
    ([[(1, 1, 4, 30, 50), (0, 0, 0, 0, 0), (1, 3, 4, 40, 80)]], {"write_cost": 5}),
    ([[(1, 1, 4, 250, 200), (0, 0, 0, 0, 100)]], {"write_cost": 2}),
    ([[(1, 0, 4, 100, 50)]], {"write_cost": 3}),
    ([[(0, 0, 0, 0, 2)]], {"maintenance_cost": 5}),
    ([[(0, 0, 0, 0, 250)]], {"replenish_numer": 1 << 32, "replenish_amount": 20}),
    ([[(1, 255, 255, 255, 254)]], {"write_cost": 255, "maintenance_cost": 255}),
    ([[(1, 255, 253, 255, 0)]], {"mut_numer": 1 << 32}),
], ids=["template", "contest", "spill", "self-transfer", "decay", "replenish",
        "starved", "free-write-perturbation"])
def test_hand_boundary_multitick_parity(modules, grid, parameters):
    kwargs = dict(write_cost=0, maintenance_cost=0, replenish_numer=0,
                  replenish_amount=0, mut_numer=0)
    kwargs.update(parameters)
    world = modules.source_cpu.Aeth01World(
        len(grid), len(grid[0]), seed=(1 << 64) - 1,
        tick=(1 << 64) - 6, grid=grid, **kwargs
    )
    _assert_trajectory(modules, world, str(parameters))


@pytest.mark.parametrize("H,W", [(1, 1), (1, 2), (2, 1), (2, 2)])
@pytest.mark.parametrize("numer", [0, 1, 1 << 31, 1 << 32])
def test_torus_probability_boundaries_multitick_parity(modules, H, W, numer):
    grid = [[(1, r * W + c, (r + c + 3) % 5, 255, 255)
             for c in range(W)] for r in range(H)]
    world = modules.source_cpu.Aeth01World(H, W, 0, 1, 1, numer, 255, numer, grid=grid)
    _assert_trajectory(modules, world, f"{H}x{W} numer={numer}")


@pytest.mark.parametrize("size", [0, 4, 6])
def test_serialization_rejects_wrong_buffer_lengths_identically(modules, size):
    messages = []
    for module in (modules.cpu, modules.source_cpu):
        with pytest.raises(ValueError) as error:
            module.Aeth01World.from_bytes(1, 1, 0, 0, 0, 0, 0, 0, bytes(size))
        messages.append(str(error.value))
    assert messages[0] == messages[1]


def test_cpu_tick_overflow_parity(modules):
    messages = []
    for module in (modules.cpu, modules.source_cpu):
        world = module.Aeth01World(1, 1, 0, 0, 0, 0, 0, 0, tick=module.MASK64)
        with pytest.raises(module.TickOverflowError) as error:
            world.step()
        messages.append(str(error.value))
    assert messages[0] == messages[1]