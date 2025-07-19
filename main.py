import time
import telebot
import os
import re
import json
import threading
import platform
from telebot import types
from threading import Lock
from config_parser import ConfigParser
from frontend import Bot_inline_btns
from backend import DbAct
from db import DB

config_name = 'secrets.json'


def main():
    @bot.message_handler(commands=['start', 'admin'])
    def start(message):
        command = message.text.replace('/', '')
        user_id = message.from_user.id
        buttons = Bot_inline_btns()
        if command == 'start':
            db_actions.set_user_system_key(user_id, "index", None)
            if db_actions.user_is_existed(user_id):
                bot.send_message(user_id, "👷‍♂️ Привет! Добро пожаловать в строительный бот.\n" \
                "Здесь ты можешь быстро ввести данные о выполненных работах и сформировать отчёты.\n\n" \
                "Готов начать? Нажми кнопку ниже 👇", reply_markup=buttons.unregister_buttons())
            else:
                db_actions.add_user(user_id, message.from_user.first_name, message.from_user.last_name,
                            f'@{message.from_user.username}', None, None)
                bot.send_message(user_id, "👷‍♂️ Привет! Добро пожаловать в строительный бот.\n" \
                "Здесь ты можешь быстро ввести данные о выполненных работах и сформировать отчёты.\n\n" \
                "Готов начать? Нажми кнопку ниже 👇", reply_markup=buttons.unregister_buttons())
        elif command == 'admin':
            if db_actions.user_is_admin(user_id):
                bot.send_message(user_id, "<b>Добро пожаловать в Админ-Панель!</b>"
                             "\n\nВыберите пункт ниже!", reply_markup=buttons.admin_buttons(), parse_mode='HTML')
            else:
                bot.send_message(user_id, "<b>Вы не администратор</b>", parse_mode='HTML')


                


    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        user_id = call.message.chat.id
        buttons = Bot_inline_btns()
        if db_actions.user_is_existed(user_id):
            if db_actions.user_is_admin(user_id):
                if call.data == "add_object":
                    db_actions.set_user_system_key(user_id, "index", 1)
                    bot.send_message(user_id, "Отправьте название объекта")
                elif call.data == "delete_object":
                    objects = db_actions.get_all_objects(user_id)
                    bot.send_message(user_id, "Выберите объект для удаления\n\n" \
                    "Учтите! При удалении объекта, удаляться записи о нем!", reply_markup=buttons.delete_object_buttons(objects))
                elif call.data[:6] == "object":
                    object_name = call.data[6:]
                    db_actions.delete_object(user_id, object_name)
                    bot.send_message(user_id, "Объект удален! ✅")

                elif call.data == "see_objects":
                    object_names = db_actions.get_all_objects(user_id)
                    objects_list = "\n".join([f"{i[0]}" for i in object_names])
                    bot.send_message(user_id, "Список существующих объектов:\n" \
                    f"{objects_list}")
            if call.data == "registration_foreman":
                bot.send_message(user_id, "Первым делом заполни небольшую анкету, уточни своё ФИО.")
                db_actions.set_user_system_key(user_id, "index", 0)
        if call.data == "accept_reg":
            db_actions.set_user_is_foreman(db_actions.get_user_id_from_topic(call.message.reply_to_message.id))
            bot.send_message(chat_id=db_actions.get_user_id_from_topic(call.message.reply_to_message.id), text='✅ Регистрация пройдена!')
        elif call.data == "reject_reg":
            bot.send_message(chat_id=db_actions.get_user_id_from_topic(call.message.reply_to_message.id), text='❌ Регистрация не пройдена! Повторите попытку')
    

    @bot.message_handler(content_types=['text', 'photo'])
    def text_message(message):
        buttons = Bot_inline_btns()
        user_input = message.text
        user_id = message.chat.id
        code = db_actions.get_user_system_key(user_id, "index")
        if db_actions.user_is_existed(user_id):
            if code == 0:
                topic_id = telebot.TeleBot.create_forum_topic(bot, chat_id=group_id,
                                                            name=f'{message.from_user.first_name} '
                                                                f'{message.from_user.last_name} Регистрация',
                                                            icon_color=0x6FB9F0).message_thread_id
                bot.forward_message(chat_id=group_id, from_chat_id=message.chat.id, message_id=message.id,
                                    message_thread_id=topic_id)
                bot.send_message(chat_id=group_id, message_thread_id=topic_id, text=f"Заявка на регистрацию!\nВыше информация о ФИО пользователя\nUsername пользователя: @{message.from_user.username}", reply_markup=buttons.manager_btns())
                db_actions.set_user_id_in_topic(user_id, topic_id)
                bot.send_message(user_id, '⏳ Ваша заявка принята, ожидайте!')
                db_actions.set_user_system_key(user_id, "index", None)
            elif code == 1:
                db_actions.set_user_system_key(user_id, "index", None)
                db_actions.write_new_object(user_id, user_input)
                object_names = db_actions.get_all_objects(user_id)
                objects_list = "\n".join([f"{i[0]}" for i in object_names])
                bot.send_message(user_id, "Новый объект записан, вот список существующих объектов:\n" \
                f"{objects_list}")

    bot.polling(none_stop=True)



if '__main__' == __name__:
    os_type = platform.system()
    work_dir = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser(f'{work_dir}/{config_name}', os_type)
    db = DB(config.get_config()['db_file_name'], Lock())
    group_id = config.get_config()['group_id']
    db_actions = DbAct(db, config, config.get_config()['xlsx_path'])
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    main()