# Long Tail Keywords Crawler and Scraper

This project implements a long-tail keyword crawler and scraper for search engines like Google and Bing. It is designed to extract keyword suggestions and search engine results pages (SERPs) data.

## Project Structure

```
/long-tail-keywords-crawler/
|- src/
|  |- crawlers/
|  |  |- base_crawler.py      # Abstract base class for crawlers
|  |  |- google_crawler.py    # Specific crawler for Google
|  |  |- bing_crawler.py      # Specific crawler for Bing
|  |- scrapers/
|  |  |- serp_scraper.py      # Class for parsing SERP HTML
|  |- core/
|  |  |- engine.py            # Main orchestration engine
|  |- utils/
|  |  |- file_io.py           # Utilities for file reading/writing
|  |  |- network.py           # Utilities for network management (HTTP requests, User-Agents)
|  |  |- selenium_driver.py   # Selenium WebDriver configuration and management
|  |- main.py                # Program entry point
|- config/
|  |- settings.yaml          # Configuration for search engines, delays, etc.
|  |- keywords.txt           # Initial keywords for crawling
|- data/
|  |- results.json           # Scraping results (automatically generated)
|- requirements.txt         # Project dependencies
|- README.md                # This documentation file
```

## Features

- **Suggestion Crawling:** Obtains long-tail keywords from Google and Bing autocomplete suggestions.
- **SERP Scraping:** Extracts title, URL, and description from search results.
- **Configurable:** Parameters like User-Agents, delays, and CSS selectors are configurable via `config/settings.yaml`.
- **Basic Robustness Handling:** Includes User-Agent rotation and random delays between requests to reduce the likelihood of being blocked.
- **Results Storage:** Saves extracted data in JSON format.

## Installation

1.  **Clone the repository:** (Skip if you already have the files locally)
    ```bash
    # git clone <REPOSITORY_URL>
    # cd long-tail-keywords-crawler
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Configure initial keywords:**
    Edit the `config/keywords.txt` file and add the keywords (one per line) you want to use as a starting point for suggestion extraction and scraping.

    Example `config/keywords.txt`:
    ```
    digital marketing
    SEO positioning
    SEO tools
    ```

2.  **Adjust configuration (optional):**
    Review and modify the `config/settings.yaml` file to adjust delays, add more User-Agents, or modify CSS selectors if search engines change their HTML structure.

3.  **Run the scraper:**
    ```bash
    python src/main.py
    ```

    The program will process the keywords, obtain suggestions, search the SERPs, and save the results in `data/results.json`.

## Development Notes

-   **Handling Blocks:** Although User-Agents and delays are implemented, search engines may detect and block scraping activity. Consider using proxies for a higher level of anonymity and request distribution.
-   **HTML Structure Changes:** CSS selectors in `config/settings.yaml` are critical. If Google or Bing update their design, you may need to adjust these selectors.
-   **Scalability:** For large-scale scraping, it is recommended to implement a queuing system (e.g., Celery with Redis/RabbitMQ) and a more sophisticated proxy manager.