# TODO Roadmap

## P0 – Must Fix Now

### Fix snapshot_type Inconsistency

Task 1: Fix class_summary snapshot_type values
- Edit `app/main.py` function `upsert_class_summary()`
- Change snapshot_type validation to ONLY accept: "baseline", "actual_hk2"
- Add assertion: `assert snapshot_type in {"baseline", "actual_hk2"}`

Task 2: Fix KQGD parsing gate in process_files()
- Edit `app/main.py` function `process_files()`
- Add gate: only call `_parse_class_summary()` and upsert class_summary when `snapshot_type in {"baseline", "actual_hk2"}`
- Current code appends all class_summary regardless of snapshot_type

Task 3: Remove invalid "actual" snapshot_type
- Search codebase for "actual" as snapshot_type
- Replace with correct values: "actual_hk1" or "actual_hk2"
- Update LABEL_MAP in main.py

---

### Implement Column Grouping Detection

Task 4: Add column grouping detection in parser
- Edit `app/infra/vnedu_parser.py`
- Add function `_detect_subject_type(col_idx, plan)`:
  - If current and next column have same subject header AND both are valid → scored subject
  - If only current column has valid header → qualitative subject
- Validate: do NOT treat scored subjects as score-only

Task 5: Add subject type validation
- Add function `validate_subject_type(subject_data)`:
  - Scored: assert avg_score is not NULL
  - Qualitative: assert avg_score IS NULL
- Call after `parse_sheet()` returns

Task 6: Update `_build_column_plan()` to track column pairings
- Return structured data: `{subject: {level_col, score_col}}`
- Detect 2-column vs 1-column groupings
- Log detected type per subject

---

### Implement KQGD Validation

Task 7: Add KQGD sum validation
- Edit `app/infra/vnedu_parser.py` in `_parse_class_summary()`
- After counting HTXS/HTT/HT/CHT:
  - Assert: `HTXS + HTT + HT + CHT == total_students_from_KQGD`
  - If mismatch: raise ValueError with class_name, academic_year

Task 8: Add KQGD parsing gate enforcement
- Add parameter `allow_kqgd: bool` to `_parse_class_summary()`
- If `allow_kqgd=False`: return empty class_summary
- Wire this gate from `process_files()` based on snapshot_type

Task 8a: Add KQGD zero-data check
- Edit `_parse_class_summary()`
- After counting HTXS/HTT/HT/CHT:
  - Compute: total_students_from_KQGD
  - If total_students_from_KQGD == 0: raise ValueError
  - Message: "KQGD: empty data in class {class_name}, year {academic_year}"

---

## P1 – Important

### Data Validation

Task 9: Add T+H+C consistency validation
- Edit `app/infra/vnedu_parser.py` in `parse_sheet()`
- After parsing each subject:
  - Validate: T >= 0, H >= 0, C >= 0
  - For qualitative subjects: validate T+H+C <= student_count
  - If violated: raise ValueError

Task 10: Add student_count cross-validation
- Edit `app/main.py` function `process_files()`
- After parsing:
  - Query subject_snapshots for student_count by class
  - Compare with class_summary.total_students
  - If mismatch: raise ValueError and stop processing
  - DO NOT warn user - MUST fail hard

Task 11: Add avg_score range validation
- In parser or upsert layer:
  - Validate: 0 <= avg_score <= 10
  - If violated: raise ValueError

Task 11a: Normalize subject headers before grouping
- Edit `app/infra/vnedu_parser.py` in `_build_column_plan()`
- Implement normalization function:
  - lowercase
  - remove accents (đ → d)
  - trim whitespace
- Apply normalization before comparing column headers
- Use existing `_norm()` function

Task 11b: Validate adjacent column pairing
- Edit `app/infra/vnedu_parser.py`
- When grouping two adjacent columns:
  - Normalize both headers
  - Assert normalized headers are identical
  - If not identical: raise ValueError("Column pairing failed: headers do not match")

Task 11c: Validate KQGD total > 0
- Edit `app/infra/vnedu_parser.py` in `_parse_class_summary()`
- After counting HTXS/HTT/HT/CHT:
  - Compute: total_students_from_KQGD = HTXS + HTT + HT + CHT
  - If total_students_from_KQGD == 0: raise ValueError

---

### Parser Unit Tests

Task 12: Create unit test for _eval_bucket()
- File: `tests/test_vnedu_parser.py`
- Test cases: "T", "H", "C", None, "HTXS", "htt"
- Assert: returns correct bucket letter or None

Task 13: Create unit test for is_checked()
- File: `tests/test_vnedu_parser.py`
- Test cases: "✓", "✔", "v", "x", "1" → True
- Test cases: "abc", None, 123, "" → False

Task 14: Create unit test for subject type detection
- File: `tests/test_vnedu_parser.py`
- Create synthetic DataFrame with 2-column scored subject
- Create synthetic DataFrame with 1-column qualitative subject
- Assert: parser correctly identifies each type

Task 15: Create unit test for KQGD parsing gate
- File: `tests/test_vnedu_parser.py`
- Test: `_parse_class_summary(df, ..., allow_kqgd=True)` returns data
- Test: `_parse_class_summary(df, ..., allow_kqgd=False)` returns empty/Nothing

Task 16: Create unit test for KQGD sum validation
- File: `tests/test_vnedu_parser.py`
- Create synthetic KQGD block with mismatch
- Assert: raises ValueError

---

### Architecture Cleanup

Task 17: Remove transformation logic from main.py
- Edit `app/main.py` function `process_files()`
- Remove calls to `shift_class_name()`, `increment_academic_year()`
- Remove baseline transform block (lines 361-376)
- Move baseline mapping logic to `compare.py`

Task 18: Move SQL out of main.py
- Create `app/infra/database.py`
- Move: `get_conn()`, `init_db()`, `migrate_db()`, `table_exists()`
- Move: `upsert_subject()`, `upsert_class_summary()`, `upsert_teacher_commitment()`, `upsert_student_achievement()`
- Verify main.py still works

---

## P2 – Optional

### Domain Model

Task 19: Create pydantic models for data contracts
- File: `app/models/domain.py`
- Class `SubjectSnapshot`: fields matching subject_snapshots table
- Class `ClassSummary`: fields matching class_summary table
- Add validators for constraints

Task 20: Create repository classes
- File: `app/infra/repositories.py`
- Class `SubjectSnapshotRepository`: CRUD for subject_snapshots
- Class `ClassSummaryRepository`: CRUD for class_summary
- Use pydantic models as input/output

---

### Integration Tests

Task 21: Create integration test for parse → insert pipeline
- File: `tests/test_integration.py`
- Use synthetic VNEDU Excel file (created with openpyxl)
- Steps:
  1. Create test Excel with known data
  2. Call `parse_vnedu_file_with_class_summary()`
  3. Call upsert functions
  4. Query database
  5. Assert: values match expected

Task 22: Fix test_db.py to work with current architecture
- Delete or rewrite `test_db.py`
- Current version references deleted modules

---

## Completed Tasks

### Phase 1 – Code Quality (DONE)
- [x] Fixed linting issues in `app/infra/vnedu_parser.py`
- [x] Fixed linting issues in `app/main.py`
- [x] Deleted dead code files

### Phase 0 – Foundation (DONE)
- [x] Parse VNEDU Excel files
- [x] Store subject-level data in subject_snapshots
- [x] Store class-level data in class_summary
- [x] Create teacher_commitments table
- [x] Create student_achievements table
- [x] Build Streamlit UI with tabs
- [x] Implement comparison logic
- [x] Add Vietnamese comments

---

## Definition of Done

Each task must have:

1. **Code written** - Implementation complete
2. **Tests written** - Unit or integration tests cover the feature
3. **Manual verification** - Tested with real data
4. **contracts.md aligned** - No contradictions with contract

### Testing Requirements

| Task Type | Test Coverage |
|-----------|---------------|
| Parser functions | 100% - test all branches |
| Validation functions | 100% - test all constraint paths |
| KQGD gate | 100% - test both paths |
| avg_score range | 100% - test 0, 5, 10, -1, 11 |
| KQGD zero check | 100% - test total==0 |
| Column header normalization | 100% - test accent/case variations |
| Database operations | 80% - test happy path and errors |
