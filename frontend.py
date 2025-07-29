from telebot import types


class Bot_inline_btns:
    def __init__(self):
        super(Bot_inline_btns, self).__init__()
        self.__markup = types.InlineKeyboardMarkup(row_width=1)

    def unregister_buttons(self):
        one = types.InlineKeyboardButton('📄 Регистрация', callback_data="registration_foreman")
        self.__markup.add(one)
        return self.__markup
    
    def foreman_buttons(self):
        one = types.InlineKeyboardButton("📄 Выбрать объект", callback_data="foreman_select_objects")
        self.__markup.add(one)
        return self.__markup
    
    def manager_btns(self):
        one = types.InlineKeyboardButton('✅ Одобрить', callback_data="accept_reg")
        two = types.InlineKeyboardButton('❌ Отклонить', callback_data='reject_reg')
        self.__markup.add(one, two)
        return self.__markup
    
    
    def admin_buttons(self):
        one = types.InlineKeyboardButton("➕ Добавить объект", callback_data="add_object")
        two = types.InlineKeyboardButton("🗑️ Удалить объект", callback_data="delete_object")
        three = types.InlineKeyboardButton("❗️ Управление объектом", callback_data="control_object")
        four = types.InlineKeyboardButton("📇 Посмотреть объекты", callback_data="see_objects")
        five = types.InlineKeyboardButton("📌 Прикрепить прораба", callback_data="attach_foreman_to_object")
        six = types.InlineKeyboardButton('🔹 Экспорировать', callback_data="export_object_data")
        self.__markup.add(one, two, three, four, five, six)
        return self.__markup
    
    def choose_control_object(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'admin_object_control{i[0]}')
            markup.add(aero)
        return markup
    
    def control_object_panel(self):
        one = types.InlineKeyboardButton("📄 Управление категорией", callback_data="category_control")
        two = types.InlineKeyboardButton("📑 Управление подкатегорией", callback_data="subcategory_control")
        three = types.InlineKeyboardButton("📇 Управление видом работы", callback_data="work_type_control")
        four = types.InlineKeyboardButton("🌳 Управление материалом", callback_data="material_control")
        five = types.InlineKeyboardButton("📦 Управление приходом", callback_data="coming_control")
        six = types.InlineKeyboardButton("🚚 Управление техникой", callback_data="technical_control")
        self.__markup.add(one, two, three, four, five, six)
        return self.__markup
    
    def foreman_object_buttons(self):
        one = types.InlineKeyboardButton("🌳 Материалы", callback_data="add_materials")
        two = types.InlineKeyboardButton("🚚 Техника", callback_data="add_technique")
        three = types.InlineKeyboardButton("📦 Приход", callback_data="go_coming")
        four = types.InlineKeyboardButton("📇 Просмотреть отчет", callback_data="get_report")
        self.__markup.add(one, two, three, four)
        return self.__markup
    
    def material_control_buttons(self):
        one = types.InlineKeyboardButton("🗑️ Удалить материал", callback_data="delete_materials")
        two = types.InlineKeyboardButton("➕ Добавить норму и ед. измерения", callback_data="add_norma_and_unit")
        self.__markup.add(one, two)
        return self.__markup
    
    def control_category_buttons(self):
        one = types.InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category")
        two = types.InlineKeyboardButton("🗑️ Удалить категорию", callback_data="delete_category")
        self.__markup.add(one, two)
        return self.__markup

    def control_subcategory_buttons(self):
        one = types.InlineKeyboardButton("➕ Добавить подкатегорию", callback_data="add_subcategory")
        two = types.InlineKeyboardButton("🗑️ Удалить подкатегорию", callback_data="delete_subcategory")
        self.__markup.add(one, two)
        return self.__markup
    
    def control_work_type_buttons(self):
        one = types.InlineKeyboardButton("➕ Добавить тип работы", callback_data="add_type_work")
        two = types.InlineKeyboardButton("🗑️ Удалить тип работы", callback_data="delete_type_work")
        self.__markup.add(one, two)
        return self.__markup
    
    def control_coming_buttons(self):
        one = types.InlineKeyboardButton("Удалить приход", callback_data="delete_coming")
        self.__markup.add(one)
        return self.__markup
    
    def choose_coming_buttons(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'admin_delete_coming{i[0]}')
            markup.add(aero)
        return markup

    def choose_object_export(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'export_objectdata{i[0]}')
            markup.add(aero)
        return markup
    
    def delete_object_buttons(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'object{i[1]}')
            markup.add(aero)
        return markup
    
    def get_object_buttons(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'foreman_object{i[0]}')
            markup.add(aero)
        return markup
    
    def choose_object_to_attach(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'choose_object_attach{i[1]}')
            markup.add(aero)
        return markup
    
    def choose_foreman_to_attach(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'choose_foreman_attach{i[0]}')
            markup.add(aero)
        return markup
    
    def foreman_work_object(self):
        one = types.InlineKeyboardButton("➕ Добавить работу", callback_data="add_work")
        self.__markup.add(one)
        return self.__markup
    

    def delete_category_buttons(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'delete_work_category{i[0]}')
            markup.add(aero)
        return markup
    
    def delete_subcategory_buttons(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'delete_work_subcategory{i[0]}')
            markup.add(aero)
        return markup
    
    def delete_work_type(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'delete_work_type{i[0]}')
            markup.add(aero)
        return markup
    
    def choose_add_subcategory(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'work_category{i[0]}')
            markup.add(aero)
        return markup
    
    def foreman_choose_add_work_types(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'category_work1{i[0]}')
            markup.add(aero)
        return markup
    
    def foreman_need_choose_subcategory(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'work_subcategory1{i[0]}')
            markup.add(aero)
        return markup
    
    def foreman_need_choose_category(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'foreman_category{i[0]}')
            markup.add(aero)
        return markup
    
    def foreman_choose_subcategory(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'foreman_subcategory{i[0]}')
            markup.add(aero)
        return markup
    
    def foreman_choose_work_type(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'foreman_work_type{i[0]}')
            markup.add(aero)
        return markup
    
    def del_mat_category(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'delete_mat_categ{i[0]}')
            markup.add(aero)
        return markup
    
    def del_mat_subcategory(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'delete_mat_subcateg{i[0]}')
            markup.add(aero)
        return markup
    
    def del_mat_work_type(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'delete_mat_type_work{i[0]}')
            markup.add(aero)
        return markup
    
    def delete_material_buttons(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'material_delete{i[0]}')
            markup.add(aero)
        return markup
    
    def admin_choose_category(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'admin_category{i[0]}')
            markup.add(aero)
        return markup
    
    def admin_choose_subcategory(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'admin_subcategory{i[0]}')
            markup.add(aero)
        return markup
    
    def admin_choose_work_type(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[1], callback_data=f'admin_work_type{i[0]}')
            markup.add(aero)
        return markup