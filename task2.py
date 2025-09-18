import requests

def find_street_intersection(street1, street2):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    area["name"="Санкт-Петербург"]->.spb;
    (
        way(area.spb)["name"="{street1}"];
        way(area.spb)["name"="{street2}"];
    );
    (._;>;);
    out;
    """

    response = requests.post(overpass_url, data=query)
    response.raise_for_status()
    data = response.json()

    street1_nodes = set()
    street2_nodes = set()

    for element in data['elements']:
        if element['type'] == 'way':
            if 'tags' in element and element['tags'].get('name') == street1:
                street1_nodes.update(element.get('nodes', []))
            elif 'tags' in element and element['tags'].get('name') == street2:
                street2_nodes.update(element.get('nodes', []))

    common_nodes = street1_nodes & street2_nodes
    intersections = set()

    for element in data['elements']:
        if element['type'] == 'node' and element['id'] in common_nodes:
            lat = element['lat']
            lon = element['lon']
            intersections.add((lat, lon))

    return intersections


if __name__ == "__main__":
    street1 = input("Введите название первой улицы: ")
    street2 = input("Введите название второй улицы: ")

    intersections = find_street_intersection(street1, street2)

    if intersections:
        print("Точки пересечения найдены:")
        for point in intersections:
            print(f"({point[0]}, {point[1]})")
    else:
        print("Пересечений не найдено")