import os
import sqlite3


class DB:
    def __init__(self, path, lock):
        super(DB, self).__init__()
        self.__lock = lock
        self.__db_path = path
        self.__cursor = None
        self.__db = None
        self.init()

    def init(self):
        if not os.path.exists(self.__db_path):
            self.__db = sqlite3.connect(self.__db_path, check_same_thread=False)
            self.__cursor = self.__db.cursor()
            self.__cursor.execute('PRAGMA foreign_keys = ON')
            self.__cursor.execute('''
            CREATE TABLE IF NOT EXISTS users(
                row_id INTEGER primary key autoincrement not null,
                user_id INTEGER NOT NULL,
                full_name TEXT,
                nick_name TEXT,
                is_admin BOOL,
                is_foreman BOOL,
                topic_id INTEGER,
                system_data TEXT,
                UNIQUE(user_id)
                )
            ''')
            
            self.__cursor.execute('''
            CREATE TABLE IF NOT EXISTS construction_objects(
                row_id INTEGER primary key autoincrement not null,
                user_id INTEGER,
                object_name TEXT,
                UNIQUE(row_id)
                )
            ''')
            
            self.__cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_categories(
                row_id INTEGER primary key autoincrement not null,
                object_id INTEGER NOT NULL,
                name TEXT,
                FOREIGN KEY (object_id) REFERENCES construction_objects(row_id) ON DELETE CASCADE,
                UNIQUE(row_id)
                )
            ''')
            
            self.__cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_subcategories(
                row_id INTEGER primary key autoincrement not null,
                category_id INTEGER NOT NULL,
                name TEXT,
                FOREIGN KEY (category_id) REFERENCES work_categories(row_id) ON DELETE CASCADE,
                UNIQUE(row_id)
                )
            ''')
            
            self.__cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_types(
                row_id INTEGER primary key autoincrement not null,
                subcategory_id INTEGER NOT NULL,
                name TEXT,
                unit TEXT,
                volume TEXT,
                cost TEXT,
                FOREIGN KEY (subcategory_id) REFERENCES work_subcategories(row_id) ON DELETE CASCADE,
                UNIQUE(row_id)
                )
            ''')
            
            self.__cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_materials(
                row_id INTEGER primary key autoincrement not null,
                work_type_id INTEGER NOT NULL,
                date TEXT,
                name TEXT,
                norm TEXT,
                unit TEXT,
                counterparty TEXT,
                state_registration_number_vehicle TEXT,
                volume TEXT,
                cost TEXT,
                FOREIGN KEY (work_type_id) REFERENCES work_types(row_id) ON DELETE CASCADE,
                UNIQUE(row_id)
                )
            ''')
            
            self.__cursor.execute('''
            CREATE TABLE IF NOT EXISTS list_technique(
                row_id INTEGER primary key autoincrement not null,
                object_id INTEGER NOT NULL,
                name TEXT,
                counterparty TEXT,
                state_registration_number_vehicle TEXT,
                unit TEXT,
                volume TEXT,
                cost TEXT,
                FOREIGN KEY (object_id) REFERENCES construction_objects(row_id) ON DELETE CASCADE,
                UNIQUE(row_id)
                )
            ''')
            
            self.__cursor.execute('''
            CREATE TABLE IF NOT EXISTS list_coming(
                row_id INTEGER primary key autoincrement not null,
                object_id INTEGER NOT NULL,
                date TEXT,
                name TEXT,
                unit TEXT,
                volume TEXT,
                supplier TEXT,
                cost TEXT,
                FOREIGN KEY (object_id) REFERENCES construction_objects(row_id) ON DELETE CASCADE,
                UNIQUE(row_id)
                )
            ''')
            
            self.__db.commit()
        else:
            self.__db = sqlite3.connect(self.__db_path, check_same_thread=False)
            self.__cursor = self.__db.cursor()
            self.__cursor.execute('PRAGMA foreign_keys = ON')

    def db_write(self, queri, args):
        self.set_lock()
        self.__cursor.execute(queri, args)
        status = self.__cursor.lastrowid
        self.__db.commit()
        self.realise_lock()
        return status

    def db_read(self, queri, args):
        self.set_lock()
        self.__cursor.execute(queri, args)
        self.realise_lock()
        return self.__cursor.fetchall()

    def set_lock(self):
        self.__lock.acquire(True)

    def realise_lock(self):
        self.__lock.release()