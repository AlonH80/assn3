from flask_restful import Resource
from flask import request
from .processor import MealsProcessor
from .output_status_codes import HttpCodes, ErrorCodes


class MealsApi(Resource):
    SQL_TABLE_SCHEMA = ["ID INT", "name CHAR(50)", "appetizer INT", "main INT", "dessert INT", "cal REAL", "sodium REAL", "sugar REAL"]
    processor = None

    @staticmethod
    def setup():
        MealsApi.processor = MealsProcessor(MealsApi.SQL_TABLE_SCHEMA)

    def get(self):
        dishes, status_code = MealsApi.processor.get_all()
        status_code = status_code.value if isinstance(status_code, HttpCodes) else status_code
        output_data = dishes.value if isinstance(dishes, ErrorCodes) else dishes
        return output_data, status_code

    def post(self):
        if request.content_type != 'application/json':
            return 0, 415
        input_data = request.get_json(force=True)
        output_data, status_code = MealsApi.processor.create_entity(input_data)
        status_code = status_code.value if isinstance(status_code, HttpCodes) else status_code
        output_data = output_data.value if isinstance(output_data, ErrorCodes) else output_data
        return output_data, status_code

    class MealById(Resource):

        def get(self, meal_id):
            output_data, status_code = MealsApi.processor.get_by_name_or_id(ent_id=str(meal_id))
            status_code = status_code.value if isinstance(status_code, HttpCodes) else status_code
            output_data = output_data.value if isinstance(output_data, ErrorCodes) else output_data
            return output_data, status_code

        def delete(self, meal_id):
            output_data, status_code = MealsApi.processor.delete_by_name_or_id(ent_id=str(meal_id))
            status_code = status_code.value if isinstance(status_code, HttpCodes) else status_code
            output_data = output_data.value if isinstance(output_data, ErrorCodes) else output_data
            return output_data, status_code

        def put(self, meal_id):
            input_data = request.get_json(force=True)
            input_data["ID"] = meal_id
            output_data, status_code = MealsApi.processor.put_by_id(input_data)
            status_code = status_code.value if isinstance(status_code, HttpCodes) else status_code
            output_data = output_data.value if isinstance(output_data, ErrorCodes) else output_data
            return output_data, status_code

    class MealByName(Resource):

        def get(self, meal_name):
            output_data, status_code = MealsApi.processor.get_by_name_or_id(ent_name=str(meal_name))
            status_code = status_code.value if isinstance(status_code, HttpCodes) else status_code
            output_data = output_data.value if isinstance(output_data, ErrorCodes) else output_data
            return output_data, status_code

        def delete(self, meal_name):
            output_data, status_code = MealsApi.processor.delete_by_name_or_id(ent_name=str(meal_name))
            status_code = status_code.value if isinstance(status_code, HttpCodes) else status_code
            output_data = output_data.value if isinstance(output_data, ErrorCodes) else output_data
            return output_data, status_code
