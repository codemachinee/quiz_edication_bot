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
