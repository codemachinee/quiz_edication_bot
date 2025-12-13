from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

from google_sheets import get_sheet_base
from paswords import admin_id, loggs_acc

# --- Классы состояний FSM для различных сценариев взаимодействия с ботом ---


class Get_admin(StatesGroup):
    # Состояние для обработки сообщений, поступающих от пользователя
    # в режиме чата с администратором.
    message = State()


class Message_from_admin(StatesGroup):
    # Состояние для запроса идентификатора пользователя (user_id)
    # при отправке сообщения от администратора.
    user_id = State()
    # Состояние для получения текста сообщения, которое администратор
    # хочет отправить пользователю.
    message = State()


class Rassylka(StatesGroup):
    # Состояние для выбора базы клиентов для рассылки (например, "Общая база клиентов").
    base = State()
    # Состояние для получения контента (текста или медиа) для рассылки.
    post = State()


class Breef(StatesGroup):
    # Состояние, указывающее, что пользователь в данный момент проходит опрос (бриф).
    in_progress = State()


# --- Асинхронные функции-обработчики, использующие FSM-состояния ---


async def message_from_user(message, state: FSMContext, bot):
    """
    Обработчик сообщений от пользователя в режиме чата с администратором.
    Пересылает сообщение пользователя администратору и подтверждает отправку пользователю.
    """
    try:
        await bot.send_message(
            admin_id, f"Сообщение от пользователя @{message.from_user.username}:"
        )
        await bot.copy_message(admin_id, message.chat.id, message.message_id)
        await bot.send_message(message.chat.id, "Ваше сообщение отправлено ✅")
        await state.clear()
    except Exception as e:
        logger.exception("Ошибка в FSM/message_from_users", e)
        await bot.send_message(loggs_acc, f"Ошибка в FSM/message_from_users: {e}")
        await state.clear()


async def message_from_admin_chat(message, state: FSMContext, bot):
    """
    Обработчик для получения user_id пользователя, которому администратор хочет отправить сообщение.
    Проверяет, является ли введенное значение числом, и переводит бота в следующее состояние для ввода сообщения.
    """
    try:
        if str.isdigit(message.text):
            await state.update_data(user_id=message.text)
            await bot.send_message(message.chat.id, "Введите сообщение")
            await state.set_state(Message_from_admin.message)
        else:
            await bot.send_message(
                message.chat.id,
                "Неверные данные... Повтори попытку используя цифры (Например: 1338281106)",
            )
            await state.set_state(Message_from_admin.user_id)
    except Exception as e:
        logger.exception("Ошибка в FSM/message_from_admin_chat", e)
        await bot.send_message(loggs_acc, f"Ошибка в FSM/message_from_admin_chat: {e}")
        await bot.send_message(
            message.chat.id,
            "Неверные данные... Повтори попытку используя цифры (Например: 1338281106)",
        )
        await state.set_state(Message_from_admin.user_id)


async def message_from_admin_text(message, state: FSMContext, bot):
    """
    Обработчик для отправки сообщения от администратора конкретному пользователю.
    Использует user_id, сохраненный в FSM-контексте, для пересылки сообщения.
    """
    try:
        data = await state.get_data()
        user_id = data.get("user_id")
        await bot.copy_message(user_id, message.chat.id, message.message_id)
        await bot.send_message(message.chat.id, "Ваше сообщение отправлено ✅")
        await state.clear()
    except Exception as e:
        logger.exception("Ошибка в FSM/message_from_admin_text", e)
        await bot.send_message(loggs_acc, f"Ошибка в FSM/message_from_admin_text: {e}")
        await state.clear()


async def rassylka(message, bot, state: FSMContext):
    """
    Обработчик для выполнения рассылки сообщения всем пользователям из базы.
    Использует функцию `rasylka_v_bazu` из модуля `google_sheets`.
    """
    try:
        sheet_base = await get_sheet_base()
        await sheet_base.rasylka_v_bazu(bot, message)
        await state.clear()
    except Exception as e:
        logger.exception("Ошибка в FSM/rassylka", e)
        await bot.send_message(loggs_acc, f"Ошибка в FSM/rassylka: {e}")
        await state.clear()
