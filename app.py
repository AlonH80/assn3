import os.path

import yaml
import signal

import processes


class FoodApplication:

    def __init__(self, config_file):
        self.__config_file = config_file
        self.__config = None
        self.__server_process = None

    def __config_application(self):
        config = {}
        if os.path.exists(self.__config_file):
            with open(self.__config_file) as cf:
                config.update(yaml.safe_load(cf) or {})
        self.__server_process = processes.ServerProcess(config)

    def setup_app(self):
        self.__config_application()
        # self.set_on_sigterm()

    def run_app(self):
        self.__server_process.start()

    def join_app(self):
        try:
            self.__server_process.join()
        except:
            print("Bye!")
