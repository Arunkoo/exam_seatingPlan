# Exam Seating Arrangement System — Anti Cheat

A web-based exam seating arrangement system built with **Python + FastAPI**. Automatically arranges students in a hall so that classmates (same branch & year) never sit adjacent to each other — preventing copying during exams.

---

## Features

- Upload student list as CSV (name, roll, branch, year)
- Auto-generates anti-cheat seating arrangement
- Two modes:
  - **Multi Group** — separates students by branch + year (no same-group neighbours)
  - **Same Exam** — checkerboard pattern (empty seat on all 4 sides)
- Color-coded seating grid by branch + year
- Download seating plan as PDF
- Print-ready layout for notice board

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, FastAPI |
| Frontend | HTML, CSS (Jinja2 templates) |
| Algorithm | Constraint-based greedy shuffle (AI/ML concept) |
| PDF Export | fpdf2 |
| Server | Uvicorn |

---

## Project Structure

```
exam_seatingPlan/
├── main.py              # FastAPI routes
├── seating.py           # Anti-cheat arrangement algorithm
├── pdf_gen.py           # PDF generation
├── templates/
│   ├── index.html       # Upload form page
│   └── result.html      # Seating grid display
├── static/
│   └── style.css        # Styling
└── requirement.txt     # Python dependencies
```

---

## How to Run

### 1. Install dependencies
```bash
pip install -r requirement.txt
```

### 2. Start the server
```bash
python -m uvicorn main:app --reload
```

### 3. Open browser
```
http://localhost:8000
```

---

## CSV Format

Upload a `.csv` file with these columns:

```
name,roll,branch,year
Amit Sharma,101,CSE,1
Priya Singh,201,ECE,2
Rahul Verma,301,MECH,3
```

---

## Algorithm (for Viva)

The seating engine uses a **constraint-based greedy algorithm** — a classic AI technique:

1. Students are shuffled randomly (randomization layer)
2. Each student is placed one by one into the grid
3. Before placing, left and top neighbours are checked
4. If a conflict exists (same branch+year), the next candidate is tried
5. The whole process runs **50 times**, and the arrangement with **zero conflicts** is selected
6. In checkerboard mode, students are placed only on alternate seats — guaranteeing no direct neighbours

This is equivalent to a **Constraint Satisfaction Problem (CSP)** in Artificial Intelligence.

---

## Modes

Change the `STRATEGY` variable in `seating.py` to switch modes:

```python
STRATEGY = "multi_group"   # separate by branch+year
STRATEGY = "same_exam"     # checkerboard pattern
```

---

## Screenshots

> Upload CSV → Generate → View grid → Download PDF

---

## Developer

Made by **Arun** — College Project  
Branch: CSE | Subject: AI/ML Web Application
