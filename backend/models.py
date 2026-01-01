from pydantic import BaseModel
from typing import Dict, Tuple, List, Optional


# BASE MODELS

class TimeSlot(BaseModel):
    day: str
    start_time: str
    end_time: str
    slot_id: int


class Professor(BaseModel):
    name: str
    unavailable_slots: List[int] = []
    preferred_slots: List[int] = []
    hates_slots: List[int] = []


class Room(BaseModel):
    name: str
    capacity: int
    unavailable_slots: List[int] = []


class Course(BaseModel):
    name: str
    enrollment: int
    professor: str
    department: str
    is_elective_for: List[str] = []


# SCHEDULE MODEL

class Schedule(BaseModel):
    assignments: Dict[str, Tuple[Optional[str], Optional[int]]] = {}
