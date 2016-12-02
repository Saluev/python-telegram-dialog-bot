import collections
import collections.abc

from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram import ReplyKeyboardMarkup
from telegram import ReplyMarkup
from telegram.ext import Updater

from .items import *


class DialogBot(object):

    def __init__(self, token, generator):
        self.updater = Updater(token=token)
        handler = MessageHandler(Filters.text | Filters.command, self.handle_message)
        self.updater.dispatcher.add_handler(handler)
        self.handlers = collections.defaultdict(generator)

    def start(self):
        self.updater.start_polling()

    def handle_message(self, bot, update):
        print("Received", update.message)
        chat_id = update.message.chat_id
        if update.message.text == "/start":
            self.handlers.pop(chat_id, None)
        if chat_id not in self.handlers:
            answer = next(self.handlers[chat_id])
        else:
            try:
                answer = self.handlers[chat_id].send(update.message)
            except StopIteration:
                del self.handlers[chat_id]
                return self.handle_message(bot, update)
        self._send_answer(bot, chat_id, answer)

    def _send_answer(self, bot, chat_id, answer):
        print("Sending answer %r to %s" % (answer, chat_id))
        if isinstance(answer, collections.abc.Iterable) and not isinstance(answer, str):
            # мы получили несколько объектов -- сперва каждый надо обработать
            answer = list(map(self._convert_answer_part, answer))
        else:
            # мы получили один объект -- сводим к более общей задаче
            answer = [self._convert_answer_part(answer)]
        # перед тем, как отправить очередное сообщение, идём вперёд в поисках
        # «довесков» -- клавиатуры там или в перспективе ещё чего-нибудь
        current_message = None
        for part in answer:
            if isinstance(part, Message):
                if current_message is not None:
                    # сообщение, которое мы встретили раньше, пора бы отправить.
                    options = dict(current_message.options)
                    # поскольку не все объекты исчерпаны, пусть это сообщение
                    # не вызывает звоночек (если не указано обратное)
                    options.setdefault("disable_notification", True)
                    bot.sendMessage(chat_id=chat_id, text=current_message.text, **options)
                current_message = part
            if isinstance(part, ReplyMarkup):
                # ага, а вот и довесок! добавляем текущему сообщению.
                # нет сообщения -- ну извините, это ошибка.
                current_message.options["reply_markup"] = part
        # надо не забыть отправить последнее встреченное сообщение.
        if current_message is not None:
            bot.sendMessage(chat_id=chat_id, text=current_message.text, **current_message.options)

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
        return answer_part
