# Scan Splitter
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sco1/scan-splitter/main.svg)](https://results.pre-commit.ci/latest/github/sco1/scan-splitter/main)
[![lint-and-test](https://github.com/sco1/scan-splitter/actions/workflows/lint_test.yml/badge.svg?branch=main)](https://github.com/sco1/scan-splitter/actions/workflows/lint_test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

Split composite scan files into separate landmark & measurement files.

## Installation
This project utilizes [`poetry`](https://python-poetry.org/) for dependency & environment management. Clone or download this repository to your local machine and create a new environment:

```bash
$ cd <project_dir>
$ poetry install
```

Though it's recommended to utilize `poetry`, the cloned project may also be installed via `pip`:

```bash
$ cd <project_dir>
$ pip install .
```

## Standalone Usage
Self-contained executables are provided for each release. They can be downloaded from [the project's Releases page](https://github.com/sco1/scan-splitter/releases).

## Usage
Once installed, the `scansplitter` CLI can be invoked directly from the command line:
```bash
$ scansplitter <inputs go here>
```

The `scansplitter` CLI can also be invoked from the root of this repository using Python:
```bash
$ python ./src/ui.py <inputs go here>
```

If using the self-contained executable, the invocation is similar:
```bash
$ ./scansplitter.exe <inputs go here>
```

### `scansplitter --help`
Show the tool's help message & exit.

### `scansplitter single`
Slice the provided scan file and output to CSV.

#### Input Parameters
| Parameter         | Description                                     | Type    | Default    |
|-------------------|-------------------------------------------------|---------|------------|
| `--scan-filepath` | Path to composite scan file to split            | String  | GUI Prompt |

### `scansplitter batch`
Batch process all scans in the specified directory and output to CSVs.

**NOTE:** Scan files must end in `*_composite.txt` to be considered for splitting. This is case-sensitive.

#### Input Parameters
| Parameter                  | Description                                                                | Type   | Default             |
|----------------------------|----------------------------------------------------------------------------|--------|---------------------|
| `--scan-dir`               | Path to directory of composite scan files to split                         | String | GUI Prompt          |
| `--pattern`                | Glob pattern to use for selecting scan files to split                      | String | `"*_composite.txt"` |
| `--recurse / --no-recurse` | Recurse through child directories & process all scan files                 | Bool   | `False`             |

## Examples
```bash
$ scansplitter single --scan-filepath "./sample_data/067 2021-05-18_06-30-20_composite.txt"
Processing '067 2021-05-18_06-30-20_composite' ... Done!
```

```bash
$ scansplitter batch --scan-dir ./sample_data/
Processing '067 2021-05-18_06-30-20_composite' ... Done!
Processing '068 2021-05-18_06-47-57_composite' ... Done!
Processing '069 2021-05-18_07-04-46_composite' ... Done!
```

```bash
$ scansplitter batch --recurse --scan-dir .
Processing '067 2021-05-18_06-30-20_composite' ... Done!
Processing '068 2021-05-18_06-47-57_composite' ... Done!
Processing '069 2021-05-18_07-04-46_composite' ... Done!
```
