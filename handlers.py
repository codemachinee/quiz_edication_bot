from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from FSM import Breef, Get_admin, Message_from_admin, Rassylka
from functions import clients_base, is_today
from google_sheets import get_sheet_base, moscow_tz
from keyboards import Buttons
from paswords import admin_id, admins_list, loggs_acc
from structure import HELP_TEXT, structure_menu


async def start(message: Message, bot, state: FSMContext):
    await state.clear()
    try:
        await bot.send_message(
            message.chat.id,
            "<b>Инструкция по использованию бота:</b>\n\n\n"
            '- Выберите интересующий <b>опрос</b> (например, "🌐 Опрос '
            '"создание сайта") для прохождения брифа.\n\n'
            "- Отвечайте на вопросы, отправляя <b>текстовые сообщения</b>.\n\n"
            "- Если ответа нет, <b>отправьте любой текст</b>, чтобы перейти к "
            "следующему вопросу.\n\n"
            '- Нажмите <b>"✅ Отправить ответы"</b>. - для отправки ответов '
            "исполнителю.\n\n"
            '- Выберите <b>"⬅️ Предыдущий вопрос"</b> для изменения ответа на предыдущий вопрос.\n\n'
            '- Выберите <b>"❌ Отмена"</b> для выхода в главное меню.',
            parse_mode="html",
        )
        if message.chat.id in admins_list:
            await Buttons(
                bot,
                message,
                structure_menu["Основное меню"],
                question="<b>Бот-опросник для разработки цифровых продуктов </b>\n"
                "<b>Режим доступа</b>: Администратор\n"
                "/help - справка по боту\n\n"
                "Пожалуйста выберите интересующий пункт меню:",
            ).menu_buttons()
        else:
            await Buttons(
                bot,
                message,
                structure_menu["Основное меню"],
                question="<b>Бот-опросник для разработки цифровых продуктов.</b>\n"
                "/help - справка по боту\n\n"
                "Пожалуйста выберите интересующий пункт меню:",
            ).menu_buttons()
    except Exception as e:
        logger.exception("Ошибка в handlers/start", e)
        await bot.send_message(loggs_acc, f"Ошибка в handlers/start: {e}")


async def help(message: Message, bot, state: FSMContext):
    await state.clear()
    try:
        if (
            message.chat.id in admins_list
        ):  # условия демонстрации различных команд для админа и клиентов
            await bot.send_message(
                message.chat.id,
                "<b>Основные команды поддерживаемые ботом:\n</b>"
                "/menu - главное функциональное меню\n"
                "/start - инициализация бота\n"
                "/help - список доступных команд\n"
                "/post - устроить рассылку\n"
                "/sent_message -  отправка через бота сообщения клиенту по id чата\n"
                "/day_visitors - пользователи посетившие бота сегодня",
                parse_mode="html",
            )
        else:
            await bot.send_message(
                message.chat.id,
                "<b>Основные команды поддерживаемые ботом:\n</b>"
                "/menu - главное функциональное меню\n"
                "/start - инициализация бота\n"
                "/help - список доступных команд\n\n\n"
                "@hlapps - разработка ботов любой сложности",
                parse_mode="html",
            )
    except Exception as e:
        logger.exception("Ошибка в handlers/help", e)
        await bot.send_message(loggs_acc, f"Ошибка в handlers/help: {e}")


async def menu(message: Message, bot, state: FSMContext):
    await state.clear()
    try:
        if (
            message.chat.id in admins_list
        ):  # условия демонстрации различных команд для админа и клиентов
            await Buttons(
                bot,
                message,
                structure_menu["Основное меню"],
                question="Пожалуйста выберите интересующий пункт меню:",
            ).menu_buttons()

        else:
            await Buttons(
                bot,
                message,
                structure_menu["Основное меню"],
                question="Пожалуйста выберите интересующий пункт меню:",
            ).menu_buttons()
    except Exception as e:
        logger.exception("Ошибка в handlers/menu", e)
        await bot.send_message(loggs_acc, f"Ошибка в handlers/menu: {e}")


async def post(message: Message, bot, state: FSMContext):
    await state.clear()
    try:
        if message.chat.id in admins_list:
            await Buttons(bot, message, {}).rasylka_buttons()
            await state.set_state(Rassylka.post)

        else:
            await bot.send_message(
                message.chat.id, "У Вас нет прав для использования данной команды"
            )
    except Exception as e:
        logger.exception("Ошибка в handlers/post", e)
        await bot.send_message(loggs_acc, f"Ошибка в handlers/post {e}")


async def sent_message(message: Message, bot, state: FSMContext):
    try:
        await state.clear()
        if message.chat.id in admins_list:
            await bot.send_message(
                message.chat.id,
                "Введи id чата клиента, которому нужно написать от лица бота",
            )
            await state.set_state(Message_from_admin.user_id)
        else:
            await bot.send_message(
                message.chat.id, "У Вас нет прав для использования данной команды"
            )
    except Exception as e:
        logger.exception("Ошибка в handlers/sent_message", e)
        await bot.send_message(loggs_acc, f"Ошибка в handlers/sent_message: {e}")


async def day_visitors(message: Message, bot, state: FSMContext):
    await state.clear()
    today_list = []
    mess = await bot.send_message(message.chat.id, "Загрузка..🚀")
    try:
        if message.chat.id in admins_list:
            data = await clients_base.get_clients()
            for d in data:
                if await is_today(data[d]["date"]):
                    today_list.append(
                        [d, data[d]["username"], data[d]["name"], data[d]["date"]]
                    )
                else:
                    del data[d]
                    pass

            if len(today_list) == 0:
                await bot.edit_message_text(
                    chat_id=message.chat.id,
                    text="Сегодня пользователей не было",
                    message_id=mess.message_id,
                )
            else:
                table_header = f"Пользователи воспользовавшиеся ботом сегодня {len(today_list)}:\n\n"
                table_body = " *Telegram ID* | *Ссылка* | *Имя* | *Время*\n"
                table_body += "-" * 39 + "\n"
                for i in today_list:
                    table_body += f"{i[0]} | @{i[1]} | {i[2]} | {i[3][9:]}\n" + (
                        "-" * 39 + "\n"
                    )

                await bot.edit_message_text(
                    chat_id=message.chat.id,
                    text=table_header + table_body,
                    message_id=mess.message_id,
                    parse_mode="Markdown",
                )
        else:
            await bot.send_message(
                message.chat.id,
                "Недостаточно прав",
                message_thread_id=message.message_thread_id,
            )
    except Exception as e:
        logger.exception("Ошибка в handlers/day_visitors", e)
        await bot.send_message(loggs_acc, f"Ошибка в handlers/day_visitors: {e}")


async def check_callbacks(callback: CallbackQuery, bot, state: FSMContext):
    assert (
        callback is not None
    )  # обозначаем для проверочной библиотеки mypy, чтобы избегать лишних ошибок при тесте
    assert callback.data is not None
    try:
        if callback.data == "ℹ️ Обо мне":
            await state.clear()
            await Buttons(
                bot, callback.message, {}, "Основное меню", question=HELP_TEXT
            ).menu_buttons()

        elif callback.data == "🔎 Примеры работ":
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text="<b>Перейти на google диск для просмотра портфолио: </b>"
                "https://drive.google.com/drive/folders/1IJIbj-ML4eG5jdoWohRyRC2fqR92jkUE?usp=sharing",
                parse_mode="html",
            )

        elif callback.data == "👨🏻‍💻 Чат с администратором":
            await state.clear()
            await bot.edit_message_text(
                chat_id=callback.message.chat.id,
                text="Информация передана администратору, с Вами скоро свяжутся. "
                "Если желаете сообщить что-то дополнительно, отправьте в сообщении 💬\n"
                "Спасибо, что выбрали нас.🤝\n"
                "Для возвращения меню: /menu",
                message_id=callback.message.message_id,
            )

            await bot.send_message(
                chat_id=admin_id,
                text=f"🚨!!!СРОЧНО!!!🚨\n"
                f"<b>поступил запрос на ЧАТ С АДМИНИСТРАТОРОМ от:</b>\n"
                f"Ссылка: @{callback.from_user.username}\n"
                f"id чата: {callback.message.chat.id}\n"
                f"<b>Если ссылка на чат отсутствует запроси контакт или отправь свой с помощью команды</b>:\n"
                f"/sent_message - отправить сообщение с помощью бота",
                parse_mode="html",
            )
            await state.set_state(Get_admin.message)

        elif callback.data == "Основное меню":
            await state.clear()
            await Buttons(
                bot,
                callback.message,
                structure_menu["Основное меню"],
                question="Пожалуйста выберите интересующий пункт меню:",
            ).menu_buttons()

        elif callback.data == "назад":
            data = await state.get_data()
            section = data["section"]
            idx = data["question_idx"]
            answers = data["answers"]
            bot_message_id = data["bot_message_id"]
            idx -= 1
            if idx == 0:
                bot_message = await Buttons(
                    bot,
                    callback.message,
                    question=structure_menu["Основное меню"][section][idx],
                ).breef_buttons(
                    bot_message_id,
                    idx=0,
                    answer=answers[idx],
                    quantity_of_questions=len(structure_menu["Основное меню"][section]),
                )
            else:
                bot_message = await Buttons(
                    bot,
                    callback.message,
                    question=structure_menu["Основное меню"][section][idx],
                ).breef_buttons(
                    bot_message_id=bot_message_id,
                    answer=answers[idx],
                    quantity_of_questions=len(structure_menu["Основное меню"][section]),
                    number_of_question=idx + 1,
                )
            # answers.pop()
            await state.update_data(
                question_idx=idx, answers=answers, bot_message_id=bot_message.message_id
            )

        elif callback.data in [
            '🌐 Опрос "создание сайта"',
            '🤖 Опрос "создание бота"',
            '🖼 Опрос "другое"',
        ]:
            if str(callback.message.chat.id) not in await clients_base.get_clients():
                sheet_base = await get_sheet_base()
                await sheet_base.chec_and_record_in_client_base(bot, callback.message)
                await clients_base.set_clients(
                    data={
                        "id": callback.message.chat.id,
                        "username": callback.message.chat.username,
                        "name": callback.message.chat.first_name,
                        "reasons": callback.data,
                        "date": str(datetime.now(moscow_tz).strftime("%d.%m.%y %H:%M")),
                    }
                )
            else:
                await clients_base.update_clients(
                    str(callback.message.chat.id),
                    "date",
                    str(datetime.now(moscow_tz).strftime("%d.%m.%y %H:%M")),
                )
            bot_message = await Buttons(
                bot,
                callback.message,
                question=structure_menu["Основное меню"][callback.data][0],
            ).breef_buttons(
                callback.message.message_id,
                idx=0,
                quantity_of_questions=len(
                    structure_menu["Основное меню"][callback.data]
                ),
            )
            await state.update_data(
                section=callback.data,
                question_idx=0,
                answers=[],
                bot_message_id=bot_message.message_id,
            )
            await state.set_state(Breef.in_progress)

        elif callback.data == "✅ Отправить ответы":
            data = await state.get_data()
            section = data["section"]
            answers = data["answers"]
            await bot.edit_message_text(
                text="✅ Результаты опроса отправлены",
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
            )
            sheet_base = await get_sheet_base()
            await sheet_base.record_in_base(
                bot, message=callback.message, section=section, answers=answers
            )
            await state.clear()

        elif callback.data == "Общая база клиентов":
            await bot.edit_message_text(
                text="База для рассылки: Общая база клиентов\nОтправь мне пост 💬",
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
            )
            await state.update_data(base=callback.data)
            await state.set_state(Rassylka.post)

    except Exception as e:
        logger.exception("Ошибка в handlers/check_callbacks", e)
        await bot.send_message(loggs_acc, f"Ошибка в handlers/check_callbacks: {e}")


async def check_messages(message: Message, bot, state: FSMContext):
    try:
        if message.text == "назад":
            data = await state.get_data()
            section = data["section"]
            idx = data["question_idx"]
            answers = data["answers"]
            bot_message_id = data["bot_message_id"]
            idx -= 1
            if idx == 0:
                await Buttons(
                    bot, message, question=structure_menu["Основное меню"][section][idx]
                ).breef_buttons(
                    bot_message_id,
                    idx=0,
                    answer=answers[idx],
                    number_of_question=idx + 1,
                    quantity_of_questions=len(structure_menu["Основное меню"][section]),
                )
            else:
                await Buttons(
                    bot, message, question=structure_menu["Основное меню"][section][idx]
                ).breef_buttons(
                    bot_message_id=bot_message_id,
                    answer=answers[idx],
                    number_of_question=idx + 1,
                    quantity_of_questions=len(structure_menu["Основное меню"][section]),
                )
            answers.pop()  # Удаляем последний ответ
            await state.update_data(question_idx=idx, answers=answers)

        elif message.text == "Основное меню":
            await state.clear()
            await Buttons(
                bot,
                message,
                structure_menu["Основное меню"],
                question="Пожалуйста выберите интересующий пункт меню:",
            ).menu_buttons()
        else:
            data = await state.get_data()
            section = data["section"]
            idx = data["question_idx"]
            answers = data["answers"]
            bot_message_id = data["bot_message_id"]
            if len(answers) > idx:
                answers[idx] = message.text
            else:
                answers.append(message.text)

            idx += 1

            if idx < len(structure_menu["Основное меню"][section]):
                await state.update_data(question_idx=idx, answers=answers)
                await Buttons(
                    bot, message, question=structure_menu["Основное меню"][section][idx]
                ).breef_buttons(
                    bot_message_id,
                    idx=1,
                    number_of_question=idx + 1,
                    quantity_of_questions=len(structure_menu["Основное меню"][section]),
                )
            else:
                questions = list(structure_menu["Основное меню"][section])
                combined_answers = [
                    f"<b>{questions.index(item1) + 1}. {item1}:</b>\n{item2}"
                    for item1, item2 in zip(questions, answers)
                ]
                answer = "\n".join(combined_answers)
                await Buttons(
                    bot,
                    message,
                    question="Cпасибо за прохождение опроса! Выберите (✅ Отправить ответы) для передачи "
                    "исполнителю или же пройдите опрос заново (❌ Отмена)."
                    "\n\n" + answer,
                ).breef_buttons(idx=2, bot_message_id=bot_message_id)
                await bot.send_message(
                    admin_id,
                    f"🚨!!!СРОЧНО!!!🚨\n"
                    f"<b>Заполненный бриф от:</b>\n"
                    f"Псевдоним: @{message.from_user.username}\n"
                    f"id чата: {message.chat.id}\n\n"
                    f"<b>Предмет интереса:</b>\n"
                    f"Категория: {section}\n"
                    f"/sent_message - отправить сообщение с помощью бота",
                    parse_mode="html",
                )
                await bot.send_message(
                    admin_id,
                    f"<b>Ответы:</b>\n\n {answer}\n"
                    "Дополнительная информация в гугл таблице: "
                    "https://docs.google.com/spreadsheets/d/"
                    "1oGihEnG8KIsnZxd8W_B-TxGc10s_aOxpLPZgaqFBTIc/edit?usp=sharing",
                    parse_mode="html",
                )
    except Exception as e:
        logger.exception("Ошибка в handlers/check_messages", e)
        await bot.send_message(loggs_acc, f"Ошибка в handlers/check_messages: {e}")
