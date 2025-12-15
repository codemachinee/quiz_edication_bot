import asyncio
from datetime import datetime

from loguru import logger

# --- Класс для управления клиентской базой в оперативной памяти ---


class Clients:
    def __init__(self):
        """
        Инициализирует пустой словарь для хранения данных клиентов.
        """
        self.dict = {}

    async def set_clients(self, data: dict):
        """
        Добавляет данные нового клиента в словарь `self.dict`.
        Обрабатывает возможные исключения при попытке записи.
        """
        try:
            self.dict[f"{data['id']}"] = {
                "username": data["username"],
                "name": data["name"],
                "reasons": data["reasons"],
                "date": data["date"],
            }
        except Exception as e:
            logger.exception("Исключение вызванное functions/set_clients", e)

    async def update_clients(self, id: str, key: str, value: str):
        """
        Обновляет определенное поле (по `key`) для клиента с заданным `id`.
        """
        try:
            self.dict[id][key] = value
        except Exception as e:
            logger.exception("Исключение вызванное functions/update_clients", e)

    async def get_clients(self) -> dict:
        """
        Возвращает полный словарь всех клиентов, хранящихся в памяти.
        """
        return self.dict

    async def load_base(self, clients_list: list):
        """
        Загружает список клиентов (например, полученный из Google Sheets) в оперативную память.
        Итерируется по списку и использует `set_clients` для добавления каждого клиента.
        """
        try:
            for i in clients_list:
                data = {
                    "id": i[0],
                    "username": i[1],
                    "name": i[2],
                    "reasons": i[3],
                    "date": i[4],
                }
                await self.set_clients(data)
        except Exception as e:
            logger.exception("Исключение вызванное functions/load_base", e)


# Создание единственного экземпляра класса Clients для использования в других модулях.
clients_base = Clients()


# --- Вспомогательная функция для работы с датами ---


async def is_today(date_str: str) -> bool:
    """
    Проверяет, относится ли переданная строка даты к сегодняшнему дню.
    Возвращает `True`, если дата совпадает с текущей, иначе `False`.
    """
    try:
        input_date = datetime.strptime(date_str, "%d.%m.%y %H:%M")
        now = datetime.now()
        return input_date.date() == now.date()
    except ValueError:
        # В случае ошибки парсинга даты, считается, что дата не сегодняшняя.
        return False


async def send_long_message(bot, chat_id, text, parse_mode="html"):
    """
    Разбивает длинное сообщение на части по 4096 символов и отправляет их.
    """
    MAX_MESSAGE_LENGTH = 4096
    if len(text) <= MAX_MESSAGE_LENGTH:
        await bot.send_message(chat_id, text, parse_mode=parse_mode)
    else:
        # Простая разбивка, можно улучшить, чтобы не обрезать слова посередине
        chunks = []
        while text:
            if len(text) > MAX_MESSAGE_LENGTH:
                chunk = text[:MAX_MESSAGE_LENGTH]
                last_newline_index = chunk.rfind('\n') # Попробуем обрезать по последнему переводу строки
                if last_newline_index != -1 and last_newline_index > MAX_MESSAGE_LENGTH - 500: # Если перевод строки достаточно близко к концу чанка
                    chunk = text[:last_newline_index]
                    text = text[last_newline_index:].lstrip('\n') # Удаляем лишние переводы строки в начале следующего чанка
                else:
                    chunk = text[:MAX_MESSAGE_LENGTH]
                    text = text[MAX_MESSAGE_LENGTH:]
            else:
                chunk = text
                text = ""
            chunks.append(chunk)

        for i, chunk in enumerate(chunks):
            await bot.send_message(chat_id, chunk, parse_mode=parse_mode)
            await asyncio.sleep(0.5)