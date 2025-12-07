"""
Ultra-simple Step Renderer for Virtual Memory Simulator.

Features:
- First / Prev / Next / Last
- Step slider
- Simple frame display (no replaced, no faults)
- Very stable (only state + rerun)
"""

import streamlit as st
import html


def _normalize_step(step):
    """Return frames list from a step, safely."""
    if isinstance(step, dict):
        return list(step.get("frames", []))
    try:
        return list(step)
    except:
        return []


def _frame_html(val):
    """Simple grey frame box."""
    safe = html.escape(str(val)) if val is not None else "_"
    style = (
        "display:inline-block;padding:10px 14px;margin:6px;border-radius:8px;"
        "font-size:20px;font-family:monospace;border:2px solid #ccc;"
    )
    return f'<div style="{style}">{safe}</div>'


class StepRenderer:
    def __init__(self, key="simple_renderer"):
        self.key = key
        st.session_state.setdefault(f"{self.key}_cur", 0)

    def render(self, steps):
        steps = list(steps or [])
        n = len(steps)

        if n == 0:
            st.info("No steps to display.")
            return

        cur_key = f"{self.key}_cur"
        cur = st.session_state[cur_key]
        cur = max(0, min(cur, n - 1))
        st.session_state[cur_key] = cur

        # ---- BUTTON ROW ----
        c1, c2, c3, c4 = st.columns(4)

        if c1.button("⏮ First", key=f"{self.key}_first"):
            st.session_state[cur_key] = 0
            st.rerun()

        if c2.button("◀ Prev", key=f"{self.key}_prev"):
            st.session_state[cur_key] = max(0, cur - 1)
            st.rerun()

        if c3.button("Next ▶", key=f"{self.key}_next"):
            st.session_state[cur_key] = min(n - 1, cur + 1)
            st.rerun()

        if c4.button("Last ⏭", key=f"{self.key}_last"):
            st.session_state[cur_key] = n - 1
            st.rerun()

        cur = st.session_state[cur_key]

        # ---- SLIDER ----
        slider_key = f"{self.key}_slider"
        st.slider("Step", 0, n - 1, cur, key=slider_key)

        new_val = st.session_state[slider_key]
        if new_val != cur:
            st.session_state[cur_key] = new_val
            st.rerun()

        cur = st.session_state[cur_key]

        st.markdown(f"### Step {cur + 1} / {n}")

        # ---- FRAME DISPLAY ----
        frames = _normalize_step(steps[cur])
        html_blocks = "".join(_frame_html(v) for v in frames)

        st.markdown(
            f'<div style="display:flex;flex-wrap:wrap;">{html_blocks}</div>',
            unsafe_allow_html=True,
        )

        # Optional info (simple)
        st.write("Frames:", frames)
