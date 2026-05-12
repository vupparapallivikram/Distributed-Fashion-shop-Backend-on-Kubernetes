import requests
import json

query = {"size": 5, "query": {"knn": {"embedding": {"vector": [0.1] * 768, "k": 5}}}}

response = requests.get(
    "http://localhost:9200/items_vector/_search",
    headers={"Content-Type": "application/json"},
    json=query,
)

print(json.dumps(response.json(), indent=2))
