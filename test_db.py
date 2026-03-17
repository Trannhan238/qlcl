import shutil
from pathlib import Path
from app.infra import database
from app.infra.repositories import ClassRepository, MetricRepository, SnapshotRepository
from app.models.domain import ClassInfo, Metric, MetricSnapshot

def test_db():
    # Setup test DB
    test_db_path = Path("test_sqms.db")
    if test_db_path.exists():
        test_db_path.unlink()
    
    database.set_db_path(test_db_path)
    database.init_db()
    print("Database initialized.")

    # Repositories
    class_repo = ClassRepository()
    metric_repo = MetricRepository()
    snapshot_repo = SnapshotRepository()

    # 1. Create Class
    c1 = ClassInfo(id="c1", grade="10", name="10A1")
    class_repo.add(c1)
    
    # 2. Create Metric
    m1 = Metric(id="m1", name="Math Score", description="Average Math Score")
    metric_repo.add(m1)

    # 3. Create Snapshots
    s1 = MetricSnapshot(id="s1", class_id="c1", metric_id="m1", snapshot_type="baseline", value=6.5)
    s2 = MetricSnapshot(id="s2", class_id="c1", metric_id="m1", snapshot_type="target", value=8.0)
    snapshot_repo.add(s1)
    snapshot_repo.add(s2)

    # 4. Verify Retrieval
    classes = class_repo.get_all()
    print(f"Classes: {classes}")
    assert len(classes) == 1
    assert classes[0].name == "10A1"

    metrics = metric_repo.get_all()
    print(f"Metrics: {metrics}")
    assert len(metrics) == 1

    snapshots = snapshot_repo.get_all_for_class("c1")
    print(f"Snapshots for c1: {snapshots}")
    assert len(snapshots) == 2

    print("All tests passed! Cleaning up...")
    if test_db_path.exists():
        test_db_path.unlink()

if __name__ == "__main__":
    test_db()
