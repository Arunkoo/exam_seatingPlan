"""
seating.py — Anti-Cheat Seating Arrangement
--------------------------------------------
Groups students by branch + year (e.g. CSE 1st, ECE 2nd, MECH 3rd).
Students from the same branch+year are classmates — they must NOT sit adjacent.

STRATEGY = "same_exam"
    All students write the same exam paper (e.g. Engineering Maths).
    Uses CHECKERBOARD — every seat surrounded by empty seats on all 4 sides.
    Best for preventing copying entirely.

STRATEGY = "multi_group"
    Multiple branch+year groups in one hall.
    No two students from the same branch+year sit adjacent (L/R/T/B).
"""

from typing import List, Dict, Optional
import random

# ─────────────────────────────────────────
#   CHANGE THIS LINE TO SWITCH MODE
STRATEGY = "multi_group"   # or "same_exam"
# ─────────────────────────────────────────


def get_group(student: Dict) -> str:
    """Return the group key: branch + year, e.g. 'CSE-1', 'ECE-2'"""
    branch = student.get("branch", "").strip().upper()
    year   = student.get("year",   "").strip()
    return f"{branch}-{year}"


def generate_seating(students: List[Dict], rows: int, cols: int) -> List[List[Optional[Dict]]]:
    if STRATEGY == "same_exam":
        return _checkerboard(students, rows, cols)
    else:
        return _multi_group(students, rows, cols)


# ── STRATEGY 1: Checkerboard (same exam) ─────────────────────────────────────

def _checkerboard(students: List[Dict], rows: int, cols: int) -> List[List[Optional[Dict]]]:
    """
    Place students only on (r+c) % 2 == 0 seats.
    Every direct neighbour (L/R/T/B) is guaranteed empty.
    Students sorted by roll number for predictable assignment.
    """
    pool = sorted(students, key=lambda s: _roll_key(s))

    positions = [(r, c) for r in range(rows) for c in range(cols) if (r + c) % 2 == 0]

    grid = [[None for _ in range(cols)] for _ in range(rows)]
    for i, (r, c) in enumerate(positions):
        if i < len(pool):
            grid[r][c] = pool[i]

    return grid


# ── STRATEGY 2: Multi group (different branch+year) ──────────────────────────

def _multi_group(students: List[Dict], rows: int, cols: int) -> List[List[Optional[Dict]]]:
    """
    50 shuffles, keep arrangement with fewest same-group neighbours.
    """
    total_seats = rows * cols
    pool = students.copy()

    while len(pool) < total_seats:
        pool.append(None)
    pool = pool[:total_seats]

    best_grid      = None
    best_conflicts = float("inf")

    for _ in range(50):
        random.shuffle(pool)
        grid      = _fill_greedy(pool, rows, cols)
        conflicts = check_conflicts(grid)
        if conflicts < best_conflicts:
            best_conflicts = conflicts
            best_grid      = grid
        if best_conflicts == 0:
            break

    return best_grid


def _fill_greedy(pool: list, rows: int, cols: int) -> List[List[Optional[Dict]]]:
    remaining = pool.copy()
    grid      = [[None for _ in range(cols)] for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            placed = False
            for i in range(len(remaining)):
                candidate = remaining[i]
                if candidate is None:
                    grid[r][c] = remaining.pop(i)
                    placed = True
                    break
                conflict = False
                if c > 0 and grid[r][c-1] and get_group(grid[r][c-1]) == get_group(candidate):
                    conflict = True
                if not conflict and r > 0 and grid[r-1][c] and get_group(grid[r-1][c]) == get_group(candidate):
                    conflict = True
                if not conflict:
                    grid[r][c] = remaining.pop(i)
                    placed = True
                    break
            if not placed and remaining:
                grid[r][c] = remaining.pop(0)

    return grid


# ── Helpers ───────────────────────────────────────────────────────────────────

def _roll_key(s):
    try:
        return int(s["roll"])
    except:
        return s["roll"]


def grid_to_flat(grid: List[List[Optional[Dict]]]) -> List[Dict]:
    flat    = []
    seat_no = 1
    for r, row in enumerate(grid):
        for c, student in enumerate(row):
            flat.append({
                "seat_no": seat_no,
                "row":     r + 1,
                "col":     c + 1,
                "name":    student["name"]   if student else "-",
                "roll":    student["roll"]   if student else "-",
                "branch":  student.get("branch", "-") if student else "-",
                "year":    student.get("year",   "-") if student else "-",
                "group":   get_group(student) if student else "-",
            })
            seat_no += 1
    return flat


def check_conflicts(grid: List[List[Optional[Dict]]]) -> int:
    """Count adjacent pairs from the same branch+year group."""
    if STRATEGY == "same_exam":
        return 0  # checkerboard guarantees no direct neighbours

    conflicts = 0
    rows = len(grid)
    cols = len(grid[0]) if grid else 0

    for r in range(rows):
        for c in range(cols):
            cell = grid[r][c]
            if cell is None:
                continue
            for dr, dc in [(0, 1), (1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc]:
                    if get_group(cell) == get_group(grid[nr][nc]):
                        conflicts += 1
    return conflicts


def max_students_checkerboard(rows: int, cols: int) -> int:
    return sum(1 for r in range(rows) for c in range(cols) if (r + c) % 2 == 0)


# ── TEST ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    students = [
        {"name": "Amit Sharma",   "roll": "101", "branch": "CSE", "year": "1"},
        {"name": "Priya Singh",   "roll": "102", "branch": "CSE", "year": "1"},
        {"name": "Rahul Verma",   "roll": "103", "branch": "CSE", "year": "1"},
        {"name": "Neha Gupta",    "roll": "201", "branch": "ECE", "year": "2"},
        {"name": "Vikas Kumar",   "roll": "202", "branch": "ECE", "year": "2"},
        {"name": "Anita Rao",     "roll": "203", "branch": "ECE", "year": "2"},
        {"name": "Sunita Devi",   "roll": "301", "branch": "MECH","year": "3"},
        {"name": "Mohan Lal",     "roll": "302", "branch": "MECH","year": "3"},
        {"name": "Kavita Joshi",  "roll": "401", "branch": "CSE", "year": "2"},
        {"name": "Deepak Nair",   "roll": "402", "branch": "CSE", "year": "2"},
        {"name": "Ritu Patel",    "roll": "501", "branch": "IT",  "year": "1"},
        {"name": "Sanjay Tiwari", "roll": "502", "branch": "IT",  "year": "1"},
    ]

    rows, cols = 3, 4
    grid       = generate_seating(students, rows, cols)
    conflicts  = check_conflicts(grid)

    print(f"Strategy: {STRATEGY}")
    print(f"Room: {rows}x{cols}\n")
    print("Grid (Branch-Year | Roll):")
    for row in grid:
        print([f"{get_group(c)}|{c['roll']}" if c else "--------" for c in row])
    print(f"\nSame-group conflicts: {conflicts}")
    print("PASS!" if conflicts == 0 else "WARN — some conflicts remain")