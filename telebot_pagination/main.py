from collections.abc import Callable
from typing import Any
import telebot

class Chooser:
    """
    Class for creating paginated buttons for telegram bot
    """
    def __init__(self,
                 bot: telebot.TeleBot,
                 prev_button_text: str = "⬅️",
                 next_button_text: str = "➡️",
                 multi_prev_button_text: str = None,
                 multi_next_button_text: str = None,
                 cancel_button_text: str = "❌",
                 prev_button_callback_text: str = "prev",
                 next_button_callback_text: str = "next",
                 multi_skip_pages: int = 5,
                 cancel_button_callback_text: str = "cancel",
                 choose_button_prefix: str = "choose",
                 row_width: int = 3,
                 page_size: int = 6,
                 del_message_after: bool = True,
                 choose_page_button: bool = True,
                 choose_page_message_text: str = "Choose page",
                 choose_page_callback_text: str = "page",
                 choose_page_error_text: str = "Invalid page number",
                 ):
        """
        Initing the Chooser
        :param bot: Bot instance
        :type bot: telebot.TeleBot
        :param prev_button_text: Previous button text
        :type prev_button_text: string
        :param next_button_text: Next button text
        :type next_button_text: string
        :param cancel_button_text: Cancel button text
        :type cancel_button_text: string
        :param prev_button_callback_text: Previous button callback text
        :type prev_button_callback_text: string
        :param next_button_callback_text: Next button callback text
        :type next_button_callback_text: string
        :param cancel_button_callback_text: Cancel button callback text
        :type cancel_button_callback_text: string
        :param row_width: Number of buttons in a row
        :type row_width: int
        :param page_size: Number of items per page
        :type page_size: int
        :param del_message_after: whether to delete the message after сhoise if no only inline keyboard has been deleted
        :type del_message_after: bool
        :return: None
        """
        self.prev_button_text = prev_button_text
        self.next_button_text = next_button_text
        self.bot = bot
        self.row_width = row_width
        self.page_size = page_size
        self.cancel_button_text = cancel_button_text
        self.prev_button_callback_text = prev_button_callback_text
        self.next_button_callback_text = next_button_callback_text
        self.cancel_button_callback_text = cancel_button_callback_text
        self.choose_button_prefix = choose_button_prefix
        self.del_message_after = del_message_after
        self.multi_prev_button_text = multi_prev_button_text
        self.multi_next_button_text = multi_next_button_text
        self.multi_skip_pages = multi_skip_pages
        self.choose_page_button = choose_page_button
        self.choose_page_message_text = choose_page_message_text
        self.choose_page_callback_text = choose_page_callback_text
        self.choose_page_error_text = choose_page_error_text
        self.active_page_chooser = {}
        self.chooses = {}

        @self.bot.callback_query_handler(func=lambda call: self.choose_button_prefix in call.data)
        def choose_handler(call):
            if call.message.message_id not in self.chooses:
                return
            ans = call.data.replace(self.choose_button_prefix+"_", "")
            data = self.chooses[call.message.message_id]
            self.bot.clear_step_handler(data['message'])
            callback_func = data['handler']
            if self.del_message_after:
                bot.delete_message(call.message.chat.id, call.message.message_id)

            else:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)

            callback_func(call, ans)

        @self.bot.callback_query_handler(func=lambda call: self.cancel_button_callback_text in call.data)
        def cancel(call):
            if call.message.message_id not in self.chooses:
                return
            data = self.chooses[call.message.message_id]
            self.bot.clear_step_handler(data['message'])
            callback_func = data['cancel_handler']
            if self.del_message_after:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            else:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id
                                              )
            if callback_func is not None:
                callback_func(call)

        @self.bot.callback_query_handler(func=lambda call: self.prev_button_callback_text in call.data)
        def prev(call):
            if call.message.message_id not in self.chooses:
                return
            index = int(call.data.replace(self.prev_button_callback_text+"_", ""))
            data = self.chooses[call.message.message_id]
            self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=self.get_keyboard(index, data['data'], data['page_size']))

        @self.bot.callback_query_handler(func=lambda call: self.next_button_callback_text in call.data)
        def next(call):
            if call.message.message_id not in self.chooses:
                return
            index = int(call.data.replace(self.next_button_callback_text + "_", ""))
            data = self.chooses[call.message.message_id]
            self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                               reply_markup=self.get_keyboard(index, data['data'], data['page_size']))

        @self.bot.callback_query_handler(func=lambda call: self.choose_page_callback_text in call.data)
        def choose_page_call(call):
            if call.message.message_id not in self.chooses:
                return
            message_id = call.message.message_id
            self.active_page_chooser[call.message.chat.id] = message_id
            self.bot.answer_callback_query(call.id, text=self.choose_page_message_text)
            bot.register_next_step_handler(call.message, choose_page)

        def choose_page(message):
            try:
                int(message.text)

            except ValueError:
                bot.send_message(message.chat.id, self.choose_page_error_text)
                return

            message_id = self.active_page_chooser[message.chat.id]
            data = self.chooses[message_id]['data']

            if int(message.text) < 1 or int(message.text) > len(data) // self.chooses[message_id]['page_size'] + 1:
                bot.send_message(message.chat.id, self.choose_page_error_text)
                return
            page_size = self.chooses[message_id]['page_size']
            print(page_size)
            try:
                self.bot.edit_message_reply_markup(message.chat.id, message_id,
                                                   reply_markup=self.get_keyboard(current_index=int(message.text)*self.chooses[message_id]['page_size']-1,
                                                                                  data=data,
                                                                                  page_size=page_size))

            except telebot.apihelper.ApiTelegramException:
                return

    def get_keyboard(self,
                     current_index: int,
                     data: list[str],
                     page_size: int,
                     ):
        print(page_size)
        print(current_index, current_index//page_size)
        new_data = data[current_index:current_index + page_size]
        parsed_data = []
        for choose in enumerate(new_data):
            print(choose)
            print(choose[0] // page_size)
            if len(parsed_data) <= choose[0] // page_size:
                parsed_data.append([])

            parsed_data[choose[0] // page_size].append(telebot.types.InlineKeyboardButton(
                text=choose[1],
                callback_data=self.choose_button_prefix + "_" + choose[1]
            ))

        keyboard = telebot.types.InlineKeyboardMarkup()
        for row in parsed_data:
            keyboard.row(*row)

        row = []
        if self.multi_prev_button_text is not None and current_index-page_size*self.multi_skip_pages >= 0:
            row.append(telebot.types.InlineKeyboardButton(text=self.multi_prev_button_text,
                                                          callback_data=self.prev_button_callback_text+
                                                                        "_"+
                                                                        str(
                                                                            current_index-
                                                                            self.multi_skip_pages*page_size)))
        if current_index-page_size >= 0:
            row.append(telebot.types.InlineKeyboardButton(text=self.prev_button_text,
                                                          callback_data=self.prev_button_callback_text+
                                                                        "_"+
                                                                        str(current_index-page_size)))
        row.append(telebot.types.InlineKeyboardButton(
            text=self.cancel_button_text,
            callback_data=self.cancel_button_callback_text))

        if len(data) > current_index + page_size:
            row.append(telebot.types.InlineKeyboardButton(text=self.next_button_text,
                                                          callback_data=self.next_button_callback_text+
                                                                        "_"+
                                                                        str(current_index+page_size)))
        if self.multi_next_button_text is not None and len(data) > current_index + page_size*self.multi_skip_pages:
            row.append(telebot.types.InlineKeyboardButton(text=self.multi_next_button_text,
                                                          callback_data=self.next_button_callback_text+
                                                                        "_"+
                                                                        str(
                                                                            current_index+
                                                                            self.multi_skip_pages*page_size)))
        keyboard.row(*row)
        keyboard.add(telebot.types.InlineKeyboardButton(text=str(current_index//page_size+1), callback_data=self.choose_page_callback_text))

        return keyboard

    def create_choose(self,
                      message: telebot.types.Message,
                      handler: Callable[[telebot.types.CallbackQuery, str], Any],
                      data: list[str],
                      cancel_handler: Callable[[telebot.types.CallbackQuery], Any] = None,
                      page_size: int = None,
                      del_message_after: bool = None,
                      ):
        """
        Create a paginated choose for telegram bot
        :param message: Message object
        :type message: telebot.types.Message
        :param handler: Handler for choosing item
        :type handler: Callable
        :param data: Data for choosing
        :type data: list[str]
        :param cancel_handler: Handler for canceling choose
        :type cancel_handler: Callable
        :param page_size: Number of items per page
        :type page_size: int
        :param del_message_after: Whether to delete the message after сhoise if no only inline keyboard has been deleted
        :type del_message_after: bool
        :return: None
        """
        if del_message_after is None:
            del_message_after = self.del_message_after

        if page_size is None:
            page_size = self.page_size

        current_index = 0
        keyboard = self.get_keyboard(current_index, data, page_size)
        self.bot.edit_message_reply_markup(message.chat.id, message.message_id, reply_markup=keyboard)

        self.chooses[message.message_id] = {'data': data,
                                            'handler': handler,
                                            'cancel_handler': cancel_handler,
                                            'page_size': page_size,
                                            'del_message_after': del_message_after,
                                            'message': message
                                            }
