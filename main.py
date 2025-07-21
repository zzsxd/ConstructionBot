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
            bot.send_message(chat_id=foreman_user_id, text='✅ Регистрация пройдена!')
        elif call.data == "reject_reg":
            foreman_user_id = db_actions.get_user_id_from_topic(call.message.reply_to_message.id)
            bot.send_message(chat_id=foreman_user_id, text='❌ Регистрация не пройдена! Повторите попытку')

        # ПРОРАБ ОБРАБОТКА
        elif db_actions.user_is_foreman(user_id):
            # ОБРАБОТКА ОБЪЕКТОВ
            if call.data[:14] == "foreman_object":
                object_name = call.data[:14]
                bot.send_message(user_id, "Выберите название работы", reply_markup=buttons.name_of_where_work())
            if call.data[:19] == "foreman_info_object":
                object_name = call.data[:19]
                bot.send_message(user_id, "Выберите название работы")
            # СТАРТОВАЯ ОБРАБОТКА ПРОРАБА
            elif call.data == "foreman_select_objects":
                objects = db_actions.get_foreman_objects(user_id)
                bot.send_message(user_id, "Выберите свой объект", reply_markup=buttons.get_object_buttons(objects))
            elif call.data == "foreman_check_object":
                objects = db_actions.get_foreman_objects(user_id)
                bot.send_message(user_id, "Выбери объект", reply_markup=buttons.get_info_object_buttons(objects))
            # НА КРОВЛЕ ПАРКИНГА КНОПКИ ОБРАБОТКА
            elif call.data == "on_roof_parking":
                bot.send_message(user_id, "Выберите тип работы", reply_markup=buttons.roof_parking_work())
            elif call.data == "curb_curbstone":
                bot.send_message(user_id, "Выбери вид работы", reply_markup=buttons.curb_and_curbstone_work())
            elif call.data == "sidewalk_area":
                bot.send_message(user_id, "Выбери вид работы", reply_markup=buttons.sidewalk_blind_area_work())
            elif call.data == "tartan_coating":
                bot.send_message(user_id, "Выбери вид работы", reply_markup=buttons.tartan_covering_work())

            # В ГРАНИЦЕ УЧАСТКА И ПОДСЧЕТА РАБОТ ОБРАБОТКА
            elif call.data == "in_site_boundary":
                bot.send_message(user_id, "Выберите тип работы", reply_markup=buttons.site_boundary_work())
            elif call.data == "earth_works":
                bot.send_message(user_id, "Выбери вид работы", reply_markup=buttons.earthworks_work())
            elif call.data == "border_stone":
                bot.send_message(user_id, "Выбери вид работы", reply_markup=buttons.curbstone_work())
            elif call.data == "asphalt_roads":
                bot.send_message(user_id, "Выбери вид работы", reply_markup=buttons.asphalt_driveways_work())
            elif call.data == "sidewalk_blind":
                bot.send_message(user_id, "Выбери вид работы", reply_markup=buttons.sidewalk_blind_word())

            # БОРДЮР И ПОРЕБРИК
            elif call.data == "hidden_steel_curbs":
                bot.send_message(user_id, "Введите название материала")
            elif call.data == "drainage_for_curb":
                pass
            elif call.data == "granite_curb_100208":
                pass
            elif call.data == "drainage_for_border":
                pass
            elif call.data == "granite_border_1003015":
                pass
            # ТРОТУАР И ОТМОСТКА
            elif call.data == "pavement_dismantling":
                pass
            elif call.data == "drainage_layers_30cm":
                pass
            elif call.data == "geotextile_laying":
                pass
            elif call.data == "sidewalk_type1":
                pass
            # ТАРТАНОВОЕ ПОКРЫТИЕ
            elif call.data == "drainage_300_400":
                pass
            elif call.data == "concrete_base_tartan":
                pass
            # ЗЕМЛЯНЫЕ РАБОТЫ
            elif call.data == "ground_leveling":
                pass
            elif call.data == "pit_excavation":
                pass
            elif call.data == "compaction":
                pass
            elif call.data == "soil_transport_1km":
                pass
            # БОРТОВОЙ КАМЕНЬ
            elif call.data == "yard_drainage_porebrik":
                pass
            elif call.data == "straight_granite_curb":
                pass
            elif call.data == "yard_drainage_bordur":
                pass
            elif call.data == "straight_granite_border":
                pass
            # АСФАЛЬТ ПО ПРОЕЗДАМ
            elif call.data == "base_stabilization":
                pass
            elif call.data == "gravel_base":
                pass
            elif call.data == "pre_KZ_pouring":
                pass
            elif call.data == "coarse_asphalt_6cm":
                pass
            elif call.data == "pre_MZ_pouring":
                pass
            elif call.data == "fine_asphalt_5cm":
                pass
            # ТРОТУАР, ОТМОСТКА
            elif call.data == "drainage_15cm":
                pass
            elif call.data == "sidewalk_coating":
                pass



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
                db_actions.set_user_system_key(user_id, "index", None)
                db_actions.write_new_object(user_id, user_input)
                object_names = db_actions.get_all_objects(user_id)
                objects_list = "\n".join([f"{i[1]}" for i in object_names])
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