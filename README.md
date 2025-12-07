Virtual Memory Simulator

A visual, interactive simulator for classic OS page-replacement algorithms — FIFO, LRU, and Optimal — built with Python and Streamlit.

The app helps students and developers understand how frames update on every memory access and how page faults occur.
It also includes a clean step-by-step renderer that lets you move through the execution like a timeline.

🚀 Features
✔ Page Replacement Algorithms

FIFO (First-In First-Out)

LRU (Least Recently Used)

Optimal (Belady’s Optimal Algorithm)

✔ Interactive Visualization

Step-by-step view

Next / Previous / First / Last navigation

Frame display updates at each step

Shows final frames, total faults, and hits

✔ Input Flexibility

Accepts space- or comma-separated reference strings

Configurable number of frames

✔ Clean UI

Built using Streamlit, with responsive layout and fast updates.

📸 Screenshots (optional)

Add 1–2 screenshots here once you run the app:

Home page

Step-by-step visualization

Example placeholder:

/assets/screenshot_main.png
/assets/screenshot_stepper.png

🛠️ Installation & Setup
1. Clone the project
git clone https://github.com/Amritanshu2580/OS_PROJECT

2. Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

3. Install dependencies
pip install -r requirements.txt

4. Run the app
streamlit run app.py

📌 How It Works
1. Enter Inputs

Reference string (e.g., 7 0 1 2 0 3 0 4 2 3 0 3)

Number of frames

Algorithm (FIFO / LRU / Optimal)

2. Run Simulation

Click Run Simulation — the app computes:

step-by-step execution

total page faults

hits

final frame layout

3. Step Renderer

Use the controls to navigate the simulation:

⏮ First step

◀ Prev

Next ▶

Last ⏭

Step slider

📦 Project Structure
.
├── app.py
├── ui/
│   ├── frame_renderer.py        # step-by-step UI renderer
├── algorithms/
│   ├── fifo.py
│   ├── lru.py
│   └── optimal.py
├── utils/
│   ├── parser.py
├── requirements.txt
└── README.md

📚 OS Concepts Covered

This simulator demonstrates:

🧠 Page Replacement

FIFO anomaly

Optimal algorithm behavior

Working set relevance

🧠 Page Faults

When a page is not found in frames

How replacement decisions affect performance

🧠 Memory Visualization

Frame-by-frame evolution

Real-time navigation through steps

Great for students, educators, and OS learners.

🧪 Testing 

Light tests can be added under a /tests folder:

Check parser input

Algorithm correctness

Simulation consistency

(Not required for basic use.)

👤 Author

Built by Loic, Amritanshu and Jasleen as part of an Operating Systems project.

If you found it useful, leave a ⭐ on the repo!