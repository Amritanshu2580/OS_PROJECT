# File: algorithms/lru.py
"""LRU (Least Recently Used) page replacement algorithm for Virtual Memory Simulator.

Implementation notes:
- Uses collections.OrderedDict to maintain recency order of pages currently in frames.
- The OrderedDict maps page -> frame_index. The least-recently-used page is at the beginning.

Public API:
- lru(reference: list[int], frames_count: int) -> dict

Returned structure matches algorithms/fifo.py for UI compatibility.
"""
from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from typing import Dict, List, Optional


def lru(reference: List[int], frames_count: int) -> Dict:
    if frames_count < 1:
        raise ValueError("frames_count must be >= 1")

    frames: List[Optional[int]] = [None] * frames_count
    # OrderedDict preserves insertion order; we'll treat the rightmost as most-recently-used
    order: "OrderedDict[int, int]" = OrderedDict()  # page -> frame_index
    steps = []
    faults = 0
    hits = 0

    for i, req in enumerate(reference, start=1):
        replaced: Optional[int] = None
        is_hit = req in order

        if is_hit:
            hits += 1
            # move to most recent
            order.move_to_end(req, last=True)
        else:
            faults += 1
            if len(order) < frames_count:
                # find first empty slot
                empty_index = next(idx for idx, v in enumerate(frames) if v is None)
                frames[empty_index] = req
                order[req] = empty_index
            else:
                # evict least recently used (leftmost)
                evict_page, evict_index = order.popitem(last=False)
                replaced = evict_page
                # replace the evicted slot with the new page
                frames[evict_index] = req
                order[req] = evict_index

        steps.append(
            {
                "step": i,
                "request": req,
                "frames": deepcopy(frames),
                "is_hit": is_hit,
                "replaced": replaced,
                "fault_count": faults,
                "hit_count": hits,
            }
        )

    return {"steps": steps, "faults": faults, "hits": hits, "final_frames": deepcopy(frames)}


# ---------------------------
# File: tests/test_lru.py
# ---------------------------

