# File: ui/segment_renderer.py
import streamlit as st

class SegmentRenderer:
    def __init__(self, key="seg_renderer"):
        self.key = key
        self.state_key = f"{self.key}_cur"
        self.slider_key = f"{self.key}_slider"

        if self.state_key not in st.session_state:
            st.session_state[self.state_key] = 0

    def _render_memory_bar(self, memory, total_size):
        """Renders the memory bar using CSS absolute positioning."""
        # FIX: Removed indentation and newlines to prevent Markdown interpreting this as a code block
        html = "<div style='position: relative; width: 100%; height: 80px; background: #222; border: 2px solid #555; border-radius: 8px; margin: 20px 0; overflow: hidden;'>"
        
        for seg in memory:
            # Calculate width and position in %
            width_pct = (seg['size'] / total_size) * 100
            left_pct = (seg['start'] / total_size) * 100
            
            # Styles
            is_free = seg['id'] == 'Free'
            
            # CSS Logic
            bg = "repeating-linear-gradient(45deg, #333, #333 10px, #444 10px, #444 20px)" if is_free else "linear-gradient(180deg, #6200ea, #3700b3)"
            border = "#555" if is_free else "#bb86fc"
            color = "#888" if is_free else "#fff"
            label = "Free" if is_free else f"PID: {seg['id']}"
            
            # Tooltip content
            title_attr = f"Start: {seg['start']}, Size: {seg['size']}KB"

            # Append segment div (Compact string to avoid Markdown issues)
            html += f"<div style='position: absolute; left: {left_pct}%; width: {width_pct}%; height: 100%; background: {bg}; border-right: 1px solid {border}; display: flex; flex-direction: column; align-items: center; justify-content: center; color: {color}; font-size: 0.8rem; font-weight: bold; white-space: nowrap; overflow: hidden; transition: all 0.3s ease;' title='{title_attr}'>"
            html += f"<span>{label}</span><span style='font-size: 0.7rem; opacity: 0.8;'>{seg['size']}KB</span></div>"
            
        html += "</div>"
        
        # Axis labels (0 and Max)
        html += f"<div style='display: flex; justify-content: space-between; color: #888; font-size: 0.8rem; padding: 0 5px;'><span>0 KB</span><span>{total_size} KB</span></div>"
        return html

    def render(self, result_data, total_ram):
        steps = result_data["steps"]
        total_steps = len(steps)
        
        # Navigation State Handling
        current_step = st.session_state[self.state_key]
        current_step = max(0, min(current_step, total_steps - 1))
        st.session_state[self.state_key] = current_step
        
        step_data = steps[current_step]
        
        # -- UI Layout --
        st.markdown(f"### 🎞️ Step {current_step + 1}: {step_data['operation']}")
        
        # Status Badge
        status_color = "#00e676" if step_data['success'] else "#ff5252"
        status_text = "SUCCESS" if step_data['success'] else "FAILED (No Space)"
        st.markdown(f"<div style='margin-bottom: 10px; color: {status_color}; border: 1px solid {status_color}; display: inline-block; padding: 2px 10px; border-radius: 5px; font-weight:bold;'>{status_text}</div>", unsafe_allow_html=True)

        # 1. The Memory Bar (Rendered with unsafe_allow_html=True)
        st.markdown(self._render_memory_bar(step_data['memory_state'], total_ram), unsafe_allow_html=True)
        
        # 2. Stats
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Total RAM", f"{total_ram} KB")
        with c2:
            st.metric("External Fragmentation (Free Space)", f"{step_data['external_fragmentation']} KB")

        st.divider()

        # -- Controls --
        def go_first(): st.session_state[self.state_key] = 0
        def go_prev(): st.session_state[self.state_key] = max(0, st.session_state[self.state_key] - 1)
        def go_next(): st.session_state[self.state_key] = min(total_steps - 1, st.session_state[self.state_key] + 1)
        def go_last(): st.session_state[self.state_key] = total_steps - 1
        def on_slider_change(): st.session_state[self.state_key] = st.session_state[self.slider_key]

        c_slider, _ = st.columns([1, 0.1])
        with c_slider:
            st.slider("Navigation", 0, total_steps - 1, key=self.slider_key, on_change=on_slider_change)

        b1, b2, b3, b4, b5 = st.columns([1, 1, 2, 1, 1])
        b1.button("⏮ Start", on_click=go_first, key="seg_start", use_container_width=True)
        b2.button("◀ Prev", on_click=go_prev, key="seg_prev", use_container_width=True)
        with b3:
             st.markdown(f"<div style='text-align:center; padding-top:10px; color:#bb86fc'>Step <b>{current_step + 1}</b> / {total_steps}</div>", unsafe_allow_html=True)
        b4.button("Next ▶", on_click=go_next, key="seg_next", use_container_width=True)
        b5.button("End ⏭", on_click=go_last, key="seg_end", use_container_width=True)
