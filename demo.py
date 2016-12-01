# -*- coding: utf-8 -*-
import logging
import sys

from telegram_dialog import *


def basic_dialog():
    answer = yield "Hi there, babe! What's your name?"
    answer = yield [
        HTML("Nice to meet you, <b>%s</b>!" % answer.text),
        "Do you like Python?",
        ["Hell yes!", "Fuck no!"]
    ]
    while answer.text not in ["Hell yes!", "Fuck no!"]:
        answer = yield "What?"
    if "yes" in answer.text:
        yield "Me too!"
    else:
        yield "Fuck why?"

    while True:
        yield "Whatever."


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dialog_bot = DialogBot(sys.argv[1], basic_dialog)
    dialog_bot.start()
