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
            if db_actions.user_is_existed(user_id) and db_actions.user_is_foreman(user_id):
                bot.send_message(user_id, "👷‍♂️ Привет! Добро пожаловать в строительный бот.\n" \
                "Здесь ты можешь быстро ввести данные о выполненных работах и сформировать отчёты.\n\n" \
                "Готов начать? Выбери свой объект ниже 👇", reply_markup=buttons.foreman_buttons())
            else:
                db_actions.add_user(user_id, None, f'@{message.from_user.username}', None)
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
                    try:
                        # Получаем список всех объектов пользователя
                        objects = db_actions.get_all_objects(user_id)
                        
                        if not objects:
                            bot.send_message(user_id, "У вас нет созданных объектов")
                            return
                        
                        # Собираем информацию по каждому объекту
                        objects_info = []
                        for obj in objects:
                            # Получаем прорабов для каждого объекта
                            foremen = db_actions.get_name_from_user_id(obj[0])  # obj[0] - user_id из construction_objects
                            
                            if not foremen:
                                objects_info.append(f"{obj[1]} - Нет прикрепленного прораба")
                            else:
                                for foreman in foremen:
                                    objects_info.append(f"{obj[1]} - {foreman[0]}")  # foreman[0] - full_name
                        
                        # Формируем итоговое сообщение
                        message = (
                            "Список ваших объектов:\n"
                            "Формат: Объект - Ответственный прораб\n\n"
                            + "\n".join(objects_info)
                        )
                        bot.send_message(user_id, message)
                        
                    except Exception as e:
                        bot.send_message(user_id, f"Произошла ошибка: {str(e)}")
                elif call.data == "attach_foreman_to_object":
                    objects = db_actions.get_all_objects(user_id)
                    bot.send_message(user_id, "Выберите объект:", reply_markup=buttons.choose_object_to_attach(objects))
                elif call.data[:20] == "choose_object_attach":
                    foremans = db_actions.get_foremans(user_id)
                    bot.send_message(user_id, "Выберите прораба", reply_markup=buttons.choose_foreman_to_attach(foremans))
                    db_actions.set_user_system_key(user_id, "attach_object_name", call.data[20:])
                elif call.data[:21] == "choose_foreman_attach":
                    object_name = db_actions.get_user_system_key(user_id, "attach_object_name")
                    db_actions.attach_foreman_to_object(user_id=call.data[21:], object_name=object_name)
                    bot.send_message(user_id, f"Прораб прикреплен к объекту {object_name}")
            if call.data == "registration_foreman":
                bot.send_message(user_id, "Первым делом заполни небольшую анкету, уточни своё ФИО.")
                db_actions.set_user_system_key(user_id, "index", 0)
        if call.data == "accept_reg":
            foreman_user_id = db_actions.get_user_id_from_topic(call.message.reply_to_message.id)
            foreman_full_name = db_actions.get_user_system_key(foreman_user_id, "full_name")
            db_actions.set_user_is_foreman(foreman_user_id)
            db_actions.set_user_full_name(foreman_user_id, foreman_full_name)
            bot.send_message(chat_id=foreman_user_id, text='✅ Регистрация пройдена!\n\nПропишите /start для начала')
        elif call.data == "reject_reg":
            foreman_user_id = db_actions.get_user_id_from_topic(call.message.reply_to_message.id)
            bot.send_message(chat_id=foreman_user_id, text='❌ Регистрация не пройдена! Повторите попытку')
        elif db_actions.user_is_foreman(user_id):
            # СТАРТОВАЯ ОБРАБОТКА ПРОРАБА
            if call.data == "foreman_select_objects":
                objects = db_actions.get_foreman_objects(user_id)
                if objects:
                    bot.send_message(user_id, "Выберите свой объект", reply_markup=buttons.get_object_buttons(objects))
                else:
                    bot.send_message(user_id, "Объекты не найдены")
            elif call.data == "foreman_check_object":
                objects = db_actions.get_foreman_objects(user_id)
                if objects:
                    bot.send_message(user_id, "Выбери объект", reply_markup=buttons.get_info_object_buttons(objects))
                else:
                    bot.send_message(user_id, "Объекты не найдены")
            elif call.data[:14] == "foreman_object":
                db_actions.set_user_system_key(user_id, "object_id", call.data[14:])
                bot.send_message(user_id, "Выберите действие", reply_markup=buttons.foreman_object_buttons())
            
            elif call.data == "add_work":
                bot.send_message(user_id, "Выберите тип работы", reply_markup=buttons.foreman_choose_type_work())

            elif call.data == "foreman_add_category":
                bot.send_message(user_id, "Введите название категории")
                db_actions.set_user_system_key(user_id, "index", 2)
            
            elif call.data == "foreman_add_subcategory":
                categories = db_actions.get_work_categories(user_id)
                if categories:
                    bot.send_message(user_id, "Выберите категорию", reply_markup=buttons.foreman_choose_add_subcategory(categories))
                else:
                    bot.send_message(user_id, "Категории не найдены")
            elif call.data[:13] == "work_category":
                db_actions.set_user_system_key(user_id, "category_id", call.data[13:])
                bot.send_message(user_id, "Введите название подкатегории")
                db_actions.set_user_system_key(user_id, "index", 3)

            elif call.data == "foreman_add_type_work":
                categories = db_actions.get_work_categories(user_id)
                if categories:
                    bot.send_message(user_id, "Выберите категорию", reply_markup=buttons.foreman_choose_add_work_types(categories))
                else:
                        bot.send_message(user_id, "Категории не найдены")

            elif call.data[:14] == "category_work1":
                db_actions.set_user_system_key(user_id, "category_id", call.data[14:])
                subcategories = db_actions.get_work_subcategories(user_id)
                if subcategories:
                    bot.send_message(user_id, "Выберите подкатегорию", reply_markup=buttons.foreman_need_choose_subcategory(subcategories))
                else:
                    bot.send_message(user_id, "Подкатегории не найдены")
            elif call.data[:17] == "work_subcategory1":
                db_actions.set_user_system_key(user_id, "subcategory_id", call.data[17:])
                bot.send_message(user_id, "Введите название работы")
                db_actions.set_user_system_key(user_id, "index", 4)
                
    @bot.message_handler(content_types=['text', 'photo'])
    def text_message(message):
        buttons = Bot_inline_btns()
        user_input = message.text
        user_id = message.chat.id
        code = db_actions.get_user_system_key(user_id, "index")
        if db_actions.user_is_existed(user_id):
            if code == 0:
                db_actions.set_user_system_key(user_id, "full_name", user_input)
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
                db_actions.write_new_object(user_id, user_input)
                object_names = db_actions.get_all_objects(user_id)
                objects_list = "\n".join([f"{i[1]}" for i in object_names])
                bot.send_message(user_id, "Новый объект записан, вот список существующих объектов:\n" \
                f"{objects_list}")
                db_actions.set_user_system_key(user_id, "index", None)
            elif code == 2:
                # user_input - category name
                object_id = db_actions.get_user_system_key(user_id, "object_id")
                db_actions.add_work_categories(user_id, object_id, user_input)
                bot.send_message(user_id, "Категория записана")
                db_actions.set_user_system_key(user_id, "index", None)

            elif code == 3:
                category_id = db_actions.get_user_system_key(user_id, "category_id")
                db_actions.add_work_subcategories(user_id, category_id, user_input)
                bot.send_message(user_id, "Подкатегория добавлена")
            
            elif code == 4:
                db_actions.set_user_system_key(user_id, "work_type_name", user_input)
                db_actions.set_user_system_key(user_id, "index", 5)
                bot.send_message(user_id, "Введите единицу измерения")
            
            elif code == 5:
                db_actions.set_user_system_key(user_id, "work_type_unit", user_input)
                db_actions.set_user_system_key(user_id, "index", 6)
                bot.send_message(user_id, "Введите объем")

            elif code == 6:
                db_actions.set_user_system_key(user_id, "work_type_volume", user_input)
                db_actions.set_user_system_key(user_id, "index", 7)
                bot.send_message(user_id, "Введите цену")

            elif code == 7:
                subcategory_id = db_actions.get_user_system_key(user_id, "subcategory_id")
                name = db_actions.get_user_system_key(user_id, "work_type_name")
                unit = db_actions.get_user_system_key(user_id, "work_type_unit")
                volume = db_actions.get_user_system_key(user_id, "work_type_volume")
                db_actions.add_work_type(user_id, subcategory_id, name, unit, volume, user_input)
                bot.send_message(user_id, "Тип работы записан")                
                db_actions.set_user_system_key(user_id, "index", None)



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