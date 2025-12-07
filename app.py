# File: app.py
"""Streamlit UI for the Virtual Memory Simulator (basic version).

Features:
- Input: reference string (space or comma separated)
- Input: frames count
- Algorithm selection: FIFO, LRU, Optimal
- Run button: execute single simulation and show final counts
- Simple presentation of final frames and a step table

This is a minimal starter UI designed to connect the algorithm modules to the front-end.
"""
from __future__ import annotations

import streamlit as st
from typing import Callable, Dict, List

from utils import parser
from algorithms.fifo import fifo
from algorithms.lru import lru
from algorithms.optimal import optimal


ALGORITHM_MAP: Dict[str, Callable[[List[int], int], Dict]] = {
    "FIFO": fifo,
    "LRU": lru,
    "Optimal": optimal,
}


def run_simulation(ref_str: str, frames_count: int, algorithm_name: str) -> Dict:
    """Parse inputs, run chosen algorithm, return result dict or raise ValueError.

    The UI layer handles exceptions and displays errors to the user.
    """
    pages = parser.parse_reference_string(ref_str)
    frames = parser.validate_frames(frames_count)
    algo = ALGORITHM_MAP.get(algorithm_name)
    if algo is None:
        raise ValueError(f"Unknown algorithm: {algorithm_name}")
    return algo(pages, frames)


def main():
    st.set_page_config(page_title="Virtual Memory Simulator", layout="wide")
    st.title("Virtual Memory Optimization — Simulator (Basic)")

    with st.sidebar:
        st.header("Simulation Inputs")
        ref_input = st.text_area("Reference string (pages) - space/comma separated", value="7 0 1 2 0 3 0 4 2 3 0 3", height=120)
        frames_input = st.number_input("Frames", min_value=1, max_value=100, value=3)
        algorithm = st.selectbox("Algorithm", options=["FIFO", "LRU", "Optimal"]) 
        run_button = st.button("Run Simulation")

    if run_button:
        try:
            with st.spinner("Running simulation..."):
                result = run_simulation(ref_input, frames_input, algorithm)
        except Exception as e:
            st.error(str(e))
            return

        # Display summary
        st.subheader("Summary")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Page Faults", result["faults"])
        c2.metric("Total Hits", result["hits"])
        c3.metric("Final Frames (non-empty)", ", ".join([str(x) for x in result["final_frames"] if x is not None]) or "(empty)")

        # Show final frame layout
        st.subheader("Final Frame Layout")
        st.write(result["final_frames"])

        # Show step table (compact)
        st.subheader("Step-by-step (first 200 steps)")
        steps = result["steps"][:200]
        # Build a compact table
        rows = []
        for s in steps:
            rows.append({
                "step": s["step"],
                "req": s["request"],
                "frames": " | ".join([str(x) if x is not None else "_" for x in s["frames"]]),
                "hit": s["is_hit"],
                "replaced": s["replaced"],
                "fault_count": s["fault_count"],
            })
        st.table(rows)

    else:
        st.info("Set inputs in the sidebar and click 'Run Simulation' to start.")


if __name__ == "__main__":
    main()
