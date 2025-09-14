import overpass
import json
from typing import Dict, Any
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, 'spb_gazetteer.json')


def get_spb_metro_stations(api: overpass.API) -> Dict[str, Any]:
    print("Fetching metro stations from OSM...")
    query = """
    area["name:ru"="Санкт-Петербург"]->.spb;
    (
      node["railway"="station"]["station"="subway"](area.spb);
      relation["railway"="station"]["station"="subway"](area.spb);
    );
    out center;
    """
    response = api.get(query, responseformat="json")
    stations = {}
    for element in response['elements']:
        if 'tags' in element and 'name' in element['tags']:
            name = element['tags']['name']
            if "станция метро" not in name.lower():
                 name = "станция метро " + name
            
            lat, lon = (element['lat'], element['lon']) if 'lat' in element else (element['center']['lat'], element['center']['lon'])
            
            stations[name] = {
                "name": name,
                "lat": lat,
                "lon": lon
            }
    print(f"Found {len(stations)} metro stations.")
    return stations

def get_spb_streets(api: overpass.API) -> Dict[str, Any]:
    print("Fetching streets from OSM... (this may take a while)")
    query = """
    area["name:ru"="Санкт-Петербург"]->.spb;
    (
      way["highway"]["name"](area.spb);
    );
    out geom;
    """
    response = api.get(query, responseformat="json")
    streets = {}
    for element in response['elements']:
        if 'tags' in element and 'name' in element['tags']:
            name = element['tags']['name']
            if 'geometry' in element and element['geometry']:
                coordinates = [(node['lat'], node['lon']) for node in element['geometry']]
                
                # Add street type if not present
                if not any(t in name.lower() for t in ['улица', 'проспект', 'шоссе', 'переулок', 'набережная', 'проезд']):
                     if 'highway' in element['tags']:
                         if element['tags']['highway'] in ['primary', 'secondary', 'tertiary', 'residential']:
                             name = "улица " + name

                if name in streets:
                    streets[name]['coordinates'].extend(coordinates)
                else:
                    streets[name] = {
                        "name": name,
                        "coordinates": coordinates
                    }
    print(f"Found {len(streets)} streets.")
    return streets

def build_gazetteer(output_file: str = OUTPUT_FILE):
    api = overpass.API(timeout=600)
    
    metro_stations = get_spb_metro_stations(api)
    streets = get_spb_streets(api)
    
    gazetteer = {
        "metro_stations": metro_stations,
        "streets": streets
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(gazetteer, f, ensure_ascii=False, indent=2)
    
    print(f"Gazetteer successfully built and saved to {output_file}")

if __name__ == '__main__':
    build_gazetteer()
