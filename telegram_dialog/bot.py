import collections
import collections.abc

from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram import ReplyKeyboardMarkup
from telegram import ReplyMarkup
from telegram.ext import Updater

from .items import *


class DialogBot(object):

    def __init__(self, token, dialog):
        self.updater = Updater(token=token)
        handler = MessageHandler(Filters.text | Filters.command, self.handle_message)
        self.updater.dispatcher.add_handler(handler)
        self.handlers = collections.defaultdict(lambda: dialog())

    def start(self):
        self.updater.start_polling()

    def handle_message(self, bot, update):
        print("Received", update.message)
        chat_id = update.message.chat_id
        if update.message.text == "/start":
            del self.handlers[chat_id]
        handler = self.handlers[chat_id]
        try:
            try:
                answer = handler.send(update.message)
            except TypeError:
                answer = next(handler)
            print("Answer: %r" % answer)
        except StopIteration:
            del self.handlers[chat_id]
            return self.handle_message(bot, update)
        self._send_answer(bot, chat_id, answer)

    def _send_answer(self, bot, chat_id, answer):
        print("Sending answer %r to %s" % (answer, chat_id))
        if isinstance(answer, collections.abc.Iterable) and not isinstance(answer, str):
            answer = list(map(self._convert_answer_part, answer))
        else:
            answer = [self._convert_answer_part(answer)]
        current_message = None
        for part in answer:
            if isinstance(part, Message):
                if current_message is not None:
                    options = dict(current_message.options)
                    options.setdefault("disable_notification", True)
                    bot.sendMessage(chat_id=chat_id, text=current_message.text, **options)
                current_message = part
            if isinstance(part, ReplyMarkup):
                current_message.options["reply_markup"] = part
        if current_message is not None:
            bot.sendMessage(chat_id=chat_id, text=current_message.text, **current_message.options)

    def _convert_answer_part(self, answer_part):
        if isinstance(answer_part, str):
            return Message(answer_part)
        if isinstance(answer_part, collections.abc.Iterable):
            # a keyboard?
            answer_part = list(answer_part)
            if isinstance(answer_part[0], str):
                return ReplyKeyboardMarkup([answer_part], one_time_keyboard=True)
            elif isinstance(answer_part[0], collections.abc.Iterable):
                # a two-dimensional keyboard!
                if isinstance(answer_part[0][0], str):
                    return ReplyKeyboardMarkup(map(list, answer_part), one_time_keyboard=True)
        return answer_part
