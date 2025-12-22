from datetime import datetime

import pytz
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from FSM import Breef, Get_admin
from functions import clients_base, is_today, send_long_message
from keyboards import Buttons
from paswords import admin_id, admins_list, loggs_acc
from structure import HELP_TEXT, structure_menu

moscow_tz = pytz.timezone('Europe/Moscow')


async def start(message: Message, bot, state: FSMContext):
    await state.clear()
    try:
        if message.chat.id in admins_list:
            await Buttons(
                bot,
                message,
                structure_menu["Основное меню"],
                question="<b>Бот-для проведения тестов</b>\n"
                "<b>Режим доступа</b>: Администратор\n"
                "/help - справка по боту\n\n"
                "Пожалуйста выберите интересующий пункт меню:",
            ).menu_buttons()
        else:
            await Buttons(
                bot,
                message,
                structure_menu["Основное меню"],
                question="<b>Бот-для проведения тестов</b>\n"
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
                "/help - список доступных команд\n",
                # "/day_visitors - пользователи посетившие бота сегодня",
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
            await bot.answer_callback_query(callback.id)
            await Buttons(
                bot, callback.message, {}, "Основное меню", question=HELP_TEXT
            ).menu_buttons()

        elif callback.data == "👨🏻‍💻 Чат с администратором":
            await state.clear()
            await bot.answer_callback_query(callback.id)
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
                f"<b>Если ссылка на чат отсутствует запроси контакт или отправь свой с помощью команды</b>:\n",
                parse_mode="html",
            )
            await state.set_state(Get_admin.message)

        elif callback.data == "Основное меню":
            await state.clear()
            await bot.answer_callback_query(callback.id)
            await Buttons(
                bot,
                callback.message,
                structure_menu["Основное меню"],
                question="Пожалуйста выберите интересующий пункт меню:",
            ).menu_buttons()

        elif callback.data == "назад":
            data = await state.get_data()
            if len(data) == 0:
                await bot.answer_callback_query(callback.id)
                await Buttons(
                    bot,
                    callback.message,
                    structure_menu["Основное меню"],
                    question="Пожалуйста выберите интересующий пункт меню:",
                ).menu_buttons()
            else:
                section = data["section"]
                idx = data["question_idx"]
                idx -= 1
                question = structure_menu["Основное меню"]['✍🏼 Тесты ️'][section]['questions'][idx]
                text = question['part'] + '\n\n' + question['text']
                keys_dict = {}
                for k in question['options']:
                    keys_dict[f'{k}'] = f'answer_{k}_{question["options"][k]}'
                await bot.answer_callback_query(callback.id)
                if idx == 0:
                    await Buttons(
                        bot,
                        callback.message,
                        question=text,
                        back_button='✍🏼 Тесты ️', keys_dict=keys_dict).test_buttons()
                    await state.update_data(
                        question_idx=0,
                        answers = []
                    )
                else:
                    await Buttons(
                        bot,
                        callback.message,
                        question=text,
                        back_button='назад', keys_dict=keys_dict).test_buttons(type=question['type'])
                    await state.update_data(
                        question_idx=idx
                    )
                await state.update_data(question_idx=idx)

        elif callback.data == '✍🏼 Тесты ️':
            await state.clear()
            text = "Для прохождения доступны следующие тесты:\n\n\n"
            keys_dict = {}
            for i in structure_menu["Основное меню"][callback.data]:
                text = text + i['id'] + " " + i['title'] + "\n\n"
                keys_dict[f'{i["id"]}'] = f'test_{structure_menu["Основное меню"][callback.data].index(i)}'
            await bot.answer_callback_query(callback.id)
            await Buttons(
                bot,
                callback.message,
                question=text,
                back_button='Основное меню', keys_dict=keys_dict).test_buttons()

        elif callback.data.startswith('test_'):
            if str(callback.message.chat.id) not in await clients_base.get_clients():
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
            data = int(str(callback.data)[len('test_'):])
            question = structure_menu["Основное меню"]['✍🏼 Тесты ️'][data]['questions'][0]
            text = question['part'] + '\n\n' + question['text']
            keys_dict = {}
            for k in question['options']:
                keys_dict[f'{k}'] = f'answer_{k}'
            await bot.answer_callback_query(callback.id)
            await Buttons(
                bot,
                callback.message,
                question=text,
                back_button='✍🏼 Тесты ️', keys_dict=keys_dict).test_buttons()
            await state.update_data(
                section=data,
                question_idx=0,
                answers=[]
            )
            await state.set_state(Breef.in_progress)

        elif callback.data.startswith('answer_'):
            answer_value = callback.data.split('_')[1]
            data = await state.get_data()
            if len(data) == 0:
                await bot.answer_callback_query(callback.id)
                await Buttons(
                    bot,
                    callback.message,
                    structure_menu["Основное меню"],
                    question="Пожалуйста выберите интересующий пункт меню:",
                ).menu_buttons()
            else:
                section = data["section"]
                idx = data["question_idx"]
                answers = data["answers"]
                question = structure_menu["Основное меню"]['✍🏼 Тесты ️'][section]['questions'][idx]
                data_dict = {
                        'part': question['part'],
                        'type': question['type'],
                        'text': question['text'],
                        'answer': answer_value,
                        'correct': question['correct'],
                        'interpretation': question['interpretation']
                    }
                if len(answers) > idx:
                    answers[idx] = data_dict
                else:
                    answers.append(data_dict)

                idx += 1

                if idx < len(structure_menu["Основное меню"]['✍🏼 Тесты ️'][section]['questions']):
                    question = structure_menu["Основное меню"]['✍🏼 Тесты ️'][section]['questions'][idx]
                    text = question['part'] + '\n\n' + question['text']
                    keys_dict = {}
                    for k in question['options']:
                        keys_dict[f'{k}'] = f'answer_{k}'
                    await bot.answer_callback_query(callback.id)
                    await Buttons(
                        bot,
                        callback.message,
                        question=text,
                        back_button='назад', keys_dict=keys_dict).test_buttons(type=question['type'])
                    await state.update_data(question_idx=idx, answers=answers)

        elif callback.data.startswith('multi_'):
            type_value = callback.data.split('_')[1]
            data = await state.get_data()
            await bot.answer_callback_query(callback.id)
            if len(data) == 0:
                await Buttons(
                    bot,
                    callback.message,
                    structure_menu["Основное меню"],
                    question="Пожалуйста выберите интересующий пункт меню:",
                ).menu_buttons()
            else:
                section = data["section"]
                idx = data["question_idx"]
                answers = data["answers"]
                question = structure_menu["Основное меню"]['✍🏼 Тесты ️'][section]['questions'][idx]
                data_dict = {
                    'part': question['part'],
                    'type': question['type'],
                    'text': question['text'],
                    'answer': [],
                    'correct': question['correct'],
                    'interpretation': question['interpretation']
                }
                if len(answers) == idx:
                    answers.append(data_dict)

                if type_value == 'on':
                    answer_value = callback.data.split('_')[2]
                    if answer_value in answers[idx]['answer']:
                        pass
                    else:
                        answers[idx]['answer'].append(answer_value)

                elif type_value == 'off':
                    answer_value = callback.data.split('_')[2]
                    if answer_value[2:] in answers[idx]['answer']:
                        answers[idx]['answer'].remove(answer_value[2:])
                    else:
                        pass
                elif type_value == 'answer':
                    idx += 1

                question = structure_menu["Основное меню"]['✍🏼 Тесты ️'][section]['questions'][idx]
                text = question['part'] + '\n\n' + question['text']
                keys_dict = {}
                for k in question['options']:
                    if idx < len(answers):
                        if k in answers[idx]['answer']:
                            keys_dict[f'✅ {k}'] = f'multi_off_{k}'
                        else:
                            keys_dict[f'{k}'] = f'multi_on_{k}'

                    else:
                        keys_dict[f'{k}'] = f'multi_on_{k}'
                if idx < len(answers):
                    await Buttons(
                        bot,
                        callback.message,
                        question=text,
                        back_button='назад', keys_dict=keys_dict).test_buttons(type=question['type'])
                    await state.update_data(question_idx=idx, answers=answers)
                else:
                    bot_message = await Buttons(
                                        bot,
                                        callback.message,
                                        question=text,
                                        back_button='назад', keys_dict=keys_dict).test_buttons(type=question['type'])
                    await state.update_data(question_idx=idx, answers=answers, bot_message=bot_message)

    except Exception as e:
        logger.exception("Ошибка в handlers/check_callbacks", e)
        await bot.send_message(loggs_acc, f"Ошибка в handlers/check_callbacks: {e}")


async def check_messages(message: Message, bot, state: FSMContext):
    try:
        data = await state.get_data()
        if len(data) != 0:
            section = data["section"]
            idx = data["question_idx"]
            answers = data["answers"]
            bot_message = data["bot_message"]
            question = structure_menu["Основное меню"]['✍🏼 Тесты ️'][section]['questions'][idx]
            if question['type'] == 'matching':
                data_dict = {
                    'part': question['part'],
                    'type': question['type'],
                    'text': question['text'],
                    'answer': message.text,
                    'correct': question['correct'],
                    'interpretation': question['interpretation']
                }
                if len(answers) > idx:
                    answers[idx] = data_dict
                else:
                    answers.append(data_dict)

                idx += 1

                if idx < len(structure_menu["Основное меню"]['✍🏼 Тесты ️'][section]['questions']):
                    question = structure_menu["Основное меню"]['✍🏼 Тесты ️'][section]['questions'][idx]
                    text = question['part'] + '\n\n' + question['text']
                    mess = await Buttons(
                        bot,
                        message,
                        question=text,
                        back_button='назад', keys_dict={}).test_buttons(type=question['type'], bot_message=bot_message)
                    await state.update_data(question_idx=idx, answers=answers, bot_message=mess)
                else:
                    text = "РЕЗУЛЬТАТЫ ПРОХОЖДЕНИЯ\n\n\n"
                    for i in answers:
                        user_answer = ", ".join(i['answer']) if isinstance(i['answer'], list) else i['answer']
                        correct = ", ".join(i['correct']) if isinstance(i['correct'], list) else i['correct']
                        text = (text
                                + i['part']
                                + '\n\n'
                                + f"<i>{i['text']}</i>"
                                + '\n\n'
                                + '<b>Ваш ответ: </b>'
                                + user_answer
                                + '\n'
                                + '<b>Правильный ответ: </b>'
                                + correct
                                + '\n\n'
                                + "Пояснение:"
                                + i['interpretation']
                                + '\n\n')
                    await send_long_message(
                        bot,
                        message.chat.id,  # Отправляем результаты пользователю
                        f"{text}\n",
                        parse_mode="html"
                    )
                    # await bot.send_message(
                    #     admin_id,
                    #     f"🚨Уведомление🚨\n"
                    #     f"<b>Пройденный тест от:</b>\n"
                    #     f"Псевдоним: @{message.from_user.username}\n"
                    #     f"id чата: {message.chat.id}\n\n",
                    #     parse_mode="html"
                    # )
                    # await send_long_message(
                    #     bot,
                    #     admin_id,  # Отправляем результаты пользователю
                    #     f"<b>Результаты прохождения:</b>\n\n {text}\n",
                    #     parse_mode="html"
                    # )
                    await state.clear()

        else:
            pass
    except Exception as e:
        logger.exception("Ошибка в handlers/check_messages", e)
        await bot.send_message(loggs_acc, f"Ошибка в handlers/check_messages: {e}")
        await state.clear()