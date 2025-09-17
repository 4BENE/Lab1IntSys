import json
import pymorphy3
from typing import Dict, Optional, Tuple
from shapely.geometry import LineString
import os

from structures import MetroStation, Street

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GAZETTEER_FILE = os.path.join(SCRIPT_DIR, 'spb_gazetteer.json')


gazetteer_streets: Dict[str, Street] = {}
gazetteer_metro_stations: Dict[str, MetroStation] = {}
morph = pymorphy3.MorphAnalyzer()

def normalize_street_name(name: str) -> str:
    name = name.lower().strip()
    words = name.replace('ё', 'е').split()
    lemmatized_words = []
    for word in words:
        p = morph.parse(word)[0]
        if p.tag.POS not in ['PREP', 'CONJ', 'PRCL']:
            lemmatized_words.append(p.normal_form)
    return " ".join(lemmatized_words)

def load_gazetteer(filename: str = GAZETTEER_FILE):
    if not os.path.exists(filename):
        raise FileNotFoundError(
            f"Gazetteer file not found at {filename}. "
            "Please run builder.py first to create it."
        )
        
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for name, s in data.get("metro_stations", {}).items():
        station = MetroStation(s["name"], s["lat"], s["lon"])
        gazetteer_metro_stations[normalize_street_name(name)] = station
    for name, st in data.get("streets", {}).items():
        street = Street(st["name"], [(float(b), float(a)) for a, b in st["coordinates"]])
        gazetteer_streets[normalize_street_name(name)] = street

def find_street(query: str) -> Optional[Street]:
    normalized_query = normalize_street_name(query)
    return gazetteer_streets.get(normalized_query)

def find_metro_station(query: str) -> Optional[MetroStation]:
    normalized_query = normalize_street_name(query)
    return gazetteer_metro_stations.get(normalized_query)

def find_intersection(street1_name: str, street2_name: str) -> Optional[Tuple[float, float]]:
    s1 = find_street(street1_name)
    s2 = find_street(street2_name)
    if not s1 or not s2:
        return None
    
    line1 = LineString(s1.coordinates)
    line2 = LineString(s2.coordinates)
    
    if line1.intersects(line2):
        intersection = line1.intersection(line2)
        if not intersection.is_empty:
            if intersection.geom_type == 'Point':
                return (intersection.y, intersection.x)
            elif intersection.geom_type == 'MultiPoint':
                first_point = intersection.geoms[0]
                return (first_point.y, first_point.x)
    return None
