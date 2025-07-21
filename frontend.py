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
        two = types.InlineKeyboardButton("Посмотреть информацию об обьекте", callback_data="foreman_check_object")
        self.__markup.add(one, two)
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
            aero = types.InlineKeyboardButton(i[0], callback_data=f'foreman_object{i[0]}')
            markup.add(aero)
        return markup
    
    def get_info_object_buttons(self, data):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            aero = types.InlineKeyboardButton(i[0], callback_data=f'foreman_info_object{i[0]}')
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

    def name_of_where_work(self):
        one = types.InlineKeyboardButton("На кровле паркинга", callback_data="on_roof_parking")
        two = types.InlineKeyboardButton("В границе участка и подсчета работ", callback_data='in_site_boundary')
        self.__markup.add(one, two)
        return self.__markup

    def roof_parking_work(self):
        one = types.InlineKeyboardButton("Бордюр и поребрик", callback_data="curb_curbstone")
        two = types.InlineKeyboardButton("Тротуар и отмостка", callback_data="sidewalk_area")
        three = types.InlineKeyboardButton("Тартановое покрытие", callback_data="tartan_coating")
        self.__markup.add(one, two, three)
        return self.__markup

    def site_boundary_work(self):
        one = types.InlineKeyboardButton("Земляные работы", callback_data="earth_works")
        two = types.InlineKeyboardButton("Бортовой камень", callback_data="border_stone")
        three = types.InlineKeyboardButton("Асфальт по проездам", callback_data="asphalt_roads")
        four = types.InlineKeyboardButton("Тротуар, Отмостка", callback_data="sidewalk_blind")
        self.__markup.add(one, two, three, four)
        return self.__markup

    def curb_and_curbstone_work(self):
        one = types.InlineKeyboardButton("Скрытые стальные поребрики (кривые)", callback_data="hidden_steel_curbs")
        two = types.InlineKeyboardButton("Дренирующие слои под поребрик", callback_data="drainage_for_curb")
        three = types.InlineKeyboardButton("Гранитный поребрик БР100,20,8", callback_data="granite_curb_100208")
        four = types.InlineKeyboardButton("Дренирующие слои под бордюр", callback_data="drainage_for_border")
        five = types.InlineKeyboardButton("Гранитный бордюр БР100,30,15", callback_data="granite_border_1003015")
        self.__markup.add(one, two, three, four, five)
        return self.__markup

    def sidewalk_blind_area_work(self):
        one = types.InlineKeyboardButton("Демонтаж брусчатки", callback_data="pavement_dismantling")
        two = types.InlineKeyboardButton("Дренирующие слои (H=0,30м)", callback_data="drainage_layers_30cm")
        three = types.InlineKeyboardButton("Укладка геотекстиля", callback_data="geotextile_laying")
        four = types.InlineKeyboardButton("Покрытие тротуара тип 1", callback_data="sidewalk_type1")
        self.__markup.add(one, two, three, four)
        return self.__markup

    def tartan_covering_work(self):
        one = types.InlineKeyboardButton("Дренирующие слои (H=300-400мм)", callback_data="drainage_300_400")
        two = types.InlineKeyboardButton("Бетонное основание под тартан", callback_data="concrete_base_tartan")
        self.__markup.add(one, two)
        return self.__markup

    def earthworks_work(self):
        one = types.InlineKeyboardButton("Планировка земляного полотна", callback_data="ground_leveling")
        two = types.InlineKeyboardButton("Разработка котлована", callback_data="pit_excavation")
        three = types.InlineKeyboardButton("Уплотнение", callback_data="compaction")
        four = types.InlineKeyboardButton("Перевозка грунта (до 1км)", callback_data="soil_transport_1km")
        self.__markup.add(one, two, three, four)
        return self.__markup

    def curbstone_work(self):
        one = types.InlineKeyboardButton("Дренирующие слои для территории (поребрик)", callback_data="yard_drainage_porebrik")
        two = types.InlineKeyboardButton("Гранитный поребрик (прямой)", callback_data="straight_granite_curb")
        three = types.InlineKeyboardButton("Дренирующие слои для территории (бордюр)", callback_data="yard_drainage_bordur")
        four = types.InlineKeyboardButton("Бордюр гранитный (прямой)", callback_data="straight_granite_border")
        self.__markup.add(one, two, three, four)
        return self.__markup

    def asphalt_driveways_work(self):
        one = types.InlineKeyboardButton("Стабилизация основания (бут)", callback_data="base_stabilization")
        two = types.InlineKeyboardButton("Основание из щебня", callback_data="gravel_base")
        three = types.InlineKeyboardButton("Розлив перед КЗ", callback_data="pre_KZ_pouring")
        four = types.InlineKeyboardButton("Крупнозернистый асфальт 6см", callback_data="coarse_asphalt_6cm")
        five = types.InlineKeyboardButton("Розлив перед МЗ", callback_data="pre_MZ_pouring")
        six = types.InlineKeyboardButton("Мелкозернистый асфальт 5см", callback_data="fine_asphalt_5cm")
        self.__markup.add(one, two, three, four, five, six)
        return self.__markup

    def sidewalk_blind_word(self):
        one = types.InlineKeyboardButton("Дренирующие слои (H=15см)", callback_data="drainage_15cm")
        two = types.InlineKeyboardButton("Покрытие тротуара/отмостки", callback_data="sidewalk_coating")
        self.__markup.add(one, two)
        return self.__markup