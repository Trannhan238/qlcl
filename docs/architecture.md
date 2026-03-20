# Architecture

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        UI Layer                              │
│                   (Streamlit - main.py)                     │
│   - File upload                                            │
│   - Data display                                           │
│   - Charts                                                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Domain Layer                             │
│                 (app/core/*.py)                             │
│   - compare.py: comparison logic                           │
│   - Baseline mapping handled at compare layer               │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                     Parser Layer                            │
│           (app/infra/vnedu_parser.py)                      │
│   - Excel file reading                                     │
│   - Header detection                                       │
│   - Subject structure detection (scored vs qualitative)     │
│   - Column grouping (1 column vs 2 columns per subject)     │
│   - KQGD extraction (only baseline, actual_hk2)            │
│   - Checkbox counting                                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Storage Layer                             │
│               (SQLite - sqms.db)                           │
│   - subject_snapshots                                     │
│   - class_summary                                         │
│   - teacher_commitments                                   │
│   - student_achievements                                  │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Responsibility | Files |
|-------|----------------|-------|
| **UI** | User interaction, data display, file upload trigger | `main.py` |
| **Domain** | Comparison logic, baseline mapping | `compare.py` |
| **Parser** | Excel parsing, subject structure detection, KQGD extraction | `vnedu_parser.py` |
| **Storage** | Data persistence | SQLite tables |

---

## 2. Data Model

### Subject-Level Data

**Table: `subject_snapshots`**

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `academic_year` | TEXT | e.g., "2024-2025" (NOT modified by parser) |
| `class_name` | TEXT | e.g., "1A" (NOT modified by parser) |
| `subject` | TEXT | e.g., "Toán", "Tiếng Việt" |
| `snapshot_type` | TEXT | "actual_hk1", "actual_hk2", "baseline", "target" |
| `avg_score` | REAL | Average score (0-10), NULL for qualitative subjects |
| `student_count` | INTEGER | Total students in class |
| `T` | INTEGER | Count of "Hoàn thành xuất sắc" students |
| `H` | INTEGER | Count of "Hoàn thành" students |
| `C` | INTEGER | Count of "Chưa hoàn thành" students |

**Unique constraint**: `(academic_year, class_name, subject, snapshot_type)`

**Valid snapshot_type values**: `actual_hk1`, `actual_hk2`, `baseline`, `target`

---

### Class-Level Data (KQGD)

**Table: `class_summary`**

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `academic_year` | TEXT | e.g., "2024-2025" |
| `class_name` | TEXT | e.g., "1A" |
| `snapshot_type` | TEXT | **ONLY**: "baseline", "actual_hk2" |
| `HTXS` | INTEGER | Count of "Hoàn thành xuất sắc" |
| `HTT` | INTEGER | Count of "Hoàn thành tốt" |
| `HT` | INTEGER | Count of "Hoàn thành" |
| `CHT` | INTEGER | Count of "Chưa hoàn thành" |
| `HTCTLH_HT` | INTEGER | Count of "Hoàn thành chất lượng học tập" |
| `HTCTLH_CHT` | INTEGER | Count of "Chưa hoàn thành chất lượng học tập" |
| `HSXS` | INTEGER | Count of "Học sinh xuất sắc" |
| `HS_TieuBieu` | INTEGER | Count of "Học sinh tiêu biểu" |

**Unique constraint**: `(academic_year, class_name, snapshot_type)`

**KQGD constraint**: `HTXS + HTT + HT + CHT == total_students_from_KQGD_block`
- Mismatch MUST raise ValueError

---

### School-Level Data

**Table: `teacher_commitments`**

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `academic_year` | TEXT | e.g., "2024-2025" |
| `class_name` | TEXT | e.g., "1A" |
| `subject` | TEXT | e.g., "Toán" |
| `avg_score_target` | REAL | Target average score |
| `T_pct_target` | REAL | Target T percentage |
| `H_pct_target` | REAL | Target H percentage |
| `C_pct_target` | REAL | Target C percentage |
| `HTXS_target` | INTEGER | Target HTXS count |
| `HTT_target` | INTEGER | Target HTT count |
| `HT_target` | INTEGER | Target HT count |
| `CHT_target` | INTEGER | Target CHT count |

**Unique constraint**: `(academic_year, class_name, subject)`

---

**Table: `student_achievements`**

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `academic_year` | TEXT | e.g., "2024-2025" |
| `category` | TEXT | e.g., "Văn Toán Tuổi thơ", "IOE" |
| `level` | TEXT | "Xã", "Quận/Huyện", "Tỉnh", "Quốc gia" |
| `quantity` | INTEGER | Number of students |

**Unique constraint**: `(academic_year, category, level)`

---

## 3. Subject Structure Rules (CRITICAL)

### Two Subject Types

**A. Scored Subjects (môn có điểm)**
- Structure: TWO adjacent columns
  - Column N:   T/H/C bucket counts
  - Column N+1: Numeric score
- REQUIRED fields:
  - `avg_score` MUST NOT be NULL
  - T, H, C MUST exist
- Example: Toán, Tiếng Việt, Tiếng Anh, Khoa học

**B. Qualitative Subjects (môn nhận xét)**
- Structure: ONE column only
  - Column N: T/H/C bucket counts
- REQUIRED fields:
  - `avg_score` MUST be NULL
  - T, H, C MUST exist
  - T + H + C <= student_count
- Example: Đạo đức, Nghệ thuật, GDTC

### Column Grouping Detection (Core Invariant)

The parser MUST detect subject type by STRUCTURE:
- Two adjacent columns with same subject header → scored subject
- Single column with subject header → qualitative subject

**Parser MUST NOT rely solely on column names to determine type.**
**Parser MUST validate column grouping consistency.**

---

## 4. Data Flow

### Pipeline: Excel → Database → UI

```
1. User uploads Excel file
          ↓
2. Parser reads file (pd.read_excel)
          ↓
3. Detect class name, academic year
          ↓
4. Detect subject structure (scored vs qualitative)
          ↓
5. Group columns by subject (1 column vs 2 columns)
          ↓
6. Parse subject data (T/H/C counts, avg_score)
          ↓
7. IF snapshot_type IN {"baseline", "actual_hk2"}:
      Parse KQGD section (HTXS/HTT/HT/CHT)
      Validate: sum == total_students
   ELSE:
      Skip KQGD parsing
          ↓
8. Validate data consistency
   - avg_score NOT NULL for scored subjects
   - avg_score IS NULL for qualitative subjects
   - T, H, C >= 0
   - T + H + C <= student_count (qualitative only)
          ↓
9. Insert to database (upsert)
          ↓
10. Query from database
          ↓
11. Compare with targets/baselines (compare layer)
          ↓
12. Display in UI (table, charts)
```

### Baseline Mapping

**Baseline mapping is handled in the compare layer, NOT in the parser.**
- Parser preserves original `academic_year` and `class_name`
- Compare layer performs baseline-to-current mapping for display/comparison
- No shifting at parser level

---

## 5. Data Integrity Rules

### Subject Type Constraints

| Subject Type | avg_score | T, H, C | T+H+C |
|--------------|-----------|---------|-------|
| Scored | MUST NOT be NULL | MUST exist | <= student_count |
| Qualitative | MUST be NULL | MUST exist | <= student_count |

### KQGD Presence Rules

| snapshot_type | Parse KQGD? | class_summary populated? |
|--------------|-------------|---------------------------|
| baseline | YES | YES |
| actual_hk2 | YES | YES |
| actual_hk1 | NO | NO |
| target | NO | NO |
| commitment | NO | NO |

### student_count Consistency

- subject_snapshots.student_count: Total students from subject data rows
- class_summary: HTXS+HTT+HT+CHT == student_count_from_KQGD
- Cross-validation: class_summary student_count should align with subject_snapshots

---

## 6. Snapshot Rules

### Snapshot Types

| snapshot_type | Description | KQGD? | subject_snapshots? |
|--------------|-------------|-------|-------------------|
| baseline | HK2 of previous academic year | YES | YES |
| actual_hk1 | Current academic year, HK1 | NO | YES |
| actual_hk2 | Current academic year, HK2 | YES | YES |
| target | Phấn đấu (derived from baseline) | NO | YES |
| commitment | Cam kết GV (manual input) | NO | NO |

### class_summary Constraint

class_summary is populated ONLY for:
- baseline
- actual_hk2

---

## 7. Parser Rules

### Identity Preservation
- Parser MUST NOT modify `academic_year`
- Parser MUST NOT modify `class_name`

### Required Validations
- Header row detection
- Subject grouping (1 column vs 2 columns per subject)
- Data consistency within grouped columns
- Non-negative numeric fields

### Failure Semantics
- Parser MUST NOT silently fail
- Parser MUST raise structured errors with descriptive messages
- Errors must include: class_name, academic_year, subject (if applicable)

---

## 8. Forbidden Patterns

- Treating scored subjects as score-only (ignoring T/H/C)
- Ignoring T/H/C in scored subjects
- Mixing subject types within same logical group
- Setting avg_score for qualitative subjects
- Setting NULL avg_score for scored subjects
- Silent exception handling
- Shifting academic_year or class_name in parser layer
- Skipping KQGD validation
- Allowing T + H + C > student_count for qualitative subjects
- Parsing KQGD for snapshot_type NOT IN {"baseline", "actual_hk2"}

---

## 9. Current Implementation State

### Actually Implemented
- `app/main.py`: UI, data upload, process_files, upsert logic, some transformation
- `app/infra/vnedu_parser.py`: Excel parsing, header detection, checkbox counting, KQGD extraction
- `app/core/compare.py`: Comparison logic

### NOT Implemented (TODO)
- Formal data access layer (repositories/DAO)
- Domain model (pydantic/dataclass)
- Unit tests for parser
- Column grouping validation (scored vs qualitative detection)

### Known Issues
- Transformation logic (class shifting) still in main.py, not in compare layer
- No formal validation of subject type constraints
- No unit tests for KQGD parsing gate
- Dead code files were deleted but test_db.py references them

---

## 10. File Structure

```
D:\coding\qlcl\
├── app/
│   ├── main.py              # Streamlit UI, upsert, transformation
│   ├── core/
│   │   └── compare.py       # Comparison logic
│   └── infra/
│       └── vnedu_parser.py  # Excel parser, KQGD extraction
├── docs/
│   ├── contracts.md         # SINGLE SOURCE OF TRUTH
│   ├── engineering_review.md
│   ├── todo.md
│   └── architecture.md
├── input/                  # Sample Excel files
├── sqms.db                 # SQLite database
└── requirements.txt
```
