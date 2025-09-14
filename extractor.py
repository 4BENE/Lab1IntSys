import statistics
from typing import List, Tuple

from structures import CoordinateCandidate
from gazetteer import gazetteer_streets, gazetteer_metro_stations, find_intersection, morph

INTERSECTION_KEYWORDS = {'пересечение', 'перекресток', 'перекрёсток'}

def analyze_text(text: str) -> List[CoordinateCandidate]:
    candidates = []
    lemmatized_text = " ".join([morph.parse(word)[0].normal_form for word in text.lower().split()])
    
    mentioned_streets = []
    for street_name in gazetteer_streets.keys():
        if street_name in lemmatized_text:
            mentioned_streets.append(gazetteer_streets[street_name])
        else:
            street_words = street_name.split()
            if len(street_words) >= 2:
                main_words = [w for w in street_words if w not in ['улица', 'проспект', 'переулок', 'набережная', 'бульвар', 'площадь']]
                if main_words and all(word in lemmatized_text for word in main_words):
                    mentioned_streets.append(gazetteer_streets[street_name])

    for i in range(len(mentioned_streets)):
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
