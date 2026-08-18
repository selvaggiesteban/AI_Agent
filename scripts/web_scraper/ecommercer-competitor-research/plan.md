Below is a Python script (1 file) that:

Scrapes your Tienda Nube store (I detected that the pagination is https://lanuscomputacion.mitiendanube.com/productos/page/2/ and that there are 8 pages: "1 / 8" appears at the bottom of the list).

For each product, it generates alternative queries (literal name + normalizations + configurable synonyms).

It searches for competitors and prices on:

MercadoLibre (Official API)

Google (Official Custom Search JSON API)

Google Shopping (via third-party API like SerpApi)

Facebook Marketplace: I'm leaving an optional "adapter" because there is no simple public endpoint for competitive scraping; if you have approved access to Meta/Content Library tools, you could integrate it from there.

Legal/ToS note (important): I do not recommend scraping HTML from Google/Shopping/Facebook (captcha/anti-bot/ToS). The script uses APIs (official or third-party) to keep it cleaner and more stable.

Output (list format)

It generates an output.csv and also prints lines to the console like this:

{product name}, {competitor name}, {price}, {url}, {suggested price with applied margin}

The script is the same as the one in `ecommerce_competitor_research.py`.