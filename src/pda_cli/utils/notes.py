import math
from typing import Optional, Tuple


def freq_to_note(frequency: float, a4: float = 440.0) -> Tuple[str, int, int]:
    """Convert frequency to musical note.

    Args:
        frequency: Frequency in Hz
        a4: Reference frequency for A4 (default: 440 Hz)

    Returns:
        Tuple of (note_name, octave, cents_offset)
    """
    # Calculate MIDI note number
    midi_num = 69 + 12 * math.log2(frequency / a4)
    midi_rounded = round(midi_num)

    # Calculate cents offset from nearest note
    cents_offset = int((midi_num - midi_rounded) * 100)

    # Convert to note name
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    note_name = note_names[midi_rounded % 12]
    octave = (midi_rounded // 12) - 1

    return note_name, octave, cents_offset


def format_note(frequency: Optional[float], show_cents: bool = True) -> str:
    """Format frequency as musical note string.

    Args:
        frequency: Frequency in Hz (or None)
        show_cents: Whether to show cents offset

    Returns:
        Formatted note string like "A4 +5c" or "---"
    """
    if not frequency or frequency < 50 or frequency > 2000:
        return "---"

    note, octave, cents = freq_to_note(frequency)

    if show_cents and cents != 0:
        sign = "+" if cents > 0 else ""
        return f"{note}{octave} {sign}{cents}c"
    else:
        return f"{note}{octave}"
