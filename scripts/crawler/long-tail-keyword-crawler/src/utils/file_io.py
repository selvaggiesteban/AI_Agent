import json

def save_results_to_json(data, filepath='data/results.json'):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Results successfully saved to {filepath}")
    except IOError as e:
        print(f"Error saving results to {filepath}: {e}")