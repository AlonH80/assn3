import flask
import flask_restful
from multiprocessing import Process

import modules


class ServerProcess(Process):

    def __init__(self, config):
        super().__init__()
        self.daemon = True
        self.__config = config
        self.__server_name = config["server"]["name"]
        self.__server_host = config["server"]["host"]
        self.__server_port = config["server"]["port"]
        modules.SqliteConnector.OUTPUT_DB = config["sql_connector"]["db_name"]
        self.__server: flask.Flask = None
        self.__api: flask_restful.Api = None

    def run(self) -> None:
        modules.NutritionApiConnector(self.__config["ninja_api"])
        modules.DishesApi.setup()
        modules.MealsApi.setup()
        self.__server = flask.Flask(self.__server_name)
        self.__api = flask_restful.Api(self.__server)
        self._set_rules()
        self.__server.run(self.__server_host, self.__server_port)

    def _set_rules(self):
        self.__api.add_resource(modules.DishesApi, "/dishes")
        self.__api.add_resource(modules.DishesApi.DishById, "/dishes/<int:dish_id>")
        self.__api.add_resource(modules.DishesApi.DishByName, "/dishes/<dish_name>")
        self.__api.add_resource(modules.MealsApi, "/meals")
        self.__api.add_resource(modules.MealsApi.MealById, "/meals/<int:meal_id>")
        self.__api.add_resource(modules.MealsApi.MealByName, "/meals/<meal_name>")

