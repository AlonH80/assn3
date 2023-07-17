import json
from functools import cache
from collections.abc import Iterable
from singleton_decorator import singleton
import requests
import numbers


@singleton
class NutritionApiConnector:

    def __init__(self, config):
        with open(config["ninja_api_key_file"]) as f:
            self.__api_key = f.read().strip()
        self.__base_url = config["ninja_url"]
        self.__api_request_kwargs = {"verify": False, "headers": {"X-Api-Key": self.__api_key}}
        self.__map_field_to_api = config["api_map_fields"]

    @cache
    def get_dish(self, dish_name):
        print(f"{self.__base_url}?query={dish_name}", self.__api_request_kwargs)
        req = requests.get(f"{self.__base_url}?query={dish_name}", **self.__api_request_kwargs)
        output_data = {}
        status_code = req.status_code
        if status_code == 200:
            output_list = json.loads(req.content.decode())
            if len(output_list) > 0:
                output_data["name"] = dish_name
                for key_in_api, output_field in self.__map_field_to_api.items():
                    iter_value_per_dish = map(lambda raw_dish: raw_dish.get(key_in_api), output_list)
                    output_data[output_field] = self.reduce_iterable_based_on_type(iter_value_per_dish)
        print(status_code, output_data)
        return status_code, output_data

    @staticmethod
    def reduce_iterable_based_on_type(it: Iterable):
        iter_list = list(it)
        if isinstance(iter_list[0], str):
            return " and ".join(iter_list)
        elif isinstance(iter_list[0], numbers.Number):
            return sum(iter_list)
