import csv
import requests
import time
import sys

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
    }
}

def clean_price(val):
    if not val: return ""
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
    params = {"sku": sku, "consumer_key": store['ck'], "consumer_secret": store['cs']}
    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code == 200:
            products = r.json()
            return products[0]['id'] if products else None
    except:
        pass
    return None

def sync_store(store_key, store_config, rows):
    mode = "retail" if store_key == "retail" else "wholesale"
    print(f"\n🚀 Iniciando Carga Ligera: {store_config['name']}")
    
    price_col = "Precios Minorista" if mode == "retail" else "Precios Mayorista"
    sale_price_col = "Precios oferta minorista" if mode == "retail" else "Precios oferta Mayorista"
    status_col = "Publicada Minorista" if mode == "retail" else "Publicada Mayorista"
    stock_status_col = "Existencias Minorista" if mode == "retail" else "Existencias Mayorista"
    stock_qty_col = "Inventario Minorista" if mode == "retail" else "Inventario Mayorista"

    parents = [r for r in rows if r.get('Tipo', '').lower() == 'variable']
    variations = [r for r in rows if r.get('Tipo', '').lower() == 'variation']

    for label, queue in [("PADRES", parents), ("VARIACIONES", variations)]:
        print(f"\n📦 Procesando {label} ({len(queue)} items)...")
        for idx, row in enumerate(queue):
            sku = str(row.get('Item', '')).strip().upper()
            if not sku: continue

            payload = {
                "name": row.get("Nombre/titulo", ""),
                "type": row.get("Tipo", "simple").lower(),
                "sku": sku,
                "regular_price": clean_price(row.get(price_col)),
                "sale_price": clean_price(row.get(sale_price_col)),
                "description": row.get("Descripción Larga FINAL AUTOMATICA", ""),
                "status": "publish" if str(row.get(status_col, "")).lower() in ["1", "si"] else "draft",
                "stock_status": "instock" if str(row.get(stock_status_col, "")).lower() in ["1", "si"] else "outofstock",
                "manage_stock": "yes" if str(row.get(stock_status_col, "")).lower() in ["1", "si"] else "no",
                "stock_quantity": int(row.get(stock_qty_col, 0)) if str(row.get(stock_qty_col, "")).isdigit() else 0,
            }

            if payload["type"] == "variation":
                attr_map = {"Variable Color / Terminación": "pa_color", "Variable Tamaño": "pa_size", "Variable Diametro": "pa_diametro", "Variable Modelo": "pa_modelo"}
                attrs = []
                for col, slug in attr_map.items():
                    val = row.get(col)
                    if val: attrs.append({"name": slug, "option": str(val).strip()})
                payload["attributes"] = attrs

            imgs = []
            for col in ['Imágenes Principal', 'Imágenes Galeria 1', 'Imágenes Galeria 2', 'Imágenes Galeria 3', 'Imágenes Galeria 4']:
                url = row.get(col)
                if url: imgs.append({"src": str(url).strip()})
            payload["images"] = imgs

            url = f"{store_config['url']}/wp-json/wc/v3/products"
            params = {"consumer_key": store_config['ck'], "consumer_secret": store_config['cs']}

            try:
                r = requests.post(url, params=params, json=payload, timeout=20)
                if r.status_code == 201:
                    print(f"[{idx+1}] ✅ CREATED: {sku}")
                elif r.status_code == 400 and "woocommerce_rest_product_not_created" in r.text:
                    prod_id = get_product_id(store_config, sku)
                    if prod_id:
                        res = requests.put(f"{url}/{prod_id}", params=params, json=payload, timeout=20)
                        if res.status_code == 200:
                            print(f"[{idx+1}] 🔄 RESCUED: {sku}")
                        else:
                            print(f"[{idx+1}] ❌ RESCUE FAIL: {sku}")
                else:
                    print(f"[{idx+1}] ❌ FAIL: {sku} - {r.status_code}")
            except Exception as e:
                print(f"[{idx+1}] 🚨 ERROR: {sku} - {e}")
            
            time.sleep(1)

if __name__ == "__main__":
    try:
        print("📖 Reading Master CSV (Light Mode)...")
        with open(CONFIG["MASTER_FILE"], mode='r', encoding='utf-8') as f:
            sample = f.readline()
            sep = ';' if ';' in sample else ','
            f.seek(0)
            reader = csv.DictReader(f, delimiter=sep)
            rows = list(reader)
        
        print(f"CSV Read Success! Rows: {len(rows)}")
        for sk, cfg in CONFIG["STORES"].items():
            sync_store(sk, cfg, rows)
        
        print("\n✨ ¡Sincronización ligera completada!")
    except Exception as e:
        print(f"FATAL ERROR: {e}")
