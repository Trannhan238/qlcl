# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────┐
│                  UI Layer (Streamlit)                │
│                  app/main.py                        │
│   Upload → Process → Display → Export               │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              Use Case Layer (app/usecases)           │
│              process_excel.py                        │
│   Orchestrate: parse → normalize → validate → persist│
│   Handles snapshot_type gating (KQGD, targets)       │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              Domain Layer (app/domain)               │
│   models.py      → SubjectSnapshot, ClassSummary     │
│   normalizers.py → Business rules (subject naming)   │
│   adapters.py    → Parser dict → Domain objects      │
│   Pure domain logic, no I/O                          │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│           Infrastructure Layer (app/infra)            │
│   vnedu_parser.py  → Excel parsing (layout-aware)    │
│   file_loader.py   → .xls/.xlsx loading               │
│   excel_normalizer.py → format normalization          │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│           Repository Layer (app/repositories)         │
│   interfaces.py       → Abstract repository           │
│   sqlite_repository.py → SQLite implementation        │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              Database (app/db)                        │
│   connection.py → SQLite connection management        │
│   Tables: subject_snapshots, class_summary,           │
│           teacher_commitments, student_achievements   │
└─────────────────────────────────────────────────────┘

Supporting:
┌─────────────────────────────────────────────────────┐
│              Core Layer (app/core)                    │
│   compare.py  → Baseline vs actual comparison        │
│   snapshot.py → Snapshot management                   │
│   ports.py    → Interface definitions                 │
└─────────────────────────────────────────────────────┘
```

## Data Flow

```
Excel (.xls/.xlsx)
  │
  ▼
file_loader.load_excel()
  │  Handles .xls → .xlsx conversion (pywin32)
  │  Returns Dict[sheet_name, DataFrame]
  ▼
parse_vnedu_file_with_class_summary()
  │  RAW DATA EXTRACTION ONLY (no business rules)
  │  1. Dynamic header detection (group/main/sub/metric)
  │  2. Build column plan (dynamic subject detection)
  │  3. Filter by group header ("Môn học" section only)
  │  4. Parse each subject (T/H/C counts, avg_score)
  │  5. Parse KQGD (if allow_kqgd=True)
  ▼
ParserResultAdapter.convert_parser_output()
  │  1. normalize_subject_name() → apply business rules
  │     "Nghệ thuật - Âm nhạc" → "Âm nhạc"
  │     "Nghệ thuật" → removed
  │  2. Inject snapshot_type
  │  3. Convert dict → SubjectSnapshot / ClassSummary
  ▼
ProcessExcelUseCase.execute()
  │  1. Validate domain objects
  │  2. Deduplicate subjects
  │  3. Generate targets (if baseline + delta)
  │  4. Persist via repository
  ▼
SQLite Database
```

### Separation of Concerns

```
parse (infra)  → raw dict    (NO transformation)
normalize (domain) → business rules  (subject naming, etc.)
adapter (domain) → domain objects
repository → persistence
```

## Key Design Decisions

### 1. Dynamic Header Detection (Not Hardcoded)

Parser dynamically detects header positions by scanning for keywords:
- `_detect_header_layout(df)` scans first 15 rows
- Finds "Môn học" / "Hoạt động giáo dục" keyword → group_row
- Infers: main_row = group_row + 1, sub_row = group_row + 2, metric_row = group_row + 3
- No hardcoded row indices

This tolerates extra title rows, merged cells, and different grade layouts.

### 2. Region-Based Parsing

The parser filters by group header:
- **"Môn học và hoạt động giáo dục"** → subjects (parsed)
- **"Năng lực cốt lõi"** → skipped
- **"Phẩm chất chủ yếu"** → skipped
- **"Đánh giá KQGD"** → KQGD section (parsed separately)

### 3. Pure Functions (No Shared State)

`_parse_kqgd_summary()` is pure:
- All variables initialized inside function
- `df = df.copy()` at start
- No caching between calls
- Batch processing produces identical results

### 4. Defensive Parsing

- Tolerates empty score columns → downgrades to qualitative
- Handles `\uf0fc` (Wingdings) tick marks
- Accepts float STT values (1.0, 2.0)
- Single-column subjects forced to qualitative
- No hardcoded subject names

## File Structure

```
app/
├── __init__.py
├── main.py                    # Streamlit UI
├── core/
│   ├── __init__.py
│   ├── compare.py             # Baseline vs actual comparison
│   ├── snapshot.py            # Snapshot management
│   └── ports.py               # Interface definitions
├── db/
│   └── connection.py          # SQLite connection
├── domain/
│   ├── models.py              # SubjectSnapshot, ClassSummary, SnapshotType
│   └── adapters.py            # Parser dict → domain objects
├── infra/
│   ├── __init__.py
│   ├── vnedu_parser.py        # Excel parser (main)
│   ├── file_loader.py         # File loading + .xls conversion
│   └── excel_normalizer.py    # Format normalization
├── repositories/
│   ├── __init__.py
│   ├── interfaces.py          # Abstract repository
│   └── sqlite_repository.py   # SQLite implementation
├── usecases/
│   └── process_excel.py       # Orchestration
└── models/
    └── __init__.py             # Legacy (deprecated)

docs/
├── architecture.md            # This file
├── contracts.md               # Layer contracts
├── engineering_review.md      # Post-refactor review
└── todo.md                    # Roadmap
```

## Known Edge Cases

| Issue | Cause | Mitigation |
|-------|-------|------------|
| Missing KQGD columns | File has no KQGD section | Return None, skip class_summary |
| Baseline grade 5 | Policy mismatch (TT22 vs TT27) | Domain-level validation |
| XLS encoding issues | xlrd can't read corrupted .xls | pywin32 COM fallback |
| Tick symbols `\uf0fc` | Wingdings font in Excel | Normalize in CHECKBOX_MARKERS |
| Empty score columns | HK1 files lack "Điểm KTĐK" | Downgrade scored → qualitative |
| Multi-grade subjects | Different column layouts per grade | Dynamic column plan detection |
