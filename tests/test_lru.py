import pytest
from algorithms.lru import lru

def test_lru_basic_counts():
    ref = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3]
    res = lru(ref, 3)
    # Correct expected value: LRU produces 9 faults for this reference with 3 frames
    assert res["faults"] == 9
    assert res["hits"] == len(ref) - 9

def test_lru_no_eviction():
    res = lru([1, 2, 1, 2], 5)
    assert res["faults"] == 2
    assert res["hits"] == 2

def test_lru_single_frame():
    res = lru([1, 2, 1, 2, 3], 1)
    # with 1 frame, every change is a fault and no hits in this sequence
    assert res["faults"] == 5
    assert res["hits"] == 0

def test_lru_empty_ref():
    res = lru([], 3)
    assert res["faults"] == 0
    assert res["hits"] == 0
    assert res["steps"] == []

def test_lru_step_behavior():
    res = lru([1,2,3,1,4], 3)
    # steps should correctly reflect hits/faults ordering
    assert res["steps"][3]["request"] == 1
    # after step 4 (request 1) it's a hit
    assert res["steps"][3]["is_hit"] is True
