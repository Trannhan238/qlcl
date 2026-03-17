import uuid
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ClassInfo:
    grade: str
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Metric:
    name: str
    description: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class MetricSnapshot:
    class_id: str
    metric_id: str
    snapshot_type: str  # baseline, commitment, target, actual_hk1, actual_hk2
    value: Optional[float]
    academic_year: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
