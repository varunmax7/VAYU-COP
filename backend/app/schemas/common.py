from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base for every API schema: camelCase JSON in/out, snake_case Python attributes."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class ProvenanceRead(CamelModel):
    source: str
    source_ts: datetime
    fused_ts: datetime
    confidence: float
    stale: bool
