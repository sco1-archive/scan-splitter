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
For users on Windows, self-contained executables are provided for each release.

They can be downloaded from [the project's Releases page](https://github.com/sco1/scan-splitter/releases).

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

Inline help may also be viewed using `$ scansplitter single --help`

#### Input Parameters
| Parameter         | Description                          | Type    | Default    |
|-------------------|--------------------------------------|---------|------------|
| `--scan-filepath` | Path to composite scan file to split | Path    | GUI Prompt |

#### Examples
```bash
$ scansplitter single --scan-filepath "./sample_data/067 2021-05-18_06-30-20_composite.txt"
Processing '067 2021-05-18_06-30-20_composite' ... Done!
```

### `scansplitter batch`
Batch process all scans in the specified directory and output to CSVs.

Inline help may also be viewed using `$ scansplitter batch --help`

#### Input Parameters
| Parameter                  | Description                                                       | Type   | Default             |
|----------------------------|-------------------------------------------------------------------|--------|---------------------|
| `--scan-dir`               | Path to directory of composite scan files to split                | Path   | GUI Prompt          |
| `--pattern`                | Glob pattern to use for selecting scan files to split<sup>1</sup> | String | `"*_composite.txt"` |
| `--recurse / --no-recurse` | Recurse through child directories & process all scan files        | Bool   | `False`             |

1. **NOTE:** This scan pattern is assumed to be case-sensitive

#### Examples
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

### `scansplitter aggregate`
Aggregate a directory of split anthro measurement files into a single CSV.

Inline help may also be viewed using `$ scansplitter aggregate --help`

#### Input Parameters
| Parameter                  | Description                                                                         | Type   | Default                    |
|----------------------------|-------------------------------------------------------------------------------------|--------|----------------------------|
| `--anthro-dir`             | Path to directory of anthro files to aggregate                                      | Path   | GUI Prompt                 |
| `--new_names`              | Optional path to a text file for replacement of antho measurement names<sup>1</sup> | Path   | `None`                     |
| `--location_fill`          | Optional fill value for measurement site if missing from filename                   | String | `""`                       |
| `--pattern`                | Glob pattern to use for selecting anthro files to aggregate<sup>2</sup>             | String | `"*_composite.anthro.csv"` |
| `--recurse / --no-recurse` | Recurse through child directories & process all scan files                          | Bool   | `False`                    |

1. **NOTE:** Quantity and order of replacement row names is assumed to match all scans being aggregated. Only quantity is checked before processing.
2. **NOTE:** This scan pattern is assumed to be case-sensitive

#### Examples
```bash
$ scansplitter aggregate
Found 84 anthro measurement files to aggregate.
Using measurement names from: '001 2021-03-31_18-20-36_composite.anthro.csv'
Consolidated measurements file written to: '<data path>/consolidated_anthro.CSV'
```

```bash
$ scansplitter aggregate --location-fill TBS
Found 84 anthro measurement files to aggregate.
Using measurement names from: '001 2021-03-31_18-20-36_composite.anthro.csv'
Consolidated measurements file written to: '<data path>/consolidated_anthro.CSV'
```

```bash
$ scansplitter aggregate --new-row-names "./updated_row_names.txt"
Found 84 anthro measurement files to aggregate.
Using replacement measurement names.
Consolidated measurements file written to: '<data path>/consolidated_anthro.CSV'
```
