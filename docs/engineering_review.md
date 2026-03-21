# Engineering Review — Post-Refactor

## Problems Encountered

### 1. Excel Layout Complexity

VNEDU Excel files use merged cells across 4 header rows. A single subject name spans multiple columns. Column positions shift between grade levels and file versions.

**Impact:** Parser initially assumed fixed column positions. Broke on grade 5 files with different subject counts.

### 2. Multi-Header Ambiguity

Rows 5-8 contain overlapping information:
- Row 5: Section group ("Môn học", "Năng lực cốt lõi", "Đánh giá KQGD")
- Row 6: Subject name (ffill for merged cells)
- Row 8: Metric label ("Mức đạt được", "Điểm KTĐK")

Without ffill on row 6, adjacent columns couldn't be grouped correctly.

### 3. Subject Type Assumption

Initial code used hardcoded keywords ("toán", "tiếng anh", "tin học") to determine scored vs qualitative. This failed when:
- Tiếng Anh had no score column in HK1 files
- Tin học was scored in some grades, qualitative in others
- New subjects were added without updating the keyword list

### 4. State Contamination Bug

KQGD parsing worked for single files but failed in batch (grade 5). Root cause: `_parse_kqgd_summary` used closures and cached state between calls. The second file's KQGD was polluted by the first file's data.

### 5. XLS Loading Issues

xlrd 2.0.2 can't read some .xls files (corrupted BIFF format). Batch import failed silently. Added pywin32 COM fallback for .xls → .xlsx conversion, but required `pythoncom.CoInitialize()` in Streamlit threads.

### 6. Policy Drift (TT22 vs TT27)

Grade 5 uses different KQGD categories than grades 1-4. Parser needed to handle both layouts dynamically.

---

## Solutions Implemented

### Region-Based Parsing

Parser now reads the group header (row 5) and filters by section:
- "Môn học và hoạt động giáo dục" → parse subjects
- "Năng lực cốt lõi", "Phẩm chất" → skip
- "Đánh giá KQGD" → parse KQGD separately

This handles any number of subjects in any order.

### Pure Functions

`_parse_kqgd_summary` is now pure:
- `df = df.copy()` at start
- All variables initialized inside function
- No closures, no caching
- Batch processing produces identical results

### Dynamic Column Plan

`_build_column_plan` groups columns by subject name from h_main (row 6, ffill). Subject type is determined by whether a "score" metric column exists, not by subject name.

Single-column subjects are forced to `qualitative`.

### Defensive Validation

- Empty score columns → downgrade to qualitative
- `\uf0fc` (Wingdings) tick marks → recognized as checked
- Float STT values (1.0, 2.0) → accepted as student rows
- avg_score out of range [0, 10] → raise ValueError
- T+H+C > student_count → raise ValueError
- KQGD total == 0 → raise ValueError

### Domain Model Cleanup

Removed `is_scored()` heuristic based on subject name. Now `is_scored()` returns `avg_score is not None`. Removed `validate_subject_type()` that enforced name-based rules. Domain model is now data-driven, not name-driven.

---

## Lessons Learned

### Layout ≠ Data

Excel layout is not a database schema. Row positions, merged cells, and column order can change between files. Parser must read structure dynamically, not assume positions.

### Do Not Trust Excel Structure

Header rows may be missing, shifted, or duplicated. Parser must handle:
- Missing metric labels (HK1 without "Điểm KTĐK")
- Missing sections (no KQGD block)
- Corrupted files (xlrd fails, pywin32 fallback needed)

### Batch Systems Must Be Stateless

Every function that processes data must be pure. No caching, no closures, no shared mutable state. `df = df.copy()` at the start of every parsing function.

### Data Pipelines Must Tolerate Imperfect Input

Don't raise errors on partial data. Downgrade gracefully:
- Score column empty → qualitative
- No KQGD section → skip class_summary
- Non-numeric STT → skip row

Only raise on hard constraints (KQGD sum mismatch, negative counts).

---

## Architecture Changes

| Before | After |
|--------|-------|
| 4-layer (UI → Domain → Parser → Storage) | 6-layer (UI → UseCase → Domain → Infra → Repository → DB) |
| Parser returns domain objects | Parser returns raw dicts, adapter converts |
| No use case layer | `ProcessExcelUseCase` orchestrates flow |
| Inline SQL in main.py | Repository pattern with abstract interface |
| Hardcoded subject names | Dynamic detection from header structure |
| `_is_student()` used `isdigit()` | `_is_student()` uses `float()` for tolerance |

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Files | 4 | 12 |
| Layers | 3 | 6 |
| Subject detection | Hardcoded keywords | Dynamic from header |
| KQGD parsing | Shared state | Pure function |
| Error handling | Silent catch | Defensive downgrade |
| Batch consistency | Inconsistent | Deterministic |
