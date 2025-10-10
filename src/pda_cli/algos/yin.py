from typing import Optional

import numpy as np


def yin(
    signal: np.ndarray, sample_rate: int, threshold: float = 0.1
) -> Optional[float]:
    """YIN pitch detection algorithm.

    Args:
        signal: Audio signal as numpy array
        sample_rate: Sample rate in Hz
        threshold: YIN threshold parameter (default: 0.1)

    Returns:
        Detected frequency in Hz, or None if no pitch detected
    """
    signal = signal.astype(np.float32)
    W = len(signal)
    tau_max = min(W // 2, int(sample_rate / 50))  # Cap at 50Hz minimum

    df = np.zeros(tau_max)

    for tau in range(1, tau_max):
        for j in range(0, W - tau):
            df[tau] += (signal[j] - signal[j + tau]) ** 2

    cmndf = df.copy()
    cmndf[0] = 1

    cumulative = np.cumsum(df[1:], dtype=np.float32)

    for tau in range(1, tau_max):
        denom_sum = cumulative[tau - 1] if tau - 1 < len(cumulative) else cumulative[-1]
        if denom_sum > 0:
            cmndf[tau] = df[tau] * tau / denom_sum
        else:
            cmndf[tau] = 1

    tau = 1
    while tau < tau_max - 1:
        if cmndf[tau] < threshold:
            while tau + 1 < tau_max and cmndf[tau + 1] < cmndf[tau]:
                tau += 1
            break
        tau += 1

    if tau == tau_max - 1 or cmndf[tau] >= threshold:
        return None

    x0 = tau - 1 if tau > 0 else tau
    x2 = tau + 1 if tau < tau_max - 1 else tau

    if x0 == tau:
        if cmndf[tau] <= cmndf[x2]:
            period = tau
        else:
            period = x2
    elif x2 == tau:
        if cmndf[tau] <= cmndf[x0]:
            period = tau
        else:
            period = x0
    else:
        s0 = cmndf[x0]
        s1 = cmndf[tau]
        s2 = cmndf[x2]

        period = tau + (s2 - s0) / (2 * (2 * s1 - s2 - s0))

    frequency = sample_rate / period
    return frequency
