# Conditioned Markov Chains for Polyphonic Japanese Chiptune

This repository is a project developed for a postgraduate course at UFMG 
(course: DCC831 - Generative AI for Music). It implements a polyphonic 
(multi-voice) chiptune generator built with Markov chains. The melody 
chain learns intervals from NES-MDB (NES game music) and JSMel (Japanese
songs), which are blended using a weight λ. The bass follows the 
melody through a vertical interval learned from NES-MDB, and the drums 
are fixed. The stylistic constraint is Japanese 8-bit chiptune: AABA 
form, with 16 measures, 4/4 time, a yo pentatonic scale on D, and NES 
timbres (pulse for the melody and triangle for the bass).

## What is in this Repository

| Path | Content |
|------|---------|
| `src/representation.py` | Scales, intervals, allowed pitches, consonance check, rhythm patterns to onset times |
| `src/nesmdb_data.py` | NES-MDB loading: notes per voice, melody voice, melody–bass vertical intervals, corpus per split |
| `src/jsmel_data.py` | JSMel loading: metadata, melodies as MIDI pitches (rests skipped), corpus of Japanese songs |
| `src/markov.py` | n-gram training, backoff, λ mixing, scale constraint, sampling, perplexity, longest copy |
| `src/generate.py` | Melody, bass and drums for one section; full AABA song from a seed |
| `src/midi_export.py` | MIDI export (melody, bass, drums) and JSON with the configuration |
| `src/synthesis.py` | Pulse and triangle waves; WAV rendering of melody and bass (no drums) |
| `src/evaluation.py` | Interval histogram, total variation distance, japaneseness, coherence |
| `src/make_song.py` | **Entry point:** builds and caches the corpora, trains the chains, generates 30 candidate songs |
| `src/experiments.py` | **Entry point:** experiments E1 (order *n*) and E2 (weight λ) |
| `outputs/` | The 6 delivered songs (`.mid`, `.json`, `.wav`) |
| `requirements.txt` | Python dependencies |

This repository does not include:

- `data/`: the datasets belong to their authors and are not redistributed 
here. Section 2 explains how to download them from the original sources.
- `cache/` and `outputs/candidates/`: created when the code runs (Section 3).
- `.venv/`: created during installation (Section 1).

## 1. Installation

Tested with Python 3.13.5 on Linux (Debian 13).

Clone the repository and enter its folder:
```bash
git clone https://github.com/anacelos/tp1-markov-nes.git
cd tp1-markov-nes 
```
Create a virtual environment and install the dependencies (from the repository root):
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip 
pip install -r requirements.txt
``` 
If the `venv` fails with "ensurepip is not available" install the system package:
```bash
sudo apt install python3-venv
```
Check the installation:
```bash
python -c "import numpy, pretty_midi, pandas, openpyxl; print('ok')"
```

## 2. Data

The files are downloaded to `~/Downloads/` and extracted to `data/`, with the commands run from the root of the repository.

|Dataset | Used for | Source | License |
|------|---------|------|---------|
|NES-MDB (MIDI format)| Melody intervals and melody–bass relation | [nesmdb README](https://github.com/chrisdonahue/nesmdb#download-links) |No explicit license; paper in Section 7|
|JSMel (public subset)| Melody intervals (Japanese songs)|  [Zenodo 20078158](https://zenodo.org/records/20078158)| CC BY-NC 4.0|


Download each one and place it under a new folder (`data/`) exactly as shown below:
```bash
mkdir -p data
```
### 2.1 NES-MDB (MIDI, 12 MB)
1. Download "NES-MDB in MIDI Format" from the [nesmdb README](https://github.com/chrisdonahue/nesmdb#download-links) (file `nesmdb_midi.tar.gz`).
2. Verify the checksum. Expected: 37610e2ca5fe70359c85170cf1f4982596783bb304c59d9c439f68c24ff4ee93
```bash
sha256sum ~/Downloads/nesmdb_midi.tar.gz
```
3. Extract:
```bash
tar -xzf ~/Downloads/nesmdb_midi.tar.gz -C data/
```
### 2.2 JSMel (~11.5 MB)
1. On [Zenodo 20078158](https://zenodo.org/records/20078158), click *Download all* (saved as `20078158.zip`).
2. Check the archive and extract it to a temporary folder:
```bash
unzip -t ~/Downloads/20078158.zip
unzip ~/Downloads/20078158.zip -d ~/Downloads/jsmel_raw
```
3. Extract the 17 letter archives (A.zip … R.zip) and copy the metadata spreadsheet:
```bash
for f in ~/Downloads/jsmel_raw/*.zip; do unzip -q "$f" -d data/jsmel/; done
cp ~/Downloads/jsmel_raw/Metadata_JSMel.xlsx data/jsmel/
```
### 2.3 Check the Data 
```bash
find data/nesmdb_midi -name "*.mid" | wc -l     # expected: 5278
find data/jsmel -name "P_*.txt" | wc -l         # expected: 545
```
Expected layout:
```text
data/
├── nesmdb_midi/
│   ├── train/        # training
│   ├── valid/
│   └── test/         # perplexity and references (split by game)
└── jsmel/
    ├── Metadata_JSMel.xlsx
    ├── A/            # P_A002.txt (pitches), D_A002.txt (durations), ...
    └── ...           # 17 folders, A to R (no I)
```

YM2413-MDB was part of the original plan but is not used in this version, since the rhythm is fixed.


## 3. Reproducing the Results

Always run the commands from the repository root.

1. Train the Markov chains and generate the candidate songs (corpora, chains and 30 candidates):

```bash
mkdir -p cache outputs/candidates
python3 src/make_song.py
```
This script reads the data, saves the processed corpora to `cache/`, trains the Markov chains and generates 30 candidate songs in `outputs/candidates/`, each in three formats: `.mid`, `.json` and `.wav`. The six delivered songs in `outputs/` are six of these candidates (see Section 4). Expected counters: NES train 4502 read / 3094 used; JSMel 426 used.

The audio is synthesized by `src/synthesis.py`: the melody with a square wave (the NES pulse channel) and the bass with a triangle wave (the NES triangle channel); the file is mono, 16-bit, 44.1 kHz. The drums are only present in the MIDI — they are not synthesized in the `.wav`.

2. Run the experiments (E1: perplexity, copy and reference; E2: the effect of λ):
```bash
python3 src/experiments.py
```
It requires the cache (run step 1 first).

Every song is reproducible: the same configuration and seed (stored in its `.json`) produce the same song.

## 4. Delivered Songs

The six songs were chosen by ear among the 10 seeds of each λ. All of them share the same setup: n = 3, yo scale on D, AABA form, 16 bars, 120 BPM.
The λ and the seed of each song are also stored in its `.json`.

|File|λ	| Seed	|Melody source|
|--|-----|-----|-------|
|`outputs/lam0.0_n3_yo_s7.{mid,json,wav}`|	0.0	|7	|NES-MDB only (baseline)|
|`outputs/lam0.0_n3_yo_s10.{mid,json,wav}`|	0.0|	10	|NES-MDB only (baseline)|
|`outputs/lam0.5_n3_yo_s7.{mid,json,wav}`|	0.5	|7|	NES-MDB and JSMel, equal weight|
|`outputs/lam0.5_n3_yo_s10.{mid,json,wav}`|	0.5	|10	|NES-MDB and JSMel, equal weight|
|`outputs/lam1.0_n3_yo_s7.{mid,json,wav}`|	1.0|	7|	JSMel only|
|`outputs/lam1.0_n3_yo_s10.{mid,json,wav}`|	1.0	|10	|JSMel only|

What can be heard, based on E2: with λ = 0 the melody leaps more, while with λ = 1 it moves note by note and repeats more notes, the mean interval falls from 4.2 semitones (λ = 0) to 1.5 (λ = 1), and repeated notes rise from 27% to 45%.

## 5. Results

Here are the quantitative results of our generation models. We evaluated the system across two main dimensions:

* **E1:** How the Markov chain order (*n*) affects the model's perplexity and its tendency to copy the training data.

* **E2:** How the interpolation weight (λ) controls the stylistic blend between NES-MDB (chiptune) and JSMel (Japanese melodies), and its impact on melody–bass coherence.

### E1: order *n* (λ = 0)

Perplexity on the NES-MDB test split (add-k smoothing, k = 0.1, vocabulary of 25 intervals) and longest copy: the longest run of consecutive intervals that also appears in the NES-MDB training melodies (64-note melodies, 10 seeds).

| *n*   | 0 |  1 | 2 | 3  | 4 | 5 |
|-------|---|---|---|---|----|---|
| Perplexity | 18.42 | 10.50 | 8.90 | **8.61** |    9.04 |  10.08 |
| Longest copy (mean) | –   |  10.1 |  16.5 | 22.4 |  27.7 | 29.8 |
| Longest copy (max) | – | 21 |   24 |  34 | 55 | 55    |

Reference: real NES-MDB test melodies (first 63 intervals, 144 melodies) copy 15.74 intervals on average from the training set (max 63).

### E2: weight λ (*n* = 3)

Full AABA songs, 10 seeds per λ; mean ± standard deviation.

| λ   |  Japaneseness *J* | Coherence | Copy NES |Copy JSMel | Repeated notes | Mean abs. interval (semitones)|
|---|-------|-----|---|---|----|-----|
| 0.00 | 0.54 ± 0.06 | 0.81 ± 0.12 | 22.4 |   16.0 | 0.27 |   4.16 |
| 0.25    | 0.61 ± 0.06     | 0.77 ± 0.16 |  14.8 | 13.5 |   0.39 |   2.63 |
| 0.50 | 0.65 ± 0.07 | 0.76 ± 0.15 |  15.0 |  14.6 |  0.43 | 1.86  |
| 0.75  | 0.67 ± 0.06 | 0.83 ± 0.09 |  12.7 | 12.5 |   0.43 | 1.81 |
| 1.00 |    0.70 ± 0.04 |  0.75 ± 0.12 |   12.6 | 12.4 | 0.45 |    1.53 |
| Real NES-MDB |    0.21   | 0.75 | – | – | 0.11 | 3.49 |
| Real JSMel |    1 (by definition) | –  | –  | –  | 0.30  | 1.92   |

*J* = d(h, NES) / (d(h, NES) + d(h, JSMel)), where d is the total variation distance between interval histograms (0 = NES-like, 1 = JSMel-like). Coherence = fraction of bass onsets whose interval to the melody is consonant (unison/octave, thirds, fifth, sixths). Real NES-MDB: *J* and coherence on the test split; repeated notes and mean interval on the training split.

## 6. Use of AI
1. Tools Used

    - Assistant: Claude Code, Claude Opus 5.5 model (Anthropic).

    - Browser: Gemini 3.1 Pro (Google, web)

    - Period of use: 2 Oct 2026 to 11 Oct 2026.

2. What the AI was used for

    - **Planning and Design:** Discussion of the system design, methods (Markov, λ mixture, constraints) and viability of the idea. The proposals were discussed with the AI, but the original idea and the final scope choices were entirely mine.
    - **Research and Bibliography:** Research on dataset licenses (NES-MDB, JSMel), search for bibliographical references (ISMIR papers), and gathering of notes and equations for the abstract.
    - **Guide and Structure:** Creation of a no-code implementation guide, environment setup, and terminal commands to download the datasets.
    - **Theoretical Explanations:** Questions about concepts involving Python, MIDI, music theory, Markov Chains, and evaluation metrics.
    - **Review and Templates:** Line-by-line review of my code (pointing out errors without rewriting the logic) and provision of "word templates" (step-by-step structures described in words, without code) for structuring various functions throughout the project.
    - **Auxiliary Scripts and Git:** Suggestion of Git commands (executed by me) and writing of short exploration snippets in the Python terminal (>>>), used to test data, inspect melodies, and generate local `.wav` files.
    - **Documentation:** Assembly of the file and result table structures here in the README, as well as text review.
    - **Translation:** translating texts into English. (Gemini)
    - **Extra explanations:** Additional explanations of certain functions and concepts, with more examples and applications. (Gemini)
    - The AI also helped with formatting daily personal study reports.

3. What the AI did not do
    - The solution's source code: The implementation of the methods in `src/` (generation, extraction, and evaluation codes). The AI did not write the final logic of the project.
    - The abstract text: The final text of the submitted abstract was written entirely by me, using the AI only for structural review.

#### Detailed Usage Record (Daily) 

| Date | Use and Objective |
|-----|-------|
| 2 Oct 2026 | Reading the assignment, schedule setup, research on dataset licenses, bibliographic research, and discussion of system design and method choice (Markov, polyphony, baseline). Creation of the implementation guide and the `CLAUDE.md` rules. |
| 3 Oct 2026 | Web search for the abstract writing guide, explanations of Python and music, and structural review of `representation.py` with a "word template" for the voice range function. |
| 4 Oct 2026 | Review of `representation.py` and the load function, with MIDI/NES explanations. Suggestion of Git commands and short interactive explorations (>>>). |
| 5 Oct 2026 | Line-by-line review and creation of logical "word templates" for the mean_pitches, melody_voice, vertical_intervals, and list_files functions. |
| 6 Oct 2026 | Review and "word templates" for: build_corpus, the entire jsmel_data.py, train, distribution, mix, and constrain functions. Search for training and backoff references. |
| 7 Oct 2026 | Review and "word templates" for: sample, `generate.py`, `midi_export.py`, make_song.py, and `synthesis.py`. AI wrote the `.wav` test loop in the terminal and suggested Git repository corrections. |
| 8 Oct 2026 | Review and logical "word templates" for log_prob, perplexity, copy functions, `experiments.py`, and `evaluation.py`. Interactive terminal inspection of 10 generated copies and help interpreting the results. |
| 9 Oct 2026 |Organization of the README (this declaration, formatting of file and result tables). Textual review and template for generating `.wav` files in the song iteration. |
|10 - 11 Oct 2026 | Help with the ISMIR LaTeX template and structural review of my abstract. | 

## 7. Citations

Datasets used in this project:

```bibtex
@inproceedings{donahue2018nesmdb,
  title     = {The {NES} Music Database: A multi-instrumental dataset with expressive performance attributes},
  author    = {Donahue, Chris and Mao, Huanru Henry and McAuley, Julian},
  booktitle = {Proc. International Society for Music Information Retrieval Conference (ISMIR)},
  year      = {2018},
  pages = {475--482}
}

@article{matsunaga2026jsmel,
  title   = {{JSMel}: A dataset of 960 song melodies widely shared in contemporary {Japan}},
  author  = {Matsunaga, R. and Ishimoto, T. and Hartono, P. and Abe, J.},
  journal = {Data in Brief},
  volume  = {66},
  pages   = {112869},
  year    = {2026},
  doi     = {10.1016/j.dib.2026.112869}
}
```

Software used in this project:

```bibtex
@inproceedings{raffel2014prettymidi,
  title     = {Intuitive Analysis, Creation and Manipulation of {MIDI} Data with {pretty\_midi}},
  author    = {Raffel, Colin and Ellis, Daniel P. W.},
  booktitle = {Proc. 15th International Conference on Music Information Retrieval (ISMIR), Late Breaking and Demo Papers},
  year      = {2014}
}
```


**Copyright Notice:** The datasets used belong to their original authors and are not redistributed here. The original compositions belong to their respective copyright holders.