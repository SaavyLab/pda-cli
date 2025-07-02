from typing import Callable, Dict, Optional

import numpy as np

from .acf import autocorrelation
from .mpm import mpm
from .yin import yin
from .zcr import zero_crossing_rate

__all__ = ["zero_crossing_rate", "autocorrelation", "yin", "mpm", "ALGORITHMS"]

PitchDetector = Callable[[np.ndarray, int], Optional[float]]

ALGORITHMS: Dict[str, PitchDetector] = {
    "zcr": zero_crossing_rate,
    "acf": autocorrelation,
    "yin": yin,
    "mpm": mpm,
}
