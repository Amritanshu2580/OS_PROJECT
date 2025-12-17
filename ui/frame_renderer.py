"""
Advanced Step Renderer for Virtual Memory Simulator.
Features:
- Split Layout: Main Simulation (Left) | Fragmentation Stack (Right)
- Visual Reference Tape
- Color-coded Frames
- Disk/Swap Space Visualization
- Vertical Stack for Internal Fragmentation Analysis
- Robust Navigation
"""

import streamlit as st

class StepRenderer:
    def __init__(self, key="vis_renderer"):
        self.key = key
        self.state_key = f"{self.key}_cur"
        self.slider_key = f"{self.key}_slider"

        if self.state_key not in st.session_state:
            st.session_state[self.state_key] = 0

    def _render_frag_stack(self, frames, frag_map, page_size):
        """
        Renders the Right-Side Stack for Internal Fragmentation.
        Uses single-line string concatenation to prevent Markdown indentation issues.
        """
        # 1. Container Start
        html = "<div style='background: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 20px; border: 1px solid rgba(255,255,255,0.08); height: 100%;'>"
        html += "<h4 style='margin-top:0; border-bottom:1px solid #444; padding-bottom:10px; font-size:1.1rem; color: #e0d4fc;'>🧩 RAM Monitor</h4>"
        
        total_wasted = 0
        
        for i, p_id in enumerate(frames):
            html += f"<div style='margin-top: 15px; font-size: 0.8rem; text-transform: uppercase; color: #888; letter-spacing: 1px;'>Frame {i}</div>"
            
            if p_id is None:
                # Empty Frame Visual
                html += "<div style='width: 100%; height: 35px; background: transparent; border: 2px dashed #444; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #555; font-size: 0.85rem;'>[ Empty Slot ]</div>"
            else:
                # Calculate metrics
                wasted = frag_map.get(p_id, 0) if frag_map else 0
                used = page_size - wasted
                total_wasted += wasted
                
                pct_used = (used / page_size) * 100
                pct_wasted = (wasted / page_size) * 100
                
                # Header
                html += "<div style='display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 0.9rem;'>"
                html += f"<span style='font-weight: bold; color: #fff;'>Process {p_id}</span>"
                html += f"<span style='color: #aaa;'>Size: {page_size}KB</span></div>"
                
                # Bar Container
                html += "<div style='width: 100%; height: 30px; display: flex; border-radius: 6px; overflow: hidden; background: #222; border: 1px solid #444;'>"
                # Green Bar
                html += f"<div style='width: {pct_used}%; background: linear-gradient(90deg, #00c853, #69f0ae); height: 100%;'></div>"
                # Red Bar
                html += f"<div style='width: {pct_wasted}%; background: linear-gradient(90deg, #d50000, #ff5252); height: 100%;'></div>"
                html += "</div>"
                
                # Legend
                html += "<div style='display: flex; justify-content: space-between; font-size: 0.75rem; margin-top: 4px;'>"
                html += f"<span style='color: #69f0ae;'>Used: {used:.2f} KB</span>"
                html += f"<span style='color: #ff5252;'>Wasted: {wasted:.2f} KB</span></div>"
        
        # Summary Footer
        html += "<div style='margin-top: 25px; border-top: 1px solid #444; padding-top: 15px; text-align: center;'>"
        html += "<div style='font-size: 0.85rem; color: #aaa;'>Current Total Fragmentation</div>"
        html += f"<div style='font-size: 1.5rem; font-weight: bold; color: #ff5252; text-shadow: 0 0 10px rgba(255, 82, 82, 0.4);'>{total_wasted:.2f} KB</div>"
        html += "</div></div>"
        
        return html

    def _render_reference_tape(self, all_requests, cur_idx, current_req):
        html = "<div class='ref-tape-container'><div class='ref-tape'>"
        for i, val in enumerate(all_requests):
            val_str = str(val)
            css_class = "ref-item ref-current" if i == cur_idx else ("ref-item ref-past" if i < cur_idx else "ref-item ref-future")
            html += f"<div class='{css_class}'>{val_str}</div>"
        html += "</div></div>"
        return html

    def _render_frames(self, frames, current_req, is_hit, replaced_val):
        html = "<div class='frames-container'>"
        for f_val in frames:
            content = str(f_val) if f_val is not None else "-"
            box_class = "frame-box"
            if f_val == current_req and f_val is not None:
                box_class += " frame-hit" if is_hit else " frame-fault"
            html += f"<div class='{box_class}'><div class='frame-content'>{content}</div><div class='frame-label'>Frame</div></div>"
        html += "</div>"
        return html

    def _render_disk(self, all_requests, current_step, current_frames, current_req, is_hit):
        pages_in_ram = set([f for f in current_frames if f is not None])
        history = set(all_requests[:current_step])
        pages_seen_total = set(all_requests[:current_step+1])
        disk_pages = sorted(list(pages_seen_total - pages_in_ram))
        is_swapped_in = (not is_hit) and (current_req in history)
        
        html = "<div style='margin-top: 20px; padding: 15px; border: 1px dashed #555; border-radius: 10px; background: rgba(0,0,0,0.2);'>"
        html += "<h5 style='text-align: center; color: #888; margin-bottom: 10px;'>💾 Disk / Swap Space</h5>"
        html += "<div style='display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; min-height: 50px;'>"
        
        if not disk_pages and not is_swapped_in:
             html += "<div style='color: #666; font-style: italic; align-self: center;'>Disk is empty</div>"
        else:
            display_list = list(disk_pages)
            if is_swapped_in and current_req not in display_list:
                display_list.append(current_req)
                display_list.sort()
            
            for page in display_list:
                style = "width: 40px; height: 40px; background: #333; color: #aaa; display: flex; align-items: center; justify-content: center; border-radius: 5px; font-weight: bold; border: 1px solid #555;"
                if is_swapped_in and page == current_req:
                    style = "width: 40px; height: 40px; background: #e65100; color: #fff; display: flex; align-items: center; justify-content: center; border-radius: 5px; font-weight: bold; border: 2px solid #ffab00; box-shadow: 0 0 15px #ffab00; transform: scale(1.15); z-index: 10;"
                html += f"<div style='{style}'>{page}</div>"
        html += "</div></div>"
        return html

    def _render_final_summary(self, final_step, total_steps):
        st.markdown("---")
        st.markdown("### 🏁 Simulation Complete")
        faults = final_step['fault_count']
        hits = final_step['hit_count']
        hit_ratio = (hits / total_steps) * 100 if total_steps > 0 else 0
        fault_ratio = (faults / total_steps) * 100 if total_steps > 0 else 0
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Requests", total_steps)
        m2.metric("Total Hits", hits, f"{hit_ratio:.1f}%")
        m3.metric("Total Faults", faults, f"{fault_ratio:.1f}%", delta_color="inverse")
        m4.metric("Hit Ratio", f"{hit_ratio:.1f}%")

    def render(self, steps, frag_map=None, page_size=4):
        if not steps:
            st.warning("No simulation steps available.")
            return

        total_steps = len(steps)
        current_step = st.session_state[self.state_key]
        current_step = max(0, min(current_step, total_steps - 1))
        st.session_state[self.state_key] = current_step
        st.session_state[self.slider_key] = current_step

        step_data = steps[current_step]
        all_requests = [s['request'] for s in steps]
        current_req = step_data['request']
        current_frames = step_data['frames']
        is_hit = step_data['is_hit']
        replaced = step_data.get('replaced', None)
        fault_count_so_far = step_data['fault_count']

        st.markdown("### 🎞️ Simulation View")
        
        # --- LAYOUT ---
        c_main, c_stack = st.columns([3, 1.2])

        # --- LEFT COLUMN ---
        with c_main:
            st.markdown("**Reference String (Process Requests):**")
            st.markdown(self._render_reference_tape(all_requests, current_step, current_req), unsafe_allow_html=True)

            status_color = "#00e676" if is_hit else "#ff5252"
            status_text = "✅ PAGE HIT" if is_hit else "❌ PAGE FAULT"
            # Badge HTML (Single Line)
            badge_html = f"<div style='text-align:center; margin: 20px 0;'><span style='background-color: {status_color}22; border: 1px solid {status_color}; color: {status_color}; padding: 8px 16px; border-radius: 20px; font-weight: bold; font-size: 1.1rem; letter-spacing: 1px;'>{status_text}</span><div style='margin-top:10px; font-size: 0.9rem; color: #ccc;'>Request: <strong>{current_req}</strong> | Replaced: <strong>{replaced if replaced is not None else 'None'}</strong></div></div>"
            st.markdown(badge_html, unsafe_allow_html=True)

            st.markdown(self._render_frames(current_frames, current_req, is_hit, replaced), unsafe_allow_html=True)
            st.markdown(self._render_disk(all_requests, current_step, current_frames, current_req, is_hit), unsafe_allow_html=True)

        # --- RIGHT COLUMN ---
        with c_stack:
            st.markdown(self._render_frag_stack(current_frames, frag_map, page_size), unsafe_allow_html=True)

        # --- CONTROLS ---
        st.divider()
        if current_step == total_steps - 1:
            self._render_final_summary(step_data, total_steps)

        def go_first(): st.session_state[self.state_key] = 0
        def go_prev(): st.session_state[self.state_key] = max(0, st.session_state[self.state_key] - 1)
        def go_next(): st.session_state[self.state_key] = min(total_steps - 1, st.session_state[self.state_key] + 1)
        def go_last(): st.session_state[self.state_key] = total_steps - 1
        def on_slider_change(): st.session_state[self.state_key] = st.session_state[self.slider_key]

        c_slider, _ = st.columns([1, 0.1])
        with c_slider:
            st.slider("Timeline Navigation", 0, total_steps - 1, key=self.slider_key, on_change=on_slider_change)

        b1, b2, b3, b4, b5 = st.columns([1, 1, 2, 1, 1])
        b1.button("⏮ Start", on_click=go_first, use_container_width=True)
        b2.button("◀ Prev", on_click=go_prev, use_container_width=True)
        with b3:
            st.markdown(f"<div style='text-align:center; padding-top:10px; color:#bb86fc'>Step <b>{current_step + 1}</b> / {total_steps}</div>", unsafe_allow_html=True)
        b4.button("Next ▶", on_click=go_next, use_container_width=True)
        b5.button("End ⏭", on_click=go_last, use_container_width=True)
