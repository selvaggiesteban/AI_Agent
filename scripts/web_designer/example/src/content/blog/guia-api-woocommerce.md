---
title: "Guía de API de WooCommerce"
description: "Aprende a automatizar la sincronización de tu tienda WooCommerce vía API REST: alta y modificación de productos, precios, stock, pedidos y carga de imágenes con ejemplos reales en cURL."
pubDate: 2026-06-26
heroImage: "/assets/blog/covers/guia-api-woocommerce.svg"
seoTitle: "Guía de API REST de WooCommerce | Productos, pedidos, stock e imágenes"
seoDescription: "Documentación técnica completa de la API REST de WooCommerce v3. Ejemplos de cURL para crear y modificar productos, gestionar stock, recibir pedidos y subir fotos automáticamente."
permalink: "/blog/guia-api-woocommerce"
altTexts: ["Claves API en panel de WooCommerce", "Endpoint de productos con cURL", "Webhook de pedidos en WooCommerce", "Carga de imágenes por API REST"]
---
*   La API REST de WooCommerce v3 permite automatizar la gestión completa de productos, precios, stock, pedidos e imágenes mediante peticiones HTTP estándar.
*   Para autenticarte necesitas generar claves de API en WooCommerce > Ajustes > Avanzado > REST API, con permisos de Lectura y Escritura.
*   Se recomienda usar webhooks para recibir pedidos en tiempo real y el endpoint `/products/batch` para actualizaciones masivas desde tu ERP.

## Requisitos previos y autenticación

Debes generar las claves de la API en tu panel de WordPress: **WooCommerce > Ajustes > Avanzado > REST API**. Crea una clave con permisos de Lectura y Escritura.

Para producción (bajo HTTPS), se utiliza autenticación básica estándar enviando las credenciales en el encabezado `Authorization` codificadas en Base64, o pasando los parámetros `ck_` y `cs_` por la URL si tu servidor tiene restricciones de lectura de cabeceras.

## 1. Dar de alta y modificar artículos, precios y stock

El endpoint principal para productos simples es `/wp-json/wc/v3/products`.

### A. Crear un producto nuevo (alta)

Para crear un producto con stock administrado y precio, envía una petición **POST**.

```
POST https://tu-sitio.com/wp-json/wc/v3/products
```

```bash
curl -X POST https://tu-sitio.com/wp-json/wc/v3/products \
  -u ck_tu_consumer_key:cs_tu_consumer_secret \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Notebook Pro de Prueba",
    "type": "simple",
    "regular_price": "1250.00",
    "description": "Excelente equipo de alto rendimiento.",
    "short_description": "Notebook para trabajo pesado.",
    "manage_stock": true,
    "stock_quantity": 15,
    "sku": "NB-PRO-001"
  }'
```

La respuesta devuelve un JSON con el campo `id` (ej: `1234`), que necesitarás para modificarlo en el futuro.

### B. Modificar precio y stock (actualización)

Para actualizar un artículo existente, usa su ID con el método **PUT**. Solo necesitas enviar los campos que cambian.

```
PUT https://tu-sitio.com/wp-json/wc/v3/products/1234
```

```bash
curl -X PUT https://tu-sitio.com/wp-json/wc/v3/products/1234 \
  -u ck_tu_consumer_key:cs_tu_consumer_secret \
  -H "Content-Type: application/json" \
  -d '{
    "regular_price": "1300.00",
    "stock_quantity": 12
  }'
```

### C. Actualizaciones masivas (batch update)

Si necesitas actualizar el stock o los precios de muchos productos a la vez, usa el endpoint de lote (`/products/batch`) para evitar sobrecargar el servidor. Permite hasta 100 artículos por petición.

```
POST https://tu-sitio.com/wp-json/wc/v3/products/batch
```

```bash
curl -X POST https://tu-sitio.com/wp-json/wc/v3/products/batch \
  -u ck_tu_consumer_key:cs_tu_consumer_secret \
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

## 2. Cómo recibir pedidos de forma automatizada

Existen dos estrategias principales para integrar los pedidos a tu sistema.

### Estrategia A: Webhooks (recomendada — tiempo real)

WooCommerce puede notificar a tu servidor inmediatamente cuando ocurra un evento. Ve a **WooCommerce > Ajustes > Avanzado > Webhooks** y añade uno nuevo con:

- **Acción/Evento:** Pedido creado (o `woocommerce_payment_complete`)
- **URL de entrega:** `https://api.tu-sistema.com/webhook-pedidos`

Tu sistema recibirá un POST con la estructura completa del pedido en JSON cada vez que un cliente finalice una compra.

### Estrategia B: Consulta por API (polling)

Si prefieres descargar periódicamente los pedidos (ej. cada 15 minutos), realiza un GET filtrando por estado o fecha.

```
GET https://tu-sitio.com/wp-json/wc/v3/orders?status=processing
```

```bash
curl -X GET "https://tu-sitio.com/wp-json/wc/v3/orders?status=processing&per_page=20" \
  -u ck_tu_consumer_key:cs_tu_consumer_secret \
  -H "Content-Type: application/json"
```

Estructura clave que recibirás para procesar en tu ERP:

```json
[
  {
    "id": 9876,
    "status": "processing",
    "total": "2700.00",
    "billing": {
      "first_name": "Juan",
      "last_name": "Pérez",
      "email": "juan@email.com"
    },
    "line_items": [
      {
        "id": 45,
        "name": "Notebook Pro de Prueba",
        "product_id": 1234,
        "quantity": 2,
        "sku": "NB-PRO-001",
        "price": "1350.00"
      }
    ]
  }
]
```

## 3. Cómo subir fotos de forma automatizada

La API de WooCommerce no procesa cargas binarias directas en el endpoint de productos. Tienes dos alternativas funcionales.

### Método 1: URL pública (más sencillo y rápido)

Si las imágenes ya están alojadas en un servidor externo, CDN o sistema en la nube, pasa la URL directa en el array `images`. WooCommerce descargará la foto, procesará las miniaturas y la guardará en la biblioteca multimedia.

```bash
curl -X PUT https://tu-sitio.com/wp-json/wc/v3/products/1234 \
  -u ck_tu_consumer_key:cs_tu_consumer_secret \
  -H "Content-Type: application/json" \
  -d '{
    "images": [
      {
        "src": "https://imagenes-tu-erp.com/articulos/NB-PRO-001.jpg",
        "name": "Vista Principal Notebook Pro",
        "position": 0
      },
      {
        "src": "https://imagenes-tu-erp.com/articulos/NB-PRO-001-lateral.jpg",
        "name": "Vista Lateral",
        "position": 1
      }
    ]
  }'
```

### Método 2: Subir el archivo local a la API de Medios de WordPress

Si las imágenes están guardadas localmente y no disponen de URL pública, subelas primero al endpoint de medios de WordPress (`/wp/v2/media`).

**Subir la imagen a la biblioteca:**

```bash
curl -X POST https://tu-sitio.com/wp-json/wp/v2/media \
  -u ck_tu_consumer_key:cs_tu_consumer_secret \
  -H "Content-Disposition: attachment; filename=notebook.jpg" \
  -H "Content-Type: image/jpeg" \
  --data-binary "@./ruta/local/de/la/foto.jpg"
```

La respuesta devuelve un JSON con el campo `id` (ej: `5566`). Luego asocia ese ID al producto:

```bash
curl -X PUT https://tu-sitio.com/wp-json/wc/v3/products/1234 \
  -u ck_tu_consumer_key:cs_tu_consumer_secret \
  -H "Content-Type: application/json" \
  -d '{
    "images": [
      {
        "id": 5566
      }
    ]
  }'
```

Con estos endpoints y ejemplos probados podés integrar WooCommerce con cualquier sistema externo de forma robusta y automatizada.
