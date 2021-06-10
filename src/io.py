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
