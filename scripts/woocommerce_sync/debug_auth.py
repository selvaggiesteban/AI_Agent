import requests
import sys

STORES = {
    "retail": {
        "url": "https://decotay.com.ar",
        "ck": "ck_e5b2cbf086ea5705b5c6f789b88fce85a5010196",
        "cs": "cs_13d216beeaf3e75fad64210c72fa327235a6bf77",
    },
    "wholesale": {
        "url": "https://tay.com.ar",
        "ck": "ck_588f508b47d417c5e43a2247c0f724a3eaf3938a",
        "cs": "cs_1a51b1ff7b0bd7e5481bdd2dce6cf74e1fa98f33",
    }
}

def test_auth(name, config):
    print(f"Testing {name}...")
    url = f"{config['url']}/wp-json/wc/v3/products"
    params = {"consumer_key": config['ck'], "consumer_secret": config['cs'], "per_page": 1}
    try:
        r = requests.get(url, params=params, timeout=10)
        print(f"Response: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        print(f"Error: {e}")

for name, cfg in STORES.items():
    test_auth(name, cfg)
