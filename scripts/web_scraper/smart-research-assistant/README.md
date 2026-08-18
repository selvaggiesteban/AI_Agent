# Smart Research Assistant

A clean, modular Python tool that automates web research. It searches for a given term, scrapes the top results, summarizes the content using NLP (LSA), and generates a consolidated PDF report.

## Features

- **Automated Search:** Uses DuckDuckGo for privacy-friendly searching.
- **Web Scraping:** Extracts clean text from webpages.
- **Summarization:** Uses `sumy` (LSA) to extract key insights from long articles.
- **PDF Reporting:** Generates a professional-looking PDF with links and summaries.
- **Monorepo Structure:** Clean architecture ready for GitHub.

## Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) First run might download NLTK tokenizers automatically.

## Usage

Run the main script:

```bash
python main.py
```

Enter your search term when prompted (e.g., "system prompt leak"). The tool will generate a PDF report in the root directory.

## Project Structure

```
smart-research-assistant/
├── src/
│   ├── search_engine.py  # Search logic
│   ├── scraper.py        # Web scraping logic
│   ├── analyzer.py       # NLP summarization
│   └── pdf_generator.py  # PDF creation
├── main.py               # Entry point
├── requirements.txt      # Dependencies
└── README.md             # Documentation
```

## License

MIT
