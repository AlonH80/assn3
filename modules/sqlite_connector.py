import queue
import sqlite3
import time
from threading import Thread


class SqliteConnector:

    OUTPUT_DB = "food.db"

    def __init__(self, db_name=None):
        self.__db_name = db_name or SqliteConnector.OUTPUT_DB
        self.__connection = None
        self.__cursor = None
        self.__execute_queue = queue.Queue()
        self.__queries_output = dict()
        self.__stop_thread = False
        self.__executing_thread = Thread(target=self.sql_executor_loop)
        self.__executing_thread.start()
        self.__tables_to_schema = self.get_all_tables()

    def sql_executor_loop(self):
        self.__connection = sqlite3.connect(self.__db_name)
        self.__cursor = self.__connection.cursor()
        while not self.__stop_thread:
            try:
                query_to_execute = self.__execute_queue.get()
                self.__cursor.execute(query_to_execute)
                self.__connection.commit()
                self.__queries_output[query_to_execute] = self.__cursor.fetchall()
            except queue.Empty:
                continue
        self.__connection.commit()
        self.__connection.close()

    def get_query_output(self, query, timeout=0.2):
        self.__execute_queue.put(query)
        timeout_partitions = 1000
        for _ in range(timeout_partitions):
            if query in self.__queries_output.keys():
                break
            time.sleep(timeout / timeout_partitions)
        output = self.__queries_output.pop(query, [])
        return output

    def create_table(self, table_name, primary_key, *cols):
        self.get_query_output(f"CREATE TABLE IF NOT EXISTS {table_name}({primary_key} PRIMARY KEY, {', '.join(cols)})")
        self.__tables_to_schema = self.get_all_tables()

    def get_all_tables(self):
        output_data = self.get_query_output("SELECT name FROM sqlite_master WHERE type='table';", timeout=0.1)
        raw_tables = list(map(lambda t: t[0], output_data))
        table_to_schema = {}
        for table in raw_tables:
            raw_schema = self.get_query_output(f"pragma table_info('{table}')")
            schema = list(map(lambda col: col[1], raw_schema))
            table_to_schema[table] = schema
        return table_to_schema

    def insert_to_table(self, table_name, values_map):
        cols = self.__tables_to_schema[table_name]
        values = map(lambda c: "NULL" if values_map[c] is None else f"'{values_map[c]}'", cols)
        insert_query = f"INSERT OR REPLACE INTO {table_name}({', '.join(cols)}) VALUES({', '.join(values)})"
        self.get_query_output(insert_query)

    def select_table(self, table_name):
        select_query = f"SELECT * FROM {table_name}"
        raw_data_list = self.get_query_output(select_query) or []
        output_data = list(
            map(lambda raw_data: dict(zip(self.__tables_to_schema[table_name], raw_data)), raw_data_list))
        return output_data

    def select_by_id(self, table_name, data_id):
        select_query = f"SELECT * FROM {table_name} WHERE id='{data_id}'"
        raw_data_list = self.get_query_output(select_query)
        raw_data = raw_data_list[0] if raw_data_list is not None and len(raw_data_list) > 0 else []
        output_data = dict(zip(self.__tables_to_schema[table_name], raw_data))
        return output_data

    def select_by_name(self, table_name, name):
        select_query = f"SELECT * FROM {table_name} WHERE name='{name}'"
        raw_data_list = self.get_query_output(select_query)
        raw_data = raw_data_list[0] if len(raw_data_list) > 0 else []
        output_data = dict(zip(self.__tables_to_schema[table_name], raw_data))
        return output_data

    def delete_by_id(self, table_name, data_id):
        deleted_data = self.select_by_id(table_name, data_id)
        self.get_query_output(f"DELETE FROM {table_name} WHERE id='{data_id}'")
        return deleted_data

    def delete_by_name(self, table_name, name):
        deleted_data = self.select_by_name(table_name, name)
        if len(deleted_data) > 0:
            self.get_query_output(f"DELETE FROM {table_name} WHERE name='{name}'")
        return deleted_data

    def close(self):
        self.__stop_thread = True
        self.__executing_thread.join(0.3)
