import numpy as np
import pytest
from pda_cli.algos import autocorrelation, mpm, yin, zero_crossing_rate


class TestPitchDetectionAlgorithms:
    @pytest.fixture
    def generate_sine_wave(self):
        def _generate(frequency, sample_rate=48000, duration=0.1):
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            signal = np.sin(2 * np.pi * frequency * t)
            return signal

        return _generate

    def test_zcr_basic(self, generate_sine_wave):
        signal = generate_sine_wave(440)
        pitch = zero_crossing_rate(signal, 48000)
        assert pitch is not None
        assert abs(pitch - 440) < 50  # Loose tolerance for ZCR

    def test_acf_basic(self, generate_sine_wave):
        signal = generate_sine_wave(440)
        pitch = autocorrelation(signal, 48000)
        assert pitch is not None
        assert abs(pitch - 440) < 10

    def test_yin_basic(self, generate_sine_wave):
        signal = generate_sine_wave(440)
        pitch = yin(signal, 48000)
        assert pitch is not None
        assert abs(pitch - 440) < 5

    def test_mpm_basic(self, generate_sine_wave):
        signal = generate_sine_wave(440)
        pitch = mpm(signal, 48000)
        assert pitch is not None
        assert abs(pitch - 440) < 5

    def test_algorithms_with_noise(self, generate_sine_wave):
        signal = generate_sine_wave(440)
        noise = np.random.normal(0, 0.1, len(signal))
        noisy_signal = signal + noise

        for algo in [autocorrelation, yin, mpm]:
            pitch = algo(noisy_signal, 48000)
            assert pitch is not None
            assert abs(pitch - 440) < 20

    def test_algorithms_silent_input(self):
        signal = np.zeros(2048)

        for algo in [zero_crossing_rate, autocorrelation, yin, mpm]:
            pitch = algo(signal, 48000)
            assert pitch is None or pitch < 50  # Should detect no pitch or very low
