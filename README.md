**University Schedule Planner**

University Schedule Planner is an intelligent scheduling application that uses a hybrid AI approach to solve the complex problem of university course timetabling. It combines Local Search and Heuristic Optimization to generate valid, clash-free schedules that are optimized for a set of real-world soft constraints.

**Features:**

Dynamic & Interactive UI: A full web-based dashboard for adding/managing courses, professors, rooms, and time slots via forms and dynamic lists.

JSON File Upload: Easily import entire problem sets from JSON files for rapid testing.

Robust Hard Constraint Validation: The AI engine validates against a comprehensive set of rules, including capacity, availability, and department-level clashes.

Advanced Soft Constraint Optimization: The system doesn't just find a valid schedule; it finds the best one, optimizing a "Desirability" based on room efficiency and multiple professor preferences.

Resilient Three-Stage Solver: A sophisticated hybrid AI architecture that uses Hill Climbing, recovers from failure with the help of Simulated Annealing, and then optimizes the final result.

Explainable AI: Generates a human-readable log explaining the stages of its process.

**Tech Stack:**

Backend: Python, FastAPI
AI & Core Logic: Pydantic (for data modeling), Standard Python libraries
Frontend: Vanilla HTML5, CSS3, and JavaScript
Server: Uvicorn

**How to Run:**

Follow these steps to get University Schedule Planner running.

1. Prerequisites
   Python
   pip (Python package installer)

2. Clone the Repository
   Clone or download this project to your local machine.

3. Install Dependencies
   Install all the required Python packages using the requirements.txt file.
   pip install -r requirements.txt

4. Launch the Server
   Run the Uvicorn server from the project's root directory.
   uvicorn main:app --reload

5. Open the Application
   Open your web browser and navigate to:
   http://127.0.0.1:8000/
   You should now see the University Schedule Planner user interface and can begin creating and solving schedules.

**Project Structure:**

USP/
│
├── main.py # The FastAPI server and API endpoints.
├── models.py # The Pydantic data models (Course, Professor, etc.).
├── solver.py # The Core AI logic (Hill Climbing, Simulated Annealing).
├── constraints.py # The constraint validation and Desirability (happiness scoring) functions.
├── test_cli.py # A command-line script for testing the solver directly.
├── requirements.txt # A list of all Python dependencies.
│
└── frontend/
├── index.html # The main user interface page.
├── style.css # The styling for the UI.
└── script.js # The frontend logic for interactivity and API calls.

**How It Works:**

University Schedule Planner solves the timetabling challenge by first modeling it as a Constraint Satisfaction Problem (CSP) and then employing a powerful Local Search paradigm to find an optimal solution. The intelligence lies in its Three-Stage Cascading Solver Architecture:

**Stage 1**: Hill Climbing for Validity: The system first uses a fast Hill-Climbing algorithm to attempt to find a valid schedule by aggressively minimizing hard constraint violations. If it succeeds, it jumps directly to Stage 3.

**Stage 2**: Simulated Annealing Recovery: If Stage 1 fails and gets stuck in a local minimum, this stage activates. It takes the broken schedule and uses a Simulated Annealing algorithm, whose goal is still to find a valid (cost=0) schedule, but with the ability to escape the traps that the simple Hill Climber could not.

**Stage 3**: Simulated Annealing Optimizer: Once a valid schedule is secured (from either Stage 1 or 2), this final stage takes over. It uses another Simulated Annealing process, but this time its objective is to maximize the Desirability by intelligently satisfying the defined soft constraints.

This resilient, multi-stage approach ensures the system is robust enough to solve complex problems while also optimizing for real-world quality and user preferences.
