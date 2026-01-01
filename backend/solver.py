import random
import copy
import math
from typing import Dict, List, Tuple, Any

from models import Schedule
from constraints import get_hard_constraint_violations, calculate_happiness_score

AllData = Dict[str, List[Any]]

# Helpers

def _get_name(obj: Any) -> str:
    if obj is None:
        return ""
    if hasattr(obj, "name"):
        return getattr(obj, "name") or ""
    if isinstance(obj, dict):
        return obj.get("name", "") or ""
    return ""

def _get_slot_id(obj: Any) -> Any:
    if obj is None:
        return None
    if hasattr(obj, "slot_id"):
        return getattr(obj, "slot_id")
    if isinstance(obj, dict):
        return obj.get("slot_id")
    return None


def _ensure_all_courses(schedule: Schedule, courses: List[Any]) -> None:
    """
    Guarantee that schedule.assignments has an entry for EVERY course.
    If missing, insert (None, None) so hard constraints will flag it.
    """
    if schedule.assignments is None:
        schedule.assignments = {}
    for c in courses:
        cname = _get_name(c).strip()
        if not cname:
            continue
        if cname not in schedule.assignments:
            schedule.assignments[cname] = (None, None)


# Random schedule
def generate_random_schedule(all_data: AllData) -> Schedule:
    sched = Schedule(assignments={})
    courses = all_data.get("courses", [])
    rooms = all_data.get("rooms", [])
    slots = all_data.get("time_slots", [])

    if not rooms or not slots or not courses:
        _ensure_all_courses(sched, courses)
        return sched

    for c in courses:
        cname = _get_name(c)
        if not cname:
            continue

        r = random.choice(rooms)
        s = random.choice(slots)

        rname = _get_name(r)
        sid = _get_slot_id(s)

        if not rname or sid is None:
            sched.assignments[cname] = (None, None)
            continue

        sched.assignments[cname] = (rname, sid)

    _ensure_all_courses(sched, courses)
    return sched


# ---------------- Stage 1: Hill Climb for validity ----------------
def _hill_climbing_for_validity(all_data: AllData, verbose: bool = True) -> Tuple[Schedule, int]:
    courses = all_data.get("courses", []) or []
    rooms = all_data.get("rooms", []) or []
    slots = all_data.get("time_slots", []) or []

    current = generate_random_schedule(all_data)
    _ensure_all_courses(current, courses)

    current_cost = len(get_hard_constraint_violations(current, all_data))

    max_no_improve = 200
    steps_no_improve = 0

    if verbose:
        print(f"HillClimb: starting with cost {current_cost}")

    if not courses:
        return current, current_cost

    while steps_no_improve < max_no_improve:
        if current_cost == 0:
            if verbose:
                print("HillClimb: found valid schedule")
            return current, 0

        best_neighbor = None
        best_cost = current_cost

        for c in courses:
            cname = _get_name(c).strip()
            if not cname:
                continue
            orig = current.assignments.get(cname, (None, None))

            for r in rooms:
                rname = _get_name(r).strip()
                for s in slots:
                    sid = _get_slot_id(s)
                    candidate = (rname, sid)
                    if candidate == orig:
                        continue

                    neighbor = copy.deepcopy(current)
                    neighbor.assignments[cname] = candidate
                    _ensure_all_courses(neighbor, courses)

                    cost = len(get_hard_constraint_violations(neighbor, all_data))
                    if cost < best_cost:
                        best_cost = cost
                        best_neighbor = neighbor

        if best_neighbor and best_cost < current_cost:
            current = best_neighbor
            current_cost = best_cost
            steps_no_improve = 0
            if verbose:
                print(f"HillClimb: improved -> cost {current_cost}")
        else:
            steps_no_improve += 1

    if verbose:
        print(f"HillClimb: stuck at cost {current_cost}")
    return current, current_cost


# ---------------- Stage 2: SA focused on validity recovery ----------------
def _simulated_annealing_for_validity(
    broken_schedule: Schedule,
    all_data: AllData,
    verbose: bool = True
) -> Tuple[Schedule, int, List[str]]:
    """
    Tries to reduce hard constraint violations to 0 using SA.
    Returns (best_schedule_found, final_cost, explanations_for_stage)
    """
    explanations: List[str] = []

    courses = all_data.get("courses", []) or []
    rooms = all_data.get("rooms", []) or []
    slots = all_data.get("time_slots", []) or []

    current = copy.deepcopy(broken_schedule)
    _ensure_all_courses(current, courses)

    current_cost = len(get_hard_constraint_violations(current, all_data))
    best = copy.deepcopy(current)
    best_cost = current_cost

    if verbose:
        print(f"SA': starting from cost {current_cost}")

    if not courses or not rooms or not slots:
        explanations.append("SA': insufficient data to recover.")
        return current, current_cost, explanations

    temp = 500.0
    cooling = 0.995
    min_temp = 0.5
    it = 0
    max_iter = 20000

    while temp > min_temp and it < max_iter and best_cost > 0:
        it += 1

        c = random.choice(courses)
        cname = _get_name(c).strip()
        neighbor = copy.deepcopy(current)
        new_room = random.choice(rooms)
        new_slot = random.choice(slots)
        neighbor.assignments[cname] = (_get_name(new_room).strip(), _get_slot_id(new_slot))
        _ensure_all_courses(neighbor, courses)

        new_cost = len(get_hard_constraint_violations(neighbor, all_data))
        delta_energy = (-new_cost) - (-current_cost)

        accept = False
        if new_cost < current_cost:
            accept = True
        else:
            try:
                prob = math.exp(delta_energy / temp)
            except OverflowError:
                prob = 0.0
            if random.random() < prob:
                accept = True

        if accept:
            current = neighbor
            current_cost = new_cost
            if current_cost < best_cost:
                best = copy.deepcopy(current)
                best_cost = current_cost

        temp *= cooling

    explanations.append(f"SA': best cost after recovery attempt = {best_cost}")
    if best_cost == 0:
        explanations.append("SA': recovered a fully valid schedule.")
    else:
        explanations.append("SA': could not fully recover to 0 violations.")

    _ensure_all_courses(best, courses)
    return best, best_cost, explanations


# ---------------- Stage 3: SA optimize for happiness ----------------
def _simulated_annealing_for_happiness(
    valid_schedule: Schedule,
    all_data: AllData,
    verbose: bool = True
) -> Tuple[Schedule, int, List[str]]:
    """
    Given a valid schedule (cost==0), try to maximize happiness using SA (MOVE neighbor).
    Returns (best_schedule, best_score, explanations)
    """
    explanations: List[str] = []

    courses = all_data.get("courses", []) or []
    rooms = all_data.get("rooms", []) or []
    slots = all_data.get("time_slots", []) or []

    base = copy.deepcopy(valid_schedule)
    _ensure_all_courses(base, courses)

    current = copy.deepcopy(base)
    current_score = calculate_happiness_score(current, all_data)
    best = copy.deepcopy(current)
    best_score = current_score

    if verbose:
        print(f"SA: starting with desirability {current_score}")

    if len(courses) < 1 or not rooms or not slots:
        explanations.append("SA: insufficient data to optimize.")
        return current, current_score, explanations

    temp = 1000.0
    cooling = 0.995
    min_temp = 0.5
    it = 0
    max_iter = 20000

    while temp > min_temp and it < max_iter:
        it += 1
        c = random.choice(courses)
        cname = _get_name(c).strip()
        neighbor = copy.deepcopy(current)
        new_room = random.choice(rooms)
        new_slot = random.choice(slots)
        neighbor.assignments[cname] = (_get_name(new_room).strip(), _get_slot_id(new_slot))
        _ensure_all_courses(neighbor, courses)

        if get_hard_constraint_violations(neighbor, all_data):
            temp *= cooling
            continue

        neighbor_score = calculate_happiness_score(neighbor, all_data)
        delta = neighbor_score - current_score

        if neighbor_score > best_score:
            best = copy.deepcopy(neighbor)
            best_score = neighbor_score

        if delta > 0:
            current = neighbor
            current_score = neighbor_score
        else:
            try:
                prob = math.exp(delta / temp)
            except OverflowError:
                prob = 0.0
            if random.random() < prob:
                current = neighbor
                current_score = neighbor_score

        temp *= cooling

    explanations.append(f"Stage 3 (SA): best desirability found = {best_score}")
    _ensure_all_courses(best, courses)
    return best, best_score, explanations


# ---------------- Master controller ----------------
def solve_and_optimize_schedule(
    all_data: AllData,
    verbose: bool = False
) -> Tuple[Schedule, List[str], int, List[str]]:
    """
    Returns:
      final_schedule (Schedule),
      final_violations (List[str]),
      happiness_score (int),
      explanations (List[str])
    """
    explanations: List[str] = []

    # Stage 1: hill-climb for validity
    if verbose:
        print("Stage 1 (HC)")
    stage1_schedule, stage1_cost = _hill_climbing_for_validity(all_data, verbose=verbose)
    explanations.append(f"Stage 1 (HC): Finished with cost {stage1_cost}.")
    if stage1_cost == 0:
        hc_happiness = calculate_happiness_score(stage1_schedule, all_data)
        explanations.append(f"Stage 1 (HC): Valid schedule found with desirability = {hc_happiness}.")


    used_stage2 = False

    # If stage1 didn't find valid schedule, try Stage 2: SA for validity recovery
    if stage1_cost > 0:
        if verbose:
            print("Stage 2 (SA') starting")
        used_stage2 = True
        recovered_schedule, recovered_cost, stage2_expl = _simulated_annealing_for_validity(
            stage1_schedule, all_data, verbose=verbose
        )
        explanations.extend(stage2_expl)
        explanations.append(f"Stage 2 (SA'): cost {recovered_cost}.")
        schedule_after_stage2 = recovered_schedule
        final_cost = recovered_cost
    else:
        schedule_after_stage2 = stage1_schedule
        final_cost = stage1_cost

    if final_cost > 0:
        # unable to find fully valid schedule — return best attempt so far
        final_violations = get_hard_constraint_violations(schedule_after_stage2, all_data)
        explanations.append("Unable to produce fully valid schedule after Stage 2. Returning best-effort result.")
        # compute happiness for reporting
        happiness = calculate_happiness_score(schedule_after_stage2, all_data)
        return schedule_after_stage2, final_violations, int(happiness), explanations

    # Stage 3: we have a valid schedule — optimize happiness
    if verbose:
        print("Stage 3 (SA) starting")
    opt_schedule, opt_score, stage3_expl = _simulated_annealing_for_happiness(
        schedule_after_stage2, all_data, verbose=verbose
    )
    explanations.extend(stage3_expl)

    # final validation and violations
    final_violations = get_hard_constraint_violations(opt_schedule, all_data)
    final_happiness = int(opt_score)

    explanations.append("Completed optimization with SA.")
    if used_stage2:
        explanations.insert(1, "Note: Stage 2 (recovery) was used because Stage 1 failed to find a valid solution.")

    return opt_schedule, final_violations, final_happiness, explanations