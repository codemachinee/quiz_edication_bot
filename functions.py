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
    Разбивает длинное сообщение на части, корректно обрабатывая HTML-теги.
    """
    MAX_MESSAGE_LENGTH = 4096
    if len(text) <= MAX_MESSAGE_LENGTH:
        await bot.send_message(chat_id, text, parse_mode=parse_mode)
        return

    import re
    chunks = []
    open_tags = []
    
    while text:
        # Добавляем открытые теги в начало
        current_chunk = "".join([f"<{tag}>" for tag in open_tags])
        
        # Определяем оставшееся место в чанке
        remaining_len = MAX_MESSAGE_LENGTH - len(current_chunk)
        
        # Ищем позицию для обрезки
        if len(text) <= remaining_len:
            split_pos = len(text)
        else:
            # Пытаемся обрезать по последнему переносу строки
            split_pos = text.rfind('\n', 0, remaining_len)
            if split_pos == -1:
                # Если переносов нет, ищем последний пробел
                split_pos = text.rfind(' ', 0, remaining_len)
            if split_pos == -1 or split_pos < remaining_len / 2:
                # Если не нашли подходящего места, режем по длине
                split_pos = remaining_len

        # Добавляем текст в чанк
        current_chunk += text[:split_pos]
        text = text[split_pos:].lstrip()

        # Анализируем теги в добавленном тексте
        opened_in_chunk = re.findall(r"<([a-zA-Z1-9_]+)>", current_chunk)
        closed_in_chunk = re.findall(r"</([a-zA-Z1-9_]+)>", current_chunk)
        
        # Обновляем стек открытых тегов
        for tag in opened_in_chunk:
            open_tags.append(tag)
        for tag in closed_in_chunk:
            if tag in open_tags:
                # Удаляем последнее вхождение тега
                for i in range(len(open_tags) - 1, -1, -1):
                    if open_tags[i] == tag:
                        open_tags.pop(i)
                        break

        # Закрываем оставшиеся открытые теги
        current_chunk += "".join([f"</{tag}>" for tag in reversed(open_tags)])
        
        chunks.append(current_chunk)

    for chunk in chunks:
        await bot.send_message(chat_id, chunk, parse_mode=parse_mode)
        await asyncio.sleep(0.5)
