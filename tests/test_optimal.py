import pytest
from algorithms.optimal import optimal


def test_optimal_basic_counts():
    ref = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3]
    res = optimal(ref, 3)
    # earlier example showed Optimal produced 7 faults for this reference with 3 frames
    assert res["faults"] == 7
    assert res["hits"] == len(ref) - 7


def test_optimal_no_eviction():
    res = optimal([1, 2, 1, 2], 5)
    assert res["faults"] == 2
    assert res["hits"] == 2


def test_optimal_single_frame():
    res = optimal([1, 2, 1, 2, 3], 1)
    assert res["faults"] == 5
    assert res["hits"] == 0


def test_optimal_empty_ref():
    res = optimal([], 3)
    assert res["faults"] == 0
    assert res["hits"] == 0
    assert res["steps"] == []


def test_optimal_step_behavior():
    res = optimal([1,2,3,1,4], 3)
    # after steps, expect specific fault/hit pattern
    assert res["faults"] == 4
    assert res["hits"] == 1
