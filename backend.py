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
                    (user_id, full_name, nick_name, json.dumps({"index": None, 
                                                                "attach_object_name": None,
                                                                "full_name": None,
                                                                "object_id": None,
                                                                "admin_object_id": None,
                                                                "category_id": None,
                                                                "subcategory_id": None,
                                                                "work_type_id": None,
                                                                "work_type_name": None,
                                                                "work_type_unit": None,
                                                                "work_type_volume": None,
                                                                "material_date": None,
                                                                "material_name": None,
                                                                "material_norm": None,
                                                                "material_unit": None,
                                                                "material_counterparty": None,
                                                                "material_registration_number": None,
                                                                "material_volume": None,
                                                                "technique_name": None,
                                                                "technique_contragent": None,
                                                                "technique_number": None,
                                                                "technique_unit": None,
                                                                "technique_volume": None,
                                                                "coming_date": None,
                                                                "coming_name": None,
                                                                "coming_unit": None,
                                                                "coming_volume": None,
                                                                "coming_supplier": None}), is_admin, is_foreman))
                
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

    def add_work_material(self, user_id, work_type_id, date, name, norm, unit, counterparty, registration_number, volume, cost):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('INSERT INTO work_materials (work_type_id, date, name, norm, unit, counterparty, state_registration_number_vehicle, volume, cost) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (work_type_id, date, name, norm, unit, counterparty, registration_number, volume, cost,))

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

    def get_from_list_coming(self, user_id, object_id):
        if not self.user_is_existed(user_id):
            return None
        return self.__db.db_read('SELECT row_id, name FROM list_coming WHERE object_id = ?', (object_id,))

    def delete_from_list_coming(self, user_id, row_id):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('DELETE FROM list_coming WHERE row_id = ?', (row_id,))

    def add_unit_and_norm(self, user_id, unit, norm, work_type_id):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('UPDATE work_materials SET norm = ? and unit = ? WHERE work_type_id = ?', (norm, unit, work_type_id,))
    
    def db_export_object_report(self, object_id):
        """Экспортирует данные объекта строительства в XLSX-файл с правильной структурой сумм"""
        try:
            from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
            from openpyxl.utils import get_column_letter
            from collections import defaultdict
            import os
            from datetime import datetime

            # Стили оформления
            styles = {
                'object_name': PatternFill(start_color='FFA500', end_color='FFA500', fill_type='solid'),
                'header': PatternFill(start_color='70AD47', end_color='70AD47', fill_type='solid'),
                'category': PatternFill(start_color='548235', end_color='548235', fill_type='solid'),
                'subcategory': PatternFill(start_color='A9D08E', end_color='A9D08E', fill_type='solid'),
                'work_type': PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid'),
                'material_font': Font(color='0070C0'),
                'header_font': Font(bold=True, color='FFFFFF'),
                'category_font': Font(bold=True, color='FFFFFF'),
                'subcategory_font': Font(bold=True, color='000000'),
                'border': Border(left=Side(style='thin'), right=Side(style='thin'), 
                            top=Side(style='thin'), bottom=Side(style='thin')),
                'number_format': '0.0000',
                'money_format': '#,##0.00',
                'date_format': 'YYYY-MM-DD'
            }

            def safe_float(value):
                """Преобразует значение в float с обработкой русских форматов"""
                try:
                    if value is None or value == '':
                        return 0.0
                    if isinstance(value, str):
                        value = value.replace(' ', '').replace(',', '.')
                        cleaned = ''.join([c for c in value if c.isdigit() or c in '.-'])
                        if not cleaned:
                            return 0.0
                        value = cleaned
                    return round(float(value), 4)
                except (ValueError, TypeError) as e:
                    print(f"Ошибка преобразования '{value}': {e}")
                    return 0.0

            def safe_add(a, b):
                """Безопасное сложение с обработкой None"""
                return (a or 0.0) + (b or 0.0)

            report_filename = "report.xlsx"
            
            object_data = self.__db.db_read(
                'SELECT row_id, object_name FROM construction_objects WHERE row_id = ?', 
                (object_id,)
            )
            if not object_data:
                print(f"Объект с ID {object_id} не найден")
                return False
                    
            obj_id, obj_name = object_data[0]

            # Создаем новую книгу Excel
            from openpyxl import Workbook
            wb = Workbook()
            wb.remove(wb.active)

            # Создаем листы
            ws_prorab = wb.create_sheet("Прораб")
            ws_material = wb.create_sheet("Материал-Работа")
            ws_tech = wb.create_sheet("Техника")
            ws_coming = wb.create_sheet("Приход")

            # ==================== ЛИСТ "ПРОРАБ" ====================
            works_data = []
            all_materials = []
            columns = [
                '№ п/п', 'Наименование работ/материала', 'норма', 'ед.изм.',
                'контрагент', 'гос.№ (техники)', 'объем', 'цена', 'сумма'
            ]
            
            # Инициализация с явным указанием 0.0 для сумм
            works_data.append([f"Наименование объекта: {obj_name}"] + [None]*7 + [0.0])
            works_data.append([None]*9)
            works_data.append(columns)
            
            # Получаем категории
            categories = self.__db.db_read(
                'SELECT row_id, name FROM work_categories WHERE object_id = ? ORDER BY row_id',
                (obj_id,))
            
            # Словари для хранения данных
            category_rows = {}
            subcategory_rows = {}
            work_rows = {}

            for cat_idx, (cat_id, cat_name) in enumerate(categories, 1):
                # Добавляем категорию с инициализацией суммы
                works_data.append([f"{cat_idx}", cat_name] + [None]*7 + [0.0])
                category_rows[f"{cat_idx}"] = len(works_data) - 1
                
                subcategories = self.__db.db_read(
                    'SELECT row_id, name FROM work_subcategories WHERE category_id = ? ORDER BY row_id',
                    (cat_id,))
                
                for sub_idx, (subcat_id, subcat_name) in enumerate(subcategories, 1):
                    # Добавляем подкатегорию с инициализацией суммы
                    works_data.append([f"{cat_idx}.{sub_idx}", subcat_name] + [None]*7 + [0.0])
                    subcategory_rows[f"{cat_idx}.{sub_idx}"] = len(works_data) - 1
                    
                    work_types = self.__db.db_read(
                        'SELECT row_id, name, unit, volume, cost FROM work_types WHERE subcategory_id = ? ORDER BY row_id',
                        (subcat_id,))
                    
                    for wt_idx, (wt_id, wt_name, wt_unit, wt_volume, wt_cost) in enumerate(work_types, 1):
                        # Добавляем работу с расчетом суммы
                        work_sum = safe_float(wt_volume) * safe_float(wt_cost)
                        works_data.append([
                            f"{cat_idx}.{sub_idx}.{wt_idx}",
                            wt_name,
                            None,
                            wt_unit,
                            None, None,
                            safe_float(wt_volume),
                            safe_float(wt_cost),
                            work_sum
                        ])
                        work_row_idx = len(works_data) - 1
                        work_rows[f"{cat_idx}.{sub_idx}.{wt_idx}"] = work_row_idx
                        
                        # Получаем материалы для этой работы
                        materials = self.__db.db_read(
                            'SELECT date, name, norm, unit, counterparty, state_registration_number_vehicle, volume, cost '
                            'FROM work_materials WHERE work_type_id = ? ORDER BY date',
                            (wt_id,))
                        
                        # Группируем материалы внутри работы
                        work_materials = defaultdict(lambda: {
                            'volume': 0.0,
                            'cost': 0.0,
                            'sum': 0.0,
                            'norm': None,
                            'unit': None,
                            'counterparty': None,
                            'reg_number': None,
                            'count': 0
                        })
                        
                        for mat in materials:
                            mat_key = (mat[1].strip().lower(), mat[3], mat[4], mat[5])  # Группировка по ключу
                            mat_volume = safe_float(mat[6])
                            mat_cost = safe_float(mat[7])
                            
                            work_materials[mat_key]['volume'] += mat_volume
                            work_materials[mat_key]['cost'] = mat_cost
                            work_materials[mat_key]['sum'] += mat_volume * mat_cost
                            work_materials[mat_key]['count'] += 1
                            
                            # Сохраняем последние значения
                            if work_materials[mat_key]['norm'] is None:
                                work_materials[mat_key]['norm'] = mat[2]
                            if work_materials[mat_key]['unit'] is None:
                                work_materials[mat_key]['unit'] = mat[3]
                            if work_materials[mat_key]['counterparty'] is None:
                                work_materials[mat_key]['counterparty'] = mat[4]
                            if work_materials[mat_key]['reg_number'] is None:
                                work_materials[mat_key]['reg_number'] = mat[5]
                            
                            # Сохраняем для листа "Материал-Работа"
                            all_materials.append({
                                'date': mat[0],
                                'name': mat[1],
                                'norm': mat[2],
                                'unit': mat[3],
                                'counterparty': mat[4],
                                'state_reg_number': mat[5],
                                'volume': mat_volume,
                                'cost': mat_cost,
                                'work_id': f"{cat_idx}.{sub_idx}.{wt_idx}"
                            })
                        
                        # Добавляем объединенные материалы после работы
                        for mat_key, mat_data in work_materials.items():
                            if mat_data['count'] > 0:
                                works_data.append([
                                    None,
                                    mat_key[0].title(),  # Восстанавливаем регистр
                                    mat_data['norm'],
                                    mat_data['unit'],
                                    mat_data['counterparty'],
                                    mat_data['reg_number'],
                                    mat_data['volume'],
                                    mat_data['cost'],
                                    mat_data['sum']
                                ])
                                # Безопасное добавление суммы материала к работе
                                works_data[work_row_idx][8] = safe_add(works_data[work_row_idx][8], mat_data['sum'])
                        
                        # Безопасное добавление суммы работы к подкатегории
                        subcat_row_idx = subcategory_rows[f"{cat_idx}.{sub_idx}"]
                        works_data[subcat_row_idx][8] = safe_add(works_data[subcat_row_idx][8], works_data[work_row_idx][8])
                    
                    # Безопасное добавление суммы подкатегории к категории
                    cat_row_idx = category_rows[f"{cat_idx}"]
                    works_data[cat_row_idx][8] = safe_add(works_data[cat_row_idx][8], works_data[subcategory_rows[f"{cat_idx}.{sub_idx}"]][8])
                
                # Безопасное добавление суммы категории к общему итогу
                works_data[0][8] = safe_add(works_data[0][8], works_data[category_rows[f"{cat_idx}"]][8])

            # Записываем данные в лист "Прораб"
            for row in works_data:
                ws_prorab.append(row)
            
            # Применяем стили к листу "Прораб"
            for row in ws_prorab.iter_rows():
                for cell in row:
                    cell.border = styles['border']
                    
                    if cell.row == 1:
                        cell.fill = styles['object_name']
                        cell.font = Font(bold=True)
                    elif cell.row == 3:
                        cell.fill = styles['header']
                        cell.font = styles['header_font']
                    elif cell.row > 3 and isinstance(works_data[cell.row-1][0], str) and '.' not in str(works_data[cell.row-1][0]):
                        cell.fill = styles['category']
                        cell.font = styles['category_font']
                    elif cell.row > 3 and isinstance(works_data[cell.row-1][0], str) and str(works_data[cell.row-1][0]).count('.') == 1:
                        cell.fill = styles['subcategory']
                        cell.font = styles['subcategory_font']
                    elif cell.row > 3 and isinstance(works_data[cell.row-1][0], str) and str(works_data[cell.row-1][0]).count('.') == 2:
                        cell.fill = styles['work_type']
                        cell.font = Font()
                    elif cell.row > 3 and cell.column == 2 and works_data[cell.row-1][0] is None:
                        cell.font = styles['material_font']
                    
                    if isinstance(cell.value, (int, float)):
                        if cell.column in [7, 8]:
                            cell.number_format = styles['number_format']
                        elif cell.column == 9:
                            cell.number_format = styles['money_format']
                    
                    cell.alignment = Alignment(horizontal='left', vertical='center')

            # Настройка ширины столбцов
            for col, width in {'A':8, 'B':40, 'C':10, 'D':8, 'E':15, 'F':15, 'G':12, 'H':12, 'I':12}.items():
                ws_prorab.column_dimensions[col].width = width

            # ==================== ЛИСТ "МАТЕРИАЛ-РАБОТА" ====================
            materials_data = []
            materials_columns = [
                'Дата', 'Наименование материала', 'Норма', 'ед.изм.',
                'Контрагент', 'Гос.№ техники', 'Объем', 'Цена', 'Работа'
            ]
            
            materials_data.append([f"Наименование объекта: {obj_name}"] + [None]*8)
            materials_data.append([None]*9)
            materials_data.append(materials_columns)

            # Сортируем материалы по дате и работе
            all_materials_sorted = sorted(all_materials, key=lambda x: (x['date'], x['work_id']))
            
            # Добавляем все материалы с указанием работы
            for mat in all_materials_sorted:
                materials_data.append([
                    mat['date'],
                    mat['name'],
                    mat['norm'],
                    mat['unit'],
                    mat['counterparty'],
                    mat['state_reg_number'],
                    mat['volume'],
                    mat['cost'],
                    mat['work_id']
                ])

            # Записываем данные в лист "Материал-Работа"
            for row in materials_data:
                ws_material.append(row)
            
            # Применяем стили к листу "Материал-Работа"
            for row in ws_material.iter_rows():
                for cell in row:
                    cell.border = styles['border']
                    
                    if cell.row == 1:
                        cell.fill = styles['object_name']
                        cell.font = Font(bold=True)
                    elif cell.row == 3:
                        cell.fill = styles['header']
                        cell.font = styles['header_font']
                    elif cell.column == 1 and cell.row > 3:
                        cell.number_format = styles['date_format']
                    
                    if isinstance(cell.value, (int, float)):
                        if cell.column in [7, 8]:
                            cell.number_format = styles['number_format']
                    
                    cell.alignment = Alignment(horizontal='left', vertical='center')

            # Настройка ширины столбцов
            for col, width in {'A':12, 'B':40, 'C':10, 'D':8, 'E':15, 'F':15, 'G':12, 'H':12, 'I':15}.items():
                ws_material.column_dimensions[col].width = width

            # ==================== ЛИСТ "ТЕХНИКА" ====================
            tech_data = []
            tech_columns = [
                'Наименование техники', 'Контрагент', 'Гос.№ техники', 
                'Ед.изм.', 'Объем (часы)', 'Цена за час', 'Сумма'
            ]
            
            techniques = self.__db.db_read(
                'SELECT name, counterparty, state_registration_number_vehicle, unit, volume, cost '
                'FROM list_technique WHERE object_id = ?',
                (obj_id,))
            
            for tech in techniques:
                tech_sum = safe_float(tech[4]) * safe_float(tech[5])
                tech_data.append([
                    tech[0],
                    tech[1],
                    tech[2],
                    tech[3],
                    safe_float(tech[4]),
                    safe_float(tech[5]),
                    tech_sum
                ])

            # Заголовки
            ws_tech.append(tech_columns)
            # Данные
            for row in tech_data:
                ws_tech.append(row)

            # Применяем стили к листу "Техника"
            for row in ws_tech.iter_rows():
                for cell in row:
                    cell.border = styles['border']
                    
                    if cell.row == 1:
                        cell.fill = styles['header']
                        cell.font = styles['header_font']
                    
                    if isinstance(cell.value, (int, float)):
                        if cell.column in [5, 6]:
                            cell.number_format = styles['number_format']
                        elif cell.column == 7:
                            cell.number_format = styles['money_format']
                    
                    cell.alignment = Alignment(horizontal='left', vertical='center')

            # Настройка ширины столбцов
            for col, width in {'A':25, 'B':20, 'C':15, 'D':10, 'E':12, 'F':12, 'G':12}.items():
                ws_tech.column_dimensions[col].width = width

            # ==================== ЛИСТ "ПРИХОД" ====================
            coming_data = []
            coming_columns = ['№', 'Дата', 'Наименование', 'Ед.изм.', 'Объем', 'Поставщик', 'Цена', 'ИТОГО', 'ПРИМЕЧАНИЕ']
            
            comings = self.__db.db_read(
                'SELECT date, name, unit, volume, supplier, cost '
                'FROM list_coming WHERE object_id = ? ORDER BY date',
                (obj_id,))
            
            for idx, (date, name, unit, volume, supplier, cost) in enumerate(comings, 1):
                coming_sum = safe_float(volume) * safe_float(cost)
                coming_data.append([
                    idx,
                    datetime.strptime(date, '%Y-%m-%d').date() if isinstance(date, str) else date,
                    name,
                    unit,
                    safe_float(volume),
                    supplier,
                    safe_float(cost),
                    coming_sum,
                    'приход'
                ])

            # Заголовки
            ws_coming.append(coming_columns)
            # Данные
            for row in coming_data:
                ws_coming.append(row)

            # Применяем стили к листу "Приход"
            for row in ws_coming.iter_rows():
                for cell in row:
                    cell.border = styles['border']
                    
                    if cell.row == 1:
                        cell.fill = styles['header']
                        cell.font = styles['header_font']
                    elif cell.column == 2 and cell.row > 1:
                        cell.number_format = styles['date_format']
                    
                    if isinstance(cell.value, (int, float)):
                        if cell.column in [5, 7]:
                            cell.number_format = styles['number_format']
                        elif cell.column == 8:
                            cell.number_format = styles['money_format']
                    
                    cell.alignment = Alignment(horizontal='left', vertical='center')

            # Настройка ширины столбцов
            for col, width in {'A':5, 'B':12, 'C':30, 'D':8, 'E':12, 'F':20, 'G':12, 'H':12, 'I':15}.items():
                ws_coming.column_dimensions[col].width = width

            # Устанавливаем первый лист активным
            wb.active = 0

            # Сохраняем файл
            wb.save(report_filename)

            if os.path.exists(report_filename) and os.path.getsize(report_filename) > 0:
                return True
            return False
            
        except Exception as e:
            print(f"Критическая ошибка при экспорте: {str(e)}")
            import traceback
            traceback.print_exc()
            if os.path.exists(report_filename):
                try:
                    os.remove(report_filename)
                except:
                    pass
            return False