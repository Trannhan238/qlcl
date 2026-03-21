# Layer Contracts

Defines strict contracts between each layer. No layer may bypass its contract.

---

## 1. Parser Contract

**Module:** `app/infra/vnedu_parser.py`

### Input

```python
parse_vnedu_file_with_class_summary(
    file_path: str,
    allow_kqgd: bool = True
) -> Tuple[List[Dict], List[Dict]]
```

### Output

```python
# subjects: List[Dict]
{
    "class_name": str,
    "academic_year": str,
    "subject": str,
    "subject_type": "scored" | "qualitative",
    "avg_score": float | None,
    "student_count": int,
    "T": int, "H": int, "C": int,
    "T_pct": float | None, "H_pct": float | None, "C_pct": float | None,
}

# class_summaries: List[Dict]
{
    "class_name": str,
    "academic_year": str,
    "HTXS": int, "HTT": int, "HT": int, "CHT": int,
    "total_students": int,
}
```

### Rules

- Pure I/O: reads Excel, returns dicts. No side effects.
- Must not raise fatal errors on partial data (downgrade gracefully).
- `allow_kqgd=False` → class_summaries must be empty list.
- Subject type is determined by Excel structure, not subject name.
- Single-column subjects → forced `qualitative`.
- Empty score column → downgraded to `qualitative`.
- KQGD: `HTXS + HTT + HT + CHT == total_students` or raise ValueError.

---

## 2. Adapter Contract

**Module:** `app/domain/adapters.py`

### Input

```python
ParserResultAdapter.convert_parser_output(
    subject_dicts: List[Dict],
    class_summary_dicts: List[Dict],
    snapshot_type: SnapshotType
) -> Tuple[List[SubjectSnapshot], List[ClassSummary]]
```

### Output

- `List[SubjectSnapshot]` — domain objects with injected snapshot_type
- `List[ClassSummary]` — domain objects with injected snapshot_type

### Rules

- Converts raw parser dicts → validated domain objects.
- Injects `snapshot_type` into each object.
- Subject name normalization happens here, not in parser.
- Must not modify parser dicts (read-only).

---

## 3. Domain Contract

**Module:** `app/domain/models.py`

### SubjectSnapshot

```python
@dataclass
class SubjectSnapshot:
    academic_year: str
    class_name: str
    subject: str
    snapshot_type: SnapshotType
    avg_score: Optional[float]
    student_count: int
    T: int
    H: int
    C: int
```

**Validation rules (`validate()`):**
- T, H, C >= 0
- T + H + C <= student_count
- avg_score in [0, 10] if provided

**`is_scored()` returns `True` if `avg_score is not None`.**

### ClassSummary

```python
@dataclass
class ClassSummary:
    academic_year: str
    class_name: str
    snapshot_type: SnapshotType
    HTXS: int
    HTT: int
    HT: int
    CHT: int
    total_students: int
```

### Rules

- Domain objects are immutable after creation.
- No I/O, no database access.
- `validate()` must be called before persistence.

---

## 4. Repository Contract

**Module:** `app/repositories/interfaces.py`, `sqlite_repository.py`

### Interface

```python
class SubjectSnapshotRepository(ABC):
    def upsert(self, snapshot: SubjectSnapshot) -> None
    def find_by_class(self, class_name: str, academic_year: str) -> List[SubjectSnapshot]

class ClassSummaryRepository(ABC):
    def upsert(self, summary: ClassSummary) -> None
    def find_by_class(self, class_name: str, academic_year: str) -> Optional[ClassSummary]
```

### Rules

- Save and query only. No business logic.
- Upsert by unique key: `(academic_year, class_name, subject, snapshot_type)`.
- Must not modify domain objects.
- Must not validate business rules (that's domain layer).

---

## 5. Use Case Contract

**Module:** `app/usecases/process_excel.py`

### Input

```python
ProcessExcelUseCase.execute(
    file_path: str,
    snapshot_type: SnapshotType,
    score_delta: Optional[float] = None
) -> ProcessResult
```

### Output

```python
@dataclass
class ProcessResult:
    success: bool
    errors: List[str]
    saved_subjects: int
    saved_class_summaries: int
```

### Rules

- Orchestrates: parse → validate → persist.
- `snapshot_type` determines KQGD parsing:
  - `baseline`, `actual_hk2` → `allow_kqgd=True`
  - `actual_hk1`, `target`, `commitment` → `allow_kqgd=False`, class_summaries cleared
- If `snapshot_type=baseline` + `score_delta` → generate targets.
- Errors collected in `ProcessResult.errors`, not raised.
- Must not modify parser or domain objects.

---

## 6. Database Contract

**Module:** `app/db/connection.py`

### Tables

| Table | Unique Key |
|-------|-----------|
| `subject_snapshots` | `(academic_year, class_name, subject, snapshot_type)` |
| `class_summary` | `(academic_year, class_name, snapshot_type)` |
| `teacher_commitments` | `(academic_year, class_name, subject)` |
| `student_achievements` | `(academic_year, category, level)` |

### Rules

- Connection managed via context manager: `with get_conn() as conn:`
- Schema auto-created on first use.
- No business logic in SQL.

---

## 7. KQGD Gating Rules

| `snapshot_type` | Parse KQGD? | class_summary? | Generate targets? |
|----------------|-------------|----------------|-------------------|
| `baseline` | Yes | Yes | If score_delta |
| `actual_hk1` | No | No | No |
| `actual_hk2` | Yes | Yes | No |
| `target` | No | No | No |
| `commitment` | No | No | No |

---

## 8. Cross-Layer Rules

- Parser output is raw dicts. Domain layer converts.
- Domain objects validate themselves. Use case layer handles errors.
- Repository is dumb storage. No queries with business logic.
- UI never talks to parser directly. Always through use case.
