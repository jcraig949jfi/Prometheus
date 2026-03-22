import torch
from tii_engine import execute_tii_generation, TII_GENERATION_FAILED
from genome import SteeringGenome
from ignis_logger import slog, LogContext


def run_latent_probe(model, genome, task_prompt) -> dict:
    """
    Ignis Causal Falsification Battery.
    Tests if the steering vector is the CAUSAL driver or just noise.

    Runs five tests:
      1. Primary injection (+v)
      2. Null-A: Norm-matched Gaussian noise
      3. Null-B: Orthogonal projection (Gram-Schmidt)
      4. Sign-flip (-v)
      5. Shuffled-component (same elements, random order) — detects magnitude-only artifacts

    Recovery:
      - Each test is independently wrapped. If one test fails, the others
        still run and the failed test's output is set to TII_GENERATION_FAILED.
      - Vector construction errors (e.g., zero-norm genome) are caught and
        logged; the affected test is skipped.
    """
    results = {}
    vec_norm = genome.vector.norm().item()

    slog.debug(f"Falsification battery START: layer={genome.layer_index}, "
               f"vec_norm={vec_norm:.4f}, prompt_len={len(task_prompt)}")

    # ── 1. Primary Test: Targeted Injection ──────────────────────────────
    with LogContext(step="probe_primary"):
        try:
            slog.trace("Running primary injection (+v)")
            results["output"] = execute_tii_generation(model, task_prompt, genome)
            slog.trace(f"Primary output preview: {results['output'][:150]}")
        except Exception as e:
            slog.exception(f"Primary injection failed: {e}")
            results["output"] = TII_GENERATION_FAILED

    # ── 2. Null-A: Norm-Matched Gaussian Noise ───────────────────────────
    with LogContext(step="probe_noise"):
        try:
            slog.trace("Constructing noise vector (same norm, random direction)")
            noise_vector = torch.randn_like(genome.vector)
            noise_norm = noise_vector.norm()
            if noise_norm < 1e-10:
                slog.warning("Noise vector has near-zero norm — regenerating")
                noise_vector = torch.randn_like(genome.vector)
                noise_norm = noise_vector.norm()
            noise_vector = (noise_vector / noise_norm) * vec_norm
            noise_genome = SteeringGenome(layer_index=genome.layer_index, vector=noise_vector)

            slog.trace(f"Noise genome: norm={noise_vector.norm().item():.4f}, "
                       f"cosine_with_original={torch.dot(noise_vector, genome.vector).item() / (vec_norm ** 2 + 1e-10):.4f}")
            results["noise_output"] = execute_tii_generation(model, task_prompt, noise_genome)
            slog.trace(f"Noise output preview: {results['noise_output'][:150]}")
        except Exception as e:
            slog.exception(f"Null-A (noise) test failed: {e}")
            results["noise_output"] = TII_GENERATION_FAILED

    # ── 3. Null-B: Orthogonal Projection ─────────────────────────────────
    with LogContext(step="probe_ortho"):
        try:
            slog.trace("Constructing orthogonal vector via Gram-Schmidt")
            ortho_vector = torch.randn_like(genome.vector)
            dot_vv = torch.dot(genome.vector, genome.vector)
            if dot_vv.abs() < 1e-10:
                slog.warning("Genome vector has near-zero norm — ortho test may be unreliable")
                dot_vv = torch.tensor(1e-10, device=genome.vector.device)
            proj = (torch.dot(ortho_vector, genome.vector) / dot_vv) * genome.vector
            ortho_vector = ortho_vector - proj
            ortho_norm = ortho_vector.norm()
            if ortho_norm < 1e-10:
                slog.warning("Orthogonal vector collapsed to zero — regenerating")
                ortho_vector = torch.randn_like(genome.vector)
                ortho_vector = ortho_vector - (torch.dot(ortho_vector, genome.vector) / dot_vv) * genome.vector
                ortho_norm = ortho_vector.norm()
            ortho_vector = (ortho_vector / ortho_norm) * vec_norm

            ortho_genome = SteeringGenome(layer_index=genome.layer_index, vector=ortho_vector)
            cosine_check = torch.dot(ortho_vector, genome.vector).item() / (vec_norm ** 2 + 1e-10)
            slog.trace(f"Ortho genome: norm={ortho_vector.norm().item():.4f}, "
                       f"cosine_with_original={cosine_check:.6f} (should be ~0)")
            results["ortho_output"] = execute_tii_generation(model, task_prompt, ortho_genome)
            slog.trace(f"Ortho output preview: {results['ortho_output'][:150]}")
        except Exception as e:
            slog.exception(f"Null-B (orthogonal) test failed: {e}")
            results["ortho_output"] = TII_GENERATION_FAILED

    # ── 4. Sign-Flip Test ────────────────────────────────────────────────
    with LogContext(step="probe_signflip"):
        try:
            slog.trace("Constructing sign-flipped vector (-v)")
            flipped_vector = -genome.vector
            flipped_genome = SteeringGenome(layer_index=genome.layer_index, vector=flipped_vector)
            results["sign_flip_output"] = execute_tii_generation(model, task_prompt, flipped_genome)
            slog.trace(f"Sign-flip output preview: {results['sign_flip_output'][:150]}")
        except Exception as e:
            slog.exception(f"Sign-flip test failed: {e}")
            results["sign_flip_output"] = TII_GENERATION_FAILED

    # ── 5. Shuffled-Component Test ────────────────────────────────────────
    with LogContext(step="probe_shuffle"):
        try:
            slog.trace("Constructing shuffled-component vector (same elements, random order)")
            perm = torch.randperm(genome.vector.shape[0], device=genome.vector.device)
            shuffled_vector = genome.vector[perm]
            shuffled_genome = SteeringGenome(
                layer_index=genome.layer_index, vector=shuffled_vector,
                position_ratio=getattr(genome, 'position_ratio', 1.0)
            )
            cosine_shuf = torch.dot(shuffled_vector, genome.vector).item() / (vec_norm ** 2 + 1e-10)
            slog.trace(f"Shuffled genome: norm={shuffled_vector.norm().item():.4f}, "
                       f"cosine_with_original={cosine_shuf:.4f}")
            results["shuffle_output"] = execute_tii_generation(model, task_prompt, shuffled_genome)
            slog.trace(f"Shuffle output preview: {results['shuffle_output'][:150]}")
        except Exception as e:
            slog.exception(f"Shuffled-component test failed: {e}")
            results["shuffle_output"] = TII_GENERATION_FAILED

    # ── Summary ──────────────────────────────────────────────────────────
    n_tests = 5
    failed_tests = [k for k, v in results.items() if v == TII_GENERATION_FAILED]
    if failed_tests:
        slog.warning(f"Falsification battery completed with {len(failed_tests)} failures: {failed_tests}")
    else:
        slog.debug(f"Falsification battery completed — all {n_tests} tests produced output")

    return results
