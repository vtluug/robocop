import logging

class Handler(object):

    def __init__(self):
        self.registered = []
        self.default = None
        self._current = 100

    def register(self, command, function):
        self.registered.append((command, function))
        self._current += 100
        self.registered.sort()

    def register_default(self, command):
        self.default = command

    def handle(self, connection, event):
        command, sep, args = event.arguments[0].partition(' ')
        logging.debug("Looking for registred command: %s" % (command))
        if type(event.target) == "NickMask":
            source = event.source.nick
        else:
            source = event.target

        if self.default is not None:
            self.default(connection, event)

        for funct in self.registered:
            if funct[0] == command:
                funct[1](connection, source, args)
                return True
        return False
