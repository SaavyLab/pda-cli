from typing import Optional

import numpy as np


def autocorrelation(signal: np.ndarray, sample_rate: int) -> Optional[float]:
    """Autocorrelation-based pitch detection.

    Args:
        signal: Audio signal as numpy array
        sample_rate: Sample rate in Hz

    Returns:
        Detected frequency in Hz, or None if no pitch detected
    """
    signal = signal - np.mean(signal)

    correlation = np.correlate(signal, signal, mode="full")
    correlation = correlation[len(correlation) // 2 :]

    min_period = int(sample_rate / 1000)  # 1000 Hz max
    max_period = int(sample_rate / 50)  # 50 Hz min

    if max_period > len(correlation):
        max_period = len(correlation)

    correlation[:min_period] = 0

    if max_period > min_period:
        peak_idx = np.argmax(correlation[min_period:max_period]) + min_period

        if correlation[peak_idx] > 0.3 * correlation[0]:
            frequency = sample_rate / peak_idx
            return frequency

    return None
