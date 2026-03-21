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
│   Orchestrate: parse → validate → persist            │
│   Handles snapshot_type gating (KQGD, targets)       │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              Domain Layer (app/domain)               │
│   models.py     → SubjectSnapshot, ClassSummary      │
│   adapters.py   → Parser dict → Domain objects       │
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
  │  1. Flatten 4-row header → single column names
  │  2. Build column plan (dynamic subject detection)
  │  3. Filter by group header ("Môn học" section only)
  │  4. Parse each subject (T/H/C counts, avg_score)
  │  5. Parse KQGD (if allow_kqgd=True)
  ▼
ParserResultAdapter.convert_parser_output()
  │  Dict → SubjectSnapshot / ClassSummary
  │  Injects snapshot_type
  ▼
ProcessExcelUseCase.execute()
  │  1. Validate domain objects
  │  2. Deduplicate subjects
  │  3. Generate targets (if baseline + delta)
  │  4. Persist via repository
  ▼
SQLite Database
```

## Key Design Decisions

### 1. Layout-Aware Parsing (Not Schema-Based)

Parser reads Excel row/column positions, not cell addresses:
- Row 5: Group header ("Môn học", "Năng lực cốt lõi")
- Row 6: Subject name (ffill for merged cells)
- Row 7: Sub-name
- Row 8: Metric label ("Mức đạt được", "Điểm KTĐK")
- Row 9+: Data rows

This tolerates column insertion/deletion without breaking.

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
