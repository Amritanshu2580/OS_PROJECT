"""
Advanced Step Renderer for Virtual Memory Simulator.
Features:
- Visual Reference Tape (Past/Current/Future)
- Color-coded Frames (Green=Hit, Red=Fault, Grey=Idle)
- Status Indicators (Hit/Miss Badges)
- Robust Navigation (Callbacks + State Sync)
- Final Results Summary (Auto-appears at end)
"""

import streamlit as st

class StepRenderer:
    def __init__(self, key="vis_renderer"):
        self.key = key
        # Master state key for the current step index
        self.state_key = f"{self.key}_cur"
        # Slider specific key
        self.slider_key = f"{self.key}_slider"

        # Initialize Master State if missing
        if self.state_key not in st.session_state:
            st.session_state[self.state_key] = 0

    def _render_reference_tape(self, all_requests, cur_idx, current_req):
        """Renders the top row showing the stream of numbers."""
        html_content = '<div class="ref-tape-container"><div class="ref-tape">'
        
        for i, val in enumerate(all_requests):
            val_str = str(val)
            if i < cur_idx:
                css_class = "ref-item ref-past"
            elif i == cur_idx:
                css_class = "ref-item ref-current"
            else:
                css_class = "ref-item ref-future"
            
            html_content += f'<div class="{css_class}">{val_str}</div>'
        
        html_content += '</div></div>'
        return html_content

    def _render_frames(self, frames, current_req, is_hit, replaced_val):
        """Renders the RAM frames with color logic."""
        html_content = '<div class="frames-container">'
        
        for f_val in frames:
            content = str(f_val) if f_val is not None else "-"
            
            box_class = "frame-box"
            if f_val == current_req and f_val is not None:
                if is_hit:
                    box_class += " frame-hit"
                else:
                    box_class += " frame-fault"
            
            html_content += f'<div class="{box_class}"><div class="frame-content">{content}</div><div class="frame-label">Frame</div></div>'
            
        html_content += '</div>'
        return html_content

    def _render_final_summary(self, final_step, total_steps):
        """Renders a stats summary when the simulation is finished."""
        st.markdown("---")
        st.markdown("### 🏁 Simulation Complete")
        
        faults = final_step['fault_count']
        hits = final_step['hit_count']
        hit_ratio = (hits / total_steps) * 100 if total_steps > 0 else 0
        fault_ratio = (faults / total_steps) * 100 if total_steps > 0 else 0
        
        # Display using Streamlit metrics (styled by app.py)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Requests", total_steps)
        m2.metric("Total Hits", hits, f"{hit_ratio:.1f}%")
        m3.metric("Total Faults", faults, f"{fault_ratio:.1f}%", delta_color="inverse")
        m4.metric("Hit Ratio", f"{hit_ratio:.1f}%")

    def render(self, steps):
        if not steps:
            st.warning("No simulation steps available.")
            return

        total_steps = len(steps)
        
        # --- LOGIC: Bi-Directional Sync ---
        # 1. Ensure master state is within bounds
        current_step = st.session_state[self.state_key]
        current_step = max(0, min(current_step, total_steps - 1))
        st.session_state[self.state_key] = current_step
        
        # 2. Sync Slider to Master State
        st.session_state[self.slider_key] = current_step

        # --- DATA EXTRACTION ---
        step_data = steps[current_step]
        all_requests = [s['request'] for s in steps]
        current_req = step_data['request']
        current_frames = step_data['frames']
        is_hit = step_data['is_hit']
        replaced = step_data.get('replaced', None)
        fault_count_so_far = step_data['fault_count']

        # --- VISUALIZATION ---
        st.markdown("### 🎞️ Simulation View")
        
        # A. Reference Tape
        st.markdown("**Reference String (Process Requests):**")
        st.markdown(
            self._render_reference_tape(all_requests, current_step, current_req), 
            unsafe_allow_html=True
        )

        # B. Status Badge
        status_color = "#00e676" if is_hit else "#ff5252"
        status_text = "✅ PAGE HIT" if is_hit else "❌ PAGE FAULT"
        
        badge_html = f"""
<div style="text-align:center; margin: 20px 0;">
<span style="background-color: {status_color}22; border: 1px solid {status_color}; color: {status_color}; padding: 8px 16px; border-radius: 20px; font-weight: bold; font-size: 1.1rem; letter-spacing: 1px;">{status_text}</span>
<div style="margin-top:10px; font-size: 0.9rem; color: #ccc;">
Current Request: <strong>{current_req}</strong> | 
Replaced: <strong>{replaced if replaced is not None else 'None'}</strong> | 
Total Faults: {fault_count_so_far}
</div>
</div>
"""
        st.markdown(badge_html, unsafe_allow_html=True)

        # C. RAM Frames
        st.markdown(
            self._render_frames(current_frames, current_req, is_hit, replaced),
            unsafe_allow_html=True
        )
        
        # --- D. Final Summary (Conditional) ---
        # Only show this if we are at the very last step
        if current_step == total_steps - 1:
            self._render_final_summary(step_data, total_steps)
        
        st.divider()

        # --- CONTROLS (CALLBACK BASED) ---
        
        def go_first():
            st.session_state[self.state_key] = 0
        
        def go_prev():
            st.session_state[self.state_key] = max(0, st.session_state[self.state_key] - 1)
            
        def go_next():
            st.session_state[self.state_key] = min(total_steps - 1, st.session_state[self.state_key] + 1)
            
        def go_last():
            st.session_state[self.state_key] = total_steps - 1
            
        def on_slider_change():
            st.session_state[self.state_key] = st.session_state[self.slider_key]

        # 1. Slider Row
        c_slider, _ = st.columns([1, 0.1])
        with c_slider:
            st.slider(
                "Timeline Navigation", 
                min_value=0, 
                max_value=total_steps - 1, 
                key=self.slider_key,
                on_change=on_slider_change
            )

        # 2. Button Row
        b1, b2, b3, b4, b5 = st.columns([1, 1, 2, 1, 1])
        
        b1.button("⏮ Start", on_click=go_first, use_container_width=True)
        b2.button("◀ Prev", on_click=go_prev, use_container_width=True)
        
        with b3:
            st.markdown(f"<div style='text-align:center; padding-top:10px; color:#bb86fc'>Step <b>{current_step + 1}</b> / {total_steps}</div>", unsafe_allow_html=True)

        b4.button("Next ▶", on_click=go_next, use_container_width=True)
        b5.button("End ⏭", on_click=go_last, use_container_width=True)