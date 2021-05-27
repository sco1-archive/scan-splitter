import re
from pathlib import Path

from rich import print as rprint

# Matches a positive/negative float preceeded by whitespace
FLOAT_PATTERN = r"\s([-+]?\d*\.\d+)"


def _clean_line(line: str) -> str:
    """
    Clean out undesired elements from the provided scan data row.

    The following cleanups are performed:
        1. Remove leading `0` or `1` validity flags
        2. Strip leading & trailing whitespace
        3. Remove colons (`:`)
        4. Replace tabs with spaces

    NOTE: Rows are considered comments if they begin with an asterix (`*`) after steps 1 & 2; if a
    comment row is encountered, this function short-circuits and returns the partially cleaned line
    """
    # All non-header lines are assumed to lead off with a validitity flag (0 or 1) that we can
    # strip off, if present
    line = line.removeprefix("1").removeprefix("0")
    line = line.strip()

    # Short circuit on comment lines because they may not have the same format as data rows
    # This needs to be done after stripping the prefix, since comment lines have the flag
    if line.startswith("*"):
        return line

    line = line.replace(":", "")
    line = line.replace("\t", " ")

    return line


def _line2csv(line: str) -> str:
    """
    Convert the provided line (assumed to be cleaned) into a CSV row.

    Input lines are assumed to be a string variable name followed by one or more float values. The
    line is assumed to be space-delimited, and the variable name column may include spaces.
    """
    # Use the measurement pattern to split on the first floating point number
    measurement_name, *measurements = re.split(FLOAT_PATTERN, line, maxsplit=1)

    # Put the measurements back together, trim, then replace any whitespace with commas
    joined_measurements = " ".join(measurements).strip()
    joined_measurements = re.sub(r"\s{2,}", " ", joined_measurements)  # Collapse whitespace
    joined_measurements = joined_measurements.replace(" ", ",")

    new_line = f"{measurement_name},{joined_measurements}"
    return new_line


def split_composite_file(composite_src: list[str]) -> tuple[list[str], list[str]]:
    """
    Split composite data file into its components.

    A composite data file is assumed to contain 3 chunks of data:
        1. Core measurements
        2. Custom measurements
        3. Landmark coordinates

    Core and custom measurements are joined into a single list of anthro measurements.

    Each section is assumed to contain one or more header lines, which start with `#`. All header
    lines are discarded.

    Data rows containing one or more `*` are assumed to be comments and are discarded.
    """
    out_chunks = []
    in_header = True  # File is assumed to start with a header
    for line in composite_src:
        if in_header:
            if line.startswith("#"):
                continue
            else:
                in_header = False
                chunk: list[str] = []

        if line.startswith("#"):
            out_chunks.append(chunk)
            in_header = True
            continue

        # Clean the line before checking for a comment (starts with *) since they'll still have a
        # validitiy prefix
        # Comment lines short-circuit the line cleaner so they'll start with * when returned
        line = _clean_line(line)
        if line.startswith("*"):
            # Discard comments
            continue

        chunk.append(_line2csv(line))
    else:
        # Append the last chunk when we finish reading the file
        out_chunks.append(chunk)

    core, custom, landmark = out_chunks
    anthro = [*core, *custom]

    return anthro, landmark


def file_pipeline(in_file: Path) -> None:
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
    anthro, landmark = split_composite_file(composite_src)

    anthro_filepath.write_text("\n".join(anthro))
    landmark_filepath.write_text("\n".join(landmark))

    rprint("[green]Done!")


def batch_pipeline(in_dir: Path, pattern: str = "*_composite.txt", recurse: bool = False) -> None:
    """
    Batch process all files in the specified directory that match the provided glob pattern.

    Recursion can optionally be specified by `recurse`.

    NOTE: If `recurse` is `True`, do not include `**` in `pattern`, this is not guarded against.
    """
    if recurse:
        pattern = f"**/{pattern}"

    for composite_file in in_dir.glob(pattern):
        file_pipeline(composite_file)
