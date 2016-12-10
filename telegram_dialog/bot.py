import collections
import collections.abc
import copy

from telegram.ext import Filters
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import InlineQueryHandler
from telegram.ext import MessageHandler
from telegram import ReplyKeyboardMarkup
from telegram import ReplyMarkup
from telegram.ext import Updater

from .items import *


class DialogBot(object):

    def __init__(self, token, generator, handlers=None):
        self.updater = Updater(token=token)
        message_handler = MessageHandler(Filters.text | Filters.command, self.handle_message)
        inline_query_handler = InlineQueryHandler(self.handle_inline_query)
        self.updater.dispatcher.add_handler(message_handler)
        self.updater.dispatcher.add_handler(inline_query_handler)
        self.generator = generator
        self.handlers = handlers or {}
        self.last_message_ids = {}

    def start(self):
        self.updater.start_polling()

    def stop(self):
        self.updater.stop()

    def handle_message(self, bot, update, **kwargs):
        print("Received", update.message)
        chat_id = update.message.chat_id
        if update.message.text == "/start":
            self.handlers.pop(chat_id, None)
        self.apply_handler(bot, chat_id, update.message)

    def handle_inline_query(self, bot, update, **kwargs):
        inline_query = update.inline_query
        print("Received inline query", inline_query)
        user_id = inline_query.from_user.id
        just_started, handler = self.get_handler(user_id)
        results = list(handler.inline_query(inline_query)) if hasattr(handler, "inline_query") else []
        if just_started:
            del self.handlers[user_id]
        return bot.answerInlineQuery(inline_query.id, results)

    def get_handler(self, chat_id, *args, **kwargs):
        if chat_id not in self.handlers:
            result = self.handlers[chat_id] = self.generator(*args, **kwargs)
            return True, result
        return False, self.handlers[chat_id]

    def apply_handler(self, bot, chat_id, message=None):
        just_started, handler = self.get_handler(chat_id, message)
        if just_started:
            answer = next(handler)
        else:
            try:
                answer = handler.send(message)
            except StopIteration:
                del self.handlers[chat_id]
                return self.apply_handler(bot, chat_id, message)
        self.send_answer(bot, chat_id, answer)

    def send_answer(self, bot, chat_id, answer):
        print("Sending answer %r to %s" % (answer, chat_id))
        if isinstance(answer, collections.abc.Iterable) and not isinstance(answer, str):
            # мы получили несколько объектов -- сперва каждый надо обработать
            answer = list(map(self._convert_answer_part, answer))
        else:
            # мы получили один объект -- сводим к более общей задаче
            answer = [self._convert_answer_part(answer)]
        # перед тем, как отправить очередное сообщение, идём вперёд в поисках
        # «довесков» -- клавиатуры там или в перспективе ещё чего-нибудь
        current_message = last_message = None
        for part in answer:
            if isinstance(part, Message):
                if current_message is not None:
                    # сообщение, которое мы встретили раньше, пора бы отправить.
                    # поскольку не все объекты исчерпаны, пусть это сообщение
                    # не вызывает звоночек (если не указано обратное)
                    current_message = copy.deepcopy(current_message)
                    current_message.options.setdefault("disable_notification", True)
                    self._send_or_edit(bot, chat_id, current_message)
                current_message = part
            if isinstance(part, ReplyMarkup):
                # ага, а вот и довесок! добавляем текущему сообщению.
                # нет сообщения -- ну извините, это ошибка.
                current_message.options["reply_markup"] = part
        # надо не забыть отправить последнее встреченное сообщение.
        if current_message is not None:
            self._send_or_edit(bot, chat_id, current_message)

    def _send_or_edit(self, bot, chat_id, message):
        if isinstance(message, EditLast):
            bot.editMessageText(text=message.text, chat_id=chat_id, message_id=self.last_message_ids[chat_id], **message.options)
        else:
            print("Sending message: %r" % message.text)
            self.last_message_ids[chat_id] = bot.sendMessage(chat_id=chat_id, text=message.text, **message.options)

    def _convert_answer_part(self, answer_part):
        if isinstance(answer_part, str):
            return Message(answer_part)
        if isinstance(answer_part, collections.abc.Iterable):
            # клавиатура?
            answer_part = list(answer_part)
            if isinstance(answer_part[0], str):
                # она! оформляем как горизонтальный ряд кнопок.
                # кстати, все наши клавиатуры одноразовые -- нам пока хватит.
                return ReplyKeyboardMarkup([answer_part], one_time_keyboard=True)
            elif isinstance(answer_part[0], collections.abc.Iterable):
                # двумерная клавиатура?
                answer_part = list(map(list, answer_part))
                if isinstance(answer_part[0][0], str):
                    # она!
                    return ReplyKeyboardMarkup(answer_part, one_time_keyboard=True)
        if isinstance(answer_part, Inline):
            return answer_part.convert()
        return answer_part
