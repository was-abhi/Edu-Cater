# Edu-Cater ML Model Server — Backend Integration Guide

This document contains everything the **Backend Developer** needs to integrate the FastAPI backend with the **ML Recommendation Microservice** and the **Supabase PostgreSQL Database**.

---

## 1. Architecture & Flow

```
[ Frontend ]
     │ (1) User inputs: keam_rank, category, courses, types
     ▼
[ FastAPI Backend ] (Port 8000)
     │ (2) POST /api/v1/recommend  (to ML Server)
     ▼
[ ML Model Server ] (Port 8001)
     │ (3) Evaluates allotments, cutoffs & category quotas
     │ (4) Returns Top 5 recommendations + college_ids: [130, 78, 42, 32, 91]
     ▼
[ FastAPI Backend ]
     │ (5) SELECT * FROM public.colleges WHERE id IN (130, 78, 42, 32, 91)
     ▼
[ Supabase PostgreSQL ]
     │ (6) Returns full college metadata (pass %, district, type, accreditation, etc.)
     ▼
[ Frontend ] ── Displays enriched 5 college recommendations to student!
```

---

## 2. Running the ML Server

### On Linux / macOS:
```bash
# Using the preconfigured virtual environment:
./model/.venv/bin/python -m uvicorn model.server:app --host 0.0.0.0 --port 8001 --reload

# Or via the shell script:
chmod +x model/run_server.sh
./model/run_server.sh
```

### On Windows:
From Command Prompt:
```cmd
model\run_server.bat
```
Or in PowerShell:
```powershell
.\model\run_server.ps1
```
Or standard Python:
```cmd
python -m pip install -r model\requirements.txt
python -m uvicorn model.server:app --host 0.0.0.0 --port 8001 --reload
```

* **Base URL:** `http://127.0.0.1:8001`
* **Swagger Docs:** `http://127.0.0.1:8001/docs`
* **Health Check:** `http://127.0.0.1:8001/health`

### Data-source boundary

The ML server loads its college catalogue and cutoff statistics from Supabase
at startup. It queries `public.colleges` and `public.college_cutoffs` using the
database credentials in `model/.env`.

The recommendation response includes `college_ids`. The main backend can use
those IDs to fetch the full college records from Supabase's
`public.colleges` table. The existing Supabase connection/query helpers are in
`Dama Mining/db.py`.

The live ranking separates admission feasibility from college quality:
historical closing rank determines eligibility and the Safe/Match/Dream
classification, while pass percentage, cutoff selectivity, requested course
order, requested college-type order, and accreditation determine the ranking
among eligible colleges. The API's `admission_probability` is an estimate from
the historical rank position, not a guaranteed admission probability.

---

## 3. ML Server API Reference

### `POST /api/v1/recommend`

#### Request Pydantic Model (FastAPI Backend -> ML Server)
```python
from typing import Literal
from pydantic import BaseModel, Field

class RecommendationRequest(BaseModel):
    keam_rank: int = Field(gt=0, description="Student KEAM rank")
    category: Literal[
        "general",
        "obc",
        "bx",
        "sc",
        "st",
    ] = Field(description="Reservation category: general, obc, bx, sc, st")
    courses: list[str] = Field(min_length=1, description="Courses in preferred order (e.g. ['CS', 'CY'])")
    types: list[str] = Field(min_length=1, description="Types in preferred order: 'government', 'autonomous', 'private'")
```

#### Example Request Body
```json
{
  "keam_rank": 4500,
  "category": "bx",
  "courses": ["CS", "CY"],
  "types": ["government", "autonomous"]
}
```

* **`keam_rank`**: Student's KEAM rank (integer > 0).
* **`category`**: `"general"`, `"obc"`, `"bx"`, `"sc"`, `"st"`.
* **`courses`**: Ordered list of preferred engineering branches:
  * Supported: `"CS"` (or `"CSE"`), `"CY"` (Cyber Security), `"AD"` (AI & DS), `"AH"` / `"AI"` (AI & ML), `"EC"`, `"ME"` (Mechanical), `"EE"` (Electrical), `"CE"` (Civil).
* **`types`**: Ordered list of preferred college types:
  * Supported: `"government"`, `"autonomous"`, `"private"`.

#### Example Response Body (ML Server -> Backend)
```json
{
  "status": "success",
  "student_rank": 4500,
  "category": "bx",
  "courses": ["CS", "CY"],
  "types": ["government", "autonomous"],
  "total_recommendations": 5,
  "college_ids": [130, 78, 42, 32, 91],
  "recommendations": [
    {
      "college_id": 130,
      "college_code": "MGC",
      "college_name": "M G College of Engineering,",
      "college_type": "autonomous",
      "course_code": "CS",
      "course_name": "Computer Science & Engineering (CSE)",
      "applied_category": "BX",
      "reservation_quota_used": false,
      "admission_probability": 0.98,
      "recommendation_category": "Safe",
      "category_opening_rank": 17393,
      "category_closing_rank": 62870,
      "pass_percentage": 81.35,
      "district": "Thiruvananthapuram",
      "nba_accredited": true,
      "naac_accredited": true
    },
    {
      "college_id": 78,
      "college_code": "MDL",
      "college_name": "Model Engineering College, Ernakulam",
      "college_type": "autonomous",
      "course_code": "CS",
      "course_name": "Computer Science & Engineering (CSE)",
      "applied_category": "BX",
      "reservation_quota_used": true,
      "admission_probability": 0.86,
      "recommendation_category": "Match",
      "category_opening_rank": 648,
      "category_closing_rank": 6855,
      "pass_percentage": 83.05,
      "district": "Ernakulam",
      "nba_accredited": true,
      "naac_accredited": false
    },
    {
      "college_id": 42,
      "college_code": "TCR",
      "college_name": "Government Engineering College, Thrissur",
      "college_type": "government",
      "course_code": "CS",
      "course_name": "Computer Science & Engineering (CSE)",
      "applied_category": "BX",
      "reservation_quota_used": true,
      "admission_probability": 0.87,
      "recommendation_category": "Match",
      "category_opening_rank": 2756,
      "category_closing_rank": 9522,
      "pass_percentage": 72.78,
      "district": "Thrissur",
      "nba_accredited": true,
      "naac_accredited": false
    },
    {
      "college_id": 32,
      "college_code": "KNR",
      "college_name": "Government College of Engineering, Kannur",
      "college_type": "government",
      "course_code": "CS",
      "course_name": "Computer Science & Engineering (CSE)",
      "applied_category": "BX",
      "reservation_quota_used": false,
      "admission_probability": 0.86,
      "recommendation_category": "Match",
      "category_opening_rank": 685,
      "category_closing_rank": 62430,
      "pass_percentage": 68.69,
      "district": "Kannur",
      "nba_accredited": true,
      "naac_accredited": false
    },
    {
      "college_id": 91,
      "college_code": "AEC",
      "college_name": "College of Engineering of Aranmula,",
      "college_type": "autonomous",
      "course_code": "CS",
      "course_name": "Computer Science & Engineering (CSE)",
      "applied_category": "BX",
      "reservation_quota_used": false,
      "admission_probability": 0.98,
      "recommendation_category": "Safe",
      "category_opening_rank": 16588,
      "category_closing_rank": 66803,
      "pass_percentage": 83.42,
      "district": "Pathanamthitta",
      "nba_accredited": true,
      "naac_accredited": false
    }
  ]
}
```

---

## 4. Supabase Database Schema

### Database Credentials
* **Host:** `aws-0-ap-southeast-1.pooler.supabase.com`
* **Port:** `6543`
* **Database:** `postgres`
* **User:** `postgres.snlvfzvvcawwdrsufxzx`
* **Password:** `Edu-Cator123`
* **Connection String:**
  ```text
  postgresql://postgres.snlvfzvvcawwdrsufxzx:Edu-Cator123@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
  ```

### Table 1: `public.colleges` (133 colleges)
| Column | Type | Description |
| :--- | :--- | :--- |
| **`id`** | `SERIAL PRIMARY KEY` | Primary key (`college_id`) |
| **`college_code`** | `VARCHAR(10) UNIQUE` | 3-letter code (`TCR`, `TVE`, `MDL`, etc.) |
| **`college_name`** | `TEXT` | Official institution name |
| **`college_type`** | `VARCHAR(50)` | `"government"`, `"autonomous"`, `"private"` |
| **`district`** | `VARCHAR(100)` | District strictly from KEAM cutoff list |
| **`pass_percentage`** | `NUMERIC(5,2)` | KTU University academic pass percentage |
| **`cutoff_sm`** | `INTEGER` | State Merit closing cutoff rank |
| **`nba_accredited`** | `BOOLEAN` | NBA accreditation status |
| **`naac_accredited`**| `BOOLEAN` | NAAC accreditation status |

### Table 2: `public.college_cutoffs` (4,654 cutoff records)
| Column | Type | Description |
| :--- | :--- | :--- |
| **`id`** | `SERIAL PRIMARY KEY` | Cutoff entry ID |
| **`college_id`** | `INTEGER REFERENCES colleges(id)` | Foreign key to `public.colleges(id)` |
| **`college_code`** | `VARCHAR(10)` | KEAM college code |
| **`course_code`** | `VARCHAR(10)` | Branch code (`CS`, `ME`, `EC`, `CE`, etc.) |
| **`category`** | `VARCHAR(10)` | Reservation category (`GN`, `BH`, `BX`, `SC`, `ST`, etc.) |
| **`opening_rank`** | `INTEGER` | Opening rank for that branch & category |
| **`closing_rank`** | `INTEGER` | Closing cutoff rank for that branch & category |
| **`allotted_count`** | `INTEGER` | Total students allotted in this quota |

---

## 5. SQL Queries for the Backend Developer

### Query 1: Fetch All Colleges Where a Student with Rank $N$ Can Get Course $Y$ for Category $Z$
*(i.e. Closing Cutoff Rank $\ge N$, meaning student rank falls within the admitted range)*

```sql
SELECT 
    c.id AS college_id,
    c.college_code,
    c.college_name,
    c.college_type,
    c.district,
    c.pass_percentage,
    c.nba_accredited,
    c.naac_accredited,
    cut.course_code,
    cut.category,
    cut.opening_rank,
    cut.closing_rank
FROM public.college_cutoffs cut
JOIN public.colleges c ON c.id = cut.college_id
WHERE cut.course_code = 'CS'        -- Preferred course (e.g., CS, ME, EC, AD, CY)
  AND cut.category = 'GN'           -- Category: GN (General), BH (OBC), BX, SC, ST
  AND cut.closing_rank >= 10000     -- Student's rank N
ORDER BY cut.closing_rank ASC;
```

### Query 2: Fetch Colleges by Cutoff Rank Ceiling
If you want colleges whose cutoff is strict (rank $\le N$):
```sql
SELECT 
    c.id,
    c.college_code,
    c.college_name,
    c.college_type,
    c.district,
    cut.course_code,
    cut.category,
    cut.closing_rank
FROM public.college_cutoffs cut
JOIN public.colleges c ON c.id = cut.college_id
WHERE cut.course_code = 'CS'
  AND cut.category = 'GN'
  AND cut.closing_rank <= 5000
ORDER BY cut.closing_rank ASC;
```

### Query 3: Fetch Full College Details for the 5 Recommended IDs
```sql
SELECT 
    id,
    college_code,
    college_name,
    college_type,
    district,
    pass_percentage,
    cutoff_sm,
    nba_accredited,
    naac_accredited
FROM public.colleges
WHERE id IN (130, 78, 42, 32, 91);
```

---

## 6. Complete Backend Python Snippet (FastAPI Endpoint)

The backend developer can drop this async function directly into `backend/`:

```python
from typing import Literal, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import httpx
import psycopg2
from psycopg2.extras import RealDictCursor

router = APIRouter(prefix="/api/v1", tags=["recommendations"])

ML_SERVER_URL = "http://127.0.0.1:8001/api/v1/recommend"

DB_CONFIG = {
    "host": "aws-0-ap-southeast-1.pooler.supabase.com",
    "port": 6543,
    "dbname": "postgres",
    "user": "postgres.snlvfzvvcawwdrsufxzx",
    "password": "Edu-Cator123",
    "connect_timeout": 10
}

class RecommendationRequest(BaseModel):
    keam_rank: int = Field(gt=0, description="Student KEAM rank")
    category: Literal["general", "obc", "bx", "sc", "st"]
    courses: List[str] = Field(min_length=1, description="Courses in preferred order")
    types: List[str] = Field(min_length=1, description="Types: 'government', 'autonomous', 'private'")

@router.post("/recommend-colleges")
async def recommend_colleges(payload: RecommendationRequest):
    # 1. Forward to ML Server
    async with httpx.AsyncClient() as client:
        try:
            ml_response = await client.post(
                ML_SERVER_URL,
                json=payload.model_dump(),
                timeout=10.0
            )
            ml_response.raise_for_status()
            ml_data = ml_response.json()
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"ML server unreachable: {str(e)}")

    college_ids = ml_data["college_ids"]
    ml_lookup = {item["college_id"]: item for item in ml_data["recommendations"]}

    # 2. Query Supabase public.colleges
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM public.colleges WHERE id = ANY(%s);", (college_ids,))
    colleges = cur.fetchall()
    conn.close()

    # 3. Merge Supabase attributes with ML predictions
    merged_results = []
    for c in colleges:
        cid = c["id"]
        ml_meta = ml_lookup.get(cid, {})
        merged_results.append({
            **c,
            "recommended_course": ml_meta.get("course_name"),
            "course_code": ml_meta.get("course_code"),
            "admission_probability": ml_meta.get("admission_probability"),
            "recommendation_category": ml_meta.get("recommendation_category"),
            "applied_category": ml_meta.get("applied_category"),
            "reservation_quota_used": ml_meta.get("reservation_quota_used"),
            "category_opening_rank": ml_meta.get("category_opening_rank"),
            "category_closing_rank": ml_meta.get("category_closing_rank")
        })

    # Preserve ML recommendation priority order
    merged_results.sort(key=lambda x: college_ids.index(x["id"]) if x["id"] in college_ids else 999)

    return {
        "status": "success",
        "student_rank": payload.keam_rank,
        "recommendations": merged_results
    }
```
