from typing import List, Dict, Any, Optional, Tuple
from models import Schedule
import re

AllData = Dict[str, List[Any]]

def _get_attr(obj: Any, attr: str) -> Any:
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(attr)
    return getattr(obj, attr, None)

def _as_str(x: Any) -> str:
    return "" if x is None else str(x)

def _room_building(room_name: str) -> str:
    """
    Heuristic to extract building prefix from room name.
    e.g. 'hall_a' -> 'hall', 'lab_101' -> 'lab', 'BlockB-201' -> 'BlockB'
    """
    if not room_name:
        return ""
    token = re.split(r'[_\-]', room_name)[0]
    return re.sub(r'\d+$', '', token).lower()

def get_hard_constraint_violations(schedule: Schedule, all_data: AllData) -> List[str]:
    violations: List[str] = []

    courses_list = all_data.get("courses") or []
    profs_list = all_data.get("professors") or []
    rooms_list = all_data.get("rooms") or []
    times_list = all_data.get("time_slots") or []

    # Build quick lookups
    course_by_name: Dict[str, Any] = {}
    for c in courses_list:
        name = _get_attr(c, "name")
        if name:
            course_by_name[_as_str(name)] = c

    prof_by_name: Dict[str, Any] = {}
    for p in profs_list:
        name = _get_attr(p, "name")
        if name:
            prof_by_name[_as_str(name)] = p

    room_by_name: Dict[str, Any] = {}
    for r in rooms_list:
        name = _get_attr(r, "name")
        if name:
            room_by_name[_as_str(name)] = r

    # Normalize assignments (course_name -> (room_name, slot_id))
    assignments: Dict[str, Tuple[Optional[str], Optional[int]]] = {}
    raw_assigns = getattr(schedule, "assignments", {}) or {}
    if isinstance(raw_assigns, dict):
        for course_name, assign in raw_assigns.items():
            room_name = None
            slot_id = None
            if isinstance(assign, (list, tuple)) and len(assign) >= 2:
                room_name = assign[0]
                slot_id = assign[1]
            elif isinstance(assign, (list, tuple)) and len(assign) == 1:
                room_name = assign[0]
            assignments[_as_str(course_name)] = (room_name, slot_id)
    
    # HARD CONSTRAINT: Every course must be assigned
    for c in course_by_name.values():
        cname = _as_str(_get_attr(c, "name"))
        if cname not in assignments:
            violations.append(f"Error: Course {cname} is NOT assigned to any room or time slot.")
        else:
            room_name, slot_id = assignments[cname]
            if not room_name or slot_id is None:
                violations.append(f"Error: Course {cname} has incomplete assignment.")



    # Constraint 1: Room capacity
    for course_name, (room_name, slot_id) in assignments.items():
        course = course_by_name.get(course_name)
        if course is None:
            violations.append(f"Error: Unknown course '{course_name}' in schedule.")
            continue
        enrollment = _get_attr(course, "enrollment") or 0
        if not room_name:
            continue
        room = room_by_name.get(_as_str(room_name))
        if room is None:
            violations.append(f"Error: Course {course_name} assigned to unknown room '{room_name}'.")
            continue
        capacity = _get_attr(room, "capacity") or 0
        try:
            if int(enrollment) > int(capacity):
                violations.append(
                    f"Error: Course {course_name} ({enrollment} students) assigned to Room {room_name} ({capacity} capacity)."
                )
        except Exception:
            violations.append(f"Error: Could not compare enrollment/capacity for {course_name} and {room_name}.")

    # Constraint 2: Professor availability
    for course_name, (room_name, slot_id) in assignments.items():
        course = course_by_name.get(course_name)
        if not course:
            continue
        prof_name = _get_attr(course, "professor")
        if not prof_name or slot_id is None:
            continue
        prof = prof_by_name.get(_as_str(prof_name))
        if not prof:
            violations.append(f"Error: Course {course_name} assigned to unknown professor '{prof_name}'.")
            continue
        unavailable = _get_attr(prof, "unavailable_slots") or []
        if slot_id in unavailable:
            violations.append(f"Error: Professor {prof_name} assigned to slot {slot_id} for course {course_name}, but is unavailable.")

    # Constraint 3: Room availability
    for course_name, (room_name, slot_id) in assignments.items():
        if not room_name or slot_id is None:
            continue
        room = room_by_name.get(_as_str(room_name))
        if not room:
            continue
        room_unavail = _get_attr(room, "unavailable_slots") or []
        if slot_id in room_unavail:
            violations.append(f"Error: Room {room_name} is unavailable in slot {slot_id} but assigned to course {course_name}.")

    # Constraint 4: Professor multi-booking
    slot_prof_map: Dict[Any, Dict[str, List[str]]] = {}
    for course_name, (room_name, slot_id) in assignments.items():
        if slot_id is None:
            continue
        course = course_by_name.get(course_name)
        if not course:
            continue
        prof_name = _as_str(_get_attr(course, "professor") or "")
        if not prof_name:
            continue
        slot_prof_map.setdefault(slot_id, {}).setdefault(prof_name, []).append(course_name)
    for slot_id, prof_map in slot_prof_map.items():
        for prof_name, cnames in prof_map.items():
            if len(cnames) > 1:
                violations.append(f"Error: Professor {prof_name} multi-booked in slot {slot_id} for courses {', '.join(cnames)}.")

    # Constraint 5: Room multi-booking
    slot_room_map: Dict[Any, Dict[str, List[str]]] = {}
    for course_name, (room_name, slot_id) in assignments.items():
        if slot_id is None or not room_name:
            continue
        slot_room_map.setdefault(slot_id, {}).setdefault(_as_str(room_name), []).append(course_name)
    for slot_id, room_map in slot_room_map.items():
        for room_name, cnames in room_map.items():
            if len(cnames) > 1:
                violations.append(f"Error: Room {room_name} multi-booked in slot {slot_id} for courses {', '.join(cnames)}.")

    # Constraint 6: Department clash
    slot_dept_map: Dict[Any, Dict[str, List[str]]] = {}
    for course_name, (room_name, slot_id) in assignments.items():
        if slot_id is None:
            continue
        course = course_by_name.get(course_name)
        if not course:
            continue
        dept = _get_attr(course, "department")
        if not dept:
            continue
        slot_dept_map.setdefault(slot_id, {}).setdefault(_as_str(dept), []).append(course_name)
    for slot_id, dept_map in slot_dept_map.items():
        for dept_name, cnames in dept_map.items():
            if len(cnames) > 1:
                violations.append(
                    f"Error: Department {dept_name} is multi-booked in slot {slot_id} with courses {', '.join(cnames)}."
                )

    seen = set()
    deduped: List[str] = []
    for v in violations:
        if v not in seen:
            deduped.append(v)
            seen.add(v)
    return deduped


def calculate_happiness_score(schedule: Schedule, all_data: AllData) -> int:
    """
    Soft-constraint scorer. Higher is better.
    Combines multiple signals (room efficiency, prof prefs, professor balance, dept spread, venue efficiency).
    """
    # Start with a modest positive baseline
    score = 1000

    courses_list = all_data.get("courses") or []
    profs_list = all_data.get("professors") or []
    rooms_list = all_data.get("rooms") or []
    times_list = all_data.get("time_slots") or []

    # lookups
    prof_by_name = {}
    for p in profs_list:
        name = _get_attr(p, "name")
        if name:
            prof_by_name[_as_str(name)] = p

    room_by_name = {}
    for r in rooms_list:
        name = _get_attr(r, "name")
        if name:
            room_by_name[_as_str(name)] = r

    course_by_name = {}
    for c in courses_list:
        name = _get_attr(c, "name")
        if name:
            course_by_name[_as_str(name)] = c

    assigns = getattr(schedule, "assignments", {}) or {}

    # Soft 1: Room efficiency (penalize wasted seats)
    for course_obj in courses_list:
        cname = _get_attr(course_obj, "name")
        if not cname:
            continue
        cname = _as_str(cname)
        assign = assigns.get(cname)
        if not assign or not isinstance(assign, (list, tuple)) or len(assign) < 2:
            continue
        room_name, slot_id = assign[0], assign[1]
        if not room_name:
            continue
        room = room_by_name.get(_as_str(room_name))
        if not room:
            continue
        enrollment = _get_attr(course_obj, "enrollment") or 0
        capacity = _get_attr(room, "capacity") or 0
        try:
            wasted = int(capacity) - int(enrollment)
            if wasted > 0:
                score -= wasted
        except Exception:
            pass

    # Soft 2: Professor preferences
    for course_obj in courses_list:
        cname = _get_attr(course_obj, "name")
        if not cname:
            continue
        cname = _as_str(cname)
        assign = assigns.get(cname)
        if not assign or len(assign) < 2:
            continue
        slot_id = assign[1]
        prof_name = _get_attr(course_obj, "professor")
        if not prof_name:
            continue
        prof = prof_by_name.get(_as_str(prof_name))
        if not prof:
            continue
        preferred = _get_attr(prof, "preferred_slots") or []
        hates = _get_attr(prof, "hates_slots") or []
        try:
            if slot_id in preferred:
                score += 20
            if slot_id in hates:
                score -= 100
        except Exception:
            pass

    # Soft 3: Professor Balance Bonus
    slot_day = {}
    for t in times_list:
        sid = _get_attr(t, "slot_id")
        day = _get_attr(t, "day")
        if sid is not None and day is not None:
            slot_day[sid] = _as_str(day).lower()
    for p_name, p_obj in prof_by_name.items():
        taught = [cname for cname, assign in assigns.items()
                  if assign and len(assign) >= 2 and _as_str(_get_attr(course_by_name.get(cname), "professor") or "") == p_name]
        if len(taught) <= 1:
            continue
        days = set()
        for cname in taught:
            assign = assigns.get(cname)
            if assign and len(assign) >= 2:
                sid = assign[1]
                day = slot_day.get(sid)
                if day:
                    days.add(day)
        if len(days) >= 2:
            score += 40

    # Soft 4: Department Load Spread
    dept_courses: Dict[str, List[str]] = {}
    for c_obj in courses_list:
        cname = _get_attr(c_obj, "name")
        dept = _get_attr(c_obj, "department")
        if cname and dept:
            dept_courses.setdefault(_as_str(dept), []).append(_as_str(cname))
    for dept, clist in dept_courses.items():
        n = len(clist)
        for i in range(n):
            for j in range(i + 1, n):
                a = clist[i]; b = clist[j]
                ai = assigns.get(a); bi = assigns.get(b)
                if ai and bi and len(ai) >= 2 and len(bi) >= 2:
                    if ai[1] != bi[1]:
                        score += 30

    # Soft 5: Venue Efficiency Bonus
    for p_name, p_obj in prof_by_name.items():
        taught_rooms = []
        for cname, assign in assigns.items():
            if not assign or len(assign) < 2:
                continue
            prof_of_course = _get_attr(course_by_name.get(cname), "professor")
            if _as_str(prof_of_course) == p_name:
                taught_rooms.append(assign[0])
        if len(taught_rooms) <= 1:
            continue
        buildings = set(_room_building(r) for r in taught_rooms if r)
        if len(buildings) == 1 and list(buildings)[0] != "":
            score += 30

    try:
        score = int(score)
    except Exception:
        score = 0
    return score