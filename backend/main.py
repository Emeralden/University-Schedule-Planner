from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any

from models import TimeSlot, Professor, Room, Course, Schedule
from solver import solve_and_optimize_schedule

app = FastAPI(
    title="University Schedule Planner",
    description="Backend for the USP",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", response_class=FileResponse)
async def index():
    return "frontend/index.html"

class ProblemInput(BaseModel):
    professors: List[Professor]
    rooms: List[Room]
    time_slots: List[TimeSlot]
    courses: List[Course]

class SolveResponse(BaseModel):
    schedule: Schedule
    violations: List[str]
    cost: int
    happiness: int
    explanation: List[str]

@app.post("/solve", response_model=SolveResponse)
def solve_schedule(problem: ProblemInput) -> SolveResponse:
    all_data: Dict[str, Any] = {
        "courses": problem.courses,
        "professors": problem.professors,
        "rooms": problem.rooms,
        "time_slots": problem.time_slots
    }

    final_schedule, violations, happiness, explanations = solve_and_optimize_schedule(all_data, verbose=False)
    cost = len(violations)

    return SolveResponse(
        schedule=final_schedule,
        violations=violations,
        cost=cost,
        happiness=happiness,
        explanation=explanations
    )

@app.get("/status")
def status():
    return {"ok": True, "message": "USP running."}
