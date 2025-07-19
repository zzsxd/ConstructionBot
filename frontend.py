from telebot import types


class Bot_inline_btns:
    def __init__(self):
        super(Bot_inline_btns, self).__init__()
        self.__markup = types.InlineKeyboardMarkup(row_width=1)

    def unregister_buttons(self):
        one = types.InlineKeyboardButton('📄 Регистрация', callback_data="registration_foreman")
        self.__markup.add(one)
        return self.__markup
    
    def manager_btns(self):
        one = types.InlineKeyboardButton('✅ Одобрить', callback_data="accept_reg")
        two = types.InlineKeyboardButton('❌ Отклонить', callback_data='reject_reg')
        self.__markup.add(one, two)
        return self.__markup
    
    
    def admin_buttons(self):
        one = types.InlineKeyboardButton('🔹 Экспорировать', callback_data="export_users")
        self.__markup.add(one)
        return self.__markup
