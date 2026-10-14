"""Import every model so Base.metadata is fully populated for Alembic autogenerate
and for app.core.db.Base.metadata.create_all() (used by the SQLite dev fallback)."""

from app.models.aircraft import Aircraft
from app.models.aircraft_type import AircraftType
from app.models.airspace import Airspace
from app.models.alert import Alert
from app.models.audit import AuditEntry
from app.models.base import AirBase
from app.models.crew import CrewMember
from app.models.event import Event
from app.models.mission import Mission
from app.models.plan import Assignment, Plan, UnassignedMission
from app.models.stores import StoreInventory
from app.models.threat import ThreatZone
from app.models.user import User
from app.models.weather import WeatherCell, WeatherObs

__all__ = [
    "Aircraft",
    "AircraftType",
    "Airspace",
    "Alert",
    "AuditEntry",
    "AirBase",
    "CrewMember",
    "Event",
    "Mission",
    "Plan",
    "Assignment",
    "UnassignedMission",
    "StoreInventory",
    "ThreatZone",
    "User",
    "WeatherCell",
    "WeatherObs",
]
