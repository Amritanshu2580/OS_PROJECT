import pytest
from algorithms.fifo import fifo


def test_fifo_basic():
    # example: insert until full, then one replacement
    res = fifo([1, 2, 3, 1, 4], 3)
    assert res["faults"] == 4
    assert res["hits"] == 1
    # final_frames should contain 4,2,3 in the indices where they ended up
    assert set([p for p in res["final_frames"] if p is not None]) == {2, 3, 4}


def test_fifo_no_eviction():
    res = fifo([1, 2, 1, 2], 5)
    assert res["faults"] == 2
    assert res["hits"] == 2
    # final frames must include 1 and 2
    assert 1 in res["final_frames"] and 2 in res["final_frames"]


def test_fifo_single_frame():
    res = fifo([1, 2, 1, 2, 3], 1)
    # Access sequence: 1(fault),2(fault replace 1),1(fault replace 2),2(fault replace1),3(fault replace2)
    assert res["faults"] == 5
    assert res["hits"] == 0


def test_fifo_empty_ref():
    res = fifo([], 3)
    assert res["faults"] == 0
    assert res["hits"] == 0
    assert res["steps"] == []


def test_fifo_step_contents():
    # step content check from short sequence
    res = fifo([7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3], 3)
    # check a couple of specific step properties
    step1 = res["steps"][0]
    assert step1["request"] == 7 and step1["is_hit"] is False
    # step 5 is request 0 which should be a hit in this sequence
    step5 = res["steps"][4]
    assert step5["request"] == 0
    # Ensure counts are non-decreasing
    for idx in range(1, len(res["steps"])):
        assert res["steps"][idx]["fault_count"] >= res["steps"][idx - 1]["fault_count"]
