from locust import HttpUser, task, between
import random

ITEM_IDS = [
    38005, 9524, 27217, 52425, 48958, 58901, 7545, 58153, 34830, 50714,
    36735, 15417, 28715, 19472, 22646, 54200, 16224, 40762, 39646, 38381,
    55949, 38327, 9166, 12892, 6241, 58653, 58085, 59622, 24114, 58840,
    18389, 7408, 3819, 59796, 55828, 34541, 31435, 8366, 37512, 2540,
    21146, 32426, 51767, 44655, 27667, 21172, 20676, 31576, 18755, 2164,
    30816, 5074, 4674, 21683
]

USERS = [
    {"email": "neil.arnold-10@example.com", "password": "Neil", "uid": "chattpet"},
    {"email": "david.fell-36@example.com", "password": "David", "uid": "cyrywkbn"},
    {"email": "wes.sorley-35@example.com", "password": "Wes", "uid": "usgzvmru"},
    {"email": "david.hofrichter-60@example.com", "password": "David", "uid": "ssqmumdk"},
    {"email": "shambhu.mane-26@example.com", "password": "Shambhu", "uid": "cquauqke"},
    {"email": "david.linton-87@example.com", "password": "David", "uid": "bjjhglih"},
    {"email": "jay.biswas-76@example.com", "password": "Jay", "uid": "theitefn"},
    {"email": "fernanda.urresti-69@example.com", "password": "Fernanda", "uid": "gukyqanf"},
    {"email": "david.mckenna-54@example.com", "password": "David", "uid": "xlidkdzw"},
    {"email": "kikuko.ando-64@example.com", "password": "Kikuko", "uid": "ejuixtco"},
    {"email": "javier.skinner-58@example.com", "password": "Javier", "uid": "ywjvykgz"},
    {"email": "cora.dowell-30@example.com", "password": "Cora", "uid": "kospbjql"},
    {"email": "soma.cami-67@example.com", "password": "Soma", "uid": "uqssysyz"},
    {"email": "miles.dunsmuir-48@example.com", "password": "Miles", "uid": "xfiqdcjf"},
    {"email": "david.fox-67@example.com", "password": "David", "uid": "eleagtof"},
    {"email": "kuldeep.shek-93@example.com", "password": "Kuldeep", "uid": "errcpcqn"},
    {"email": "ian.mcmartin-59@example.com", "password": "Ian", "uid": "snvpohml"},
    {"email": "david.peden-95@example.com", "password": "David", "uid": "eiykeuhi"},
    {"email": "angela.ferrante-42@example.com", "password": "Angela", "uid": "xfyywwnv"},
]

class ShopUser(HttpUser):
    wait_time = between(0, 2)
    token = None
    uid = None
    sale_id = None

    def on_start(self):
        user = random.choice(USERS)
        self.uid = user["uid"]
        r = self.client.post("/login", json={
            "email": user["email"],
            "password": user["password"]
        })
        self.token = r.json().get("token")

    def auth(self):
        return {"Authorization": f"Bearer {self.token}"}

    @task(30)
    def get_item_list(self):
        self.client.get(f"/items?page={random.randint(1,10)}&page_size=20")

    @task(25)
    def get_item_details(self):
        self.client.get(f"/item/{random.choice(ITEM_IDS)}")

    @task(5)
    def get_user_details(self):
        self.client.get(f"/user/{self.uid}", headers=self.auth())

    @task(10)
    def get_user_sales(self):
        self.client.get(f"/user/{self.uid}/sales", headers=self.auth())

    @task(20)
    def post_sale(self):
        with self.client.post("/sales/", 
            headers=self.auth(), 
            json={
                "user_id": self.uid,
                "item_id": random.choice(ITEM_IDS),
                "quantity": 1
            }, catch_response=True) as r:
            if r.status_code in [200, 400]:
                r.success()
            if r.status_code == 200:
                data = r.json()
                self.sale_id = data.get("sale_id") 

    @task(10)
    def update_sale(self):
        if self.sale_id:
            self.client.patch(f"/sales/{self.sale_id}", headers=self.auth(), json={
                "rating": random.randint(1, 5),
                "review": "Great product!"
            })