from typing import Optional

import numpy as np


def mpm(
    signal: np.ndarray, sample_rate: int, threshold: float = 0.1
) -> Optional[float]:
    """McLeod Pitch Method (MPM) algorithm.

    Args:
        signal: Audio signal as numpy array
        sample_rate: Sample rate in Hz
        threshold: MPM threshold parameter (default: 0.1)

    Returns:
        Detected frequency in Hz, or None if no pitch detected
    """
    signal = signal.astype(np.float32)
    N = len(signal)

    max_tau = N // 2

    nsdf = np.zeros(max_tau)

    for tau in range(max_tau):
        acf = 0
        divisor_m = 0
        divisor_tau = 0

        for i in range(N - tau):
            acf += signal[i] * signal[i + tau]
            divisor_m += signal[i] ** 2
            divisor_tau += signal[i + tau] ** 2

        divisor = np.sqrt(divisor_m * divisor_tau)
        nsdf[tau] = 2 * acf / divisor if divisor > 0 else 0

    key_max_indices = []
    pos = 0

    while pos < max_tau - 1 and nsdf[pos] > 0:
        pos += 1

    while pos < max_tau - 1:
        if nsdf[pos] < 0:
            pos += 1
            continue

        max_pos = pos
        while pos < max_tau - 1 and nsdf[pos] > 0:
            if nsdf[pos] > nsdf[max_pos]:
                max_pos = pos
            pos += 1

        if nsdf[max_pos] > threshold:
            key_max_indices.append(max_pos)

    if not key_max_indices:
        return None

    max_idx = key_max_indices[0]
    max_val = nsdf[max_idx]

    for idx in key_max_indices[1:]:
        if nsdf[idx] > max_val:
            max_val = nsdf[idx]
            max_idx = idx

    tau = max_idx

    x0 = tau - 1 if tau > 0 else tau
    x2 = tau + 1 if tau < max_tau - 1 else tau

    if x0 == x2:
        period = tau
    else:
        y0 = nsdf[x0]
        y1 = nsdf[tau]
        y2 = nsdf[x2]

        a = (y0 - 2 * y1 + y2) / 2
        b = (y2 - y0) / 2

        x_offset = -b / (2 * a) if a != 0 else 0
        period = tau + x_offset

    if period > 0:
        frequency = sample_rate / period
        return frequency

    return None
