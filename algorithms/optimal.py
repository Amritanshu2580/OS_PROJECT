# File: algorithms/optimal.py
"""Optimal page replacement algorithm for Virtual Memory Simulator.

Algorithm idea:
- For each request position, when a replacement is needed, evict the page whose next
  use is farthest in the future (or not used again at all).

Implementation details:
- Precompute a mapping: page -> deque of future positions (indices where it appears).
  Pop from the left as we advance through the reference string so the leftmost is the
  next use position for that page.
- When need to evict, check next-use for each resident page; page with no future uses
  (i.e., deque empty) gets highest priority to evict.

Public API:
- optimal(reference: list[int], frames_count: int) -> dict

The returned structure matches fifo/lru functions for UI compatibility.
"""
from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy
from typing import Dict, Deque, List, Optional


def optimal(reference: List[int], frames_count: int) -> Dict:
    if frames_count < 1:
        raise ValueError("frames_count must be >= 1")

    n = len(reference)
    # Build position deques for every page
    pos_map: Dict[int, Deque[int]] = defaultdict(deque)
    for idx, p in enumerate(reference):
        pos_map[p].append(idx)

    frames: List[Optional[int]] = [None] * frames_count
    page_to_index: Dict[int, int] = {}
    steps = []
    faults = 0
    hits = 0

    for i, req in enumerate(reference, start=1):
        # Pop current index from pos_map for req (we are visiting it now)
        # The deque's leftmost is the current position; pop it so next-use refers to future positions
        if pos_map[req]:
            # remove current occurrence
            pos_map[req].popleft()

        replaced: Optional[int] = None
        is_hit = req in page_to_index

        if is_hit:
            hits += 1
        else:
            faults += 1
            if len(page_to_index) < frames_count:
                # place in first empty slot
                empty_index = next(idx for idx, v in enumerate(frames) if v is None)
                frames[empty_index] = req
                page_to_index[req] = empty_index
            else:
                # decide which page to evict: the page with farthest next use (or no use)
                farthest_page = None
                farthest_next_use = -1
                for p in list(page_to_index.keys()):
                    # look at pos_map[p] to find its next use; if empty -> it's not used again
                    if not pos_map[p]:
                        # choose this page immediately (best candidate)
                        farthest_page = p
                        break
                    else:
                        next_use = pos_map[p][0]
                        if next_use > farthest_next_use:
                            farthest_next_use = next_use
                            farthest_page = p

                # evict farthest_page
                evict_index = page_to_index.pop(farthest_page)
                replaced = farthest_page
                frames[evict_index] = req
                page_to_index[req] = evict_index

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
# File: tests/test_optimal.py
# ---------------------------

