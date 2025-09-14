import json
from geopy.distance import geodesic
import os

from gazetteer import load_gazetteer
from extractor import get_final_coordinates

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_FILE = os.path.join(SCRIPT_DIR, 'rta_texts.json')
RESULTS_FILE = os.path.join(SCRIPT_DIR, 'test_results.json')

def main():
    load_gazetteer()
    
    with open(TEST_DATA_FILE, 'r', encoding='utf-8') as f:
        test_data = json.load(f)['text_list']
        
    results = []
    total_error = 0.0

    print(f"{'ID':<3} | {'Text Snippet':<40} | {'Predicted Coords':<25} | {'Actual Coords':<25} | {'Error (m)':<10}")
    print("-" * 130)

    for i, item in enumerate(test_data):
        text = item['text']
        actual_coords = tuple(item['rta_coords'])
        
        predicted_coords = get_final_coordinates(text)
        
        error = geodesic(predicted_coords, actual_coords).meters
        total_error += error
        
        results.append({
            "id": i + 1,
            "predicted": predicted_coords,
            "actual": actual_coords,
            "error_meters": error
        })
        
        text_snippet = text.replace('\n', ' ')[:37] + '...'
        pred_str = f"{predicted_coords[0]:.6f}, {predicted_coords[1]:.6f}"
        act_str = f"{actual_coords[0]:.6f}, {actual_coords[1]:.6f}"
        print(f"{i+1:<3} | {text_snippet:<40} | {pred_str:<25} | {act_str:<25} | {error:<10.2f}")

    avg_error = total_error / len(test_data)
    print("-" * 130)
    print(f"\nAverage error: {avg_error:.2f} meters")
    
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump({"results": results, "average_error_meters": avg_error}, f, ensure_ascii=False, indent=2)
    print(f"Results saved to {RESULTS_FILE}")

if __name__ == "__main__":
    main()
