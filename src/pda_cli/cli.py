import csv
import sys
from typing import Any, Optional

import click
import numpy as np
import sounddevice as sd

from .algos import ALGORITHMS
from .utils import AmplitudeGate, PitchSmoother, format_note


@click.command()
@click.option(
    "--algo",
    default="yin",
    type=click.Choice(["zcr", "acf", "yin", "mpm"]),
    help="Pitch detection algorithm",
)
@click.option("--sr", default=48000, type=int, help="Sample rate (Hz)")
@click.option("--frames", default=2048, type=int, help="Window length (samples)")
@click.option("--device", default=None, type=str, help="Audio device name/id")
@click.option("--list-devices", is_flag=True, help="List available audio devices")
@click.option(
    "--file", type=click.Path(exists=True), help="Process audio file instead of mic"
)
@click.option("--debug", is_flag=True, help="Show debug info (RMS levels)")
@click.option("--no-cents", is_flag=True, help="Hide cents offset in note display")
@click.option(
    "--smooth", default=5, type=int, help="Smoothing window size (0 to disable)"
)
@click.option(
    "--gate", default=0.005, type=float, help="Amplitude gate threshold (RMS)"
)
@click.option("--log", type=click.Path(), help="Log results to CSV file")
@click.option(
    "--update-rate", default=10, type=int, help="Display updates per second (Hz)"
)
def main(
    algo: str,
    sr: int,
    frames: int,
    device: Optional[str],
    list_devices: bool,
    file: Optional[str],
    debug: bool,
    no_cents: bool,
    smooth: int,
    gate: float,
    log: Optional[str],
    update_rate: int,
) -> None:
    """Real-time pitch detection CLI."""
    if list_devices:
        print(sd.query_devices())
        return

    pitch_func = ALGORITHMS[algo]

    if file:
        import wave

        print(f"Processing file: {file}")
        print(f"Algorithm: {algo.upper()}, Frame size: {frames} samples\n")

        try:
            with wave.open(file, "rb") as wav:
                wav_sr = wav.getframerate()
                wav_frames = wav.getnframes()
                wav_data = wav.readframes(wav_frames)

                signal = (
                    np.frombuffer(wav_data, dtype=np.int16).astype(np.float32) / 32768.0
                )

                for i in range(0, len(signal) - frames, frames // 2):
                    window = signal[i : i + frames]
                    pitch = pitch_func(window, wav_sr)

                    time_pos = i / wav_sr
                    if pitch and 50 <= pitch <= 2000:
                        note_str = format_note(pitch, show_cents=not no_cents)
                        print(f"{time_pos:6.2f}s: {pitch:7.2f} Hz  {note_str}")
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # Initialize smoothing and gating
    smoother = PitchSmoother(window_size=smooth) if smooth > 0 else None
    amp_gate = AmplitudeGate(min_rms=gate)

    # Initialize logging
    log_file = None
    log_writer = None
    if log:
        log_file = open(log, "w", newline="")
        log_writer = csv.writer(log_file)
        log_writer.writerow(["timestamp", "frequency_hz", "note", "rms", "algorithm"])

    # Display rate limiting
    last_display_time = 0
    display_interval = 1.0 / update_rate

    print(f"Starting {algo.upper()} pitch detection...")
    print(f"Sample rate: {sr} Hz, Frame size: {frames} samples")
    if smooth > 0:
        print(f"Smoothing: {smooth} samples, Gate threshold: {gate}")
    print(f"Display rate: {update_rate} Hz")
    if log:
        print(f"Logging to: {log}")
    print("Press Ctrl+C to stop\n")

    def audio_callback(
        indata: np.ndarray, frames: int, time: Any, status: Optional[sd.CallbackFlags]
    ) -> None:
        nonlocal last_display_time
        import time as time_module

        # Use wall clock time for display rate limiting
        current_time = time_module.time()
        audio_time = time.inputBufferAdcTime if time else current_time

        if status:
            if log_writer:
                log_writer.writerow([audio_time, None, None, None, f"ERROR: {status}"])

            # Rate limit error display too
            if current_time - last_display_time >= display_interval:
                print(f"\r{status}", end="", flush=True)
                last_display_time = current_time
            return

        signal = indata[:, 0]

        # Check signal level
        rms = np.sqrt(np.mean(signal**2))

        if debug:
            print(f"\rRMS: {rms:.4f}", end="", flush=True)
            return

        # Apply amplitude gating
        if not amp_gate.process(rms):
            if smoother:
                smoother.reset()

            if log_writer:
                log_writer.writerow([audio_time, None, "quiet", f"{rms:.6f}", algo])

            if current_time - last_display_time >= display_interval:
                print(f"\r{'---.--':>7} Hz  {'---':>8} (quiet)", end="", flush=True)
                last_display_time = current_time
            return

        pitch = pitch_func(signal, sr)

        # Apply smoothing if enabled
        if smoother and pitch:
            pitch = smoother.add(pitch)
            if not pitch:  # Not enough stable samples yet
                if log_writer:
                    log_writer.writerow(
                        [audio_time, None, "stabilizing", f"{rms:.6f}", algo]
                    )

                if current_time - last_display_time >= display_interval:
                    print(f"\r{'---.--':>7} Hz  {'---':>8} (···)", end="", flush=True)
                    last_display_time = current_time
                return

        # Log and display results
        if pitch and 50 <= pitch <= 2000:
            note_str = format_note(pitch, show_cents=not no_cents)

            if log_writer:
                log_writer.writerow(
                    [audio_time, f"{pitch:.2f}", note_str, f"{rms:.6f}", algo]
                )

            if current_time - last_display_time >= display_interval:
                print(f"\r{pitch:7.2f} Hz  {note_str:>8}", end="", flush=True)
                last_display_time = current_time
        else:
            if log_writer:
                log_writer.writerow(
                    [
                        audio_time,
                        f"{pitch:.2f}" if pitch else "None",
                        "out_of_range",
                        f"{rms:.6f}",
                        algo,
                    ]
                )

            if current_time - last_display_time >= display_interval:
                print(f"\r{'---.--':>7} Hz  {'---':>8}", end="", flush=True)
                last_display_time = current_time

    try:
        # Add buffer and latency settings to prevent overflow
        with sd.InputStream(
            callback=audio_callback,
            channels=1,
            samplerate=sr,
            blocksize=frames,
            device=device,
            latency=0.1,
        ):
            print("Listening... (whistle or play a note)")
            print("(You should see 'quiet' if no sound detected)")
            while True:
                sd.sleep(100)
    except KeyboardInterrupt:
        print("\n\nStopped.")
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if log_file:
            log_file.close()
            print(f"\nLog saved to: {log}")


if __name__ == "__main__":
    main()
