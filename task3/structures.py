from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class MetroStation:
    name: str
    lat: float
    lon: float

@dataclass
class Street:
    name: str
    coordinates: List[Tuple[float, float]]

@dataclass
class GeographicMention:
    text: str
    normalized: str
    object_type: str
    position: int
    coordinates: Optional[Tuple[float, float]] = None

@dataclass
class SpatialRelation:
    relation_type: str
    objects: List[GeographicMention]
    keywords: List[str]
    coordinates: Optional[Tuple[float, float]] = None

@dataclass
class CoordinateCandidate:
    lat: float
    lon: float
    confidence: float
    source: str
    details: str
