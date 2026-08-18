import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.engine import ScraperEngine
from src.utils.file_io import save_results_to_json

def load_keywords(filepath='config/keywords.txt'):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip()]
        return keywords
    except FileNotFoundError:
        print(f"Error: Keyword file not found at {filepath}")
        return []

if __name__ == "__main__":
    initial_keywords = load_keywords()
    if not initial_keywords:
        print("No keywords to process. Please add keywords in config/keywords.txt")
    else:
        engine = ScraperEngine()
        all_scraped_data = engine.run(initial_keywords, search_engines=['google', 'bing'])
        save_results_to_json(all_scraped_data)
