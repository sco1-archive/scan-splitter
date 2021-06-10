from pathlib import Path
from textwrap import dedent

import pytest
from src import io


LINE_COUNTER_TEST_CASES = [
    (
        dedent(
            """\
            Measurement Name,Measurement
            Actual Weight,123.45
            Abdomen Circum Tape Measure,3.14
            """
        ),
        3,
    ),
    (
        dedent(
            """\
            Measurement Name,Measurement
            Actual Weight,123.45
            Abdomen Circum Tape Measure,3.14

            """
        ),
        3,
    ),
]


@pytest.mark.parametrize(("raw_src", "truth_count"), LINE_COUNTER_TEST_CASES)
def test_nonempty_line_counter(raw_src: str, truth_count: tuple[str, str]) -> None:  # noqa: D103
    assert io._nonempty_line_count(raw_src) == truth_count


BASE_PATH = Path()
AGGREGATE_HEADER_PREFIX = "Measurement Name"
AGGREGATE_HEADER_TEST_CASES = [
    (
        [
            BASE_PATH / "001 2021-03-31_18-20-36_composite.anthro.csv",
            BASE_PATH / "002 2021-03-31_18-14-36_composite.anthro.csv",
            BASE_PATH / "003 2021-03-31_18-40-49_composite.anthro.csv",
        ],
        "",
        f"{AGGREGATE_HEADER_PREFIX},001,002,003",
    ),
    (
        [
            BASE_PATH / "001 2021-03-31_18-20-36_composite.anthro.csv",
            BASE_PATH / "002 2021-03-31_18-14-36_composite.anthro.csv",
            BASE_PATH / "003 2021-03-31_18-40-49_composite.anthro.csv",
        ],
        "FOO",
        f"{AGGREGATE_HEADER_PREFIX},FOO001,FOO002,FOO003",
    ),
    (
        [
            BASE_PATH / "001 2021-03-31_18-20-36_composite.anthro.csv",
            BASE_PATH / "FOO002 2021-03-31_18-14-36_composite.anthro.csv",
            BASE_PATH / "003 2021-03-31_18-40-49_composite.anthro.csv",
        ],
        "",
        f"{AGGREGATE_HEADER_PREFIX},001,FOO002,003",
    ),
    (
        [
            BASE_PATH / "001 2021-03-31_18-20-36_composite.anthro.csv",
            BASE_PATH / "FOO002 2021-03-31_18-14-36_composite.anthro.csv",
            BASE_PATH / "003 2021-03-31_18-40-49_composite.anthro.csv",
        ],
        "BAR",
        f"{AGGREGATE_HEADER_PREFIX},BAR001,FOO002,BAR003",
    ),
]


@pytest.mark.parametrize(("files", "location_fill", "truth_header"), AGGREGATE_HEADER_TEST_CASES)
def test_aggregate_header_builder(  # noqa: D103
    files: list[Path], location_fill: str, truth_header: str
) -> None:
    assert io._build_aggregate_header(files, AGGREGATE_HEADER_PREFIX, location_fill) == truth_header


MERGER_DUMMY_FILES = [
    "some,header\nmeasurement a,11\nmeasurement b,12",
    "some,header\nmeasurement a,21\nmeasurement b,22",
    "some,header\nmeasurement a,31\nmeasurement b,32",
]
MERGED_ROW_NAMES = ["some header", "measurement a", "measurement b"]
TRUTH_MERGED = [
    "measurement a,11,21,31",
    "measurement b,12,22,32",
]


def test_measurement_merging(tmp_path: Path) -> None:  # noqa: D103
    files = []
    for idx, contents in enumerate(MERGER_DUMMY_FILES, start=1):
        filepath = tmp_path / f"file_{idx:02}.CSV"
        filepath.write_text(contents)
        files.append(filepath)

    merged_measurements = io._merge_measurements(files, MERGED_ROW_NAMES)

    assert merged_measurements == TRUTH_MERGED
