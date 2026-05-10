import io
import csv
from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from seating import generate_seating, grid_to_flat, check_conflicts, max_students_checkerboard, STRATEGY, get_group
from _pdfGen import generate_pdf

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Exam Seating System")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

current_session = {}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"error": None, "strategy": STRATEGY})


@app.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    exam_name: str = Form(...),
    rows: int = Form(...),
    cols: int = Form(...),
    file: UploadFile = File(...),
):
    try:
        content = await file.read()
        decoded = content.decode("utf-8-sig")
        reader  = csv.DictReader(io.StringIO(decoded))

        students = []
        errors   = []

        for i, row in enumerate(reader, start=2):
            name   = row.get("name",   "").strip()
            roll   = row.get("roll",   "").strip()
            branch = row.get("branch", "").strip()
            year   = row.get("year",   "").strip()

            if not name or not roll or not branch or not year:
                errors.append(f"Row {i}: missing name/roll/branch/year")
                continue

            students.append({"name": name, "roll": roll, "branch": branch, "year": year})

        if not students:
            return templates.TemplateResponse(request, "index.html", {
                "error": "No valid students found. CSV must have columns: name, roll, branch, year",
                "strategy": STRATEGY,
            })

        capacity         = max_students_checkerboard(rows, cols)
        capacity_warning = None
        if STRATEGY == "same_exam" and len(students) > capacity:
            capacity_warning = (
                f"Checkerboard fits only {capacity} students in a {rows}x{cols} room. "
                f"You have {len(students)} — increase room size."
            )

        grid      = generate_seating(students, rows, cols)
        flat      = grid_to_flat(grid)
        conflicts = check_conflicts(grid)

        # Unique groups for legend
        groups = sorted(set(get_group(s) for s in students))

        current_session.update({
            "grid": grid, "exam_name": exam_name,
            "rows": rows, "cols": cols,
        })

        return templates.TemplateResponse(request, "result.html", {
            "grid": grid, "flat": flat,
            "exam_name": exam_name,
            "rows": rows, "cols": cols,
            "total_students": len(students),
            "conflicts": conflicts,
            "groups": groups,
            "errors": errors,
            "strategy": STRATEGY,
            "capacity_warning": capacity_warning,
        })

    except Exception as e:
        return templates.TemplateResponse(request, "index.html", {
            "error": f"Error: {str(e)}",
            "strategy": STRATEGY,
        })


@app.get("/download-pdf")
async def download_pdf():
    if not current_session.get("grid"):
        return JSONResponse({"error": "No seating plan yet."}, status_code=400)
    pdf_bytes = generate_pdf(
        current_session["grid"], current_session["exam_name"],
        current_session["rows"], current_session["cols"],
    )
    filename = current_session["exam_name"].replace(" ", "_")
    return StreamingResponse(
        io.BytesIO(pdf_bytes), media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="seating_{filename}.pdf"'},
    )


@app.get("/sample-csv")
async def sample_csv():
    sample = (
        "name,roll,branch,year\n"
        "Amit Sharma,101,CSE,1\nPriya Singh,102,CSE,1\nRahul Verma,103,CSE,1\n"
        "Neha Gupta,201,ECE,2\nVikas Kumar,202,ECE,2\nAnita Rao,203,ECE,2\n"
        "Sunita Devi,301,MECH,3\nMohan Lal,302,MECH,3\nKavita Joshi,303,MECH,3\n"
        "Deepak Nair,401,CSE,2\nRitu Patel,402,CSE,2\nSanjay Tiwari,403,CSE,2\n"
        "Meena Sharma,501,IT,1\nArjun Singh,502,IT,1\nPooja Yadav,503,IT,1\n"
        "Rohit Mehta,601,ECE,3\nSneha Kapoor,602,ECE,3\nKiran Desai,603,ECE,3\n"
    )
    return StreamingResponse(
        io.BytesIO(sample.encode()), media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="sample_students.csv"'},
    )