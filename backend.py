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
        self.__db.db_write('INSERT INTO list_coming (object_id, date, name, unit, volume, supplier, cost) VALUES (?, ?, ?, ?, ?, ?)', (object_id, date, name, unit, volume, supplier, cost))

    def db_export_object_report(self, object_id):
        try:
            from openpyxl.styles import PatternFill, Font, Alignment
            from openpyxl.utils import get_column_letter
            
            # Создаем Excel writer
            writer = pd.ExcelWriter(self.__dump_path_xlsx, engine='openpyxl')
            
            # Определяем стили (остаются те же, что и в db_export_full_report)
            header_fill = PatternFill(start_color='D9D9D9', end_color='D9D9D9', fill_type='solid')
            header_font = Font(bold=True)
            object_header_fill = PatternFill(start_color='B8CCE4', end_color='B8CCE4', fill_type='solid')
            object_header_font = Font(bold=True)
            category_fill = PatternFill(start_color='DCE6F1', end_color='DCE6F1', fill_type='solid')
            category_font = Font(bold=True)
            subcategory_fill = PatternFill(start_color='E4DFEC', end_color='E4DFEC', fill_type='solid')
            alignment_center = Alignment(horizontal='center', vertical='center')
            alignment_left = Alignment(horizontal='left', vertical='center')
            money_format = '#,##0.00'
            
            def safe_float(value):
                try:
                    return float(value) if value is not None and str(value).strip() != '' else 0.0
                except (ValueError, TypeError):
                    return 0.0
            
            # Получаем данные только по выбранному объекту
            object_data = self.__db.db_read('SELECT row_id, object_name FROM construction_objects WHERE row_id = ?', (object_id,))
            
            if not object_data:
                return False
                
            obj_id, obj_name = object_data[0]
            
            # Лист "прораб" - работы и материалы
            works_data = []
            columns = [
                '№ п/п',
                'Наименование работ/материала',
                'норма',
                'ед.изм.',
                'контрагент',
                'гос.№ (техники)',
                'объем',
                'цена',
                'сумма'
            ]
            
            # Добавляем заголовок объекта
            works_data.append([f"наименование объекта: {obj_name}"] + [None]*8)
            works_data.append([None]*9)  # Пустая строка
            
            # Добавляем заголовки таблицы
            works_data.append(columns)
            
            # Получаем категории работ для объекта
            categories = self.__db.db_read(
                'SELECT row_id, name FROM work_categories WHERE object_id = ? ORDER BY row_id',
                (obj_id,))
            
            cat_counter = 1
            
            for cat_id, cat_name in categories:
                # Добавляем категорию
                works_data.append([str(cat_counter), cat_name] + [None]*7)
                
                # Получаем подкатегории
                subcategories = self.__db.db_read(
                    'SELECT row_id, name FROM work_subcategories WHERE category_id = ? ORDER BY row_id',
                    (cat_id,))
                
                sub_counter = 1
                
                for subcat_id, subcat_name in subcategories:
                    # Добавляем подкатегорию
                    works_data.append([f"{cat_counter}.{sub_counter}", subcat_name] + [None]*7)
                    
                    # Получаем типы работ
                    work_types = self.__db.db_read(
                        'SELECT row_id, name, unit, volume, cost FROM work_types WHERE subcategory_id = ? ORDER BY row_id',
                        (subcat_id,))
                    
                    wt_counter = 1
                    
                    for wt_id, wt_name, wt_unit, wt_volume, wt_cost in work_types:
                        # Добавляем тип работы
                        works_data.append([
                            f"{cat_counter}.{sub_counter}.{wt_counter}",
                            wt_name,
                            None,
                            wt_unit if wt_unit else None,
                            None, None,
                            safe_float(wt_volume),
                            safe_float(wt_cost),
                            safe_float(wt_volume) * safe_float(wt_cost)
                        ])
                        
                        # Получаем материалы
                        materials = self.__db.db_read(
                            'SELECT name, norm, unit, counterparty, state_registration_number_vehicle, volume, cost '
                            'FROM work_materials WHERE work_type_id = ? ORDER BY row_id',
                            (wt_id,))
                        
                        for mat in materials:
                            works_data.append([
                                None,
                                mat[0] if mat[0] else None,
                                safe_float(mat[1]),
                                mat[2] if mat[2] else None,
                                mat[3] if mat[3] else None,
                                mat[4] if mat[4] else None,
                                safe_float(mat[5]),
                                safe_float(mat[6]),
                                safe_float(mat[5]) * safe_float(mat[6])
                            ])
                        
                        wt_counter += 1
                    sub_counter += 1
                cat_counter += 1
            
            # Создаем DataFrame для листа "прораб"
            works_df = pd.DataFrame(works_data, columns=columns)
            
            # Записываем данные в Excel
            works_df.to_excel(writer, sheet_name='прораб', index=False, header=False)
            
            # Применяем стили к листу "прораб"
            workbook = writer.book
            worksheet = writer.sheets['прораб']
            
            # Настраиваем ширину столбцов
            for col in range(1, 10):
                worksheet.column_dimensions[get_column_letter(col)].width = 15
            worksheet.column_dimensions['B'].width = 50  # Шире для наименования
            
            # Применяем стили (аналогично db_export_full_report)
            for row_idx, row in enumerate(worksheet.iter_rows(), 1):
                for cell in row:
                    cell.alignment = alignment_left
                    
                    if cell.value is None:
                        continue
                        
                    cell_value_str = str(cell.value)
                    
                    # Заголовок объекта
                    if row_idx == 1 and cell.column == 1:
                        cell.fill = object_header_fill
                        cell.font = object_header_font
                    # Заголовки таблицы
                    elif row_idx == 3:
                        cell.fill = header_fill
                        cell.font = header_font
                        cell.alignment = alignment_center
                    # Категории (1, 2)
                    elif cell.column == 1 and cell_value_str.isdigit():
                        cell.fill = category_fill
                        cell.font = category_font
                    # Подкатегории (1.1, 1.2)
                    elif cell.column == 1 and '.' in cell_value_str and cell_value_str.count('.') == 1:
                        cell.fill = subcategory_fill
                    
                    # Форматирование числовых значений
                    if cell.column_letter in ('G', 'H', 'I'):
                        cell.number_format = money_format
                        if cell.column_letter == 'I':
                            cell.font = Font(bold=True)
            
            # Лист "список техники"
            tech_data = []
            tech_columns = [
                'Наименование объекта',
                'Наименование техники',
                'Контрагент',
                'Гос.№ техники',
                'Ед.изм.',
                'Объем (кол-во часов)',
                'Цена за час'
            ]
            
            techniques = self.__db.db_read(
                'SELECT name, counterparty, state_registration_number_vehicle, unit, volume, cost '
                'FROM list_technique WHERE object_id = ?',
                (obj_id,))
            
            for tech in techniques:
                tech_data.append([
                    obj_name,
                    tech[0] if tech[0] else None,
                    tech[1] if tech[1] else None,
                    tech[2] if tech[2] else None,
                    tech[3] if tech[3] else None,
                    safe_float(tech[4]),
                    safe_float(tech[5])
                ])
            
            tech_df = pd.DataFrame(tech_data, columns=tech_columns)
            tech_df.to_excel(writer, sheet_name='список техники', index=False)
            
            # Лист "приход"
            coming_data = []
            coming_columns = [
                '№',
                'Дата',
                'Наименование материала',
                'Ед.изм.',
                'Объем',
                'Поставщик',
                'Цена без НДС',
                'ИТОГО'
            ]
            coming_counter = 1
            
            comings = self.__db.db_read(
                'SELECT date, name, unit, volume, supplier, cost '
                'FROM list_coming WHERE object_id = ? ORDER BY date',
                (obj_id,))
            
            for come in comings:
                coming_data.append([
                    coming_counter,
                    come[0] if come[0] else None,
                    come[1] if come[1] else None,
                    come[2] if come[2] else None,
                    safe_float(come[3]),
                    come[4] if come[4] else None,
                    safe_float(come[5]),
                    safe_float(come[3]) * safe_float(come[5])
                ])
                coming_counter += 1
            
            coming_df = pd.DataFrame(coming_data, columns=coming_columns)
            coming_df.to_excel(writer, sheet_name='приход', index=False)
            
            # Сохраняем файл
            writer.close()
            return True
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return False