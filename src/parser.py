import re


# Matches a positive/negative float preceeded by whitespace
FLOAT_PATTERN = r"\s([-+]?\d*\.\d+)"

# Match the location and/or subject number at the beginning of the filename
SUBJ_RE = r"^([a-zA-Z]*)(\d+)\s"


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


def extract_subj_id(filename: str, default_location: str = "") -> tuple[str, str]:
    """
    Extract the subject ID & measurement location from the given filename.

    Filenames are assumed to be of the form: `102 2021-05-18_15-02-42_composite`, where `102` is the
    subject ID. IDs may also be concatenated with the measurement location (e.g. `CPEN102`), which
    is also extracted.

    If no measurement location is specified, `default_location` is used.
    """
    match = re.search(SUBJ_RE, filename)

    if not match:
        raise ValueError(f"Could not find subject ID or location in '{filename}'")

    location, subj_id = match.groups()
    if not location:
        location = default_location

    return subj_id, location


def extract_measurement_names(data_file_src: str) -> list[str]:
    """Extract the row name (first column) from the provided plaintext data file."""
    data_lines = data_file_src.splitlines()
    return [row.split(",")[0] for row in data_lines]
