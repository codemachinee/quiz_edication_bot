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
    
    text_remaining = text
    
    while text_remaining:
        # Start with open tags
        chunk = "".join(f"<{tag}>" for tag in open_tags)
        
        # Determine the effective max length for this chunk
        effective_max_len = MAX_MESSAGE_LENGTH - len(chunk) - (len(open_tags) * (len(max(open_tags, key=len)) + 3) if open_tags else 0)


        # Find a safe split point
        if len(text_remaining) <= effective_max_len:
            split_pos = len(text_remaining)
        else:
            split_pos = text_remaining.rfind('\n', 0, effective_max_len)
            if split_pos == -1:
                split_pos = text_remaining.rfind(' ', 0, effective_max_len)
            if split_pos == -1 or split_pos < effective_max_len / 2:
                split_pos = effective_max_len

        # Add the text to the chunk
        chunk_text = text_remaining[:split_pos]
        chunk += chunk_text
        text_remaining = text_remaining[split_pos:].lstrip()

        # Find all tags in the chunk text to update the open_tags list
        tags = re.finditer(r"(</?([a-zA-Z1-9_]+)>)", chunk_text)
        for tag_match in tags:
            full_tag, tag_name = tag_match.groups()
            if full_tag.startswith("</"):
                if tag_name in open_tags:
                    # Pop from the stack
                    last_open_tag = open_tags.pop()
                    if last_open_tag != tag_name:
                        # This indicates malformed HTML, but we'll try to recover
                        if tag_name in open_tags:
                            open_tags.remove(tag_name)

            else:
                open_tags.append(tag_name)
        
        # Close any remaining open tags
        chunk += "".join(f"</{tag}>" for tag in reversed(open_tags))
        
        chunks.append(chunk)

    for chunk in chunks:
        await bot.send_message(chat_id, chunk, parse_mode=parse_mode)
        await asyncio.sleep(0.5)
