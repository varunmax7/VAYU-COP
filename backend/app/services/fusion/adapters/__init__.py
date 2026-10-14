from app.services.fusion.adapters.airspace_notam import AirspaceNotamAdapter
from app.services.fusion.adapters.base import SourceAdapter, SourceHealth
from app.services.fusion.adapters.crew_roster import CrewRosterAdapter
from app.services.fusion.adapters.maint_mis import MaintMisAdapter
from app.services.fusion.adapters.met_feed import MetFeedAdapter
from app.services.fusion.adapters.stores_inv import StoresInvAdapter
from app.services.fusion.adapters.tasking import TaskingAdapter
from app.services.fusion.adapters.threat_intel_a import ThreatIntelAAdapter
from app.services.fusion.adapters.threat_intel_b import ThreatIntelBAdapter
from app.services.fusion.adapters.track_feed import TrackFeedAdapter

ALL_ADAPTER_CLASSES: list[type[SourceAdapter]] = [
    MaintMisAdapter,
    CrewRosterAdapter,
    StoresInvAdapter,
    MetFeedAdapter,
    AirspaceNotamAdapter,
    ThreatIntelAAdapter,
    ThreatIntelBAdapter,
    TrackFeedAdapter,
    TaskingAdapter,
]

__all__ = [
    "SourceAdapter",
    "SourceHealth",
    "ALL_ADAPTER_CLASSES",
    "MaintMisAdapter",
    "CrewRosterAdapter",
    "StoresInvAdapter",
    "MetFeedAdapter",
    "AirspaceNotamAdapter",
    "ThreatIntelAAdapter",
    "ThreatIntelBAdapter",
    "TrackFeedAdapter",
    "TaskingAdapter",
]
