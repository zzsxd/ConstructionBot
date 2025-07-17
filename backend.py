import json
import time
from datetime import datetime, timedelta
import pandas as pd
import csv
from openpyxl import load_workbook

class DbAct:
    def __init__(self, db, config, path_xlsx):
        super(DbAct, self).__init__()
        self.__db = db
        self.__config = config
        self.__fields_user = ['Имя', 'Фамилия', 'Никнейм', 'Номер телефона']
        self.__dump_path_xlsx = path_xlsx


    def add_user(self, user_id, first_name, last_name, nick_name, phone, is_):
            if not self.user_is_existed(user_id):
                if user_id in self.__config.get_config()['admins']:
                    is_admin = True
                else:
                    is_admin = False
                self.__db.db_write(
                    'INSERT INTO users (user_id, first_name, last_name, nick_name, phone, system_data, is_admin, is_foreman) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (user_id, first_name, last_name, nick_name, phone, json.dumps({"index": None}), is_admin, is_foreman))


    def user_is_existed(self, user_id: int):
            data = self.__db.db_read('SELECT count(*) FROM users WHERE user_id = ?', (user_id,))
            if len(data) > 0:
                if data[0][0] > 0:
                    status = True
                else:
                    status = False
                return status
            
    def user_is_admin(self, user_id: int):
        data = self.__db.db_read('SELECT is_admin FROM users WHERE user_id = ?', (user_id,))
        if len(data) > 0:
            if data[0][0] == 1:
                status = True
            else:
                status = False
            return status
        
    def set_user_system_key(self, user_id: int, key: str, value: any) -> None:
        system_data = self.get_user_system_data(user_id)
        if system_data is None:
            return None
        system_data = json.loads(system_data)
        system_data[key] = value
        self.__db.db_write('UPDATE users SET system_data = ? WHERE user_id = ?', (json.dumps(system_data), user_id))

    def get_user_system_key(self, user_id: int, key: str):
        system_data = self.get_user_system_data(user_id)
        if system_data is None:
            return None
        system_data = json.loads(system_data)
        if key not in system_data.keys():
            return None
        return system_data[key]

    def get_user_system_data(self, user_id: int):
        if not self.user_is_existed(user_id):
            return None
        return self.__db.db_read('SELECT system_data FROM users WHERE user_id = ?', (user_id,))[0][0]
    


    def db_export_xlsx(self):
        try:
            d = {'Имя': [], 'Фамилия': [], 'Никнейм': [], 'Номер телефона': []}
            users = self.__db.db_read('SELECT first_name, last_name, nick_name, phone FROM users', ())
            if len(users) > 0:
                for user in users:
                    for info in range(len(list(user))):
                        d[self.__fields_user[info]].append(user[info])
                df = pd.DataFrame(d)
                df.to_excel(self.__config.get_config()['xlsx_path'], sheet_name='Пользователи', index=False)
        except Exception as e:
            return print(e)