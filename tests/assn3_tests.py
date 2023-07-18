import requests
import json

class TestMealsAndDishesAPI:

    @classmethod
    def setup_class(cls) -> None:
        cls.base_url = "http://0.0.0.0:8000"
        cls.dishes_url = f"{cls.base_url}/dishes"
        cls.meals_url = f"{cls.base_url}/meals"
        cls.dish_to_id = {}
        cls.meal_to_id = {}
        for i in json.loads(requests.get(f"{cls.base_url}/dishes").content.decode()).keys():
            requests.delete(f"{cls.base_url}/dishes/{i}")
        for i in json.loads(requests.get(cls.meals_url).content.decode()).keys():
            requests.delete(f"{cls.meals_url}/{i}")

    @classmethod
    def teardown_class(cls) -> None:
        for i in json.loads(requests.get(f"{cls.base_url}/dishes").content.decode()).keys():
            requests.delete(f"{cls.base_url}/dishes/{i}")
        for i in json.loads(requests.get(cls.meals_url).content.decode()).keys():
            requests.delete(f"{cls.meals_url}/{i}")

    def test_create_dishes(self):
        dishes_to_create = ["orange", "spaghetti", "apple pie"]
        for dish in dishes_to_create:
            req = requests.post(self.dishes_url, headers={"Content-Type": "application/json"},
                                data=json.dumps({"name": dish}))
            output_status_code, output_content = req.status_code, req.content.decode().strip()
            assert output_status_code == 201
            self.dish_to_id[dish] = int(output_content)
        assert len(self.dish_to_id.values()) == len(set(self.dish_to_id.values()))

    def test_orange_sodium(self):
        req = requests.get(f"{self.dishes_url}/{self.dish_to_id['orange']}")
        output_status_code, output_content = req.status_code, json.loads(req.content)
        print(output_content)
        assert output_status_code == 200
        assert 0.9 <= output_content["sodium"] <= 1.1

    def test_get_dishes(self):
        req = requests.get(self.dishes_url)
        output_status_code, output_content = req.status_code, json.loads(req.content)
        assert output_status_code == 200
        assert len(output_content.keys()) == 3

    def test_blah(self):
        req = requests.post(self.dishes_url, headers={"Content-Type": "application/json"},
                            data=json.dumps({"name": "blah"}))
        output_status_code, output_content = req.status_code, int(req.content.decode())
        assert output_status_code in [400, 404, 422]
        assert output_content == -3

    def test_post_already_exists(self):
        req = requests.post(self.dishes_url, headers={"Content-Type": "application/json"},
                            data=json.dumps({"name": "orange"}))
        output_status_code, output_content = req.status_code, int(req.content.decode())
        assert output_status_code in [400, 404, 422]
        assert output_content == -2

    def test_post_delicious_meal(self):
        req = requests.post(self.meals_url, json={"name": "delicious",
                                                  "appetizer": self.dish_to_id['orange'],
                                                  "main": self.dish_to_id['spaghetti'],
                                                  "dessert": self.dish_to_id['apple pie']
                                                  })
        output_status_code, output_content = req.status_code, int(req.content.decode())
        assert output_status_code == 201
        assert output_content > 0
        self.meal_to_id["delicious"] = output_content

    def test_get_meals(self):
        req = requests.get(self.meals_url)
        output_status_code, output_content = req.status_code, json.loads(req.content)
        print(output_content)
        assert output_status_code == 200
        assert len(output_content) == 1
        assert 400 < list(output_content.values())[0]['cal'] < 500

    def test_post_delicious_meal_again(self):
        req = requests.post(self.meals_url, json={"name": "delicious",
                                                  "appetizer": self.dish_to_id['orange'],
                                                  "main": self.dish_to_id['spaghetti'],
                                                  "dessert": self.dish_to_id['apple pie']
                                                  })
        output_status_code, output_content = req.status_code, int(req.content.decode())
        assert output_status_code in [400, 422]
        assert output_content == -2

