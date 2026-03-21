# Roadmap

## Phase 1 — Data Pipeline (DONE)

- [x] Dynamic header detection (`_detect_header_layout`, no hardcoded indices)
- [x] Dynamic column detection from Excel headers
- [x] Region-based parsing (Subjects vs KQGD)
- [x] Stable KQGD parsing across all grades
- [x] Multi-grade support (grades 1→5)
- [x] Adapter layer (parser dict → domain objects)
- [x] Subject normalization layer (`app/domain/normalizers.py`)
- [x] Separation of parsing vs business logic
- [x] Repository pattern (SQLite)
- [x] Use case orchestration
- [x] KQGD gating by snapshot_type
- [x] Pure function refactoring (no shared state)
- [x] Defensive parsing (empty scores, Wingdings ticks, float STT)
- [x] Domain model cleanup (remove name heuristics)
- [x] XLS loading with pywin32 fallback
- [x] Debug cleanup (logging module, no file writes)

---

## Phase 2 — Business Logic

### Comparison Engine

- [ ] Compare baseline vs HK1 vs HK2 per subject
- [ ] Compute delta: actual - baseline
- [ ] Flag subjects below target
- [ ] Aggregate by grade level (all classes in khối X)

### Target Generation

- [ ] Generate targets from baseline + score_delta
- [ ] Validate targets (avg_score + delta <= 10)
- [ ] Support per-subject delta (not just global)

### Progress Tracking

- [ ] Class progress: HK2 vs baseline
- [ ] School progress: aggregate all classes
- [ ] Trend: multiple years

---

## Phase 3 — Presentation

### Dashboard (Streamlit)

- [ ] Overview tab: school-level metrics
- [ ] Class tab: per-class subject breakdown
- [ ] Comparison tab: baseline vs actual vs target
- [ ] KQGD tab: HTXS/HTT/HT/CHT distribution

### Charts

- [ ] Bar chart: subject avg_score by class
- [ ] Radar chart: multi-subject comparison
- [ ] Line chart: progress over time
- [ ] Pie chart: KQGD distribution

### Export

- [ ] Export to Excel (.xlsx)
- [ ] Export charts as images
- [ ] Print-friendly reports

---

## Phase 4 — System

### Database Migration

- [ ] Migrate SQLite → MySQL for multi-user
- [ ] Add connection pooling
- [ ] Add migration scripts

### API Layer

- [ ] Add FastAPI endpoints
- [ ] REST API for CRUD operations
- [ ] Authentication (optional)

### MQTT (Optional)

- [ ] Real-time notifications on data upload
- [ ] Dashboard auto-refresh

---

## Phase 5 — Quality

### Testing

- [ ] Unit tests for parser functions
- [ ] Integration tests for parse → persist pipeline
- [ ] Property-based tests for normalization

### CI/CD

- [ ] GitHub Actions for lint + test
- [ ] Pre-commit hooks (ruff, black)
- [ ] Coverage reporting

### Documentation

- [ ] API documentation (FastAPI auto-docs)
- [ ] User guide for Streamlit UI
- [ ] Deployment guide
