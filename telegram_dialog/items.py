from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup


class Message(object):
    def __init__(self, text, **options):
        self.text = text
        self.options = options


class Markdown(Message):
    def __init__(self, text, **options):
        super(Markdown, self).__init__(text, parse_mode="Markdown", **options)

    def __repr__(self):
        options = dict(self.options)
        options.pop("parse_mode")
        options = (", " + repr(options)) if options else ""
        return "Markdown(%r%s)" % (self.text, options)


class HTML(Message):
    def __init__(self, text, **options):
        super(HTML, self).__init__(text, parse_mode="HTML", **options)

    def __repr__(self):
        options = dict(self.options)
        options.pop("parse_mode")
        options = (", " + repr(options)) if options else ""
        return "HTML(%r%s)" % (self.text, options)


class EditLast(Message):
    pass


class Button(object):
    def __init__(self, text, **kwargs):
        self.text = text
        self.options = kwargs

    def convert(self):
        return InlineKeyboardButton(text=self.text, **self.options)


class Inline(object):
    def __init__(self, keyboard):
        self.keyboard = keyboard

    def convert(self):
        print(self.keyboard)
        keyboard = [
            [
                (button if isinstance(button, Button) else Button(button)).convert()
                for button in row
            ]
            for row in self.keyboard
        ]
        return InlineKeyboardMarkup(keyboard)


class Keyboard(object):
    def __init__(self, markup, one_time_keyboard=True, resize_keyboard=False):
        self.markup = markup
        self.one_time_keyboard = one_time_keyboard
        self.resize_keyboard = resize_keyboard
