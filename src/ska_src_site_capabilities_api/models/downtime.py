from typing import Optional, List

from pydantic import Field, BaseModel


class Downtime(BaseModel):
    downtime_from: str = Field(..., examples=["2025-01-11T11:00:00Z"])
    downtime_to: str = Field(..., examples=["2025-01-11T16:00:00Z"])
    downtime_reason: str = Field(..., examples=["Hypervisor fault"])
    downtime_type: str = Field(..., examples=["Unplanned"])

class DowntimeMetric(BaseModel):
    event_type: str = Field(..., examples=["compute_downtime"])
    node_name: str = Field(..., examples=["node-03"])
    site_name: str = Field(..., examples=["SWENODEA"])
    compute_id: Optional[str] = Field(..., examples=["compute-225"])
    service_name: Optional[str] = Field(..., examples=["service-123"])
    service_type: Optional[str] = Field(..., examples=["container"])
    storage_id: Optional[str] = Field(..., examples=["storage-456"])
    storage_area_id: Optional[str] = Field(..., examples=["storage-area-789"])
    storage_area_name: Optional[str] = Field(..., examples=["storage-area-789"])
    storage_area_type: Optional[str] = Field(..., examples=["SSD"])
    storage_area_tier: Optional[str] = Field(..., examples=["1"])
    in_downtime: bool = Field(..., examples=[False])
    downtimes: List[Downtime] = Field(..., examples=[
        [
            {
                "downtime_from": "2025-01-11T11:00:00Z",
                "downtime_to": "2025-01-11T16:00:00Z",
                "downtime_reason": "Hypervisor fault",
                "downtime_type": "Unplanned"
            }
        ]
    ])