from locust import HttpUser, task, between, constant
import random

USERS = [
    {"email": "neil.arnold-10@example.com", "password": "Neil", "uid": "chattpet"},
    {"email": "david.fell-36@example.com", "password": "David", "uid": "cyrywkbn"},
    {"email": "wes.sorley-35@example.com", "password": "Wes", "uid": "usgzvmru"},
    {"email": "david.hofrichter-60@example.com", "password": "David", "uid": "ssqmumdk"},
    {"email": "shambhu.mane-26@example.com", "password": "Shambhu", "uid": "cquauqke"},
]

FIXED_ITEMS = [38005, 9524, 27217, 52425, 48958]

class ConsistencyUser(HttpUser):
    wait_time = constant(0)

    def on_start(self):
        user = random.choice(USERS)
        self.uid = user["uid"]
        r = self.client.post("/login", json={
            "email": user["email"],
            "password": user["password"]
        })
        self.token = r.json().get("token")

    @task
    def buy_item(self):
        self.client.post("/sales/", 
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "user_id": self.uid,
                "item_id": random.choice(FIXED_ITEMS),
                "quantity": 1
            })
