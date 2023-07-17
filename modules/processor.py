import numbers
from copy import copy

from .sqlite_connector import SqliteConnector
from .nutrition_api_connector import NutritionApiConnector
from .output_status_codes import HttpCodes, ErrorCodes


class Processor:

    def __init__(self, table, table_schema):
        self._table_schema = table_schema
        self._table_columns = list(map(lambda c: c.split()[0], table_schema))
        self._sql_connector = SqliteConnector()
        self._sql_connector.create_table(table, *table_schema)
        self._api_connector = NutritionApiConnector()
        self._table = table

    def terminate(self):
        self._sql_connector.close()

    def get_all(self):
        output_data = self._sql_connector.select_table(self._table)
        output_data = dict(map(lambda d: (d["ID"], d), output_data))
        return output_data, HttpCodes.ACTION_SUCCESSFUL

    def create_entity(self, data, overwrite=False):
        raise NotImplementedError

    def get_by_name_or_id(self, ent_id=None, ent_name=None):
        output_data = {}
        status_code = HttpCodes.ACTION_SUCCESSFUL
        if ent_id is not None:
            output_data.update(self._sql_connector.select_by_id(self._table, ent_id))
        elif ent_name is not None:
            output_data.update(self._sql_connector.select_by_name(self._table, ent_name))
        output_id = output_data.get("ID", ErrorCodes.NOT_EXISTS)
        if output_id == ErrorCodes.NOT_EXISTS:
            status_code = HttpCodes.NOT_EXISTS
            output_data = output_id
        return output_data, status_code

    def delete_by_name_or_id(self, ent_id=None, ent_name=None):
        output_data = {}
        if ent_id is not None:
            output_data.update(self._sql_connector.delete_by_id(self._table, ent_id))
        elif ent_name is not None:
            output_data.update(self._sql_connector.delete_by_name(self._table, ent_name))
        output_id = output_data.get("ID", ErrorCodes.NOT_EXISTS)
        status_code = HttpCodes.ACTION_SUCCESSFUL if output_id != ErrorCodes.NOT_EXISTS else HttpCodes.NOT_EXISTS
        return output_id, status_code


class DishesProcessor(Processor):

    def __init__(self, dishes_schema):
        super().__init__("dishes", dishes_schema)

    def create_entity(self, data, overwrite=False):
        ent_id = max(list(map(lambda d: int(d["ID"]), self._sql_connector.select_table(self._table))) or [0]) + 1
        data["ID"] = ent_id
        output_id, status_code = ent_id, HttpCodes.CREATED_SUCCESSFULLY  # default

        if "name" not in data:
            output_id, status_code = ErrorCodes.PARAMETER_NOT_SPECIFIED, HttpCodes.UNPROCESSABLE
        elif self._sql_connector.select_by_name(self._table, data["name"]).get("ID") is not None:
            output_id, status_code = ErrorCodes.ALREADY_EXISTS, HttpCodes.UNPROCESSABLE

        else:
            api_status_code, api_output = self._api_connector.get_dish(data["name"])
            if api_status_code != HttpCodes.ACTION_SUCCESSFUL.value:
                output_id, status_code = ErrorCodes.API_NOT_REACHABLE, HttpCodes.UNREACHABLE
            elif len(api_output) > 0:
                data.update(api_output)
            else:
                output_id, status_code = ErrorCodes.UNRECOGNIZED_BY_API, HttpCodes.UNPROCESSABLE

        if status_code == HttpCodes.CREATED_SUCCESSFULLY:
            self._sql_connector.insert_to_table(self._table, data)

        return output_id, status_code


class MealsProcessor(Processor):

    def __init__(self, meals_schema):
        self.__meals_mandatory_fields = ["name", "appetizer", "main", "dessert"]
        self.__dishes_cols = copy(self.__meals_mandatory_fields)
        self.__dishes_cols.remove("name")
        super().__init__("meals", meals_schema)

    def create_entity(self, data, overwrite=False):
        if overwrite:
            ent_id = data["ID"]
        else:
            ent_id = max(list(map(lambda d: int(d["ID"]), self._sql_connector.select_table(self._table))) or [0]) + 1
            data["ID"] = ent_id
        output_id, status_code = ent_id, HttpCodes.CREATED_SUCCESSFULLY  # default

        if any(map(lambda c: c not in data, self.__meals_mandatory_fields)):
            output_id, status_code = ErrorCodes.PARAMETER_NOT_SPECIFIED, HttpCodes.UNPROCESSABLE
        elif self._sql_connector.select_by_name(self._table, data["name"]).get("ID") is not None and not overwrite:
            output_id, status_code = ErrorCodes.ALREADY_EXISTS, HttpCodes.UNPROCESSABLE
        else:
            data["cal"] = 0.0
            data["sodium"] = 0.0
            data["sugar"] = 0.0
            for dish_col in self.__dishes_cols:
                dish_data = self._sql_connector.select_by_id("dishes", data[dish_col])
                if dish_data.get("ID") is not None:
                    data["cal"] += dish_data.get("cal", 0.0)
                    data["sodium"] += dish_data.get("sodium", 0.0)
                    data["sugar"] += dish_data.get("sugar", 0.0)
                else:
                    output_id, status_code = ErrorCodes.DETAIL_IN_REQUEST_NOT_EXISTS, HttpCodes.UNPROCESSABLE
                    break

        if status_code == HttpCodes.CREATED_SUCCESSFULLY:
            self._sql_connector.insert_to_table(self._table, data)

        return output_id, status_code

    def put_by_id(self, data):
        entity_id, status_code = self.create_entity(data, overwrite=True)
        status_code = HttpCodes.ACTION_SUCCESSFUL if status_code == HttpCodes.CREATED_SUCCESSFULLY else status_code
        return entity_id, status_code

    def delete_dish_from_meal(self, dish_data):
        all_meals, _ = self.get_all()
        filtered_meals = filter(lambda m: dish_data["ID"] in m.values(), list(all_meals.values()))
        for meal in filtered_meals:
            for field in self.__meals_mandatory_fields:
                if meal[field] == dish_data["ID"]:
                    meal[field] = None
                    break
            for field in set(self._table_columns[1:]).difference(set(self.__meals_mandatory_fields)):
                if isinstance(meal[field], numbers.Number):
                    meal[field] = meal[field] - dish_data[field]
            self._sql_connector.insert_to_table(self._table, meal)

