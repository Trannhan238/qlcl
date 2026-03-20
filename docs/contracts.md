VNEDU Parsing and Data Integrity Contract
==========================================

This document defines a strict, enforceable contract for parsing VNEDU Excel data
and maintaining data integrity within the VNEDU aggregation system.

---

1. Snapshot Rules

1.1 Snapshot Types
- baseline      = HK2 of previous academic year
- actual_hk1   = current academic year, HK1
- actual_hk2   = current academic year, HK2

1.2 Snapshot Type Enforcement
- snapshot_type MUST be one of: {"baseline", "actual_hk1", "actual_hk2", "target"}
- Any other value MUST raise ValueError
- "commitment" is NOT a valid snapshot_type for subject_snapshots or class_summary

1.3 KQGD Presence Rule
- KQGD data MUST be parsed ONLY for:
  - baseline
  - actual_hk2
- KQGD data MUST NOT be parsed for:
  - actual_hk1
  - target
  - commitment
  - any other snapshot_type

---

2. Subject Structure Rules (CRITICAL)

2.1 Two Subject Types Exist

A. Scored Subjects (môn có điểm)
- Structure: TWO adjacent columns
  - Column N:   T/H/C bucket counts
  - Column N+1: Numeric score
- REQUIRED fields:
  - avg_score    (from score column)
  - T, H, C     (from T/H/C column)
- avg_score MUST NOT be NULL

B. Qualitative Subjects (môn nhận xét)
- Structure: ONE column only
  - Column N: T/H/C bucket counts
- REQUIRED fields:
  - T, H, C     (from T/H/C column)
- avg_score MUST be NULL

2.2 Column Grouping Detection (Core Invariant)
- Parser MUST detect subject type by STRUCTURE:
  - Two adjacent columns with same subject header → scored subject
  - Single column with subject header → qualitative subject
- Two adjacent columns belong to the same subject ONLY IF:
  - Their headers match AFTER normalization
- Normalization steps for header comparison:
  - lowercase
  - remove accents (VD: đ → d)
  - trim whitespace
- Parser MUST validate that:
  - Scored subject = exactly 2 columns
  - Qualitative subject = exactly 1 column
- If adjacent columns do NOT match after normalization → MUST raise ValueError
- If column count deviates from expected → MUST raise ValueError
- Parser MUST NOT rely solely on column names to determine type
- Parser MUST validate column grouping consistency

---

3. Data Contracts

3.1 subject_snapshots

FIELDS:
  - academic_year : str
  - class_name    : str
  - subject       : str
  - snapshot_type : str
  - avg_score     : float | NULL
  - student_count : int
  - T             : int
  - H             : int
  - C             : int

CONSTRAINTS:

  If scored subject:
    - avg_score MUST NOT be NULL
    - avg_score MUST be in range [0, 10]
    - T, H, C MUST exist (non-null)
    - T, H, C MUST be >= 0

  If qualitative subject:
    - avg_score MUST be NULL
    - T, H, C MUST exist (non-null)
    - T, H, C MUST be >= 0
    - T + H + C <= student_count

3.2 avg_score Range Validation
  - avg_score MUST be in range [0, 10]
  - If outside range → raise ValueError

3.3 class_summary (KQGD)

FIELDS:
  - academic_year : str
  - class_name    : str
  - snapshot_type : str
  - HTXS : int
  - HTT  : int
  - HT   : int
  - CHT  : int

DEFINITIONS:
  - total_students_from_KQGD = HTXS + HTT + HT + CHT

CONSTRAINTS:
  - total_students_from_KQGD MUST be > 0
  - If total_students_from_KQGD == 0 → raise ValueError
  - HTXS + HTT + HT + CHT == total_students_from_KQGD
  - If mismatch → raise structured error (NO silent fail)

3.4 Cross-Validation Rules
  - class_summary total_students (total_students_from_KQGD) MUST match subject_snapshots.student_count
  - If mismatch → raise ValueError
  - This validation applies ONLY when snapshot_type IN {"baseline", "actual_hk2"}

---

4. KQGD Rules

4.1 Parsing Gate
  - Parse KQGD ONLY IF snapshot_type IN {"baseline", "actual_hk2"}
  - Skip KQGD parsing entirely for all other snapshot_type values

4.2 Aggregation
  - Count HTXS, HTT, HT, CHT from KQGD section
  - Do NOT create student-level records

4.3 Zero-Data Protection
  - total_students_from_KQGD MUST be > 0
  - If total == 0 → raise ValueError("KQGD: empty data in class {class_name}, year {academic_year}")

4.4 Validation
  - Sum(HTXS + HTT + HT + CHT) == total_students_from_KQGD
  - Mismatch → raise ValueError("KQGD: HTXS+HTT+HT+CHT ({sum}) != total_students ({total}) in class {class_name}, year {academic_year}")

---

5. Parser Rules

5.1 Identity Preservation
  - Parser MUST NOT modify academic_year
  - Parser MUST NOT modify class_name

5.2 Required Validations
  - Header row detection
  - Subject grouping (1 column vs 2 columns per subject)
  - Data consistency within grouped columns
  - Non-negative numeric fields

5.3 Failure Semantics
  - Parser MUST NOT silently fail
  - Parser MUST raise structured errors with descriptive messages
  - Errors must include: class_name, academic_year, subject (if applicable)

---

6. Forbidden Patterns

- Treating scored subjects as score-only (ignoring T/H/C)
- Ignoring T/H/C in scored subjects
- Mixing subject types within same logical group
- Pairing adjacent columns with non-matching headers
- Allowing scored subject to have != 2 columns
- Allowing qualitative subject to have != 1 column
- Setting avg_score for qualitative subjects
- Setting NULL avg_score for scored subjects
- Allowing avg_score outside [0, 10]
- Allowing total_students_from_KQGD == 0
- Silent exception handling
- Skipping KQGD validation
- Allowing T + H + C > student_count for qualitative subjects
- Shifting academic_year or class_name in parser layer
- Using invalid snapshot_type values

---

7. Enforcement

7.1 Unit Tests Required
  - Scored vs qualitative subject detection
  - Column grouping validation
  - KQGD detection and sum validation
  - Snapshot gate enforcement (baseline, actual_hk2 vs others)

7.2 Integration Tests Required
  - End-to-end parse of synthetic VNEDU sheet with KQGD block
  - Verify class_summary output matches expected HTXS/HTT/HT/CHT
  - Verify structured errors raised on mismatch

7.3 Error Format
  - All parsing errors: ValueError with message
  - Message must include context (class_name, academic_year, reason)
  - Example: ValueError("KQGD: HTXS+HTT+HT+CHT (28) != total_students (27) in class 1A, year 2024-2025")

---

END OF CONTRACT
