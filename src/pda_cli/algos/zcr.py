from typing import Optional

import numpy as np


def zero_crossing_rate(signal: np.ndarray, sample_rate: int) -> Optional[float]:
    """Zero-crossing rate pitch detection.

    Args:
        signal: Audio signal as numpy array
        sample_rate: Sample rate in Hz

    Returns:
        Detected frequency in Hz, or None if no pitch detected
    """
    signal = signal - np.mean(signal)

    zero_crossings = np.where(np.diff(np.sign(signal)))[0]

    if len(zero_crossings) < 2:
        return None

    avg_distance = np.mean(np.diff(zero_crossings))

    if avg_distance > 0:
        frequency = sample_rate / (2 * avg_distance)
        return frequency

    return None
