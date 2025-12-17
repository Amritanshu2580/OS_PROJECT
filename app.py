"""
Streamlit UI for the Virtual Memory Simulator.
Includes:
- Elastic Graph Animation
- Advanced Styling
- StepRenderer
- NEW: Internal Fragmentation Simulation
"""
import streamlit as st
import plotly.graph_objects as go
import time
import random
from utils import parser
from algorithms.fifo import fifo
from algorithms.lru import lru
from algorithms.optimal import optimal
from ui.frame_renderer import StepRenderer

# --- CONFIGURATION ---
st.set_page_config(
    page_title="OS Simulator - Virtual Memory",
    page_icon="🟣",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* 1. DEEP PURPLE/PINK GRADIENT BACKGROUND */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #4a004e 0%, #1a0b2e 40%, #000000 100%);
        background-attachment: fixed;
        color: #e0d4fc;
    }
    
    /* 2. TEXT & HEADERS */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-family: 'Segoe UI', sans-serif;
        text-shadow: 0 0 10px rgba(187, 134, 252, 0.3);
    }
    p, label, .stMarkdown, li, .stText {
        color: #d1c4e9 !important;
    }

    /* 3. INFO CARDS */
    .info-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(5px);
        transition: transform 0.2s;
        height: 100%;
    }
    .info-card:hover {
        transform: translateY(-5px);
        background-color: rgba(255, 255, 255, 0.08);
        border-color: rgba(187, 134, 252, 0.4);
    }
    .card-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 10px;
        color: #bb86fc;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* 4. BUTTON STYLING */
    .stButton > button {
        background: linear-gradient(90deg, #7b1fa2, #4a148c);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(123, 31, 162, 0.4);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(123, 31, 162, 0.6);
        filter: brightness(1.2);
    }

    /* 5. INPUT FIELDS */
    .stTextArea textarea, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(30, 30, 40, 0.8) !important;
        color: white !important;
        border-radius: 10px;
        border: 1px solid #7c4dff;
    }
    
    /* 6. METRIC BOXES */
    div[data-testid="stMetric"] {
        background-color: rgba(46, 26, 71, 0.6);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(187, 134, 252, 0.2);
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    /* --- SIMULATOR SPECIFIC CSS --- */
    
    /* Chart Entrance Animation (Fade Up) */
    @keyframes slideUpFade {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .chart-entry {
        animation: slideUpFade 0.8s ease-out forwards;
    }

    /* Reference Tape */
    .ref-tape-container {
        overflow-x: auto;
        padding: 15px 0;
        margin-bottom: 10px;
        text-align: center;
        background: rgba(0,0,0,0.2);
        border-radius: 10px;
        border: 1px solid rgba(123, 31, 162, 0.3);
    }
    .ref-tape {
        display: inline-flex;
        gap: 10px;
        align-items: center;
    }
    .ref-item {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        font-weight: bold;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    .ref-past {
        color: #666;
        background: rgba(255,255,255,0.05);
        transform: scale(0.9);
    }
    .ref-current {
        color: #fff;
        background: #6200ea;
        border-color: #bb86fc;
        transform: scale(1.2);
        box-shadow: 0 0 15px #6200ea;
        z-index: 10;
    }
    .ref-future {
        color: #444;
        background: rgba(255,255,255,0.02);
        transform: scale(0.8);
    }

    /* Frames Container */
    .frames-container {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 20px;
        margin-top: 20px;
        padding: 20px;
    }
    
    /* Frame Box */
    .frame-box {
        width: 80px;
        height: 100px;
        background: linear-gradient(135deg, #2d2d3a 0%, #1e1e24 100%);
        border-radius: 12px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
        border: 2px solid #444;
        transition: all 0.4s ease;
        position: relative;
    }
    .frame-content {
        font-size: 2rem;
        font-weight: bold;
        color: #fff;
    }
    .frame-label {
        font-size: 0.7rem;
        color: #888;
        margin-top: 5px;
        text-transform: uppercase;
    }
    
    /* States */
    .frame-hit {
        border-color: #00e676;
        box-shadow: 0 0 20px rgba(0, 230, 118, 0.4);
        transform: translateY(-5px);
    }
    .frame-hit .frame-content { color: #00e676; }
    
    .frame-fault {
        border-color: #ff5252;
        box-shadow: 0 0 20px rgba(255, 82, 82, 0.4);
        animation: pulse-red 0.5s ease;
    }
    .frame-fault .frame-content { color: #ff5252; }

    @keyframes pulse-red {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

</style>
""", unsafe_allow_html=True)


# --- ALGORITHM MAPPING ---
ALGORITHM_MAP = {
    "FIFO": fifo,
    "LRU": lru,
    "Optimal": optimal,
}

# --- PRESET SCENARIOS ---
PRESETS = {
    "Standard Test": "7 0 1 2 0 3 0 4 2 3 0 3",
    "Thrashing (High Contention)": "1 2 3 4 5 1 2 3 4 5",
    "Locality Loop (Repeated Access)": "1 2 1 2 1 2 1 2",
    "Sequential Scan": "1 2 3 4 5 6 7 8 9 10"
}

def calculate_fragmentation(unique_pages, page_size_kb):
    """
    Simulates Internal Fragmentation.
    Assumes each unique page is the 'last page' of a process and is only partially full.
    Returns: A dictionary mapping page_id -> wasted_bytes
    """
    frag_map = {}
    for p in unique_pages:
        # Randomly decide how much of the page is used (50% to 99%)
        # In real life, internal frag is (PageSize - ProcessSize % PageSize)
        # Here we simulate the 'gap' directly.
        used_percentage = random.uniform(0.5, 0.99)
        used_space = page_size_kb * used_percentage
        wasted_space = page_size_kb - used_space
        frag_map[p] = round(wasted_space, 2)
    return frag_map

def render_landing_page():
    """Renders the educational landing page with Card-styled info."""
    st.title("🟣 Virtual Memory Simulator")
    st.markdown("### Master Page Replacement Algorithms")
    st.markdown("Select your configuration in the sidebar to begin, or learn about the algorithms below.")
    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="info-card">
            <div class="card-title">FIFO</div>
            <p><strong>First-In, First-Out</strong></p>
            <p>Replaces the oldest page in memory. Simple but can suffer from Belady's Anomaly.</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="info-card">
            <div class="card-title">LRU</div>
            <p><strong>Least Recently Used</strong></p>
            <p>Replaces the page unused for the longest time. Great performance, harder to implement.</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="info-card">
            <div class="card-title">Optimal</div>
            <p><strong>Theoretical Best</strong></p>
            <p>Replaces the page not needed for the longest time in future. Impossible in real-time.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("<h4 style='text-align: center; color: #b39ddb;'>👈 Select your inputs in the sidebar to start!</h4>", unsafe_allow_html=True)


def create_bar_chart(res, keys, faults, hits, max_y, is_zero_state=False):
    """Helper to create the Plotly Figure with controlled animation."""
    fig = go.Figure()

    # If in 'zero state', we force all values to 0 to prime the animation
    plot_faults = [0] * len(faults) if is_zero_state else faults
    plot_hits = [0] * len(hits) if is_zero_state else hits
    
    # Hide text when bars are zero
    text_pos = 'none' if is_zero_state else 'auto'
    
    # DURATION LOGIC:
    anim_duration = 0 if is_zero_state else 2500 

    fig.add_trace(go.Bar(
        name="Page Faults", 
        x=keys, 
        y=plot_faults,
        text=plot_faults,
        textposition=text_pos,
        marker=dict(color='#ff5252', cornerradius=10)
    ))
    
    fig.add_trace(go.Bar(
        name="Hits", 
        x=keys, 
        y=plot_hits,
        text=plot_hits,
        textposition=text_pos,
        marker=dict(color='#00e676', cornerradius=10)
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0d4fc'),
        barmode='group',
        xaxis_title="Algorithm",
        yaxis_title="Count",
        yaxis=dict(
            range=[0, max_y], 
            gridcolor='rgba(255,255,255,0.1)'
        ),
        hovermode="x",
        transition={'duration': anim_duration, 'easing': 'cubic-out'} 
    )
    return fig


def main():
    if "vm_last_result" not in st.session_state:
        st.session_state["vm_last_result"] = None
    if "vm_show_compare" not in st.session_state:
        st.session_state["vm_show_compare"] = False
    
    if "anim_trigger" not in st.session_state:
        st.session_state["anim_trigger"] = False

    # --- SIDEBAR INPUTS ---
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # 1. Paging Config
        frames = st.number_input("RAM Space (Slots/Frames)", min_value=1, max_value=100, value=3)
        page_size = st.number_input("Page Size (KB)", min_value=1, max_value=64, value=4, help="Used to calculate Fragmentation")
        
        # 2. Input Config
        input_method = st.radio("Process Input Mode:", ["Select Preset", "Manual Entry"], horizontal=True)
        
        if input_method == "Select Preset":
            preset_name = st.selectbox("Choose a scenario:", list(PRESETS.keys()))
            ref_str = PRESETS[preset_name]
            st.caption(f"Pattern: `{ref_str}`")
        else:
            ref_str = st.text_area("Enter Process IDs (space-separated)", value="", placeholder="e.g., 7 0 1 2 0 3...", height=100)

        algo = st.selectbox("Algorithm", ["FIFO", "LRU", "Optimal"])
        st.divider()
        
        col_run, col_comp = st.columns(2)
        with col_run:
            run_clicked = st.button("🚀 Run", use_container_width=True)
        with col_comp:
            compare_clicked = st.button("📊 Compare", use_container_width=True)

    # --- HANDLERS ---
    if run_clicked:
        try:
            if not ref_str.strip():
                st.error("Please enter a valid Reference String.")
            else:
                pages = parser.parse_reference_string(ref_str)
                res = ALGORITHM_MAP[algo](pages, frames)
                
                # Internal Fragmentation Simulation
                unique_pages = list(set(pages))
                frag_map = calculate_fragmentation(unique_pages, page_size)
                
                st.session_state["vis_renderer_cur"] = 0
                st.session_state["vm_last_result"] = {
                    "algo": algo, 
                    "res": res, 
                    "pages": pages,
                    "frag_map": frag_map # Store frag data
                }
                st.session_state["vm_show_compare"] = False
        except Exception as e:
            st.error(f"Error: {str(e)}")

    if compare_clicked:
        try:
            if not ref_str.strip():
                 st.error("Please enter a valid Reference String.")
            else:
                results = {}
                pages = parser.parse_reference_string(ref_str)
                for k, v in ALGORITHM_MAP.items():
                    results[k] = v(pages, frames)
                st.session_state["vm_compare_results"] = results
                st.session_state["vm_show_compare"] = True
                st.session_state["anim_trigger"] = True
        except Exception as e:
            st.error(f"Error: {str(e)}")

    # --- DISPLAY ---
    if st.session_state["vm_show_compare"]:
        st.title("📊 Algorithm Comparison")
        st.markdown('<div class="chart-entry">', unsafe_allow_html=True)
        
        res = st.session_state["vm_compare_results"]
        keys = list(res.keys())
        faults = [r["faults"] for r in res.values()]
        hits = [r["hits"] for r in res.values()]
        
        max_val = max(max(faults), max(hits)) if faults else 10
        y_limit = max_val * 1.3
        
        # Placeholder for the chart
        chart_spot = st.empty()
        
        # --- ANIMATION LOGIC ---
        if st.session_state["anim_trigger"]:
            fig_zero = create_bar_chart(res, keys, faults, hits, y_limit, is_zero_state=True)
            chart_spot.plotly_chart(fig_zero, use_container_width=True, key="vm_compare_chart")
            time.sleep(0.3) 
            st.session_state["anim_trigger"] = False
            st.rerun()
        else:
            fig_final = create_bar_chart(res, keys, faults, hits, y_limit, is_zero_state=False)
            chart_spot.plotly_chart(fig_final, use_container_width=True, key="vm_compare_chart")

        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### Detailed Stats")
        cols = st.columns(3)
        for idx, (name, data) in enumerate(res.items()):
            with cols[idx]:
                st.metric(f"{name} Faults", data["faults"], delta_color="inverse")

    elif st.session_state["vm_last_result"]:
        data = st.session_state["vm_last_result"]
        res = data["res"]
        frag_map = data.get("frag_map", {})
        # Retrieve page_size from session state if available, else default to 4
        current_page_size = page_size 
        
        st.title(f"🟣 Simulation: {data['algo']}")
        
        # Calculate Total Waste for resident pages
        final_frames = [f for f in res["final_frames"] if f is not None]
        if final_frames:
            current_waste = sum([frag_map.get(p, 0) for p in final_frames])
            st.info(f"💾 **Internal Fragmentation:** Total wasted RAM in current frames: **{current_waste:.2f} KB**")
        
        renderer = StepRenderer(key="vis_renderer")
        
        # --- UPDATE: Passing the fragmentation data to the render function ---
        renderer.render(res["steps"], frag_map=frag_map, page_size=current_page_size)
        
    else:
        render_landing_page()

if __name__ == "__main__":
    main()
