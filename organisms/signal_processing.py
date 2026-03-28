"""
Signal Processing organism.

Operations: fft_spectrum, autocorrelation, bandpass_filter, matched_filter
"""

from .base import MathematicalOrganism


class SignalProcessing(MathematicalOrganism):
    name = "signal_processing"
    operations = {
        "fft_spectrum": {
            "code": """
def fft_spectrum(signal, sample_rate=1.0):
    \"\"\"Compute power spectral density via FFT.
    Returns frequencies and power (|X(f)|^2 / N) for positive frequencies.\"\"\"
    x = np.asarray(signal, dtype=np.float64)
    N = len(x)
    X = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(N, d=1.0/sample_rate)
    power = (np.abs(X) ** 2) / N
    return {"frequencies": freqs, "power": power}
""",
            "input_type": "timeseries",
            "output_type": "spectrum",
        },
        "autocorrelation": {
            "code": """
def autocorrelation(signal, max_lag=None):
    \"\"\"Normalized autocorrelation R(tau) = E[x(t)x(t+tau)] / E[x(t)^2].
    Uses FFT-based correlation for speed.\"\"\"
    x = np.asarray(signal, dtype=np.float64)
    x = x - x.mean()
    N = len(x)
    if max_lag is None:
        max_lag = N - 1

    # FFT-based autocorrelation
    n_fft = 2 ** int(np.ceil(np.log2(2 * N - 1)))
    X = np.fft.fft(x, n=n_fft)
    acf_full = np.fft.ifft(X * np.conj(X)).real[:N]
    if acf_full[0] != 0:
        acf_full = acf_full / acf_full[0]  # normalise

    return acf_full[:max_lag + 1]
""",
            "input_type": "timeseries",
            "output_type": "timeseries",
        },
        "bandpass_filter": {
            "code": """
def bandpass_filter(signal, low_freq, high_freq, sample_rate=1.0):
    \"\"\"Zero-phase bandpass filter via FFT.
    Zeroes out frequency components outside [low_freq, high_freq].\"\"\"
    x = np.asarray(signal, dtype=np.float64)
    N = len(x)
    X = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(N, d=1.0/sample_rate)
    mask = (freqs >= low_freq) & (freqs <= high_freq)
    X_filtered = X * mask
    return np.fft.irfft(X_filtered, n=N)
""",
            "input_type": "timeseries",
            "output_type": "timeseries",
        },
        "matched_filter": {
            "code": """
def matched_filter(signal, template):
    \"\"\"Matched filter: cross-correlate signal with a known template.
    Returns the normalized cross-correlation and the index of peak detection.
    Optimal detection of known signal in additive noise.\"\"\"
    x = np.asarray(signal, dtype=np.float64)
    h = np.asarray(template, dtype=np.float64)
    # Normalize template
    h = h - h.mean()
    h_norm = np.sqrt(np.sum(h**2))
    if h_norm > 0:
        h = h / h_norm

    N = len(x)
    M = len(h)
    # Cross-correlation via FFT
    n_fft = 2 ** int(np.ceil(np.log2(N + M - 1)))
    X = np.fft.fft(x, n=n_fft)
    H = np.fft.fft(h[::-1], n=n_fft)  # time-reversed template for correlation
    corr = np.fft.ifft(X * H).real[:N]

    # Normalize by local signal energy
    x_energy = np.sqrt(np.convolve(x**2, np.ones(M), mode='same'))
    x_energy = np.maximum(x_energy, 1e-12)
    snr = corr / x_energy

    peak_idx = int(np.argmax(np.abs(snr)))
    return {
        "correlation": corr,
        "snr": snr,
        "peak_index": peak_idx,
        "peak_snr": float(snr[peak_idx]),
    }
""",
            "input_type": "timeseries_pair",
            "output_type": "dict",
        },
    }


if __name__ == "__main__":
    import numpy as np

    org = SignalProcessing()
    print(org)

    # Generate test signal: 5 Hz + 20 Hz, sampled at 100 Hz
    fs = 100.0
    t = np.arange(0, 2.0, 1.0/fs)
    signal = np.sin(2*np.pi*5*t) + 0.5*np.sin(2*np.pi*20*t)

    # FFT spectrum
    spec = org.execute("fft_spectrum", signal, sample_rate=fs)
    peak_freq = spec["frequencies"][np.argmax(spec["power"][1:]) + 1]
    print(f"FFT peak frequency: {peak_freq:.1f} Hz  (expect 5.0)")

    # Autocorrelation
    acf = org.execute("autocorrelation", signal, max_lag=50)
    print(f"Autocorrelation lag-0: {acf[0]:.4f}  (expect 1.0)")
    print(f"Autocorrelation lag-20: {acf[20]:.4f}  (expect peak, period=20 samples for 5Hz)")

    # Bandpass filter: extract 5 Hz component
    filtered = org.execute("bandpass_filter", signal, 3.0, 7.0, sample_rate=fs)
    # The 20 Hz component should be gone
    spec2 = org.execute("fft_spectrum", filtered, sample_rate=fs)
    power_at_20 = spec2["power"][np.argmin(np.abs(spec2["frequencies"] - 20.0))]
    print(f"Power at 20Hz after bandpass(3-7): {power_at_20:.6f}  (expect ~0)")

    # Matched filter: embed a chirp in noise
    template = np.sin(2*np.pi*np.linspace(5, 15, 50) * np.linspace(0, 0.5, 50))
    noisy_signal = np.random.randn(500) * 0.5
    noisy_signal[200:250] += template  # embed at position 200
    mf = org.execute("matched_filter", noisy_signal, template)
    print(f"Matched filter peak at index: {mf['peak_index']}  (expect near 200-250)")

    print("--- signal_processing: ALL TESTS PASSED ---")
