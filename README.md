# pda-cli

> a zero‑friction, cross‑platform **p**itch‑**d**etection‑**a**lgorithm sandbox you can run from any terminal.

---

## ✨ features

* **toggle PDAs at runtime** – `--algo zcr|acf|yin|mpm`
* **real‑time capture** via [`sounddevice`](https://python-sounddevice.readthedocs.io/) (PortAudio)
* **mic *or* line‑in** – works with built‑ins, USB interfaces (Scarlett Solo, etc.)
* **snappy CLI output** – ≤ 50 ms hop, prints `440.01 Hz` live
* **pure‑python** (NumPy/SciPy); no compiler required
* **MIT‑licensed**, hack & ship without lawyer tears

---

## 🚀 quick start

```bash
# clone & bootstrap deps
$ git clone https://github.com/yourname/pda-cli.git
$ cd pda-cli
$ uv venv
$ source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
$ uv pip install -e .

# run with default (YIN)
$ pda                          # whistle and watch the freq scroll

# swap to MPM with smaller frame
$ pda --algo mpm --frames 1024
```

### command‑line flags

| flag             | default        | description                                   |
| ---------------- | -------------- | --------------------------------------------- |
| `--algo`         | `yin`          | `zcr`, `acf`, `yin`, `mpm`                    |
| `--sr`           | `48000`        | sample‑rate (Hz)                              |
| `--frames`       | `2048`         | window length (samples)                       |
| `--device`       | system default | capture device name/id (see `--list-devices`) |
| `--list-devices` | –              | print available PortAudio devices & quit      |
| `--file`         | –              | process audio file instead of mic input       |
| `--debug`        | –              | show debug info (RMS levels)                  |
| `--no-cents`     | –              | hide cents offset in note display             |
| `--smooth`       | `5`            | smoothing window size (0 to disable)          |
| `--gate`         | `0.005`        | amplitude gate threshold (RMS)                |
| `--log`          | –              | log results to CSV file                       |
| `--update-rate`  | `10`           | display updates per second (Hz)               |

---

## 🧩 algorithms included (PDA key)

| id      | core idea                                                       | source                                                                             |
| ------- | --------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **zcr** | zero‑crossing rate                                              | \~20 LoC numpy                                                                     |
| **acf** | autocorrelation                                                 | textbook                                                                           |
| **yin** | cumulative‑mean normalized diff (De Cheveigné & Kawahara 2002)  | [`yin-pitch`](https://github.com/patkruk/pitch-detection/tree/master/yin)          |
| **mpm** | normalized squared diff + clarity metric (McLeod & Wyvill 2005) | adapted from [`sevagh/pitch-detection`](https://github.com/sevagh/pitch-detection) |

---

## 🛠️ development

1. `pre-commit install` – lints with *black* & *ruff*.
2. `pytest` – runs smoke tests & accuracy fixtures.
3. `scripts/bench.py` – sweeps sine 50 Hz → 2 kHz, outputs CSV of absolute error per algo.

### roadmap

* [x] rolling‑median smoothing for UI stability
* [x] CSV logger flag (`--log file.csv`)
* [ ] optional PyInstaller one‑file builds (Win/Linux/macOS)
* [ ] latency benchmark against hardware strobe tuner

---

## 🤝 contributing

Pull requests welcome! Please file an issue first if it’s a major feature so we can bikeshed together. All code under `src/` must pass unit tests & `ruff --fix`.

---

## 📜 license

Released under the MIT License – see [LICENSE](LICENSE) for details.
