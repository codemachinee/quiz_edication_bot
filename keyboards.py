import asyncio
from typing import Optional

from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

from paswords import loggs_acc


class Buttons:  # класс для создания клавиатур различных категорий товаров
    def __init__(
        self,
        bot,
        message: types.Message,
        keys_dict: dict,
        back_button: Optional[str] = None,
        question: Optional[str] = None,
    ):
        self.bot = bot
        self.message = message
        self.back_button = back_button
        self.question = question
        self.keys_dict = keys_dict

    async def menu_buttons(self):
        try:
            keys = {}
            keyboard_list = []
            keys_list = list(self.keys_dict)
            for i in keys_list:
                index = keys_list.index(i)
                button = types.InlineKeyboardButton(
                    text=i, callback_data=f"{i}"
                )
                keys[f"but{index}"] = button
                keyboard_list.append([button])
            if self.back_button is not None:
                back_button = types.InlineKeyboardButton(
                    text="⬅️ Назад", callback_data=self.back_button
                )
                keyboard_list.append([back_button])
            kb2 = types.InlineKeyboardMarkup(
                inline_keyboard=keyboard_list, resize_keyboard=True
            )
            await asyncio.sleep(0.3)
            await self.bot.edit_message_text(
                text=self.question,
                chat_id=self.message.chat.id,
                message_id=self.message.message_id,
                parse_mode="html", reply_markup=kb2
            )
        except TelegramBadRequest as e:
            if "message can't be edited" in str(e):
                await self.bot.send_message(
                    chat_id=self.message.chat.id,
                    text=self.question,
                    message_thread_id=self.message.message_thread_id,
                    parse_mode="html",
                    reply_markup=kb2,
                )
        except Exception as e:
            logger.exception("Ошибка в keyboards/menu_buttons", e)
            await self.bot.send_message(
                loggs_acc, f"Ошибка в keyboards/menu_buttons: {e}"
            )
    async def test_buttons(self, type: str='single', bot_message=None):
        try:
            if bot_message is None:
                bot_message = self.message.message_id
            else:
                bot_message = bot_message.message_id
            if type in ["single", 'tf']:
                keys = {}
                keyboard_list = []
                keys_list = list(self.keys_dict)
                for i in keys_list:
                    index = keys_list.index(i)
                    button = types.InlineKeyboardButton(
                        text=i, callback_data=f"{self.keys_dict[i]}"
                    )
                    keys[f"but{index}"] = button
                    keyboard_list.append([button])
                if self.back_button is not None:
                    back_button = types.InlineKeyboardButton(
                        text="⬅️ Назад", callback_data=self.back_button
                    )
                    keyboard_list.append([back_button])
                kb2 = types.InlineKeyboardMarkup(
                    inline_keyboard=keyboard_list, resize_keyboard=True
                )
                await asyncio.sleep(0.3)
                await self.bot.edit_message_text(
                    text=self.question,
                    chat_id=self.message.chat.id,
                    message_id=self.message.message_id,
                    parse_mode="html", reply_markup=kb2
                )
            elif type == "multiple":
                keys = {}
                keyboard_list = []
                keys_list = list(self.keys_dict)
                answers = 0
                for i in keys_list:
                    index = keys_list.index(i)
                    if '✅' in i:
                        button = types.InlineKeyboardButton(
                            text=i, callback_data=f"multi_off_{i}"
                        )
                        answers += 1
                    else:
                        button = types.InlineKeyboardButton(
                            text=i, callback_data=f"multi_on_{i}"
                        )
                    keys[f"but{index}"] = button
                    keyboard_list.append([button])
                if answers > 0:
                    answer_button = types.InlineKeyboardButton( text="✅ Отправить ответ", callback_data='multi_answer')
                    keyboard_list.append([answer_button])
                if self.back_button is not None:
                    back_button = types.InlineKeyboardButton(
                        text="⬅️ Назад", callback_data=self.back_button
                    )
                    keyboard_list.append([back_button])
                kb2 = types.InlineKeyboardMarkup(
                    inline_keyboard=keyboard_list, resize_keyboard=True
                )
                await self.bot.edit_message_text(
                    text=self.question,
                    chat_id=self.message.chat.id,
                    message_id=self.message.message_id,
                    parse_mode="html"
                )
                await asyncio.sleep(0.1)
                await self.bot.edit_message_reply_markup(
                    chat_id=self.message.chat.id,
                    message_id=self.message.message_id,
                    reply_markup=kb2,
                )
            if type == 'matching':
                keyboard_list = []
                if self.back_button is not None:
                    back_button = types.InlineKeyboardButton(
                        text="⬅️ Назад", callback_data=self.back_button
                    )
                    keyboard_list.append([back_button])
                kb2 = types.InlineKeyboardMarkup(
                    inline_keyboard=keyboard_list, resize_keyboard=True
                )
                message = await self.bot.edit_message_text(
                    text=self.question,
                    chat_id=self.message.chat.id,
                    message_id=bot_message,
                    parse_mode="html", reply_markup=kb2
                )
                return message
        except TelegramBadRequest as e:
            if "message can't be edited" in str(e):
                await self.bot.send_message(
                    chat_id=self.message.chat.id,
                    text=self.question,
                    message_thread_id=self.message.message_thread_id,
                    parse_mode="html",
                    reply_markup=kb2,
                )
        except Exception as e:
            logger.exception("Ошибка в keyboards/menu_buttons", e)
            await self.bot.send_message(
                loggs_acc, f"Ошибка в keyboards/menu_buttons: {e}"
            )

    async def breef_buttons(
        self,
        bot_message_id,
        idx=1,
        answer=None,
        number_of_question=1,
        quantity_of_questions=1,
    ):
        # idx = 1 - со 2 по предпоследний вопросы при последовательном ответе на вопросы
        # idx = 2 - последний вопрос
        # idx = 0 - 1 вопрос
        if answer is None:
            question_text = self.question
        else:
            question_text = f"{self.question}\n\nВаш ответ:{answer}"
        try:
            if idx == 2:
                kb_breef = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="✅ Отправить ответы",
                                callback_data="✅ Отправить ответы",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="❌ Отмена", callback_data="Основное меню"
                            )
                        ],
                    ]
                )
                message = await self.bot.edit_message_text(
                    text=f"{question_text}",
                    chat_id=self.message.chat.id,
                    message_id=bot_message_id,
                    reply_markup=kb_breef,
                    parse_mode="html",
                )
                if answer is None:
                    await self.bot.delete_message(
                        chat_id=self.message.chat.id, message_id=self.message.message_id
                    )
                return message

            else:
                if idx == 1:
                    kb_breef = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text="⬅️ Предыдущий вопрос", callback_data="назад"
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    text="❌ Отмена", callback_data="Основное меню"
                                )
                            ],
                        ]
                    )
                    if answer is None:
                        await self.bot.delete_message(
                            chat_id=self.message.chat.id,
                            message_id=self.message.message_id,
                        )

                else:
                    kb_breef = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text="❌ Отмена", callback_data="Основное меню"
                                )
                            ]
                        ]
                    )
                message = await self.bot.edit_message_text(
                    text=f"<b>Вопрос {number_of_question} из {quantity_of_questions}</b>\n\n{question_text}",
                    chat_id=self.message.chat.id,
                    message_id=bot_message_id,
                    reply_markup=kb_breef,
                    parse_mode="html",
                )

                return message
        except TelegramBadRequest as e:
            logger.info("Ошибка в keyboards/breef_buttons", e)
        except Exception as e:
            logger.exception("Ошибка в keyboards/breef_buttons", e)
            await self.bot.send_message(
                loggs_acc, f"Ошибка в keyboards/breef_buttons: {e}"
            )

    async def rasylka_buttons(self):
        try:
            kb_rasylka = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="💿 Общая база клиентов",
                            callback_data="Общая база клиентов",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="❌ Отмена", callback_data="Основное меню"
                        )
                    ],
                ]
            )
            await self.bot.send_message(
                text="Выберите базу для отправки рассылки:",
                chat_id=self.message.chat.id,
                reply_markup=kb_rasylka,
            )
        except Exception as e:
            logger.exception("Ошибка в keyboards/rasylka_buttons", e)
            await self.bot.send_message(
                loggs_acc, f"Ошибка в keyboards/rasylka_buttons: {e}"
            )
