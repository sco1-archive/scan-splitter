from pathlib import Path

from rich import print as rprint


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

        # All non-comment lines are assumed to lead off with a validitity flag (0 or 1) that we can
        # strip off, if present
        line = line.removeprefix("1  ").removeprefix("0  ")
        if line.startswith("*"):
            # Discard comments
            continue

        chunk.append(line)
    else:
        # Append the last chunk when we finish reading the file
        out_chunks.append(chunk)

    core, custom, landmark = out_chunks
    anthro = [*core, *custom]

    return anthro, landmark


def file_pipeline(in_file: Path) -> None:
    """
    Split the provided composite file into its anthro & landmark components.

    Split files are written to the same directory as the input file:
        * Anthro components append ".anthro" to the name of the file
        * Landmark components append ".lmk" to the name of the file

    e.g. `./some_scan_composite.txt` becomes:
        `./some_scan_composite.anthro.txt` and `./some_scan_composite.lmk.txt`

    Comments (lines containing `*`) and header lines (lines beginning with `#`) are discarded

    NOTE: Any existing anthro & landmark files will be overwritten
    """
    base_stem = in_file.stem
    anthro_filepath = in_file.with_stem(f"{base_stem}.anthro")
    landmark_filepath = in_file.with_stem(f"{base_stem}.lmk")

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
