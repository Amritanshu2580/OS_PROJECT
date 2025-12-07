# File: app.py
"""Streamlit UI for the Virtual Memory Simulator (with comparison panel)."""
from __future__ import annotations

import streamlit as st
from typing import Callable, Dict, List
import plotly.graph_objects as go
from utils import parser
from algorithms.fifo import fifo
from algorithms.lru import lru
from algorithms.optimal import optimal

# Step renderer import (new)
from ui.frame_renderer import StepRenderer

ALGORITHM_MAP: Dict[str, Callable[[List[int], int], Dict]] = {
    "FIFO": fifo,
    "LRU": lru,
    "Optimal": optimal,
}


def run_simulation(ref_str: str, frames_count: int, algorithm_name: str) -> Dict:
    pages = parser.parse_reference_string(ref_str)
    frames = parser.validate_frames(frames_count)
    algo = ALGORITHM_MAP.get(algorithm_name)
    if algo is None:
        raise ValueError(f"Unknown algorithm: {algorithm_name}")
    return algo(pages, frames)


def run_all_algorithms(ref_str: str, frames_count: int) -> Dict[str, Dict]:
    """Run FIFO, LRU, Optimal and return a dict keyed by algorithm name."""
    pages = parser.parse_reference_string(ref_str)
    frames = parser.validate_frames(frames_count)
    results = {}
    for name, func in ALGORITHM_MAP.items():
        results[name] = func(pages, frames)
    return results


def render_comparison_chart(results: Dict[str, Dict]):
    """Render a Plotly bar chart comparing faults & hits for each algorithm."""
    algos = list(results.keys())
    faults = [results[a]["faults"] for a in algos]
    hits = [results[a]["hits"] for a in algos]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Page Faults", x=algos, y=faults))
    fig.add_trace(go.Bar(name="Hits", x=algos, y=hits))
    fig.update_layout(barmode="group", title="Algorithm Comparison: Faults vs Hits", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)


def main():
    st.set_page_config(page_title="Virtual Memory Simulator", layout="wide")
    st.title("Virtual Memory Optimization — Simulator")

    # initialize session keys if not present
    if "vm_last_result" not in st.session_state:
        st.session_state["vm_last_result"] = None
    if "vm_show_result" not in st.session_state:
        st.session_state["vm_show_result"] = False
    if "vm_all_results" not in st.session_state:
        st.session_state["vm_all_results"] = None
    if "vm_show_compare" not in st.session_state:
        st.session_state["vm_show_compare"] = False

    with st.sidebar:
        st.header("Simulation Inputs")
        ref_input = st.text_area(
            "Reference string (pages) - space/comma separated",
            value="7 0 1 2 0 3 0 4 2 3 0 3",
            height=120,
            key="vm_ref_input",
        )
        frames_input = st.number_input("Frames", min_value=1, max_value=100, value=3, key="vm_frames_input")
        algorithm = st.selectbox("Algorithm", options=["FIFO", "LRU", "Optimal"], key="vm_algo_select")
        run_button = st.button("Run Simulation", key="vm_run_button")
        st.markdown("---")
        st.subheader("Compare Algorithms")
        compare_button = st.button("Compare all algorithms", key="vm_compare_button")

    # If user clicked Run, compute and persist the result
    if run_button:
        try:
            with st.spinner("Running simulation..."):
                result = run_simulation(ref_input, frames_input, algorithm)
        except Exception as e:
            st.error(str(e))
            return
        # persist in session_state
        st.session_state["vm_last_result"] = {
            "algorithm": algorithm,
            "ref_input": ref_input,
            "frames_input": frames_input,
            "result": result,
        }
        st.session_state["vm_show_result"] = True
        # make sure compare view is off
        st.session_state["vm_show_compare"] = False

    # If user clicked Compare, compute and persist all results
    if compare_button:
        try:
            with st.spinner("Running all algorithms..."):
                all_results = run_all_algorithms(ref_input, frames_input)
        except Exception as e:
            st.error(str(e))
            return
        st.session_state["vm_all_results"] = {
            "ref_input": ref_input,
            "frames_input": frames_input,
            "results": all_results,
        }
        st.session_state["vm_show_compare"] = True
        st.session_state["vm_show_result"] = False

    # Show the last-run individual result (if present)
    if st.session_state.get("vm_show_result") and st.session_state.get("vm_last_result"):
        last = st.session_state["vm_last_result"]
        algorithm = last["algorithm"]
        result = last["result"]

        # Display summary
        st.subheader(f"Summary — {algorithm}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Page Faults", result["faults"])
        c2.metric("Total Hits", result["hits"])
        c3.metric(
            "Final Frames (non-empty)",
            ", ".join([str(x) for x in result["final_frames"] if x is not None]) or "(empty)",
        )

        # Show final frame layout & step renderer + step table
        st.subheader("Final Frame Layout")
        st.write(result["final_frames"])

        # ------------------------------
        # Step renderer (visual stepper + playback)
        # ------------------------------
        steps = result["steps"][:200]
        renderer = StepRenderer(key=f"vm_sim_stepper_{algorithm.lower()}")
        # render the visual stepper; appears in main column
        renderer.render(steps)

        # keep the textual step table below for debugging / quick glance
        st.subheader("Step-by-step (first 200 steps)")
        rows = []
        for s in steps:
            rows.append(
                {
                    "step": s.get("step"),
                    "req": s.get("request"),
                    "frames": " | ".join([str(x) if x is not None else "_" for x in s.get("frames", [])]),
                    "hit": s.get("is_hit"),
                    "replaced": s.get("replaced"),
                    "fault_count": s.get("fault_count"),
                }
            )
        st.table(rows)

    # Show comparison view if requested
    elif st.session_state.get("vm_show_compare") and st.session_state.get("vm_all_results"):
        packed = st.session_state["vm_all_results"]
        all_results = packed["results"]

        # Build comparison table
        st.subheader("Comparison Summary")
        comp_rows = []
        for name, r in all_results.items():
            comp_rows.append({"algorithm": name, "faults": r["faults"], "hits": r["hits"]})
        st.table(comp_rows)

        # Chart
        render_comparison_chart(all_results)

        # Optional: show final frame layout for each algo in expandable sections,
        # and include a small stepper for quick playback (first 50 steps).
        for name, r in all_results.items():
            with st.expander(f"{name} — final frames / brief stats"):
                st.write("Final frames:", r["final_frames"])
                st.write("Faults:", r["faults"], "Hits:", r["hits"])
                # show first 10 steps to avoid huge tables
                st.write(r["steps"][:10])

                # Small visual stepper for this algorithm (limited steps for speed)
                small_steps = r.get("steps", [])[:50]
                # unique key per algorithm so their session_state doesn't collide
                algo_key = f"cmp_{name.replace(' ', '_').lower()}_stepper"
                algo_renderer = StepRenderer(key=algo_key)
                algo_renderer.render(small_steps, initial_step=0)

    else:
        # Default prompt when nothing has been run yet
        st.info("Set inputs in the sidebar and click 'Run Simulation' or 'Compare all algorithms' to start.")


if __name__ == "__main__":
    main()
