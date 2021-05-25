from textwrap import dedent

import pytest
from src import parser


COMPOSITE_TEST_CASES = [
    (
        dedent(  # Check that headers, line prefixes are discarded, anthro is joined
            """\
            #SizeStream Measurements
            #Stored on Tue May 18 06:49:24 2021
            #SizeStream Core Measurements
            #format - Measurement Valid (1 = valid), Measurement Name, Measurement
            #
            1  Actual Weight: 1.2
            #SizeStream Custom Measurements
            #format - Measurement Valid (1 = valid), Measurement Name, Measurement
            #
            1  Chest: 3.4
            #SizeStream Landmarks
            #format - Landmarks Valid (1 = valid), Landmark Name, Landmark x y z
            #
            1  AbdomenBack	5.6	7.8	-9.10
            """
        ),
        ["Actual Weight: 1.2", "Chest: 3.4"],
        ["AbdomenBack	5.6	7.8	-9.10"],
    ),
    (
        dedent(  # Check that comments are discarded
            """\
            #SizeStream Measurements
            #Stored on Tue May 18 06:49:24 2021
            #SizeStream Core Measurements
            #format - Measurement Valid (1 = valid), Measurement Name, Measurement
            #
            1  Actual Weight: 1.2
            #SizeStream Custom Measurements
            #format - Measurement Valid (1 = valid), Measurement Name, Measurement
            #
            1  *****  Body Fat / Fitness: *****
            1  Chest: 3.4
            #SizeStream Landmarks
            #format - Landmarks Valid (1 = valid), Landmark Name, Landmark x y z
            #
            1  AbdomenBack	5.6	7.8	-9.10
            """
        ),
        ["Actual Weight: 1.2", "Chest: 3.4"],
        ["AbdomenBack	5.6	7.8	-9.10"],
    ),
    (
        dedent(  # Check all encountered name varieties
            """\
            #SizeStream Measurements
            #Stored on Tue May 18 06:49:24 2021
            #SizeStream Core Measurements
            #format - Measurement Valid (1 = valid), Measurement Name, Measurement
            #
            1  Actual Weight: 1.2
            1  Waist at 50%: 1.2
            #SizeStream Custom Measurements
            #format - Measurement Valid (1 = valid), Measurement Name, Measurement
            #
            1  Chest: 3.4
            1  Body Fat (men): 3.4
            #SizeStream Landmarks
            #format - Landmarks Valid (1 = valid), Landmark Name, Landmark x y z
            #
            1  AbdomenBack	5.6	7.8	-9.10
            1  Small of the Back	5.6	7.8	-9.10
            """
        ),
        ["Actual Weight: 1.2", "Waist at 50%: 1.2", "Chest: 3.4", "Body Fat (men): 3.4"],
        ["AbdomenBack	5.6	7.8	-9.10", "Small of the Back	5.6	7.8	-9.10"],
    ),
]


@pytest.mark.parametrize(("raw_src", "truth_anthro", "truth_landmark"), COMPOSITE_TEST_CASES)
def test_composite_file_parsing(  # noqa: D103
    raw_src: str, truth_anthro: list[str], truth_landmark: list[str]
) -> None:
    anthro, landmark = parser.split_composite_file(raw_src.splitlines())

    assert anthro == truth_anthro
    assert landmark == truth_landmark
