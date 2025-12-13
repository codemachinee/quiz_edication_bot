import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import BotCommand
from loguru import logger

# Импорт FSM-состояний и функций-обработчиков для FSM
from FSM import (
    Breef,
    Get_admin,
    Message_from_admin,
    Rassylka,
    message_from_admin_chat,
    message_from_admin_text,
    message_from_user,
    rassylka,
)

# Импорт класса для управления клиентской базой
from functions import clients_base

# Импорт функции для получения доступа к Google Sheets
from google_sheets import get_sheet_base

# Импорт основных обработчиков команд и сообщений
from handlers import (
    check_callbacks,
    check_messages,
    day_visitors,
    help,
    menu,
    post,
    sent_message,
    start,
)

# Импорт токенов и идентификаторов для логирования и бота
from paswords import codemachinee_breef_bot, loggs_acc

# --- Настройка логирования с помощью Loguru ---
logger.remove()  # Удаляет стандартные обработчики loguru, чтобы настроить свои
logger.add(
    "loggs.log",  # Путь к файлу логов
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",  # Формат записи в лог
    level="INFO",  # Минимальный уровень логирования
    rotation="5 MB",  # Ротация файла при достижении 5 MB
    retention="10 days",  # Хранить логи за последние 10 дней
    compression="zip",  # Сжимать старые файлы логов в ZIP-архив
    backtrace=True,  # Отображать трассировку стека для ошибок
    diagnose=True,  # Включать подробную диагностику
)

# --- Инициализация бота и диспетчера ---
token = codemachinee_breef_bot  # Выбор токена для бота
# token = codemashine_test # Закомментированный тестовый токен

bot = Bot(token=token)  # Создание экземпляра бота
dp = Dispatcher()  # Создание экземпляра диспетчера для обработки событий

# --- Регистрация обработчиков сообщений и команд ---

# Регистрация обработчиков для стандартных команд Telegram
dp.message.register(start, Command(commands="start"))
dp.message.register(help, Command(commands="help"))
dp.message.register(menu, Command(commands="menu"))
dp.message.register(post, Command(commands="post"))
dp.message.register(sent_message, Command(commands="sent_message"))
dp.message.register(day_visitors, Command(commands="day_visitors"))

# Регистрация обработчиков для FSM-состояний, связанных с административными функциями и рассылками
dp.message.register(message_from_admin_chat, Message_from_admin.user_id)
dp.message.register(message_from_admin_text, Message_from_admin.message)
dp.message.register(rassylka, Rassylka.post)

# Регистрация обработчиков для callback-запросов и текстовых сообщений в контексте FSM
dp.callback_query.register(
    check_callbacks, Breef.in_progress
)  # Обработка callback-кнопок во время опроса
dp.callback_query.register(
    check_callbacks, F.data
)  # Общий обработчик для всех callback-кнопок
dp.message.register(
    check_messages, F.text, Breef.in_progress
)  # Обработка текстовых сообщений во время опроса
dp.message.register(
    message_from_user, Get_admin.message
)  # Обработка сообщений в режиме чата с админом


# --- Асинхронная функция для установки команд бота в меню Telegram ---
async def set_commands():
    """
    Устанавливает список команд, которые будут отображаться в меню бота Telegram.
    """
    commands = [
        BotCommand(command="start", description="запуск/перезапуск бота"),
        BotCommand(command="menu", description="главное функциональное меню"),
        BotCommand(command="help", description="справка по боту"),
    ]
    await bot.set_my_commands(commands)


# --- Основная функция запуска бота ---
async def main():
    """
    Основная асинхронная функция, которая запускает бота.
    Инициализирует Google Sheets, устанавливает команды, загружает клиентскую базу
    и запускает режим polling для получения обновлений от Telegram.
    Обрабатывает глобальные исключения и отправляет уведомление о выключении бота.
    """
    try:
        logger.info("включение бота")
        sheet_base = await get_sheet_base()  # Инициализация доступа к Google Sheets
        await set_commands()  # Установка команд в меню бота
        await clients_base.load_base(
            await sheet_base.get_clients(bot)
        )  # Загрузка клиентской базы в память
        await dp.start_polling(bot)  # Запуск polling-режима для получения обновлений
    except Exception as e:
        logger.exception(f"Ошибка в боте: {e}")  # Логирование критических ошибок
    finally:
        await bot.send_message(
            loggs_acc, "выключение бота"
        )  # Уведомление администратора о выключении бота


# --- Точка входа в программу ---
if __name__ == "__main__":
    # Запуск основной асинхронной функции.
    asyncio.run(main())
