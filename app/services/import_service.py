import os
from typing import Dict, List, Any
from app.infra.excel_parser import read_raw_excel, detect_tables, extract_table, map_to_metric_key
from app.core.ports import AbstractSnapshotRepository, AbstractClassRepository, AbstractMetricRepository
from app.models.domain import MetricSnapshot, ClassInfo, Metric

class ImportService:
    def __init__(
        self,
        class_repo: AbstractClassRepository,
        metric_repo: AbstractMetricRepository,
        snapshot_repo: AbstractSnapshotRepository
    ):
        self.class_repo = class_repo
        self.metric_repo = metric_repo
        self.snapshot_repo = snapshot_repo
        
    def import_excel(self, file_path: str, snapshot_type: str) -> Dict[str, Any]:
        """
        Reads excel, detects tables, extracts metrics, models, and saves snapshots.
        Returns a summary of the import.
        """
        raw_data = read_raw_excel(file_path)
        stats = {"classes_processed": 0, "snapshots_saved": 0}
        
        for sheet_name, df in raw_data.items():
            class_name = str(sheet_name).strip()
            
            # Find or create Class
            class_info = None
            for c in self.class_repo.get_all():
                if c.name == class_name:
                    class_info = c
                    break
                    
            if not class_info:
                class_info = ClassInfo(grade="unknown", name=class_name)
                self.class_repo.add(class_info)
                
            stats["classes_processed"] += 1
            
            # Detect tables and parse data
            tables = detect_tables(df)
            
            metric_averages = {}
            metric_counts = {}
            
            for table_info in tables:
                extracted = extract_table(df, table_info)
                
                # Aggregate rows. The system works with aggregated metrics per class.
                for row in extracted:
                    m_key = map_to_metric_key(row["metric_name"])
                    if not m_key:
                        continue
                        
                    val = row["value"]
                    
                    # Transform standard descriptive strings to numeric values
                    if isinstance(val, str):
                        v_str = val.strip().lower()
                        if v_str in ["htxs", "htt", "ht"]:
                            val = 1.0
                        elif v_str == "cht":
                            val = 0.0
                        else:
                            try:
                                val = float(val)
                            except ValueError:
                                continue # Unable to parse
                    
                    if isinstance(val, (int, float)):
                        if m_key not in metric_averages:
                            metric_averages[m_key] = 0.0
                            metric_counts[m_key] = 0
                        metric_averages[m_key] += float(val)
                        metric_counts[m_key] += 1
                        
            # Save aggregated snapshots
            for m_key in metric_averages:
                if metric_counts[m_key] > 0:
                    avg_val = metric_averages[m_key] / metric_counts[m_key]
                    
                    # Ensure metric exists
                    metric = self.metric_repo.get(m_key)
                    if not metric:
                        # Assuming metric id == key
                        metric = Metric(name=m_key, description=f"Imported metric: {m_key}")
                        metric.id = m_key
                        self.metric_repo.add(metric)
                        
                    snapshot = MetricSnapshot(
                        class_id=class_info.id,
                        metric_id=metric.id,
                        snapshot_type=snapshot_type,
                        value=avg_val
                    )
                    self.snapshot_repo.add(snapshot)
                    stats["snapshots_saved"] += 1
                    
        return stats
