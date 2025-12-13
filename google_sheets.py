from datetime import datetime

from google.oauth2.service_account import Credentials
from gspread_asyncio import AsyncioGspreadClientManager
from loguru import logger
from pytz import timezone

from paswords import loggs_acc

# Определение часового пояса Москвы для корректного отображения времени.
moscow_tz = timezone("Europe/Moscow")

# Глобальная переменная для хранения единственного экземпляра SheetBase (паттерн Singleton).
_sheet_instance = None


def get_creds():
    """
    Функция для получения учетных данных Google Service Account из JSON-файла.
    Определяет необходимые области доступа (scopes) для работы с Google Sheets и Drive.
    """
    return Credentials.from_service_account_file(
        "pidor-of-the-day-af3dd140b860.json",  # Имя файла ключа сервисного аккаунта
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",  # Доступ к Google Sheets
            "https://www.googleapis.com/auth/drive",  # Доступ к Google Drive (для открытия таблиц)
        ],
    )


# Менеджер для асинхронной работы с Google Sheets, использующий полученные учетные данные.
agcm = AsyncioGspreadClientManager(get_creds)


# --- Класс для взаимодействия с Google Sheets ---


class SheetBase:
    def __init__(
        self,
        worksheet_base_site,
        worksheet_base_bot,
        worksheet_base_other,
        worksheet_clients_base,
    ):
        """
        Конструктор класса SheetBase. Принимает объекты рабочих листов Google Sheets.
        """
        self.worksheet_base_site = (
            worksheet_base_site  # Лист для опросов по созданию сайтов
        )
        self.worksheet_base_bot = (
            worksheet_base_bot  # Лист для опросов по созданию ботов
        )
        self.worksheet_base_other = worksheet_base_other  # Лист для других опросов
        self.worksheet_clients_base = worksheet_clients_base  # Лист с базой клиентов

    @classmethod
    async def create(cls):
        """
        Асинхронный фабричный метод для создания экземпляра SheetBase.
        Авторизуется в Google API, открывает указанную таблицу и получает ссылки на нужные листы.
        """
        try:
            agc = await agcm.authorize()
            sh = await agc.open("breef_bot_base")  # Открытие Google таблицы по названию
            worksheet_base_site = await sh.worksheet("site")
            worksheet_base_bot = await sh.worksheet("bot")
            worksheet_base_other = await sh.worksheet("other")
            worksheet_clients_base = await sh.worksheet("clients_base")

            return cls(
                worksheet_base_site,
                worksheet_base_bot,
                worksheet_base_other,
                worksheet_clients_base,
            )
        except Exception as e:
            logger.exception("Исключение вызванное google_sheet/create", e)

    async def record_in_base(
        self, bot, message, section: str, answers: list
    ):  # функция поиска и записи в базу
        """
        Записывает ответы пользователя из опроса в соответствующий лист Google Sheets.
        Добавляет информацию о пользователе (ID, username, имя, фамилия) в начало списка ответов.
        Выбирает лист для записи в зависимости от `section` (категории опроса).
        """
        try:
            # Добавление данных пользователя в начало списка ответов
            answers[:0] = [
                message.chat.id,
                message.chat.username,
                message.chat.first_name,
                message.chat.last_name,
            ]
            # Выбор рабочего листа в зависимости от категории опроса
            if section == '🌐 Опрос "создание сайта"':
                second_column = await self.worksheet_base_site.col_values(1)
                worksheet_len = (
                    len(second_column) + 1
                )  # Находит первую пустую строку для записи
                await self.worksheet_base_site.update(
                    f"A{worksheet_len}:Y{worksheet_len}",
                    [answers],  # Обновляет диапазон ячеек
                )
            elif section == '🤖 Опрос "создание бота"':
                second_column = await self.worksheet_base_bot.col_values(1)
                worksheet_len = len(second_column) + 1
                await self.worksheet_base_bot.update(
                    f"A{worksheet_len}:X{worksheet_len}", [answers]
                )
            elif section == '🖼 Опрос "другое"':
                second_column = await self.worksheet_base_other.col_values(1)
                worksheet_len = len(second_column) + 1
                await self.worksheet_base_other.update(
                    f"A{worksheet_len}:R{worksheet_len}", [answers]
                )
        except Exception as e:
            logger.exception("Исключение вызванное google_sheet/record_in_base", e)
            await bot.send_message(
                loggs_acc, f"Исключение вызванное google_sheet/record_in_base: {e}"
            )

    async def chec_and_record_in_client_base(
        self, bot, message, reasons=None
    ):  # функция поиска и записи в базу
        """
        Проверяет, существует ли клиент в базе Google Sheets. Если нет, добавляет нового клиента.
        Записывает ID пользователя, username, имя, причину добавления и текущую дату/время.
        """
        try:
            second_column = await self.worksheet_clients_base.col_values(
                1
            )  # Получает все значения из первого столбца (ID клиентов)
            worksheet_len = (
                len(second_column) + 1
            )  # Находит первую пустую строку для записи
            if str(message.chat.id) in second_column:  # Если ID клиента уже есть в базе
                pass  # Ничего не делает
            else:  # Если клиента нет в базе, добавляет его
                await self.worksheet_clients_base.update(
                    f"A{worksheet_len}:E{worksheet_len}",
                    [
                        [
                            message.chat.id,
                            message.chat.username,
                            message.chat.first_name,
                            reasons,
                            str(datetime.now(moscow_tz).strftime("%d.%m.%y %H:%M")),
                        ]
                    ],
                )
        except Exception as e:
            logger.exception(
                "Исключение вызванное google_sheet/chec_and_record_in_client_base", e
            )
            await bot.send_message(
                loggs_acc,
                f"Исключение вызванное google_sheet/chec_and_record_in_client_base: {e}",
            )

    async def rasylka_v_bazu(self, bot, message):
        """
        Отправляет сообщение-рассылку всем клиентам, зарегистрированным в базе.
        Итерируется по списку ID клиентов и пытается отправить сообщение каждому.
        Логирует ошибки, если сообщение не удалось доставить (например, бот заблокирован).
        """
        mess = await bot.send_message(
            message.chat.id, "Загрузка..🚀"
        )  # Отправляет временное сообщение о загрузке
        ids = await self.worksheet_clients_base.col_values(
            1
        )  # Получает ID всех клиентов
        names = await self.worksheet_clients_base.col_values(
            2
        )  # Получает имена всех клиентов
        for i in range(
            1, len(ids)
        ):  # Пропускает заголовок, начинает со второго элемента
            try:
                await bot.copy_message(
                    ids[i], message.chat.id, message.message_id
                )  # Пересылает сообщение
            except Exception as e:
                logger.exception(f"Ошибка при отправке @{names[i]}")
                await bot.send_message(
                    loggs_acc, f"Босс, с @{names[i]} проблема: {e}"
                )  # Уведомляет администратора об ошибке
        await bot.delete_message(
            message.chat.id, mess.message_id
        )  # Удаляет временное сообщение
        await bot.send_message(
            message.chat.id, "Босс, рассылка выполнена ✅"
        )  # Сообщает об успешной рассылке

    async def get_clients(self, bot):
        """
        Получает список всех клиентов из Google Sheets.
        Возвращает список строк, каждая из которых представляет данные клиента.
        """
        try:
            rows = await self.worksheet_clients_base.get_values()
            return [
                row for row in rows[1:] if row
            ]  # Возвращает все строки, кроме заголовка
        except Exception as e:
            logger.exception("Ошибка в get_clients")
            await bot.send_message(loggs_acc, f"Исключение get_clients: {e}")
            return []


async def get_sheet_base():
    """
    Асинхронная функция для получения (или создания, если еще не создан)
    единственного экземпляра класса SheetBase (реализация паттерна Singleton).
    """
    try:
        global _sheet_instance
        if _sheet_instance is None:
            print("Создаю новый экземпляр SheetBase...")
            _sheet_instance = await SheetBase.create()
        return _sheet_instance
    except Exception as e:
        logger.exception(f"get_sheet_base: {e}")
