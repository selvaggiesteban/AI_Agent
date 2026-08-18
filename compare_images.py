import json
import os

# Load API data
with open('api_obras.json', 'r', encoding='utf-8') as f:
    try:
        data = json.load(f)
    except json.JSONDecodeError:
        # In case curl output has some headers or noise
        import re
        content = f.read()
        # Try to find the JSON array part
        match = re.search(r'(\[.*\])', content, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
        else:
            print("Could not find JSON array in api_obras.json")
            exit(1)

# Extract all image paths expected by API
expected_images = set()
for obra in data:
    # Check 'imagen' field
    if 'imagen' in obra and obra['imagen']:
        path = obra['imagen'].lstrip('/')
        expected_images.add(path)
    # Check 'imagenes' field (array)
    if 'imagenes' in obra and isinstance(obra['imagenes'], list):
        for img in obra['imagenes']:
            if img:
                path = img.lstrip('/')
                expected_images.add(path)

# Load local image files
with open('local_images.txt', 'r', encoding='utf-8') as f:
    local_files = set(line.strip() for line in f if line.strip())

# Since local_images.txt contains only the filenames, 
# and API paths are like "images/obras/001_01.jpg", 
# we need to extract just the filename from the API path.
expected_filenames = set()
for path in expected_images:
    filename = os.path.basename(path)
    expected_filenames.add(filename)

# Contrast
missing = expected_filenames - local_files
extra = local_files - expected_filenames

print(f"Total images expected by API (unique filenames): {len(expected_filenames)}")
print(f"Total images found locally: {len(local_files)}")

if missing:
    print("\n❌ MISSING IMAGES (Expected by API but not found locally):")
    for img in sorted(list(missing)):
        print(f"- {img}")
else:
    print("\n✅ NO IMAGES MISSING: All images expected by the API are present locally.")

if extra:
    print(f"\nℹ️  EXTRA IMAGES (Found locally but not referenced by API): {len(extra)}")
