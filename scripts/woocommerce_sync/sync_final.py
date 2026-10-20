import requests
import pandas as pd
import time
import json
import os

# --- CONFIGURACIÓN ---
CONFIG = {
    "MASTER_FILE": "/mnt/c/Users/Esteban Selvaggi/Desktop/AI_Agent/docs/tay.com.ar, decotay.com.ar/_TAY - Base de Familia.csv",
    "STORES": {
        "retail": {
            "name": "Decotay Minoristas",
            "url": "https://decotay.com.ar",
            "ck": "ck_e5b2cbf086ea5705b5c6f789b88fce85a5010196",
            "cs": "cs_13d216beeaf3e75fad64210c72fa327235a6bf77",
        },
        "wholesale": {
            "name": "Tay Mayoristas",
            "url": "https://tay.com.ar",
            "ck": "ck_588f508b47d417c5e43a2247c0f724a3eaf3938a",
            "cs": "cs_1a51b1ff7b0bd7e5481bdd2dce6cf74e1fa98f33",
        }
    },
    "API_MAPPING": {
        "Nombre/titulo": "name",
        "descripcion corta MINORISTA FINAL AUTOMATICA": "short_description_retail",
        "descripcion corta MAYORISTA FINAL AUTOMATICA": "short_description_wholesale",
        "descripcion corta manual": "short_description_manual",
        "descripcion corta AUTOMATICA": "short_description_auto",
        "Descripción Larga FINAL AUTOMATICA": "description",
        "Precios Minorista": "regular_price_retail",
        "Precios oferta minorista": "sale_price_retail",
        "Precios Mayorista": "regular_price_wholesale",
        "Precios oferta Mayorista": "sale_price_wholesale",
        "Publicada Minorista": "status_retail",
        "Publicada Mayorista": "status_wholesale",
        "Existencias Minorista": "stock_status_retail",
        "Inventario Minorista": "stock_quantity_retail",
        "Existencias Mayorista": "stock_status_wholesale",
        "Inventario Mayorista": "stock_quantity_wholesale",
        "Categoria WooCommerce": "categories",
        "Item": "sku"
    }
}

def clean_price(val):
    if pd.isna(val) or val == "": return ""
    price = str(val).strip().replace("$", "").replace(" ", "")
    if "," in price and "." in price:
        if price.find(".") < price.find(","):
            price = price.replace(".", "").replace(",", ".")
        else:
            price = price.replace(",", "")
    elif "," in price:
        price = price.replace(",", ".")

    try:
        return "{:.2f}".format(float(price))
    except:
        return ""

def get_product_id(store, sku):
    url = f"{store['url']}/wp-json/wc/v3/products"
    params = {
        "sku": sku,
        "consumer_key": store['ck'],
        "consumer_secret": store['cs']
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code == 200:
            products = r.json()
            return products[0]['id'] if products else None
    except Exception as e:
        print(f"Error buscando SKU {sku}: {e}")
    return None

def map_to_api(row, mode):
    # Determinar columnas según modo
    price_col = "Precios Minorista" if mode == "retail" else "Precios Mayorista"
    sale_price_col = "Precios oferta minorista" if mode == "retail" else "Precios oferta Mayorista"
    status_col = "Publicada Minorista" if mode == "retail" else "Publicada Mayorista"
    stock_status_col = "Existencias Minorista" if mode == "retail" else "Existencias Mayorista"
    stock_qty_col = "Inventario Minorista" if mode == "retail" else "Inventario Mayorista"

    # Descripción corta lógica
    short_desc = ""
    if mode == "retail":
        short_desc = row.get("descripcion corta MINORISTA FINAL AUTOMATICA", "")
    else:
        short_desc = row.get("descripcion corta MAYORISTA FINAL AUTOMATICA", "")

    if not short_desc:
        short_desc = row.get("descripcion corta manual", "") or row.get("descripcion corta AUTOMATICA", "")

    data = {
        "name": row.get("Nombre/titulo", ""),
        "type": row.get("Tipo", "simple").lower(),
        "sku": str(row.get("Item", "")).strip().upper(),
        "regular_price": clean_price(row.get(price_col)),
        "sale_price": clean_price(row.get(sale_price_col)),
        "description": row.get("Descripción Larga FINAL AUTOMATICA", ""),
        "short_description": short_desc,
        "status": "publish" if str(row.get(status_col, "")).lower() in ["1", "si"] else "draft",
        "categories": [{"name": row.get("Categoria WooCommerce", "")}] if row.get("Categoria WooCommerce") else [],
        "stock_status": "instock" if str(row.get(stock_status_col, "")).lower() in ["1", "si"] else "outofstock",
        "manage_stock": "yes" if str(row.get(stock_status_col, "")).lower() in ["1", "si"] else "no",
        "stock_quantity": int(row.get(stock_qty_col, 0)) if str(row.get(stock_qty_col, "")).isdigit() else 0,
    }

    # Manejo de variaciones
    if data["type"] == "variation":
        attributes = []
        attr_map = {
            "Variable Color / Terminación": "pa_color",
            "Variable Tamaño": "pa_size",
            "Variable Diametro": "pa_diametro",
            "Variable Modelo": "pa_modelo"
        }
        for col, slug in attr_map.items():
            val = row.get(col)
            if val:
                attributes.append({"name": slug, "option": str(val).strip()})
        data["attributes"] = attributes

    # Imágenes
    images = []
    img_cols = ['Imágenes Principal', 'Imágenes Galeria 1', 'Imágenes Galeria 2', 'Imágenes Galeria 3', 'Imágenes Galeria 4']
    for col in img_cols:
        url = row.get(col)
        if url and str(url).strip():
            images.append({"src": str(url).strip()})
    data["images"] = images

    return data

def sync_store(store_key, store_config, df):
    mode = "retail" if store_key == "retail" else "wholesale"
    print(f"\n🚀 Iniciando Carga: {store_config['name']}")

    # Separar Padres e Hijos
    parents = df[df['Tipo'].str.lower() == 'variable'].copy()
    variations = df[df['Tipo'].str.lower() == 'variation'].copy()

    all_queues = [
        ("PADRES", parents),
        ("VARIACIONES", variations)
    ]

    for label, queue in all_queues:
        print(f"\n📦 Procesando {label} ({len(queue)} items)...")
        for idx, row in queue.iterrows():
            row_dict = row.to_dict()
            payload = map_to_api(row_dict, mode)
            sku = payload['sku']

            if not sku: continue

            # Lógica de Create con Fail-over a Update
            url = f"{store_config['url']}/wp-json/wc/v3/products"
            params = {"consumer_key": store_config['ck'], "consumer_secret": store_config['cs']}

            try:
                r = requests.post(url, params=params, json=payload, timeout=20)
                if r.status_code == 201:
                    print(f"[{idx+1}] ✅ CREATED: {sku}")
                elif r.status_code == 400 and "woocommerce_rest_product_not_created" in r.text:
                    # RESCATE: Buscar ID y Actualizar
                    prod_id = get_product_id(store_config, sku)
                    if prod_id:
                        update_url = f"{url}/{prod_id}"
                        res = requests.put(update_url, params=params, json=payload, timeout=20)
                        if res.status_code == 200:
                            print(f"[{idx+1}] 🔄 RESCUED (Updated): {sku}")
                        else:
                            print(f"[{idx+1}] ❌ RESCUE FAIL: {sku} - {res.status_code}")
                    else:
                        print(f"[{idx+1}] ❌ SKU EXISTS BUT NO ID: {sku}")
                else:
                    print(f"[{idx+1}] ❌ FAIL: {sku} - {r.status_code}: {r.text[:100]}")
            except Exception as e:
                print(f"[{idx+1}] 🚨 ERROR: {sku} - {e}")

            time.sleep(1) # Pausa de seguridad

if __name__ == "__main__":
    try:
        print("DEBUG: Attempting to read Master CSV...")
        df = pd.read_csv(CONFIG["MASTER_FILE"], sep=None, engine='python', encoding='utf-8')
        print(f"DEBUG: CSV Read Success! Rows found: {len(df)}")

        for sk, cfg in CONFIG["STORES"].items():
            print(f"DEBUG: Starting sync for store: {sk} ({cfg['name']})")
            sync_store(sk, cfg, df)
            print(f"DEBUG: Finished sync for store: {sk}")

        print("\n✨ ¡Sincronización total completada!")
    except Exception as e:
        print(f"FATAL ERROR: {e}")
