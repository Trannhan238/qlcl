from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.domain import ClassInfo, Metric, MetricSnapshot

class AbstractClassRepository(ABC):
    @abstractmethod
    def add(self, class_info: ClassInfo) -> None:
        pass

    @abstractmethod
    def get(self, class_id: str) -> Optional[ClassInfo]:
        pass

    @abstractmethod
    def get_all(self) -> List[ClassInfo]:
        pass

class AbstractMetricRepository(ABC):
    @abstractmethod
    def add(self, metric: Metric) -> None:
        pass

    @abstractmethod
    def get(self, metric_id: str) -> Optional[Metric]:
        pass

    @abstractmethod
    def get_all(self) -> List[Metric]:
        pass

class AbstractSnapshotRepository(ABC):
    @abstractmethod
    def add(self, snapshot: MetricSnapshot) -> None:
        pass

    @abstractmethod
    def get_by_class_and_metric(self, class_id: str, metric_id: str, academic_year: Optional[str] = None) -> List[MetricSnapshot]:
        pass

    @abstractmethod
    def get_all_for_class(self, class_id: str, academic_year: Optional[str] = None) -> List[MetricSnapshot]:
        pass
