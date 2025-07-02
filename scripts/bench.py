#!/usr/bin/env python
"""Benchmark pitch detection algorithms against known frequencies."""

import csv
import sys
from pathlib import Path

import numpy as np
from pda_cli.algos import ALGORITHMS

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def generate_sine_wave(frequency, sample_rate=48000, duration=0.1):
    """Generate a pure sine wave at the given frequency."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    return np.sin(2 * np.pi * frequency * t)


def benchmark_algorithms(freq_range=(50, 2000), step=50, sample_rate=48000):
    """Benchmark all algorithms across a frequency range."""
    frequencies = list(range(freq_range[0], freq_range[1] + 1, step))
    results = {algo: [] for algo in ALGORITHMS}

    for freq in frequencies:
        signal = generate_sine_wave(freq, sample_rate)

        for algo_name, algo_func in ALGORITHMS.items():
            detected = algo_func(signal, sample_rate)
            error = abs(detected - freq) if detected else float("inf")
            results[algo_name].append(
                {
                    "true_freq": freq,
                    "detected_freq": detected,
                    "error": error,
                    "error_percent": (error / freq * 100) if detected else float("inf"),
                }
            )

    return results


def save_results_to_csv(results, output_file="benchmark_results.csv"):
    """Save benchmark results to CSV."""
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)

        # Header
        header = ["Frequency (Hz)"]
        for algo in ALGORITHMS:
            header.extend([f"{algo}_detected", f"{algo}_error", f"{algo}_error_%"])
        writer.writerow(header)

        # Data rows
        frequencies = [r["true_freq"] for r in results[list(ALGORITHMS.keys())[0]]]
        for i, freq in enumerate(frequencies):
            row = [freq]
            for algo in ALGORITHMS:
                r = results[algo][i]
                row.extend(
                    [
                        f"{r['detected_freq']:.2f}" if r["detected_freq"] else "None",
                        f"{r['error']:.2f}" if r["error"] != float("inf") else "inf",
                        f"{r['error_percent']:.2f}"
                        if r["error_percent"] != float("inf")
                        else "inf",
                    ]
                )
            writer.writerow(row)

    print(f"Results saved to {output_file}")


def print_summary(results):
    """Print a summary of the benchmark results."""
    print("\nBenchmark Summary:")
    print("-" * 60)

    for algo in ALGORITHMS:
        errors = [r["error"] for r in results[algo] if r["error"] != float("inf")]
        if errors:
            avg_error = np.mean(errors)
            max_error = np.max(errors)
            detection_rate = len(errors) / len(results[algo]) * 100
            print(f"\n{algo.upper()}:")
            print(f"  Detection rate: {detection_rate:.1f}%")
            print(f"  Average error: {avg_error:.2f} Hz")
            print(f"  Max error: {max_error:.2f} Hz")


if __name__ == "__main__":
    print("Benchmarking pitch detection algorithms...")
    print("Frequency range: 50-2000 Hz, step: 50 Hz")

    results = benchmark_algorithms()
    save_results_to_csv(results)
    print_summary(results)
