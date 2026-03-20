# TODO Roadmap

## Phase 1 – Stabilization

> **Goal**: Verify parser correctness before adding features. All tasks must pass tests.

### Parser Testing

- [ ] Create unit tests for `_eval_bucket()` with known inputs
  - Test cases: T, H, C, null, "T", "H", "C", "HTXS", "htt"
  - Expected: correct bucket letter or None

- [ ] Create unit tests for `is_checked()` with known inputs
  - Valid markers: "✓", "✔", "v", "x", "1"
  - Invalid values: "abc", None, 123, "Tiếng Việt", ""
  - Expected: True only for valid markers

- [ ] Create unit tests for `_normalize_text()`
  - Test Vietnamese diacritics: "điểm" → "diem"
  - Test whitespace: "  ab   cd  " → "ab cd"
  - Test case: "ABC" → "abc"

### Data Validation

- [ ] Add student_count validation: assert T+H+C ≤ student_count
  - Run after parse, before insert
  - Log warning if violated, reject data

- [ ] Add duplicate detection before overwrite
  - Show confirmation dialog with preview
  - User must explicitly confirm overwrite

### Code Quality

- [ ] Consolidate normalization functions into one
  - Remove `_norm()` from line 22
  - Use only `_normalize_text()` everywhere
  - Verify all tests still pass

- [x] Delete dead code files
  - `app/infra/excel_parser.py`
  - `app/services/import_service.py`
  - `app/infra/database.py`
  - `app/infra/repositories.py`
  - ✅ Verified app still runs after deletion

---

## Phase 2 – Data Model

> **Goal**: Complete the data model for class-level tracking. Add versioning to class_summary.

### Schema Changes

- [ ] Add `snapshot_type` column to `class_summary`
  - ALTER TABLE to add column
  - Update insert logic to use snapshot_type
  - Update UI to filter by snapshot_type
  - Valid values: "actual", "baseline", "target"

- [ ] Add foreign key constraints
  - Add REFERENCES clause to teacher_commitments
  - Validate academic_year exists in subject_snapshots

### Module Extraction

- [ ] Extract database operations to `database.py`
  - Move `init_*()` functions
  - Move `upsert_*()` functions
  - Move `get_*()` query functions
  - Verify main.py still works after extraction

- [ ] Extract parser to standalone module
  - Create `app/services/parser.py`
  - Move parsing logic out of main.py
  - Keep only UI code in main.py

### Testing

- [ ] Create integration test for full parse → insert pipeline
  - Use sample Excel files
  - Verify data in database after run

---

## Phase 3 – Features

> **Goal**: Build on stable foundation. All features depend on Phase 1-2 completion.

### Commitments Integration

- [ ] Show teacher commitments in comparison view
  - Query commitments by year and class
  - Display commitment target alongside actual result
  - Color code: achieved (green), not achieved (red)

- [ ] Add commitments form validation
  - Validate T%+H%+C% ≤ 100
  - Validate student counts are non-negative

### Achievements Dashboard

- [ ] Create achievements pivot table view
  - Rows: categories (Văn Toán Tuổi thơ, IOE, etc.)
  - Columns: levels (Xã, Quận/Huyện, Tỉnh, Quốc gia)
  - Values: quantity sum

- [ ] Add achievements chart
  - Bar chart grouped by category
  - Stacked by level
  - Filter by academic year

### Export

- [ ] Add CSV export for each view
  - Subject comparison table
  - Class summary table
  - Achievements pivot

- [ ] Add Excel export with formatting
  - Bold headers
  - Number formatting
  - Auto column width

### Analytics

- [ ] Add year-over-year comparison
  - Compare metrics across academic years
  - Show trend arrows (↑ ↓ →)

- [ ] Add school-wide aggregates
  - Average scores across classes
  - Total achievements count
  - Completion rate summary

---

## Completed Tasks

### Phase 1 – Code Quality (DONE)
- [x] Fixed linting issues in `app/infra/vnedu_parser.py`
  - Removed unused `Path` import
  - Fixed E701 (multiple statements on one line)
  - Fixed f-strings without placeholders
  - Removed duplicate `read_vnedu_file` function
  - Removed unused `total_evaluated` variable
- [x] Fixed linting issues in `app/main.py`
  - Fixed import order to pass E402
  - Added noqa comments for necessary local imports
- [x] Deleted dead code files (database.py, repositories.py, excel_parser.py, import_service.py)

### Phase 0 – Foundation (DONE)

- [x] Parse VNEDU Excel files
- [x] Store subject-level data in subject_snapshots
- [x] Store class-level data in class_summary
- [x] Create teacher_commitments table
- [x] Create student_achievements table
- [x] Build Streamlit UI with tabs
- [x] Implement comparison logic
- [x] Add class shifting for baseline transformation

---

## Definition of Done

Each task must have:

1. **Code written** - Implementation complete
2. **Tests written** - Unit or integration tests cover the feature
3. **Manual verification** - Tested with real data
4. **Documentation updated** - If user-facing, update docs/

### Testing Requirements

| Task Type | Test Coverage |
|-----------|---------------|
| Parser functions | 100% - test all branches |
| Database operations | 80% - test happy path and errors |
| UI components | Manual test - check render |
| API endpoints | 90% - test all status codes |
