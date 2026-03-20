# Architecture

## 1. System Overview

The system follows a layered architecture:

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
│   - transform: class shifting, year incrementing            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                     Parser Layer                            │
│           (app/infra/vnedu_parser.py)                      │
│   - Excel file reading                                     │
│   - Header detection                                       │
│   - Column mapping                                         │
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
| **UI** | User interaction, data display | `main.py` |
| **Domain** | Business logic, comparisons | `compare.py` |
| **Parser** | Excel parsing, data extraction | `vnedu_parser.py` |
| **Storage** | Data persistence | SQLite tables |

---

## 2. Data Model

### Subject-Level Data

**Table: `subject_snapshots`**

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `academic_year` | TEXT | e.g., "2024-2025" |
| `class_name` | TEXT | e.g., "1A" |
| `subject` | TEXT | e.g., "Toán", "Tiếng Việt" |
| `snapshot_type` | TEXT | "actual_hk1", "actual_hk2", "baseline", "target" |
| `avg_score` | REAL | Average score (0-10), nullable |
| `student_count` | INTEGER | Total students in class |
| `T` | INTEGER | Count of "Hoàn thành xuất sắc" students |
| `H` | INTEGER | Count of "Hoàn thành" students |
| `C` | INTEGER | Count of "Chưa hoàn thành" students |

**Unique constraint**: `(academic_year, class_name, subject, snapshot_type)`

---

### Class-Level Data

**Table: `class_summary`**

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `academic_year` | TEXT | e.g., "2024-2025" |
| `class_name` | TEXT | e.g., "1A" |
| `snapshot_type` | TEXT | "actual", "baseline", "target" |
| `HTXS` | INTEGER | Count of "Hoàn thành xuất sắc" |
| `HTT` | INTEGER | Count of "Hoàn thành tốt" |
| `HT` | INTEGER | Count of "Hoàn thành" |
| `CHT` | INTEGER | Count of "Chưa hoàn thành" |
| `HTCTLH_HT` | INTEGER | Count of "Hoàn thành chất lượng học tập" |
| `HTCTLH_CHT` | INTEGER | Count of "Chưa hoàn thành chất lượng học tập" |
| `HSXS` | INTEGER | Count of "Học sinh xuất sắc" |
| `HS_TieuBieu` | INTEGER | Count of "Học sinh tiêu biểu" |

**Unique constraint**: `(academic_year, class_name, snapshot_type)`

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

### Data Level Summary

| Level | Tables | Granularity |
|-------|--------|-------------|
| **Subject** | `subject_snapshots` | Per-class, per-subject, per-snapshot |
| **Class** | `class_summary` | Per-class, per-snapshot |
| **School** | `teacher_commitments`, `student_achievements` | Per-year, per-category |

---

## 3. Data Flow

### Pipeline: Excel → Database → UI

```
1. User uploads Excel file
          ↓
2. Parser reads file (pd.read_excel)
          ↓
3. Detect class name, academic year
          ↓
4. Parse subject data (T/H/C counts, avg_score)
          ↓
5. Parse class summary (checkbox counting)
          ↓
6. Transform (class shifting, year incrementing) [if baseline]
          ↓
7. Validate (student_count ≥ T+H+C)
          ↓
8. Insert to database (upsert)
          ↓
9. Query from database
          ↓
10. Compare with targets/baselines
          ↓
11. Display in UI (table, charts)
```

### Transformation Rules

| Operation | Description |
|-----------|-------------|
| **Class shifting** | Grade 1→2, 2→3, 3→4, 4→5, 5→skipped |
| **Year incrementing** | "2024-2025" → "2025-2026" |
| **Score delta** | Target score = baseline + delta |

---

## 4. Key Design Decisions

### Why Single Table for Snapshots?

**Decision**: Store all snapshot types in one table with `snapshot_type` column.

**Rationale**:
- Simpler queries: `WHERE snapshot_type = 'actual_hk2'`
- Easier comparison: JOIN on (class, subject) with different types
- Single upsert logic handles all types

**Alternative considered**: Separate tables per type
- Rejected: Would require 4x the query code

---

### Why Checkbox Counting?

**Decision**: Count non-empty cells per column for class summary.

**Rationale**:
- VNEDU exports checkbox matrix format
- Each student has exactly ONE classification
- Count = number of checkmarks in column

**Algorithm**:
```python
for each category_column:
    count = number_of_rows_where(cell != empty)
```

---

### Why Normalization?

**Decision**: Normalize Vietnamese text before matching.

**Rationale**:
- Excel may contain accents or diacritics
- Case variations exist ("TOÁN" vs "toán")
- Abbreviations used ("HT" vs "Hoàn thành")

**Process**:
1. Lowercase
2. Remove accents (đ → d)
3. Collapse whitespace
4. Match against keyword list

---

## 5. Constraints

### Excel Structure Constraints

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| Semi-structured | Parser may fail on format changes | Heuristic detection with fallbacks |
| No fixed schema | Column positions vary | Keyword-based column mapping |
| Checkbox markers vary | May use ✓, ✔, x, 1 | Accept multiple markers |
| Vietnamese text | Encoding issues | UTF-8, normalization |

### Data Constraints

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| Inconsistent rows | student_count mismatch | Validation before insert |
| Missing columns | Partial data | Log warnings, continue |
| Duplicate records | Data overwritten | Warn user, use upsert |

### Validation Rules

1. **Before parse**: File exists, readable
2. **After parse**: student_count ≥ T+H+C
3. **Before insert**: Duplicate check
4. **After insert**: Commit or rollback

---

## 6. Future Extensions

### FastAPI Backend

**Goal**: Separate UI from business logic.

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   Streamlit │  API  │   FastAPI   │  DB   │   SQLite    │
│   (Frontend)│ ←──→  │  (Backend)  │ ←──→  │  (Storage)  │
└─────────────┘       └─────────────┘       └─────────────┘
```

**Benefits**:
- Reusable API for mobile apps
- Better testing
- Separate deployments

---

### MySQL Migration

**Goal**: Support multiple concurrent users.

```
Current: SQLite (single user)
Future:  MySQL (multi-user)
```

**Changes required**:
- Replace `sqlite3` with `SQLAlchemy`
- Add connection pooling
- Implement user authentication
- Add row-level permissions

---

### Dashboard Analytics

**Goal**: Aggregate insights across years.

| Feature | Description |
|---------|-------------|
| Year-over-year trends | Compare metrics across academic years |
| Class rankings | Rank classes by performance |
| Subject analysis | Identify weak subjects |
| Achievement tracking | Monitor competition results |

---

### File Structure

```
D:\coding\qlcl\
├── app/
│   ├── main.py              # Streamlit UI (current)
│   ├── core/
│   │   └── compare.py       # Comparison logic
│   ├── infra/
│   │   ├── vnedu_parser.py  # Excel parser
│   │   └── database.py      # DB operations (to be extracted)
│   └── services/
│       └── parser.py        # Parser service (to be extracted)
├── docs/
│   ├── engineering_review.md
│   ├── todo.md
│   └── architecture.md
├── input/                    # Sample Excel files
├── templates/                # Excel import templates
├── sqms.db                  # SQLite database
└── requirements.txt
```
