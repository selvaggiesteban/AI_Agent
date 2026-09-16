# E-commerce Competitor Research Tool

This Python script scrapes product information from a Tienda Nube online store, searches for the same products on competitor websites (MercadoLibre, Google Shopping), and suggests prices based on the collected data and configurable profit margins.

## Features

- Scrapes a specified Tienda Nube store.
- Searches for products on MercadoLibre, Google, and Google Shopping using APIs.
- Normalizes and expands product queries using synonyms for better search results.
- Calculates suggested retail prices based on competitor pricing and a configurable margin.
- Outputs the results to a CSV file and the console.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd ecommerce-competitor-research
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure the script:**
    - The first time you run the script, it will create a `config.yaml` file.
    - Edit `config.yaml` to set up your store's URL, API keys for the search sources, and pricing rules.
    - A `synonyms.json` file will also be created with examples. You can customize this file to improve search results for your specific products.

## Usage

Run the script from your terminal:

```bash
python ecommerce_competitor_research.py
```

The script will:
1.  Scrape the products from the configured Tienda Nube store.
2.  Search for each product on the enabled competitor sources.
3.  Generate an `output.csv` file with the findings.
4.  Print a summary to the console.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
