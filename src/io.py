import typing as t
from pathlib import Path

from rich import print as rprint
from src import parser


# Default Headers
ANTHRO_HEADER = ["Measurement Name,Measurement"]
LANDMARK_HEADER = ["Landmark Name,x,y,z"]


def _dump_chunk(filepath: Path, data: list[str], header: t.Optional[list[str]] = None) -> None:
    """
    Write the input header & data line(s) to the provided output filepath.

    NOTE: Any existing file will be overwritten
    """
    with filepath.open("w") as f:
        if header:
            # Headers need a trailing newline since they'll be followed by our data
            f.write("".join(f"{line}\n" for line in header))

        f.write("\n".join(data))


def file_split_pipeline(in_file: Path) -> None:
    """
    Split the provided composite file into CSVs of its anthro & landmark components.

    Split files are written to the same directory as the input file:
        * Anthro components append ".anthro" to the name of the file
        * Landmark components append ".lmk" to the name of the file

    e.g. `./some_scan_composite.txt` becomes:
        `./some_scan_composite.anthro.csv` and `./some_scan_composite.lmk.csv`

    Comments (lines containing `*`) and header lines (lines beginning with `#`) are discarded

    NOTE: Any existing anthro & landmark files will be overwritten
    """
    base_stem = in_file.stem
    anthro_filepath = in_file.with_name(f"{base_stem}.anthro.csv")
    landmark_filepath = in_file.with_name(f"{base_stem}.lmk.csv")

    rprint(f"Processing {base_stem!r} ... ", end="")

    composite_src = in_file.read_text().splitlines()
    anthro, landmark = parser.split_composite_file(composite_src)

    _dump_chunk(anthro_filepath, anthro, ANTHRO_HEADER)
    _dump_chunk(landmark_filepath, landmark, LANDMARK_HEADER)

    rprint("[green]Done!")


def batch_split_pipeline(
    in_dir: Path, pattern: str = "*_composite.txt", recurse: bool = False
) -> None:
    """
    Batch process all files in the specified directory that match the provided glob pattern.

    Recursion can optionally be specified by `recurse`.

    NOTE: If `recurse` is `True`, do not include `**` in `pattern`, this is not guarded against.
    """
    if recurse:
        pattern = f"**/{pattern}"

    n = 0
    for composite_file in in_dir.glob(pattern):
        file_split_pipeline(composite_file)
        n += 1

    rprint(f"Processed {n} files")


def _nonempty_line_count(src: str) -> int:
    """Count the number of non-empty lines present in the provided source string."""
    return sum(1 for line in src.splitlines() if line.strip())


def _has_same_n_rows(data_file: Path, new_row_names: Path) -> bool:
    """Check that the two files provided have the same number of non-empty lines."""
    return _nonempty_line_count(data_file.read_text()) == _nonempty_line_count(
        new_row_names.read_text()
    )


def _build_aggregate_header(files: list[Path], header_prefix: str, location_fill: str) -> str:
    """Generate the header line for the aggregate measurement CSV."""
    col_names = []
    for file in files:
        subj_id, location = parser.extract_subj_id(file.name, location_fill)
        col_names.append(f"{location}{subj_id}")

    return f"{header_prefix},{','.join(col_names)}"


def _merge_measurements(files: list[Path], row_names: list[str]) -> list[str]:
    """
    Merge measurement values from the provided list of anthro measurement files.

    Files are assumed to be of the format output by our scan splitting pipeline. Measurements are
    merged into a list of strings, one measurement per row.

    e.g.:
        some,header
        measurement a,11
        measurement b,12

        some,header
        measurement a,21
        measurement b,22

    Becomes:
        ["measurement a,11,21", "measurement b,12,22"]

    Row names and order are assumed to be consistent across all input files, as well as the input
    list of row names
    """
    # Iterate through all of the anthro measurement files & pull in the entire measurements column
    # for each file & store into a list of lists
    all_measurements = []
    for file in files:
        data_lines = file.read_text().splitlines()[1:]  # skip header line
        values = [line.split(",")[1] for line in data_lines]
        all_measurements.append(values)

    # Since we have a list of columns, we can use zip to join them into a row for each column
    # We can also add the row names (sans header) in with this step
    joined_measurements = [",".join(line) for line in zip(row_names[1:], *all_measurements)]

    return joined_measurements


def anthro_measure_aggregation_pipeline(
    anthro_dir: Path,
    new_row_names: t.Optional[Path],
    location_fill: str = "",
    pattern: str = "*_composite.anthro.csv",
    recurse: bool = False,
) -> None:
    """Aggregate a directory of split anthro measurement files into a single CSV."""
    if recurse:
        pattern = f"**/{pattern}"

    # Listify here so we can run some short-circuit checks on a sample file before launching into
    # the rest of the pipeline
    anthro_files = list(anthro_dir.glob(pattern))
    if not anthro_files:
        rprint(f"No files found in '{anthro_dir}' matching '{pattern}'")
        return
    else:
        rprint(f"Found {len(anthro_files)} anthro measurement files to aggregate.")

    # Get measurement (row) names, either from the first measurement file or from the specified
    # replacement file
    # All measurement files are assumed to contain the same number & order of measurements
    if new_row_names:
        # Do a basic check to see if the replacement file has the same number of rows
        # Both files are assumed to contain one header line
        if not _has_same_n_rows(anthro_files[0], new_row_names):
            rprint(
                f"Length mismatch between anthro files & replacement measurement names, please check your file: '{new_row_names}'"  # noqa: E501
            )
            return
        else:
            rprint("Using replacement measurement names.")
            row_names = parser.extract_measurement_names(new_row_names.read_text())
    else:
        rprint(f"Using measurement names from: '{anthro_files[0].name}'")
        row_names = parser.extract_measurement_names(anthro_files[0].read_text())

    # Build the aggregate header line, which appends all of the subject IDs to the header of the row
    # names
    aggregate_header = _build_aggregate_header(
        anthro_files, header_prefix=row_names[0], location_fill=location_fill
    )
    joined_measurements = _merge_measurements(anthro_files, row_names)

    out_filepath = anthro_dir / "consolidated_anthro.CSV"
    _dump_chunk(out_filepath, joined_measurements, [aggregate_header])
    rprint(f"Consolidated measurements file written to: '{out_filepath}'")
