import requests
import json
import os

query_file = f"{os.path. dirname(__file__)}/query.txt"
output_file = "response.txt"
url = "http://0.0.0.0:8000"
dishes_url = f"{url}/dishes"

with open(query_file) as qf:
    dishes_map = map(lambda d: d.strip(), qf.readlines())
    dishes = list(filter(lambda d: len(d) > 0, dishes_map))

list(map(lambda d: requests.delete(f"{dishes_url}/{d}"), dishes))

outputs = map(lambda d: (d, requests.post(dishes_url, json={"name":d})), dishes)
dish_to_id = dict(map(lambda o: (o[0], o[1].content.decode().strip()), outputs))
dishes_from_api = json.loads(requests.get(dishes_url).content)
get_attr_from_dish = lambda dish_id, atr: dishes_from_api[dish_to_id[dish_id]][atr]

with open(output_file, "w") as of:
    list(map(lambda d: of.write(f"{d} contains {get_attr_from_dish(d, 'cal')} calories {get_attr_from_dish(d, 'sodium')} mgs of sodium, and {get_attr_from_dish(d, 'sugar')} grams of sugar\n"), dishes))
