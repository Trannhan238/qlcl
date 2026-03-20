# Engineering Review

## 1. System Overview

### Modules

| Module | File | Responsibility |
|--------|------|----------------|
| **Parser** | `app/infra/vnedu_parser.py` | Excel file parsing, extracts subject-level and class-level data |
| **Streamlit UI** | `app/main.py` | Single-file UI (~1040 lines), handles upload, processing, display |
| **Compare Logic** | `app/core/compare.py` | Metrics comparison (actual vs baseline vs target vs commitment) |
| **Database** | SQLite (`sqms.db`) | 4 tables with inline initialization |

### Data Flow

```
Excel File → Parser (vnedu_parser.py)
                    ↓
            ┌───────┴───────┐
            ↓               ↓
    subject_results   class_summary
            ↓               ↓
    subject_snapshots  class_summary
            ↓               ↓
            └───────┬───────┘
                    ↓
              Streamlit UI
                    ↓
            Display + Charts + Export
```

---

## 2. Critical Issues

| Issue | Description | Impact | Severity |
|-------|-------------|--------|----------|
| Subject parsing hardcoded structure | `_build_column_plan()` assumes fixed row indices (rows 6, 8, 9+) | Parser fails if VNEDU changes Excel format | HIGH |
| Student counting is fragile | Line 168: filters rows where first column `str(x).isdigit()` | Misses students where STT has format like "1." or "01" | HIGH |
| Duplicate handling is silent | `upsert_subject()` overwrites silently | User loses historical data without warning | HIGH |
| class_summary lacks snapshot_type | Unlike subject_snapshots, no versioning | Cannot track actual vs target vs baseline at class level | HIGH |
| Column detection uses substring matching | `if kw_norm in cell_norm` allows false positives | "T" matches "Tiếng Việt", wrong columns detected | MEDIUM |
| No foreign key constraints | All tables lack FK relationships | Orphaned records, inconsistent state | MEDIUM |
| class_summary validation not enforced | `_validate_counts()` sets flag but doesn't prevent insert | Invalid data enters database | MEDIUM |
| Two normalization functions | `_norm()` vs `_normalize_text()` | Inconsistent behavior across code | LOW |

---

## 3. Technical Debt

### Hardcoded Assumptions

| Location | Assumption | Risk |
|----------|-----------|------|
| `_build_column_plan()` | Rows 6, 8, 9+ contain headers/data | Breaks if VNEDU adds title rows |
| `_detect_class_name()` | Row 4 contains class name | Breaks if format changes |
| `_detect_academic_year()` | Row 3 contains academic year | Breaks if format changes |
| `_find_header_region()` | "stt" and "hoten" keywords exist | May misdetect in non-standard files |
| `CHECKBOX_MARKERS` set | Fixed set of accepted markers | May miss new checkbox formats |

### Weak Validation

1. **No schema validation** on insert - accepts any data
2. **No data type enforcement** - strings may be stored where numbers expected
3. **No range checks** - T+H+C may exceed student_count
4. **No duplicate detection** before parsing - processes then overwrites

### Code Quality Issues

1. **1040-line main.py** - mixed responsibilities, hard to test
2. **456 lines of dead code** - `excel_parser.py`, `import_service.py`, etc.
3. **Inline SQL** - database operations mixed with UI code
4. **No error recovery** - transaction rollback loses all progress

---

## 4. Risks

### Wrong Aggregation

**Scenario**: STT column contains "1." instead of "1"
**Effect**: Student row filtered out, student_count too low
**Probability**: Medium (depends on export format)

### Wrong Comparison Results

**Scenario**: User uploads baseline as "actual_hk1" snapshot type
**Effect**: Comparing actual vs actual, deltas always zero
**Probability**: High (no confirmation dialog)

### Corrupted Database

**Scenario**: Transaction rollback on partial insert
**Effect**: No records inserted, user loses all progress
**Probability**: Low (SQLite handles this well)

### Parser Failure

**Scenario**: VNEDU updates Excel format with new rows
**Effect**: Parser returns empty results, silent data loss
**Probability**: Medium (vendor changes are unpredictable)

---

## 5. Recommendations

### Fix Immediately (This Sprint)

1. **Create parser unit tests** - verify `_eval_bucket()`, `is_checked()`, `_normalize_text()`
2. **Add student_count validation** - assert T+H+C ≤ student_count after parse
3. **Consolidate normalization** - single function used everywhere
4. **Delete dead code files** - reduce confusion:
   - `app/infra/excel_parser.py`
   - `app/services/import_service.py`
   - `app/infra/repositories.py`

### Can Wait (Next Sprint)

1. Extract database operations to `database.py`
2. Extract parser to standalone module
3. Add foreign key constraints
4. Add confirmation dialog before insert

### Avoid

1. **Don't add features until parser is tested** - wrong data propagates everywhere
2. **Don't mix subject-level and class-level in same table** - leads to query confusion
3. **Don't add more hardcoded row indices** - use heuristics with fallbacks
4. **Don't implement comparison UI until data model is stable** - rework cost is high

---

## Summary

| Category | Critical Issues | Tech Debt Items | Phase 1 Tasks |
|----------|-----------------|-----------------|---------------|
| Count | 8 | 6 | 5 |
| Priority | Immediate | Next sprint | This sprint |
| Effort | ~1 day | ~3 days | ~2 days |
