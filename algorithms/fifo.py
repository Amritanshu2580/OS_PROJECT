# File: algorithms/fifo.py
"""FIFO page replacement algorithm implementation for Virtual Memory Simulator.

Public function:
- fifo(reference: list[int], frames_count: int) -> dict

Returned dict structure:
{
  "steps": [
      {"step": int, "request": int, "frames": list[int|None], "is_hit": bool,
       "replaced": int|None, "fault_count": int, "hit_count": int}
  ],
  "faults": int,
  "hits": int,
  "final_frames": list[int|None]
}

The function raises ValueError for invalid frames_count (<= 0).
"""
from __future__ import annotations

from collections import deque
from copy import deepcopy
from typing import Dict, List, Optional


def fifo(reference: List[int], frames_count: int) -> Dict:
    """Simulate FIFO page replacement.

    Args:
        reference: sequence of page requests (list of non-negative ints).
        frames_count: number of physical frames (must be >= 1).

    Returns:
        A dictionary containing steps (detailed snapshots), total faults, hits, and final frames.

    Raises:
        ValueError: if frames_count < 1.
    """
    if frames_count < 1:
        raise ValueError("frames_count must be >= 1")

    # Initialize frames and bookkeeping
    frames: List[Optional[int]] = [None] * frames_count
    queue: deque[int] = deque()  # arrival order of pages currently in frames
    page_to_index: Dict[int, int] = {}  # map page -> its index in frames for quick replacement

    steps = []
    faults = 0
    hits = 0

    for i, req in enumerate(reference, start=1):
        replaced: Optional[int] = None
        is_hit = req in page_to_index

        if is_hit:
            hits += 1
        else:
            faults += 1
            # If there is an empty frame, use the first None slot
            if len(page_to_index) < frames_count:
                # find first empty slot
                empty_index = next(idx for idx, v in enumerate(frames) if v is None)
                frames[empty_index] = req
                page_to_index[req] = empty_index
                queue.append(req)
            else:
                # Evict oldest page in FIFO order
                evict = queue.popleft()
                evict_index = page_to_index.pop(evict)
                replaced = evict
                # Place the new page at the same frame index
                frames[evict_index] = req
                page_to_index[req] = evict_index
                queue.append(req)

        # Snapshot for UI (copy frames to avoid mutation issues later)
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

    return {
        "steps": steps,
        "faults": faults,
        "hits": hits,
        "final_frames": deepcopy(frames),
    }


# --------------------------
# File: tests/test_fifo.py
# --------------------------

