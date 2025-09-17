import re
import statistics
from typing import List, Tuple

from structures import CoordinateCandidate
from gazetteer import (
    gazetteer_metro_stations,
    find_intersection,
    morph,
    find_street,
)

INTERSECTION_KEYWORDS = {"пересечение", "перекресток", "перекрёсток"}


def analyze_text(text: str) -> List[CoordinateCandidate]:
    candidates = []
    clean_text = re.sub(r"[^\w\s]", "", text.lower())
    lemmatized_text = " ".join(
        [morph.parse(word)[0].normal_form for word in clean_text.split()]
    )
    tokens = clean_text.split()

    mentioned_streets = []
    mentioned_streets_set = set()

    for i in range(len(tokens)):
        for j in range(i, len(tokens)):
            if j - i > 5:
                continue

            query = " ".join(tokens[i : j + 1])
            street = find_street(query)

            if street and street.name not in mentioned_streets_set:
                mentioned_streets.append(street)
                mentioned_streets_set.add(street.name)

    for i in range(len(mentioned_streets)):
        s = mentioned_streets[i]
        (lon, lat) = s.coordinates[len(s.coordinates) // 2]
        candidates.append(
            CoordinateCandidate(
                lat=lat,
                lon=lon,
                confidence=0.5,
                source="street_center",
                details=f"Центр {s.name}",
            )
        )
        for j in range(i + 1, len(mentioned_streets)):
            s1 = mentioned_streets[i]
            s2 = mentioned_streets[j]
            
            for keyword in INTERSECTION_KEYWORDS:
                if keyword in lemmatized_text:
                    intersection_coords = find_intersection(s1.name, s2.name)
                    if intersection_coords:
                        candidates.append(CoordinateCandidate(
                            lat=intersection_coords[0],
                            lon=intersection_coords[1],
                            confidence=0.9,
                            source='intersection',
                            details=f"Пересечение {s1.name} и {s2.name}"
                        ))

    mentioned_metros = []
    for station_name in gazetteer_metro_stations.keys():
        if station_name in lemmatized_text:
            mentioned_metros.append(gazetteer_metro_stations[station_name])

    for station in mentioned_metros:
        candidates.append(CoordinateCandidate(
            lat=station.lat,
            lon=station.lon,
            confidence=0.7,
            source='metro',
            details=f"Станция метро {station.name}"
        ))

    return candidates

def get_final_coordinates(text: str) -> Tuple[float, float]:
    candidates = analyze_text(text)
    
    if not candidates:
        return (59.9311, 30.3609) 

    if len(candidates) > 1:
        lat = statistics.mean(c.lat for c in candidates)
        lon = statistics.mean(c.lon for c in candidates)
        return (lat, lon)
    
    return (candidates[0].lat, candidates[0].lon)
