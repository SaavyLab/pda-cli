# pda-cli

`pda-cli` is a python command-line tool for comparing pitch detection algorithms side by side. it streams from portaudio via `sounddevice`, supports file-based runs, and prints the detected pitch in real time so you can hear how each method behaves.

## overview

- switch between `zcr`, `acf`, `yin`, and `mpm` without restarting
- live capture with configurable sample rate, frame size, and device
- optional smoothing, amplitude gating, and update throttling for stable output
- csv logging for later inspection and a benchmark script for accuracy sweeps
- pure python (numpy) with no compiled extensions

## install

```bash
git clone https://github.com/yourname/pda-cli.git
cd pda-cli
uv venv
source .venv/bin/activate
uv pip install -e .
```

## usage

### list devices

```bash
pda --list-devices
```

### capture from the default input

```bash
pda --algo yin
```

key flags:

- `--algo` chooses the detector (`zcr`, `acf`, `yin`, `mpm`)
- `--sr` and `--frames` control sample rate and window length
- `--smooth`, `--gate`, and `--update-rate` adjust display behavior
- `--log` writes csv output with timestamps, frequency, note, rms, and algo id
- `--debug` prints rms levels only

### process an audio file

```bash
pda --file path/to/take.wav --algo mpm --frames 1024
```

### tweak smoothing and gating

```bash
pda --smooth 3 --gate 0.01 --no-cents
```

## algorithms

- `zcr`: zero-crossing rate baseline
- `acf`: autocorrelation with adaptive peak picking
- `yin`: cumulative-mean normalized difference (de cheveigné & kawahara, 2002)
- `mpm`: mcLeod pitch method with nsdf maxima search

## development

```bash
uv pip install -e .[dev]
pytest
scripts/bench.py
```

`scripts/bench.py` sweeps 50 hz to 2 khz and writes a csv of absolute error for each algorithm.

## license

mit, see [LICENSE](LICENSE).
