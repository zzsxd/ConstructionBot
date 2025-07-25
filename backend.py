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


    def add_user(self, user_id, full_name, nick_name, is_foreman):
            if not self.user_is_existed(user_id):
                if user_id in self.__config.get_config()['admins']:
                    is_admin = True
                else:
                    is_admin = False
                self.__db.db_write(
                    'INSERT INTO users (user_id, full_name, nick_name, system_data, is_admin, is_foreman) '
                    'VALUES (?, ?, ?, ?, ?, ?)',
                    (user_id, full_name, nick_name, json.dumps({"index": None, "attach_object_name": None, "full_name": None, "object_id": None, "category_id": None, "subcategory_id": None, "work_type_id": None, "work_type_name": None, "work_type_unit": None, "work_type_volume": None, "material_name": None, "material_norm": None, "material_unit": None, "material_counterparty": None, "material_registration_number": None, "material_volume": None}), is_admin, is_foreman))
                
    def set_user_id_in_topic(self, user_id, topic_id):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('UPDATE users SET topic_id = ? WHERE user_id = ?', (topic_id, user_id))
                
    def get_user_id_from_topic(self, topic_id):
        data = self.__db.db_read("SELECT user_id FROM users WHERE topic_id = ?", (topic_id, ))
        if len(data) > 0:
            return data[0][0]
        
    def set_user_is_foreman(self, user_id):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('UPDATE users SET is_foreman = 1 WHERE user_id = ?', (user_id, ))

    def set_user_full_name(self, user_id, full_name):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('UPDATE users SET full_name = ? WHERE user_id = ?', (full_name, user_id,))


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
        
    def user_is_foreman(self, user_id: int):
        data = self.__db.db_read('SELECT is_foreman FROM users WHERE user_id = ?', (user_id,))
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
    
    def write_new_object(self, user_id, object_name):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('INSERT INTO construction_objects (object_name) VALUES (?)', (object_name, ))

    def get_all_objects(self, user_id):
        if not self.user_is_existed(user_id):
            return None
        return self.__db.db_read('SELECT user_id, object_name FROM construction_objects', ())
    
    def get_foreman_objects(self, user_id):
        if not self.user_is_existed(user_id):
            return None
        return self.__db.db_read('SELECT row_id, object_name FROM construction_objects WHERE user_id = ?', (user_id, ))
    

    def get_name_from_user_id(self, user_id):
        if not self.user_is_existed(user_id):
            return None
        return self.__db.db_read('SELECT full_name FROM users WHERE user_id = ?', (user_id, ))
    
    def get_foremans(self, user_id):
        if not self.user_is_existed(user_id):
            return None
        return self.__db.db_read('SELECT user_id, full_name FROM users WHERE is_foreman = True', ())
    
    def attach_foreman_to_object(self, user_id, object_name):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('UPDATE construction_objects SET user_id = ? WHERE object_name = ?', (user_id, object_name, ))
    
    def delete_object(self, user_id, object_name):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('DELETE FROM construction_objects WHERE object_name = ?', (object_name, ))
    

    def add_work_categories(self, user_id, object_id, name):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('INSERT INTO work_categories (object_id, name) VALUES (?, ?)', (object_id, name,))

    def get_work_categories(self, user_id, object_id):
        if not self.user_is_existed(user_id):
            return None
        return self.__db.db_read('SELECT row_id, name FROM work_categories WHERE object_id = ?', (object_id,))

    def delete_work_categories(self, user_id, category_id):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('DELETE FROM work_categories WHERE row_id = ?', (category_id,))

    def add_work_subcategories(self, user_id, category_id, name):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('INSERT INTO work_subcategories (category_id, name) VALUES (?, ?)', (category_id, name,))
    
    def get_work_subcategories(self, user_id, category_id):
        if not self.user_is_existed(user_id):
            return None
        return self.__db.db_read('SELECT row_id, name FROM work_subcategories WHERE category_id = ?', (category_id,))

    def delete_work_subcategories(self, user_id, subcategory_id):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('DELETE FROM work_subcategories WHERE row_id = ?', (subcategory_id,))

    def add_work_type(self, user_id, subcategory_id, name, unit, volume, cost):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('INSERT INTO work_types (subcategory_id, name, unit, volume, cost) VALUES (?, ?, ?, ?, ?)', (subcategory_id, name, unit, volume, cost,))
    
    def get_work_type(self, user_id, subcategory_id):
        if not self.user_is_existed(user_id):
            return None
        return self.__db.db_read('SELECT row_id, name FROM work_types WHERE subcategory_id = ?', (subcategory_id,))
    
    def delete_work_type(self, user_id, work_type_id):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('DELETE FROM work_types WHERE row_id = ?', (work_type_id,))

    def add_work_material(self, user_id, work_type_id, name, norm, unit, counterparty, registration_number, volume, cost):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('INSERT INTO work_materials (work_type_id, name, norm, unit, counterparty, state_registration_number_vehicle, volume, cost) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (work_type_id, name, norm, unit, counterparty, registration_number, volume, cost,))

    def get_work_material(self, user_id, work_type_id):
        if not self.user_is_existed(user_id):
            return None
        return self.__db.db_read('SELECT row_id, name, norm, unit, counterparty, state_registration_number_vehicle, volume, cost FROM work_materials WHERE work_type_id = ?', (work_type_id,))
    
    def delete_work_material(self, user_id, row_id):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('DELETE FROM work_materials WHERE row_id = ?', (row_id,))

    def db_export_xlsx(self):
        try:
            d = {'Имя': [], 'Фамилия': [], 'Никнейм': [], 'Номер телефона': []}
            users = self.__db.db_read('SELECT full_name, nick_name, phone FROM users', ())
            if len(users) > 0:
                for user in users:
                    for info in range(len(list(user))):
                        d[self.__fields_user[info]].append(user[info])
                df = pd.DataFrame(d)
                df.to_excel(self.__config.get_config()['xlsx_path'], sheet_name='Пользователи', index=False)
        except Exception as e:
            return print(e)