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
        one = types.InlineKeyboardButton("Выбрать объект", callback_data="foreman_select_objects")
        self.__markup.add(one)
        return self.__markup
    
    def manager_btns(self):
        one = types.InlineKeyboardButton('✅ Одобрить', callback_data="accept_reg")
        two = types.InlineKeyboardButton('❌ Отклонить', callback_data='reject_reg')
        self.__markup.add(one, two)
        return self.__markup
    
    
    def admin_buttons(self):
        one = types.InlineKeyboardButton("Добавить объект", callback_data="add_object")
        two = types.InlineKeyboardButton("Удалить объект", callback_data="delete_object")
        three = types.InlineKeyboardButton("Посмотреть объекты", callback_data="see_objects")
        four = types.InlineKeyboardButton("Прикрепить прораба", callback_data="attach_foreman_to_object")
        # one = types.InlineKeyboardButton('🔹 Экспорировать', callback_data="export_users")
        self.__markup.add(one, two, three, four)
        return self.__markup
    
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
    
    def foreman_object_buttons(self):
        one = types.InlineKeyboardButton("Добавить работу", callback_data="add_work")
        two = types.InlineKeyboardButton("Удалить работу", callback_data="delete_work")
        three = types.InlineKeyboardButton("Удалить материалы", callback_data="delete_materials")
        four = types.InlineKeyboardButton("Внести материалы", callback_data="add_materials")
        five = types.InlineKeyboardButton("Просмотреть отчет", callback_data="get_report")
        self.__markup.add(one, two, four, three, five)
        return self.__markup


    def foreman_choose_type_work(self):
        one = types.InlineKeyboardButton("Добавить категорию", callback_data="foreman_add_category")
        two = types.InlineKeyboardButton("Добавить подкатегорию", callback_data="foreman_add_subcategory")
        three = types.InlineKeyboardButton("Добавить тип работы", callback_data="foreman_add_type_work")
        self.__markup.add(one, two, three)
        return self.__markup
    
    def foreman_choose_delete_type_work(self):
        one = types.InlineKeyboardButton("Удалить категорию", callback_data="foreman_delete_category")
        two = types.InlineKeyboardButton("Удалить подкатегорию", callback_data="foreman_delete_subcategory")
        three = types.InlineKeyboardButton("Удалить тип работы", callback_data="foreman_delete_type_work")
        self.__markup.add(one, two, three)
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
    
    def foreman_choose_add_subcategory(self, data):
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