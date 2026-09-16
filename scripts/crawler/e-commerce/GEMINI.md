# Directory Overview

This directory contains the planning and technical details for an e-commerce pricing calculator and web scraping tool. The tool is designed to scrape product information from an online store, search for the same products on competitor websites (like MercadoLibre, Google Shopping, and Facebook Marketplace), and then suggest prices based on the collected data and configurable profit margins.

# Key Files

*   **`product-overview.md`**: This file provides a high-level summary of the project's goals and what the scraping tool is intended to achieve.
*   **`plan.md`**: This is the core technical document. It contains a complete Python script for the web scraping tool. The script is designed to:
    *   Scrape a specific Tienda Nube store.
    *   Search for products on MercadoLibre, Google, and Google Shopping using APIs.
    *   Normalize and expand product queries using synonyms for better search results.
    *   Calculate suggested retail prices based on competitor pricing and a configurable margin.
    *   Output the results to a CSV file and the console.
    The file also includes default configurations and instructions for setting up and running the script.
*   **`resume.md`**: This file is currently empty.

# Usage

The contents of this directory serve as a comprehensive plan and implementation guide for the e-commerce pricing tool. The Python script in `plan.md` can be used as the basis for the tool, and the other files provide context and a high-level overview of the project.
