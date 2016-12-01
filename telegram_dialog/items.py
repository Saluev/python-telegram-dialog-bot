class Message(object):
    def __init__(self, text, **options):
        self.text = text
        self.options = options


class Markdown(Message):
    def __init__(self, text, **options):
        super(Markup, self).__init__(text, parse_mode="Markdown", **options)

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
