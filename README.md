# University Schedule Planner

An intelligent, full-stack scheduling application that uses a hybrid AI solver to tackle the NP-hard problem of university course timetabling. This project finds not just a *valid* schedule, but an *optimal* one, balancing a dense network of real-world constraints.

---

## Key Features

*   **Interactive Web UI:** A full-featured frontend built using Gemini, with vanilla HTML/CSS/JS for creating and managing courses, professors, rooms, and time slots. This acts as a platform to feature the powerful backend.
*   **Complex Constraint Modeling:** Models the problem as a Constraint Satisfaction Problem (CSP) with a rich set of both **Hard Constraints** (e.g., no double-booking) and **Soft Constraints** (e.g., professor preferences).
*   **Hybrid AI Solver:** Implements a novel **Three-Stage Solver Architecture** that combines the speed of greedy algorithms with the robustness of heuristic optimization.
*   **Explainable AI:** Provides a clear, step-by-step output of the solving process, demonstrating the journey from a broken or suboptimal state to a valid, high-quality solution.
*   **Full-Stack Integration:** The entire AI engine is served via a **FastAPI** backend, providing a robust REST API for the frontend client.

---

## Tech Stack

| Area      | Technology                                    |
| :-------- | :-------------------------------------------- |
| **Backend** | Python, FastAPI, Pydantic, Uvicorn                |
| **AI Core** | Hill-Climbing, Simulated Annealing (Custom Implementation) |

---

## The Three-Stage AI Solver Architecture

The intelligence of this project lies in its resilient, multi-stage approach. This is not a brute-force solver; it's a sophisticated pipeline designed to mimic intelligent problem-solving.

**[Random Schedule] -> [STAGE 1] --(Stuck?)--> [STAGE 2] --(Valid)--> [STAGE 3] -> [OPTIMIZED SCHEDULE]**

### Stage 1: Hill-Climbing for Validity (The Sprinter)
*   **Algorithm:** Greedy Hill-Climbing Local Search.
*   **Goal:** Aggressively find *any* valid schedule as fast as possible by minimizing hard constraint violations. If it finds a zero-violation state, it succeeds and passes the result directly to Stage 3.

### Stage 2: Simulated Annealing for Recovery (The Escape Artist)
*   **Activation:** This stage only runs if the fast Hill-Climbing search gets stuck in a local minimum.
*   **Algorithm:** Simulated Annealing.
*   **Goal:** To intelligently escape the trap. It can make "worse" moves to navigate out of the local minimum and find a path to a valid, zero-violation state.

### Stage 3: Simulated Annealing for Optimality (The Grandmaster)
*   **Activation:** This final stage only operates on a schedule that has been proven **100% valid**.
*   **Algorithm:** Simulated Annealing.
*   **Goal:** To maximize the "Happiness Score." It explores the vast space of *valid* schedules, intelligently trading off soft constraints to find a demonstrably superior, high-quality final result.

---

## How to Run

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Emeralden/University-Schedule-Planner
    ```
2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Launch the Server**
    ```bash
    uvicorn main:app --reload
    ```
4.  **Open the Application**
    *   Navigate to `http://127.0.0.1:8000/` in your web browser.

---

