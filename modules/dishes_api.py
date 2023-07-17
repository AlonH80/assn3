from flask_restful import Resource
from flask import request

from .processor import DishesProcessor
from .output_status_codes import ErrorCodes, HttpCodes
from .meals_api import MealsApi


class DishesApi(Resource):
    SQL_TABLE_SCHEMA = ["ID INT", "name CHAR(50)", "cal REAL", "size REAL", "sodium REAL", "sugar REAL"]
    processor = None

    @staticmethod
    def setup():
        DishesApi.processor = DishesProcessor(DishesApi.SQL_TABLE_SCHEMA)

    def get(self):
        dishes, status_code = DishesApi.processor.get_all()
        status_code = status_code.value if isinstance(status_code, HttpCodes) else status_code
        dishes = dishes.value if isinstance(dishes, ErrorCodes) else dishes
        return dishes, status_code

    def post(self):
        if request.content_type != 'application/json':
            return 0, 415
        input_data = request.get_json()
        output_data, status_code = DishesApi.processor.create_entity(input_data)
        status_code = status_code.value if isinstance(status_code, HttpCodes) else status_code
        output_data = output_data.value if isinstance(output_data, ErrorCodes) else output_data
        return output_data, status_code

    def delete(self):
        return "", 405

    class DishById(Resource):

        def get(self, dish_id):
            output_data, status_code = DishesApi.processor.get_by_name_or_id(ent_id=str(dish_id))
            status_code = status_code.value if isinstance(status_code, HttpCodes) else status_code
            output_data = output_data.value if isinstance(output_data, ErrorCodes) else output_data
            return output_data, status_code

        def delete(self, dish_id):
            data_to_delete, _ = DishesApi.processor.get_by_name_or_id(ent_id=dish_id)
            output_data, status_code = DishesApi.processor.delete_by_name_or_id(ent_id=str(dish_id))
            status_code = status_code.value if isinstance(status_code, HttpCodes) else status_code
            if isinstance(output_data, ErrorCodes):
                output_data = output_data.value
            else:
                MealsApi.processor.delete_dish_from_meal(data_to_delete)
            return output_data, status_code

    class DishByName(Resource):

        def get(self, dish_name):
            output_data, status_code = DishesApi.processor.get_by_name_or_id(ent_name=dish_name)
            status_code = status_code.value if isinstance(status_code, HttpCodes) else status_code
            output_data = output_data.value if isinstance(output_data, ErrorCodes) else output_data
            return output_data, status_code

        def delete(self, dish_name):
            output_data, status_code = DishesApi.processor.delete_by_name_or_id(ent_name=dish_name)
            status_code = status_code.value if isinstance(status_code, HttpCodes) else status_code
            output_data = output_data.value if isinstance(output_data, ErrorCodes) else output_data
            return output_data, status_code
