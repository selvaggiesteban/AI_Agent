from duckduckgo_search import DDGS
import time
import random

class SearchEngine:
    def __init__(self, max_results=10):
        self.max_results = max_results

    def search(self, query):
        """
        Performs a search for the given query and returns a list of results.
        Each result is a dictionary with 'title', 'href', and 'body'.
        """
        print(f"[*] Searching for: '{query}'...")
        results = []
        try:
            # Retry logic
            for attempt in range(3):
                try:
                    ddgs = DDGS()
                    gen = ddgs.text(query, max_results=self.max_results)
                    results = list(gen)
                    if results:
                        break
                    print(f"   [!] Attempt {attempt+1} returned 0 results. Retrying...")
                    time.sleep(2 + random.random())
                except Exception as e:
                    print(f"   [!] Error on attempt {attempt+1}: {e}")
                    time.sleep(2)
                    
        except Exception as e:
            print(f"[!] Search failed completely: {e}")
        
        print(f"[*] Found {len(results)} results.")
        return results
