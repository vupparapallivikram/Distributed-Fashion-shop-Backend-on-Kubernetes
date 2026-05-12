import requests
import urllib3

urllib3.disable_warnings()

API = "http://localhost:8081"
OPENSEARCH = "http://localhost:9200"

EMBEDDING_API = "https://db.iue.haw-kiel.de/ollama/api/embeddings"

HEADERS = {"Content-Type": "application/json", "X-Api-Key": "42"}

# -----------------------------------
# Generate embedding
# -----------------------------------


def get_embedding(text):

    response = requests.post(
        EMBEDDING_API,
        headers=HEADERS,
        json={"model": "nomic-embed-text-v2-moe:latest", "prompt": text},
        timeout=60,
        verify=False,
    )

    response.raise_for_status()

    return response.json()["embedding"]


# -----------------------------------
# Fetch items from API
# -----------------------------------

print("Fetching items from API...")

all_items = []

for page in range(1, 46):
    print(f"Fetching page {page}")

    response = requests.get(f"{API}/items?page={page}&page_size=1000")

    data = response.json()

    all_items.extend(data["items"])

items = all_items

print(f"\nTotal items fetched: {len(items)}")

# -----------------------------------
# Sync items to OpenSearch
# -----------------------------------

success = 0
errors = 0

for i, item in enumerate(items):
    try:
        title = item.get("display_name", "")
        description = item.get("description", "")

        combined_text = f"{title} {description}"

        embedding = get_embedding(combined_text)

        doc = {
            "id": item["id"],
            "title": title,
            "description": description,
            "reviews": [],
            "embedding": embedding,
        }

        r = requests.put(
            f"{OPENSEARCH}/items_vector/_doc/{item['id']}",
            headers={"Content-Type": "application/json"},
            json=doc,
            timeout=60,
        )

        if r.status_code in [200, 201]:
            success += 1
        else:
            errors += 1
            print(r.text)

    except Exception as e:
        errors += 1
        print(e)

    if (i + 1) % 100 == 0:
        print(f"Progress: {i + 1}/{len(items)} success: {success} errors: {errors}")

print("\nDone!")
print(f"Success: {success}")
print(f"Errors: {errors}")
