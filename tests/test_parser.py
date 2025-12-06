import pytest
from utils import parser


def test_parse_simple():
    assert parser.parse_reference_string("7 0 1 2") == [7, 0, 1, 2]


def test_parse_commas_spaces():
    assert parser.parse_reference_string("7,0, 1  ,2") == [7, 0, 1, 2]


def test_parse_ignore_empty():
    assert parser.parse_reference_string("7,,0  ,  , 1") == [7, 0, 1]


def test_parse_invalid_token():
    with pytest.raises(ValueError):
        parser.parse_reference_string("7 a 2")


def test_parse_negative():
    with pytest.raises(ValueError):
        parser.parse_reference_string("7 -1 2")


def test_parse_empty():
    with pytest.raises(ValueError):
        parser.parse_reference_string("   ")


def test_parse_too_long():
    s = " ".join(["1"] * 5001)
    with pytest.raises(ValueError):
        parser.parse_reference_string(s, max_length=5000)


def test_validate_frames_ok():
    assert parser.validate_frames(3) == 3


def test_validate_frames_zero():
    with pytest.raises(ValueError):
        parser.validate_frames(0)


def test_validate_frames_nonint():
    with pytest.raises(ValueError):
        parser.validate_frames("three")


def test_parse_and_validate_combined():
    ref, frames = parser.parse_and_validate("7 0 1", "3")
    assert ref == [7, 0, 1] and frames == 3
