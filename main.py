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
                elif call.data == "export_object_data":
                    objects = db_actions.get_admin_objects(user_id)
                    bot.send_message(user_id, "Выберите объект", reply_markup=buttons.choose_object_export(objects))
                elif call.data[:17] == "export_objectdata":
                    object_id = call.data[17:]
                    if db_actions.db_export_object_report(object_id):
                        if os.path.exists(config.get_config()['xlsx_path']):
                            with open(config.get_config()['xlsx_path'], 'rb') as f:
                                bot.send_document(user_id, f)
                            os.remove(config.get_config()['xlsx_path'])
                        else:
                            bot.send_message(user_id, "Ошибка: файл отчета не был создан")
                    else:
                        bot.send_message(user_id, "Ошибка при создании отчета")
                elif call.data == "see_objects":
                    try:
                        objects = db_actions.get_all_objects(user_id)    
                        if not objects:
                            bot.send_message(user_id, "У вас нет созданных объектов")
                            return
                        objects_info = []
                        for obj in objects:
                            foremen = db_actions.get_name_from_user_id(obj[0])  # obj[0] - user_id
                            if not foremen:
                                objects_info.append(f"{obj[1]} - Нет прикрепленного прораба")
                            else:
                                for foreman in foremen:
                                    objects_info.append(f"{obj[1]} - {foreman[0]}")  # foreman[0] - full_name
                        message = (
                            "Список ваших объектов:\n"
                            "Формат: Объект - Ответственный прораб\n\n"
                            + "\n".join(objects_info)
                        )
                        bot.send_message(user_id, message)
                    except Exception as e:
                        bot.send_message(user_id, f"Произошла ошибка: {str(e)}")
                elif call.data == "control_object":
                    admin_object = db_actions.get_admin_objects(user_id)
                    bot.send_message(user_id, "Выберите объект", reply_markup=buttons.choose_control_object(admin_object))
                elif call.data[:20] == "admin_object_control":
                    db_actions.set_user_system_key(user_id, "admin_object_id", call.data[20:])
                    bot.send_message(user_id, "Выберите пункт управления", reply_markup=buttons.control_object_panel())
                elif call.data == "category_control":
                    bot.send_message(user_id, "Выберите пункт", reply_markup=buttons.control_category_buttons())
                elif call.data == "subcategory_control":
                    bot.send_message(user_id, "Выберите пункт", reply_markup=buttons.control_subcategory_buttons())
                elif call.data == "work_type_control":
                    bot.send_message(user_id, "Выберите пункт", reply_markup=buttons.control_work_type_buttons())
                elif call.data == "material_control":
                    bot.send_message(user_id, "Выберите пункт", reply_markup=buttons.material_control_buttons())
                elif call.data == "coming_control":
                    bot.send_message(user_id, "Выберите пункт", reply_markup=buttons.control_coming_buttons())
                elif call.data == "technical_control":
                    bot.send_message(user_id, "Выберите пункт", reply_markup=buttons.technical_control_buttons())
                elif call.data == "delete_technical":
                    technique_list = db_actions.get_list_technique(user_id, object_id=db_actions.get_user_system_key(user_id, "object_id"))
                    bot.send_message(user_id, "Выберите технику", reply_markup=buttons.admin_choose_technical_delete(technique_list))
                elif call.data[:21] == "technique_list_delete":
                    db_actions.delete_technique(user_id, call.data[21:])
                    bot.send_message(user_id, "Техника удалена ✅")
                elif call.data == "delete_coming":
                    coming_list = db_actions.get_from_list_coming(user_id, object_id=db_actions.get_user_system_key(user_id, "admin_object_id"))
                    bot.send_message(user_id, "Выберите материал прихода", reply_markup=buttons.choose_coming_buttons(coming_list))
                elif call.data[:19] == "admin_delete_coming":
                    db_actions.delete_from_list_coming(user_id, call.data[19:])
                    bot.send_message(user_id, "Приход удален ✅")
                elif call.data == "add_category":
                    bot.send_message(user_id, "Введите название категории")
                    db_actions.set_user_system_key(user_id, "index", 2)
                elif call.data == "delete_category":
                    object_id = db_actions.get_user_system_key(user_id, "admin_object_id")
                    category = db_actions.get_work_categories(user_id, object_id)
                    bot.send_message(user_id, "Выберите категорию для удаления\n\n" \
                    "Учтите, при удалении категории - удалятся подкатегории и виды работ!", reply_markup=buttons.delete_category_buttons(category))
                elif call.data[:20] == "delete_work_category":
                    category_id = call.data[20:]
                    db_actions.delete_work_categories(user_id, category_id)
                    bot.send_message(user_id, "Категория удалена ✅")
                elif call.data[:23] == "delete_work_subcategory":
                    subcategory_id = call.data[23:]
                    db_actions.delete_work_subcategories(user_id, subcategory_id)
                    bot.send_message(user_id, "Подкатегория удалена ✅")
                elif call.data[:16] == "delete_work_type":
                    work_type_id = call.data[16:]
                    db_actions.delete_work_type(user_id, work_type_id)
                    bot.send_message(user_id, "Тип работы удален ✅")
                elif call.data == "add_subcategory":
                    object_id = db_actions.get_user_system_key(user_id, "admin_object_id")
                    categories = db_actions.get_work_categories(user_id, object_id)
                    if categories:
                        bot.send_message(user_id, "Выберите категорию", reply_markup=buttons.choose_add_subcategory(categories))
                    else:
                        bot.send_message(user_id, "Категории не найдены")
                elif call.data == "delete_subcategory":
                    category_id = db_actions.get_user_system_key(user_id, "category_id")
                    subcategory = db_actions.get_work_subcategories(user_id, category_id)
                    bot.send_message(user_id, "Выберите подкатегорию для удаления\n\n" \
                    "Учтите, при удалении подкатегории - удалятся виды работ!", reply_markup=buttons.delete_subcategory_buttons(subcategory))
                elif call.data == "add_type_work":
                    object_id = db_actions.get_user_system_key(user_id, "admin_object_id")
                    categories = db_actions.get_work_categories(user_id, object_id)
                    if categories:
                        bot.send_message(user_id, "Выберите категорию", reply_markup=buttons.foreman_choose_add_work_types(categories))
                    else:
                            bot.send_message(user_id, "❌Категории не найдены")
                elif call.data == "delete_type_work":
                    subcategory_id = db_actions.get_user_system_key(user_id, "subcategory_id")
                    work_type = db_actions.get_work_type(user_id, subcategory_id)
                    bot.send_message(user_id, "Выберите тип работы для удаления", reply_markup=buttons.delete_work_type(work_type))
                elif call.data == "delete_materials":
                    object_id = db_actions.get_user_system_key(user_id, "admin_object_id")
                    category = db_actions.get_work_categories(user_id, object_id)
                    bot.send_message(user_id, "Выберите категорию", reply_markup=buttons.del_mat_category(category))
                elif call.data[:16] == "delete_mat_categ":
                    subcategory = db_actions.get_work_subcategories(user_id, call.data[16:])
                    bot.send_message(user_id, "Выберите подкатегорию", reply_markup=buttons.del_mat_subcategory(subcategory))
                elif call.data[:19] == "delete_mat_subcateg":
                    work_types = db_actions.get_work_type(user_id, call.data[19:])
                    bot.send_message(user_id, "Выберите вид работы", reply_markup=buttons.del_mat_work_type(work_types))
                elif call.data[:20] == "delete_mat_type_work":
                    materials = db_actions.get_work_material(user_id, call.data[20:])
                    bot.send_message(user_id, "Выбери материал для удаления", reply_markup=buttons.delete_material_buttons(materials))
                elif call.data[:15] == "material_delete":
                    db_actions.delete_work_material(user_id, call.data[15:])
                    bot.send_message(user_id, "Материал удален ✅")
                elif call.data == "add_norma":
                    object_id = db_actions.get_user_system_key(user_id, "admin_object_id")
                    categories = db_actions.get_work_categories(user_id, object_id)
                    bot.send_message(user_id, "Выберите категорию", reply_markup=buttons.admin_choose_category(categories))
                elif call.data == "add_unit":
                    object_id = db_actions.get_user_system_key(user_id, "admin_object_id")
                    categories = db_actions.get_work_categories(user_id, object_id)
                    bot.send_message(user_id, "Выберите категорию", reply_markup=buttons.admin_choose_category2(categories))
                elif call.data == "add_number":
                    object_id = db_actions.get_user_system_key(user_id, "admin_object_id")
                    categories = db_actions.get_work_categories(user_id, object_id)
                    bot.send_message(user_id, "Выберите категорию", reply_markup=buttons.admin_choose_category3(categories))
                elif call.data == "edit_smr":
                    object_id = db_actions.get_user_system_key(user_id, "admin_object_id")
                    categories = db_actions.get_work_categories(user_id, object_id)
                    bot.send_message(user_id, "Выберите категорию", reply_markup=buttons.admin_choose_category4(categories))
                elif call.data[:14] == "admin_category":
                    subcategories = db_actions.get_work_subcategories(user_id, call.data[14:])
                    bot.send_message(user_id, "Выберите подкатегорию", reply_markup=buttons.admin_choose_subcategory(subcategories))
                elif call.data[:17] == "admin_subcategory":
                    work_type = db_actions.get_work_type(user_id, call.data[17:])
                    bot.send_message(user_id, "Выберите вид работы", reply_markup=buttons.admin_choose_work_type(work_type))
                elif call.data[:15] == "admin_work_type":
                    db_actions.set_user_system_key(user_id, "work_type_id", call.data[15:])
                    materials = db_actions.get_work_material(user_id, call.data[15:])
                    bot.send_message(user_id, "Выберите материал", reply_markup=buttons.admin_choose_material(materials))
                elif call.data[:14] == "admin_material":
                    db_actions.set_user_system_key(user_id, "material_id", call.data[14:])
                    bot.send_message(user_id, "Введите норму")
                    db_actions.set_user_system_key(user_id, "index", 27)
                elif call.data[:15] == "2admin_category":
                    subcategories = db_actions.get_work_subcategories2(user_id, call.data[15:])
                    bot.send_message(user_id, "Выберите подкатегорию", reply_markup=buttons.admin_choose_subcategory(subcategories))
                elif call.data[:18] == "2admin_subcategory":
                    work_type = db_actions.get_work_type(user_id, call.data[18:])
                    bot.send_message(user_id, "Выберите вид работы", reply_markup=buttons.admin_choose_work_type(work_type))
                elif call.data[:16] == "2admin_work_type":
                    db_actions.set_user_system_key(user_id, "work_type_id", call.data[16:])
                    materials = db_actions.get_work_material(user_id, call.data[16:])
                    bot.send_message(user_id, "Выберите материал", reply_markup=buttons.admin_choose_material(materials))
                elif call.data[:15] == "2admin_material":
                    db_actions.set_user_system_key(user_id, "material_id", call.data[15:])
                    bot.send_message(user_id, "📏 Введите единицу измерения")
                    db_actions.set_user_system_key(user_id, "index", 28)
                elif call.data[:15] == "3admin_category":
                    subcategories = db_actions.get_work_subcategories(user_id, call.data[15:])
                    bot.send_message(user_id, "Выберите подкатегорию", reply_markup=buttons.admin_choose_subcategory(subcategories))
                elif call.data[:18] == "3admin_subcategory":
                    work_type = db_actions.get_work_type(user_id, call.data[18:])
                    bot.send_message(user_id, "Выберите вид работы", reply_markup=buttons.admin_choose_work_type(work_type))
                elif call.data[:16] == "3admin_work_type":
                    db_actions.set_user_system_key(user_id, "work_type_id", call.data[16:])
                    materials = db_actions.get_work_material(user_id, call.data[16:])
                    bot.send_message(user_id, "Выберите материал", reply_markup=buttons.admin_choose_material(materials))
                elif call.data[:15] == "3admin_material":
                    db_actions.set_user_system_key(user_id, "material_id", call.data[15:])
                    bot.send_message(user_id, "Введите гос. №. техники")
                    db_actions.set_user_system_key(user_id, "index", 29)
                elif call.data[:15] == "4admin_category":
                    subcategories = db_actions.get_work_subcategories(user_id, call.data[15:])
                    bot.send_message(user_id, "Выберите подкатегорию", reply_markup=buttons.admin_choose_subcategory4(subcategories))
                elif call.data[:18] == "4admin_subcategory":
                    work_type = db_actions.get_work_type(user_id, call.data[18:])
                    bot.send_message(user_id, "Выберите вид работы", reply_markup=buttons.admin_choose_work_type4(work_type))
                elif call.data[:16] == "4admin_work_type":
                    db_actions.set_user_system_key(user_id, "work_type_id", call.data[16:])
                    smr = db_actions.select_material_smr(user_id, call.data[16:])
                    if smr:
                        materials = db_actions.get_work_material(user_id, call.data[16:])
                        bot.send_message(user_id, "📏 Введите единицу измерения")
                        db_actions.set_user_system_key(user_id, "index", 30)
                    else:
                        bot.send_message(user_id, "❌ В данном виде работы не создан СМР!")
                elif call.data == "attach_foreman_to_object":
                    objects = db_actions.get_all_objects(user_id)
                    bot.send_message(user_id, "Выберите объект", reply_markup=buttons.choose_object_to_attach(objects))
                elif call.data == "unpin_foreman":
                    objects = db_actions.get_all_objects(user_id)
                    bot.send_message(user_id, "Выберите объект", reply_markup=buttons.choose_object_to_unpin(objects))
                elif call.data[:19] == "choose_object_unpin":
                    db_actions.unpin_foreman_from_object(user_id, call.data[19:])
                    bot.send_message(user_id, "✅ Прораб откреплен")
                elif call.data[:20] == "choose_object_attach":
                    foremans = db_actions.get_foremans(user_id)
                    bot.send_message(user_id, "Выберите прораба", reply_markup=buttons.choose_foreman_to_attach(foremans))
                    db_actions.set_user_system_key(user_id, "attach_object_name", call.data[20:])
                elif call.data[:21] == "choose_foreman_attach":
                    object_name = db_actions.get_user_system_key(user_id, "attach_object_name")
                    db_actions.attach_foreman_to_object(user_id=call.data[21:], object_name=object_name)
                    bot.send_message(user_id, f"✅ Прораб прикреплен к объекту {object_name}")
            if call.data == "registration_foreman":
                bot.send_message(user_id, "✏️ Первым делом заполни небольшую анкету, уточни своё ФИО.")
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
                    bot.send_message(user_id, "❌ Объекты не найдены")
            elif call.data[:14] == "foreman_object":
                db_actions.set_user_system_key(user_id, "object_id", call.data[14:])
                bot.send_message(user_id, "Выберите действие", reply_markup=buttons.foreman_object_buttons())
            elif call.data == "go_work":
                bot.send_message(user_id, 'Выберите пункт', reply_markup=buttons.foreman_work_object())
            elif call.data == "add_work":
                bot.send_message(user_id, "Выберите тип работы", reply_markup=buttons.foreman_choose_type_work())
            elif call.data[:13] == "work_category":
                db_actions.set_user_system_key(user_id, "category_id", call.data[13:])
                bot.send_message(user_id, "Введите название подкатегории")
                db_actions.set_user_system_key(user_id, "index", 3)
            elif call.data == "get_report":
                object_id = db_actions.get_user_system_key(user_id, "object_id")
                db_actions.db_export_object_report(object_id)
                try:
                    if not db_actions.db_export_object_report(object_id):
                        bot.send_message(user_id, "❌ Ошибка при создании отчета")
                        return
                    with open("report.xlsx", 'rb') as f:
                        bot.send_document(user_id, f)
                    try:
                        os.remove("report.xlsx")
                    except Exception as e:
                        print(f"Ошибка при удалении временного файла: {e}")
                except Exception as e:
                    bot.send_message(user_id, f"Ошибка при обработке отчета: {str(e)}")
            elif call.data[:14] == "category_work1":
                db_actions.set_user_system_key(user_id, "category_id", call.data[14:])
                subcategories = db_actions.get_work_subcategories(user_id, category_id=call.data[14:])
                if subcategories:
                    bot.send_message(user_id, "Выберите подкатегорию", reply_markup=buttons.foreman_need_choose_subcategory(subcategories))
                else:
                    bot.send_message(user_id, "❌ Подкатегории не найдены")
            elif call.data[:17] == "work_subcategory1":
                db_actions.set_user_system_key(user_id, "subcategory_id", call.data[17:])
                bot.send_message(user_id, "Введите название работы")
                db_actions.set_user_system_key(user_id, "index", 4)
            elif call.data == "add_materials":
                object_id = db_actions.get_user_system_key(user_id, "object_id")
                category = db_actions.get_work_categories(user_id, object_id)
                if category:
                    bot.send_message(user_id, "Выберите категорию", reply_markup=buttons.foreman_need_choose_category(category))
                else:
                    bot.send_message(user_id, "❌ Категории не найдены")
            elif call.data == "add_smr":
                object_id = db_actions.get_user_system_key(user_id, "object_id")
                category = db_actions.get_work_categories(user_id, object_id)
                bot.send_message(user_id, "Выберите категорию", reply_markup=buttons.foreman_choose_category1(category))
            elif call.data[:17] == "1foreman_category":
                subcategory = db_actions.get_work_subcategories(user_id, call.data[17:])
                bot.send_message(user_id, "Выберите подкатегорию", reply_markup=buttons.foreman_choose_subcategory1(subcategory))
            elif call.data[:20] == "1foreman_subcategory":
                work_type = db_actions.get_work_type(user_id, call.data[20:])
                bot.send_message(user_id, "Выберите вид работы", reply_markup=buttons.foreman_choose_work_type1(work_type))
            elif call.data[:18] == "1foreman_work_type":
                db_actions.set_user_system_key(user_id, "work_type_id", call.data[18:])
                smr = db_actions.select_material_smr(user_id, call.data[18:])
                if not smr:
                    bot.send_message(user_id, "✏️ Введите объем")
                    db_actions.set_user_system_key(user_id, "index", 34)
                else:
                    bot.send_message(user_id, "❌ Для данного вида работы СМР уже указан!")
            elif call.data[:16] == "foreman_category":
                db_actions.set_user_system_key(user_id, "category_id", call.data[16:])
                subcategory = db_actions.get_work_subcategories(user_id, category_id=call.data[16:])
                if subcategory:
                    bot.send_message(user_id, "Выберите подкатегорию", reply_markup=buttons.foreman_choose_subcategory(subcategory))
                else:
                    bot.send_message(user_id, "Подкатегории не найдены")
            elif call.data[:19] == "foreman_subcategory":
                db_actions.set_user_system_key(user_id, "subcategory_id", call.data[19:])
                work_type = db_actions.get_work_type(user_id, call.data[19:])
                bot.send_message(user_id, "Выберите тип работы", reply_markup=buttons.foreman_choose_work_type(work_type))
            elif call.data[:17] == "foreman_work_type":
                db_actions.set_user_system_key(user_id, "work_type_id", call.data[17:])
                smr = db_actions.select_material_smr(user_id, call.data[17:])
                if not smr:
                    bot.send_message(user_id, "❌ Сначала добавьте СМР!")
                else:
                    bot.send_message(user_id, "Введите название материала")
                    db_actions.set_user_system_key(user_id, "index", 8)
            elif call.data == "add_technique":
                categories = db_actions.get_work_categories(user_id, object_id=db_actions.get_user_system_key(user_id, "object_id"))
                bot.send_message(user_id, "Выберите категорию", reply_markup=buttons.categories_technique_buttons(categories))
            elif call.data[:20] == "categories_technique":
                subcategory = db_actions.get_work_subcategories(user_id, call.data[20:])
                bot.send_message(user_id, "Выберите подкатегорию", reply_markup=buttons.subcategories_technique_buttons(subcategory))
            elif call.data[:23] == "subcategories_technique":
                work_type = db_actions.get_work_type(user_id, call.data[23:])
                bot.send_message(user_id, "Выберите вид работы", reply_markup=buttons.work_types_technique_buttons(work_type))
            elif call.data[:20] == "work_types_technique":
                db_actions.set_user_system_key(user_id, "work_type_id", call.data[20:])
                bot.send_message(user_id, "🚛 Введите название техники")
                db_actions.set_user_system_key(user_id, "index", 15)
            elif call.data == "go_coming":
                bot.send_message(user_id, "⏰ Введите дату прихода\n" \
                "Вводите дату в формате год-месяц-число (Например: 2025-12-31)")
                db_actions.set_user_system_key(user_id, "index", 21)

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
                bot.send_message(user_id, "✅ Новый объект записан, вот список существующих объектов:\n" \
                f"{objects_list}")
                db_actions.set_user_system_key(user_id, "index", None)
            elif code == 2:
                # user_input - category name
                object_id = db_actions.get_user_system_key(user_id, "admin_object_id")
                db_actions.add_work_categories(user_id, object_id, user_input)
                bot.send_message(user_id, "✅ Категория записана")
                db_actions.set_user_system_key(user_id, "index", None)

            elif code == 3:
                category_id = db_actions.get_user_system_key(user_id, "category_id")
                db_actions.add_work_subcategories(user_id, category_id, user_input)
                bot.send_message(user_id, "✅ Подкатегория добавлена")
                db_actions.set_user_system_key(user_id, "index", None)
            elif code == 4:
                subcategory_id = db_actions.get_user_system_key(user_id, "subcategory_id")
                db_actions.set_user_system_key(user_id, "work_type_name", user_input)
                bot.send_message(user_id, "Введите единицу измерения")               
                db_actions.set_user_system_key(user_id, "index", 5)
            elif code == 5:
                subcategory_id = db_actions.get_user_system_key(user_id, "subcategory_id")
                work_name = db_actions.get_user_system_key(user_id, "work_type_name")
                db_actions.add_work_type(user_id, subcategory_id, work_name, user_input)
                bot.send_message(user_id, "✅ Тип работы записан") 
                db_actions.set_user_system_key(user_id, "index", None)
            elif code == 8:
                db_actions.set_user_system_key(user_id, "material_name", user_input)
                bot.send_message(user_id, "👷‍♀️ Введите контрагента")
                db_actions.set_user_system_key(user_id, "index", 10)
            elif code == 10:
                db_actions.set_user_system_key(user_id, "material_counterparty", user_input)
                bot.send_message(user_id, "✏️ Введите объем")
                db_actions.set_user_system_key(user_id, "index", 11)
            elif code == 11:
                db_actions.set_user_system_key(user_id, "material_volume", user_input)
                bot.send_message(user_id, "💸 Введите цену")
                db_actions.set_user_system_key(user_id, "index", 12)
            elif code == 12:
                from datetime import date
                work_type_id = db_actions.get_user_system_key(user_id, "work_type_id")
                name = db_actions.get_user_system_key(user_id, "material_name")
                norm = db_actions.get_user_system_key(user_id, "material_norm")
                unit = db_actions.get_user_system_key(user_id, "material_unit")
                counterparty = db_actions.get_user_system_key(user_id, "material_counterparty")
                registration_number = db_actions.get_user_system_key(user_id, "material_registration_number")
                volume = db_actions.get_user_system_key(user_id, "material_volume")
                today = date.today()
                db_actions.add_work_material(user_id, work_type_id, today, name, norm, unit, counterparty, registration_number, volume, user_input)
                bot.send_message(user_id, "✅ Материал успешно записан")
                db_actions.set_user_system_key(user_id, "index", None)
            elif code == 15:
                db_actions.set_user_system_key(user_id, "technique_name", user_input)
                bot.send_message(user_id, "👷‍♀️ Введите контрагента")
                db_actions.set_user_system_key(user_id, "index", 16)
            elif code == 16:
                db_actions.set_user_system_key(user_id, "technique_contragent", user_input)
                bot.send_message(user_id, "#️⃣ Введите государственный № техники")
                db_actions.set_user_system_key(user_id, "index", 17)
            elif code == 17:
                db_actions.set_user_system_key(user_id, "technique_contragent", user_input)
                bot.send_message(user_id, "📏 Введите единицу измерения")
                db_actions.set_user_system_key(user_id, "index", 18)
            elif code == 18:
                db_actions.set_user_system_key(user_id, "technique_unit", user_input)
                bot.send_message(user_id, "✏️ Введите объем (кол-во часов)")
                db_actions.set_user_system_key(user_id, "index", 19)
            elif code == 19:
                db_actions.set_user_system_key(user_id, "technique_volume", user_input)
                bot.send_message(user_id, "💸 Введите цену за час")
                db_actions.set_user_system_key(user_id, "index", 20)
            elif code == 20:
                object_id = db_actions.get_user_system_key(user_id, "object_id")
                work_type_id = db_actions.get_user_system_key(user_id, "work_type_id")
                name = db_actions.get_user_system_key(user_id, "technique_name")
                contragent = db_actions.get_user_system_key(user_id, "technique_contragent")
                number = db_actions.get_user_system_key(user_id, "technique_number")
                unit = db_actions.get_user_system_key(user_id, "technique_unit")
                volume = db_actions.get_user_system_key(user_id, "technique_volume")
                db_actions.add_technique(user_id, object_id, work_type_id, name, contragent, number, unit, volume, user_input)
                bot.send_message(user_id, "✅ Данные записаны")
                db_actions.set_user_system_key(user_id, "index", None)
            elif code == 21:
                db_actions.set_user_system_key(user_id, "coming_date", user_input)
                bot.send_message(user_id, "Введите название прихода")
                db_actions.set_user_system_key(user_id, "index", 22)
            elif code == 22:
                db_actions.set_user_system_key(user_id, "coming_name", user_input)
                bot.send_message(user_id, "📏 Введите единицу измерения")
                db_actions.set_user_system_key(user_id, "index", 23)
            elif code == 23:
                db_actions.set_user_system_key(user_id, "coming_unit", user_input)
                bot.send_message(user_id, "✏️ Введите объем")
                db_actions.set_user_system_key(user_id, "index", 24)
            elif code == 24:
                db_actions.set_user_system_key(user_id, "coming_volume", user_input)
                bot.send_message(user_id, "🚚 Введите поставщика")
                db_actions.set_user_system_key(user_id, "index", 25)
            elif code == 25:
                db_actions.set_user_system_key(user_id, "coming_supplier", user_input)
                bot.send_message(user_id, "💸 Введите цену без НДС")
                db_actions.set_user_system_key(user_id, "index", 26)
            elif code == 26:
                object_id = db_actions.get_user_system_key(user_id, "object_id")
                today = db_actions.get_user_system_key(user_id, "coming_date")
                name = db_actions.get_user_system_key(user_id, "coming_name")
                unit = db_actions.get_user_system_key(user_id, "coming_unit")
                volume = db_actions.get_user_system_key(user_id, "coming_volume")
                supplier = db_actions.get_user_system_key(user_id, "coming_supplier")
                db_actions.add_list_coming(user_id, object_id, today, name, unit, volume, supplier, user_input)
                bot.send_message(user_id, "✅ Данные записаны")
                db_actions.set_user_system_key(user_id, "index", None)
            elif code == 27:
                row_id = db_actions.get_user_system_key(user_id, "material_id")
                norm = db_actions.get_user_system_key(user_id, "material_norm")
                db_actions.add_mateials_norm(user_id, norm, row_id)
                bot.send_message(user_id, "✅ Данные записаны")
                db_actions.set_user_system_key(user_id, "index", None)
            elif code == 28:
                db_actions.add_materials_unit(user_id, user_input, row_id=db_actions.get_user_system_key(user_id, "material_id"))
                bot.send_message(user_id, "✅ Данные записаны")
                db_actions.set_user_system_key(user_id, "index", None)
            elif code == 29:
                db_actions.add_materials_number(user_id, user_input, row_id=db_actions.get_user_system_key(user_id, "material_id"))
                bot.send_message(user_id, "✅ Данные записаны")
                db_actions.set_user_system_key(user_id, "index", None)
            elif code == 30:
                db_actions.set_user_system_key(user_id, "material_unit", user_input)
                bot.send_message(user_id, "✏️ Введите объем")
                db_actions.set_user_system_key(user_id, "index", 31)
            elif code == 31:
                db_actions.set_user_system_key(user_id, "material_volume", user_input)
                bot.send_message(user_id, "💸 Введите цену")
                db_actions.set_user_system_key(user_id, "index", 32)
            elif code == 32:
                work_type = db_actions.get_user_system_key(user_id, "work_type_id")
                unit = db_actions.get_user_system_key(user_id, "material_unit")
                volume = db_actions.get_user_system_key(user_id, "material_volume")
                db_actions.edit_material_smr(user_id, unit, volume, user_input, work_type)
                bot.send_message(user_id, "✅ Данные записаны")
                db_actions.set_user_system_key(user_id, "index", None)
            elif code == 34:
                db_actions.set_user_system_key(user_id, "material_volume", user_input)
                bot.send_message(user_id, "📏 Введите единицу измерения")
                db_actions.set_user_system_key(user_id, "index", 35)
            elif code == 35:
                db_actions.set_user_system_key(user_id, "material_unit", user_input)
                bot.send_message(user_id, "💸 Введите цену")
                db_actions.set_user_system_key(user_id, "index", 36)
            elif code == 36:
                from datetime import date
                today = date.today()
                work_type_id = db_actions.get_user_system_key(user_id, "work_type_id")
                volume = db_actions.get_user_system_key(user_id, "material_volume")
                unit = db_actions.get_user_system_key(user_id, "material_unit")
                db_actions.add_material_smr(user_id, date=today, volume=volume, unit=unit, cost=user_input, work_type_id=work_type_id)
                bot.send_message(user_id, "✅ СМР создан!")
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