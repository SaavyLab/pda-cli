from collections import deque
from typing import Optional

import numpy as np


class PitchSmoother:
    """Rolling median filter for pitch stabilization."""

    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.buffer: deque = deque(maxlen=window_size)

    def add(self, pitch: Optional[float]) -> Optional[float]:
        """Add a pitch value and return smoothed result.

        Args:
            pitch: Detected pitch in Hz (or None)

        Returns:
            Smoothed pitch or None if not enough valid samples
        """
        if pitch is not None:
            self.buffer.append(pitch)

        if len(self.buffer) < 2:
            return None

        # Use median for robustness against outliers
        median_pitch = np.median(list(self.buffer))

        # Check if values are stable (within 5% of median)
        stable = all(abs(p - median_pitch) / median_pitch < 0.05 for p in self.buffer)

        if stable or len(self.buffer) >= self.window_size:
            return float(median_pitch)

        return None

    def reset(self) -> None:
        """Clear the buffer."""
        self.buffer.clear()


class AmplitudeGate:
    """Dynamic amplitude gating with hysteresis."""

    def __init__(self, min_rms: float = 0.005, hysteresis: float = 0.8):
        self.min_rms = min_rms
        self.hysteresis = hysteresis
        self.gate_open = False

    def process(self, rms: float) -> bool:
        """Check if signal should pass through gate.

        Args:
            rms: RMS amplitude of signal

        Returns:
            True if signal should be processed
        """
        if self.gate_open:
            # Gate is open, use lower threshold to keep it open
            if rms < self.min_rms * self.hysteresis:
                self.gate_open = False
        else:
            # Gate is closed, use normal threshold to open
            if rms > self.min_rms:
                self.gate_open = True

        return self.gate_open
