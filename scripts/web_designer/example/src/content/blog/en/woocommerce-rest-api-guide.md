---
title: "WooCommerce REST API Guide"
description: "Learn how to automate your WooCommerce store synchronization via REST API: creating and updating products, prices, stock, orders, and image uploads with real cURL examples."
pubDate: 2026-06-26
heroImage: "/assets/blog/covers/woocommerce-rest-api-guide.svg"
seoTitle: "WooCommerce REST API Guide | Products, orders, stock & images"
seoDescription: "Complete technical documentation for WooCommerce REST API v3. cURL examples for creating and updating products, managing stock, receiving orders, and uploading images automatically."
permalink: "/blog/guia-api-woocommerce"
altTexts: ["API keys in WooCommerce settings panel", "Products endpoint with cURL", "Order webhook in WooCommerce", "Image upload via REST API"]
---
*   WooCommerce REST API v3 lets you fully automate product, price, stock, order, and image management via standard HTTP requests.
*   To authenticate, generate API keys in WooCommerce > Settings > Advanced > REST API with Read/Write permissions.
*   Use webhooks for real-time order notifications and the `/products/batch` endpoint for bulk updates from your ERP.

## Prerequisites and authentication

Generate your API keys in the WordPress panel: **WooCommerce > Settings > Advanced > REST API**. Create a key with Read/Write permissions.

For production (under HTTPS), use standard basic authentication by sending the credentials in the `Authorization` header encoded in Base64, or pass `ck_` and `cs_` parameters in the URL if your server has header reading restrictions.

## 1. Creating and updating products, prices, and stock

The main endpoint for simple products is `/wp-json/wc/v3/products`.

### A. Create a new product

To create a product with managed stock and price, send a **POST** request.

```
POST https://your-site.com/wp-json/wc/v3/products
```

```bash
curl -X POST https://your-site.com/wp-json/wc/v3/products \
  -u ck_your_consumer_key:cs_your_consumer_secret \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Pro Notebook",
    "type": "simple",
    "regular_price": "1250.00",
    "description": "Excellent high-performance equipment.",
    "short_description": "Notebook for heavy work.",
    "manage_stock": true,
    "stock_quantity": 15,
    "sku": "NB-PRO-001"
  }'
```

The response returns a JSON object with the `id` field (e.g., `1234`), which you'll need for future updates.

### B. Update price and stock

To update an existing product, use its ID with the **PUT** method. You only need to send the fields that change.

```
PUT https://your-site.com/wp-json/wc/v3/products/1234
```

```bash
curl -X PUT https://your-site.com/wp-json/wc/v3/products/1234 \
  -u ck_your_consumer_key:cs_your_consumer_secret \
  -H "Content-Type: application/json" \
  -d '{
    "regular_price": "1300.00",
    "stock_quantity": 12
  }'
```

### C. Batch updates

For updating stock or prices across many products at once, use the batch endpoint (`/products/batch`) to avoid overwhelming the server. Supports up to 100 items per request.

```
POST https://your-site.com/wp-json/wc/v3/products/batch
```

```bash
curl -X POST https://your-site.com/wp-json/wc/v3/products/batch \
  -u ck_your_consumer_key:cs_your_consumer_secret \
  -H "Content-Type: application/json" \
  -d '{
    "update": [
      {
        "id": 1234,
        "regular_price": "1350.00",
        "stock_quantity": 10
      },
      {
        "id": 1235,
        "stock_quantity": 5
      }
    ]
  }'
```

## 2. Receiving orders automatically

There are two main strategies for integrating orders into your system.

### Strategy A: Webhooks (recommended — real-time)

WooCommerce can notify your server immediately when an event occurs. Go to **WooCommerce > Settings > Advanced > Webhooks** and add a new one with:

- **Action/Event:** Order created (or `woocommerce_payment_complete`)
- **Delivery URL:** `https://api.your-system.com/order-webhook`

Your server will receive a POST with the complete order structure in JSON every time a customer completes a purchase.

### Strategy B: API polling

If you prefer to periodically download orders (e.g., every 15 minutes), send a GET request filtered by status or date.

```
GET https://your-site.com/wp-json/wc/v3/orders?status=processing
```

```bash
curl -X GET "https://your-site.com/wp-json/wc/v3/orders?status=processing&per_page=20" \
  -u ck_your_consumer_key:cs_your_consumer_secret \
  -H "Content-Type: application/json"
```

Key structure you'll receive for processing in your ERP:

```json
[
  {
    "id": 9876,
    "status": "processing",
    "total": "2700.00",
    "billing": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@email.com"
    },
    "line_items": [
      {
        "id": 45,
        "name": "Test Pro Notebook",
        "product_id": 1234,
        "quantity": 2,
        "sku": "NB-PRO-001",
        "price": "1350.00"
      }
    ]
  }
]
```

## 3. Uploading images automatically

The WooCommerce API does not handle direct binary uploads in the products endpoint. You have two functional alternatives.

### Method 1: Public URL (simplest and fastest)

If your images are already hosted on an external server, CDN, or cloud system, pass the direct URL in the `images` array. WooCommerce will download the photo, process thumbnails, and save it to the media library.

```bash
curl -X PUT https://your-site.com/wp-json/wc/v3/products/1234 \
  -u ck_your_consumer_key:cs_your_consumer_secret \
  -H "Content-Type: application/json" \
  -d '{
    "images": [
      {
        "src": "https://images-your-erp.com/products/NB-PRO-001.jpg",
        "name": "Main View Notebook Pro",
        "position": 0
      },
      {
        "src": "https://images-your-erp.com/products/NB-PRO-001-side.jpg",
        "name": "Side View",
        "position": 1
      }
    ]
  }'
```

### Method 2: Upload local file to WordPress Media API

If images are stored locally without a public URL, upload them first to the WordPress media endpoint (`/wp/v2/media`).

**Upload the image to the library:**

```bash
curl -X POST https://your-site.com/wp-json/wp/v2/media \
  -u ck_your_consumer_key:cs_your_consumer_secret \
  -H "Content-Disposition: attachment; filename=notebook.jpg" \
  -H "Content-Type: image/jpeg" \
  --data-binary "@./local/path/to/photo.jpg"
```

The response returns a JSON with the `id` field (e.g., `5566`). Then associate that ID with the product:

```bash
curl -X PUT https://your-site.com/wp-json/wc/v3/products/1234 \
  -u ck_your_consumer_key:cs_your_consumer_secret \
  -H "Content-Type: application/json" \
  -d '{
    "images": [
      {
        "id": 5566
      }
    ]
  }'
```

With these tested endpoints and examples, you can integrate WooCommerce with any external system in a robust and automated way.
