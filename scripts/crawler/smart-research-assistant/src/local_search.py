import os
import glob
from src.parsers import ParserFactory

class LocalSearch:
    def __init__(self, base_path):
        self.base_path = base_path
        self.documents = []
        # Supported extensions to scan
        self.supported_exts = [
            '*.json', '*.txt', '*.md', '*.pdf', 
            '*.docx', '*.xlsx', '*.pptx',
            '*.jpg', '*.jpeg', '*.png', 
            '*.mp3', '*.wav', '*.mp4'
        ]
        self.load_documents()

    def load_documents(self):
        """
        Recursively loads supported files from the base path.
        """
        if not os.path.exists(self.base_path):
            print(f"[!] Local path does not exist: {self.base_path}")
            return

        print(f"[*] Indexing local files in {self.base_path}...")
        
        found_files = []
        for ext in self.supported_exts:
            search_pattern = os.path.join(self.base_path, "**", ext)
            found_files.extend(glob.glob(search_pattern, recursive=True))
        
        print(f"[*] Found {len(found_files)} potential documents. Processing...")
        
        for fpath in found_files:
            try:
                content = ParserFactory.get_content(fpath)
                # Filter out empty or error-only content to avoid noise
                if content and len(content) > 10 and not content.startswith("[Error"):
                    self.documents.append({
                        'title': os.path.basename(fpath),
                        'url': fpath,
                        'text': content,
                        'source': 'local'
                    })
            except Exception as e:
                print(f"   [!] Skipped {os.path.basename(fpath)}: {e}")

    def search(self, query):
        """
        Simple keyword search in local documents.
        """
        query = query.lower()
        results = []
        
        print(f"[*] Searching local knowledge base for '{query}'...")
        
        for doc in self.documents:
            if query in doc['text'].lower() or query in doc['title'].lower():
                results.append({
                    'title': "[LOCAL] " + doc['title'],
                    'href': doc['url'],
                    'body': doc['text'][:500] + "...",
                    'full_text': doc['text'],
                    'source': 'local'
                })
        
        print(f"[*] Found {len(results)} local matches.")
        return results