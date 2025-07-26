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
                    (user_id, full_name, nick_name, json.dumps({"index": None, "attach_object_name": None, "full_name": None, "object_id": None, "category_id": None, "subcategory_id": None, "work_type_id": None, "work_type_name": None, "work_type_unit": None, "work_type_volume": None, "material_name": None, "material_norm": None, "material_unit": None, "material_counterparty": None, "material_registration_number": None, "material_volume": None, "technique_name": None, "technique_contragent": None, "technique_number": None, "technique_unit": None, "technique_volume": None, "coming_date": None, "coming_name": None, "coming_unit": None, "coming_volume": None, "coming_supplier": None}), is_admin, is_foreman))
                
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
    
    def get_admin_objects(self, user_id):
        if not self.user_is_existed(user_id):
            return None
        return self.__db.db_read('SELECT row_id, object_name FROM construction_objects', ())

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

    def add_technique(self, user_id, object_id, technique_name, technique_contagent, technique_number, technique_unit, technique_volume, technique_cost):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('INSERT INTO list_technique (object_id, name, counterparty, state_registration_number_vehicle, unit, volume, cost) VALUES (?, ?, ?, ?, ?, ?, ?)', (object_id, technique_name, technique_contagent, technique_number, technique_unit, technique_volume, technique_cost,))
    
    def add_list_coming(self, user_id, object_id, date, name, unit, volume, supplier, cost):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('INSERT INTO list_coming (object_id, date, name, unit, volume, supplier, cost) VALUES (?, ?, ?, ?, ?, ?, ?)', (object_id, date, name, unit, volume, supplier, cost))

    def db_export_object_report(self, object_id):
        """Экспортирует данные объекта строительства в XLSX-файл"""
        try:
            # Импорт необходимых библиотек
            from openpyxl.styles import PatternFill, Font, Alignment
            from openpyxl.utils import get_column_letter
            import pandas as pd
            import os

            # Улучшенная функция преобразования чисел
            def safe_float(value):
                """Преобразует значение в float с обработкой русских форматов"""
                try:
                    if value is None or value == '':
                        return 0.0
                    if isinstance(value, str):
                        # Удаляем все пробелы и заменяем запятые на точки
                        value = value.replace(' ', '').replace(',', '.')
                        # Удаляем все нечисловые символы кроме точки и минуса
                        cleaned = ''.join([c for c in value if c.isdigit() or c in '.-'])
                        if not cleaned:
                            return 0.0
                        value = cleaned
                    return round(float(value), 4)
                except (ValueError, TypeError) as e:
                    print(f"Ошибка преобразования '{value}': {e}")
                    return 0.0

            # 1. Подготовка файла отчета
            report_filename = "report.xlsx"
            
            # 2. Получение данных объекта
            object_data = self.__db.db_read(
                'SELECT row_id, object_name FROM construction_objects WHERE row_id = ?', 
                (object_id,)
            )
            if not object_data:
                print(f"Объект с ID {object_id} не найден")
                return False
                
            obj_id, obj_name = object_data[0]

            # 3. Создание Excel-файла
            with pd.ExcelWriter(report_filename, engine='openpyxl') as writer:
                # Создаем workbook вручную, чтобы контролировать листы
                workbook = writer.book
                
                # Настройки стилей
                header_fill = PatternFill(start_color='D9D9D9', fill_type='solid')
                header_font = Font(bold=True)
                alignment = Alignment(horizontal='left', vertical='center')
                number_format = '0.0000'

                # 4. Лист "Прораб" (основной лист)
                works_data = []
                columns = [
                    '№ п/п', 'Наименование работ/материала', 'норма', 'ед.изм.',
                    'контрагент', 'гос.№ (техники)', 'объем', 'цена', 'сумма'
                ]
                
                # Заголовок
                works_data.append([f"Наименование объекта: {obj_name}"] + [None]*8)
                works_data.append([None]*9)
                works_data.append(columns)
                
                # Получаем иерархию работ
                categories = self.__db.db_read(
                    'SELECT row_id, name FROM work_categories WHERE object_id = ? ORDER BY row_id',
                    (obj_id,))
                
                for cat_idx, (cat_id, cat_name) in enumerate(categories, 1):
                    works_data.append([str(cat_idx), cat_name] + [None]*7)
                    
                    subcategories = self.__db.db_read(
                        'SELECT row_id, name FROM work_subcategories WHERE category_id = ? ORDER BY row_id',
                        (cat_id,))
                    
                    for sub_idx, (subcat_id, subcat_name) in enumerate(subcategories, 1):
                        works_data.append([f"{cat_idx}.{sub_idx}", subcat_name] + [None]*7)
                        
                        work_types = self.__db.db_read(
                            'SELECT row_id, name, unit, volume, cost FROM work_types WHERE subcategory_id = ? ORDER BY row_id',
                            (subcat_id,))
                        
                        for wt_idx, (wt_id, wt_name, wt_unit, wt_volume, wt_cost) in enumerate(work_types, 1):
                            # Добавляем тип работы
                            works_data.append([
                                f"{cat_idx}.{sub_idx}.{wt_idx}",
                                wt_name,
                                None,
                                wt_unit,
                                None, None,
                                safe_float(wt_volume),
                                safe_float(wt_cost),
                                safe_float(safe_float(wt_volume) * safe_float(wt_cost))
                            ])
                            
                            # Материалы для этого типа работы
                            materials = self.__db.db_read(
                                'SELECT name, norm, unit, counterparty, state_registration_number_vehicle, volume, cost '
                                'FROM work_materials WHERE work_type_id = ? ORDER BY row_id',
                                (wt_id,))
                            
                            for mat in materials:
                                works_data.append([
                                    None,
                                    mat[0],
                                    safe_float(mat[1]),
                                    mat[2],
                                    mat[3],
                                    mat[4],
                                    safe_float(mat[5]),
                                    safe_float(mat[6]),
                                    safe_float(safe_float(mat[5]) * safe_float(mat[6]))
                                ])

                # Создаем DataFrame и записываем в Excel
                works_df = pd.DataFrame(works_data, columns=columns)
                works_df.to_excel(writer, sheet_name='Прораб', index=False, header=False)
                
                # Форматируем лист
                worksheet = writer.sheets['Прораб']
                for col, width in {'A':8, 'B':40, 'C':10, 'D':8, 'E':15, 'F':15, 'G':12, 'H':12, 'I':12}.items():
                    worksheet.column_dimensions[col].width = width
                
                for row in worksheet.iter_rows():
                    for cell in row:
                        cell.alignment = alignment
                        if isinstance(cell.value, (int, float)):
                            cell.number_format = number_format

                # 5. Лист "Техника"
                tech_data = []
                tech_columns = [
                    'Наименование объекта', 'Наименование техники', 'Контрагент',
                    'Гос.№ техники', 'Ед.изм.', 'Объем (часы)', 'Цена за час'
                ]
                
                techniques = self.__db.db_read(
                    'SELECT name, counterparty, state_registration_number_vehicle, unit, volume, cost '
                    'FROM list_technique WHERE object_id = ?',
                    (obj_id,))
                
                for tech in techniques:
                    tech_data.append([
                        obj_name,
                        tech[0],
                        tech[1],
                        tech[2],
                        tech[3],
                        safe_float(tech[4]),
                        safe_float(tech[5])
                    ])
                
                tech_df = pd.DataFrame(tech_data, columns=tech_columns)
                tech_df.to_excel(writer, sheet_name='Техника', index=False)
                
                # 6. Лист "Приход"
                coming_data = []
                coming_columns = ['№', 'Дата', 'Наименование', 'Ед.изм.', 'Объем', 'Поставщик', 'Цена', 'ИТОГО', 'ПРИМЕЧАНИЕ']
                
                comings = self.__db.db_read(
                    'SELECT date, name, unit, volume, supplier, cost '
                    'FROM list_coming WHERE object_id = ? ORDER BY date',
                    (obj_id,))
                
                for idx, (date, name, unit, volume, supplier, cost) in enumerate(comings, 1):
                    coming_data.append([
                        idx,
                        date,
                        name,
                        unit,
                        safe_float(volume),
                        supplier,
                        safe_float(cost),
                        safe_float(safe_float(volume) * safe_float(cost)),
                        None
                    ])
                
                coming_df = pd.DataFrame(coming_data, columns=coming_columns)
                coming_df.to_excel(writer, sheet_name='Приход', index=False)
                
                # Убедимся, что все листы видны
                for sheet in workbook.worksheets:
                    sheet.sheet_view.tabSelected = True

            # Проверка результата
            if os.path.exists(report_filename) and os.path.getsize(report_filename) > 0:
                return True
            return False
            
        except Exception as e:
            print(f"Критическая ошибка при экспорте: {str(e)}")
            import traceback
            traceback.print_exc()
            # Пытаемся удалить битый файл, если он создался
            if os.path.exists(report_filename):
                try:
                    os.remove(report_filename)
                except:
                    pass
            return False