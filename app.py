# File: app.py
"""
Streamlit UI for the Virtual Memory Simulator.
Updates: Rounded Graph Bars, Entrance Animation, Fixed Axis Scaling.
"""
import streamlit as st
import plotly.graph_objects as go
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
    p, label, .stMarkdown, li {
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
        border-radius: 20px;
        border: none;
        padding: 10px 24px;
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


def main():
    if "vm_last_result" not in st.session_state:
        st.session_state["vm_last_result"] = None
    if "vm_show_compare" not in st.session_state:
        st.session_state["vm_show_compare"] = False

    # --- SIDEBAR INPUTS ---
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        frames = st.number_input("RAM Space (Slots/Frames)", min_value=1, max_value=100, value=3)
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
                st.session_state["main_renderer_cur"] = 0
                st.session_state["vm_last_result"] = {"algo": algo, "res": res, "pages": pages}
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
        except Exception as e:
            st.error(f"Error: {str(e)}")

    # --- DISPLAY ---
    if st.session_state["vm_show_compare"]:
        st.title("📊 Algorithm Comparison")
        res = st.session_state["vm_compare_results"]
        
        # Prepare Data
        keys = list(res.keys())
        faults = [r["faults"] for r in res.values()]
        hits = [r["hits"] for r in res.values()]
        
        # Calculate max Y value to fix axis (Crucial for animation effect)
        max_y = max(max(faults), max(hits)) if faults else 10
        
        fig = go.Figure()

        # Trace 1: Faults (with Rounded Corners)
        fig.add_trace(go.Bar(
            name="Page Faults", 
            x=keys, 
            y=faults,
            marker=dict(color='#ff5252', cornerradius=15) # Rounded Corners
        ))
        
        # Trace 2: Hits (with Rounded Corners)
        fig.add_trace(go.Bar(
            name="Hits", 
            x=keys, 
            y=hits,
            marker=dict(color='#00e676', cornerradius=15) # Rounded Corners
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0d4fc'),
            barmode='group',
            xaxis_title="Algorithm",
            yaxis_title="Count",
            # Fix Y-axis range so bars grow INTO the space
            yaxis=dict(range=[0, max_y * 1.2]),
            # Animation Config
            transition={
                'duration': 1200,
                'easing': 'cubic-out'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### Detailed Stats")
        cols = st.columns(3)
        for idx, (name, data) in enumerate(res.items()):
            with cols[idx]:
                st.metric(f"{name} Faults", data["faults"], delta_color="inverse")

    elif st.session_state["vm_last_result"]:
        data = st.session_state["vm_last_result"]
        res = data["res"]
        
        cur_idx = st.session_state.get("main_renderer_cur", 0)
        cur_idx = min(cur_idx, len(res["steps"]) - 1)
        step_data = res["steps"][cur_idx]

        st.title(f"🟣 Simulation Results: {data['algo']}")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Process Requests", len(data['pages']))
        m2.metric("Page Faults", step_data["fault_count"], delta="-Faults", delta_color="inverse")
        m3.metric("RAM Hits", step_data["hit_count"], delta="+Hits")

        st.divider()
        st.subheader("🎞️ Step-by-Step Visualization")
        renderer = StepRenderer(key="main_renderer")
        renderer.render(res["steps"])
        
    else:
        render_landing_page()

if __name__ == "__main__":
    main()
