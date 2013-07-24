class Handler(object):

    def __init__(self):
        self.registered = []
        self._current = 100

    def register(self, command, function):
        self.registered.append((command, function))
        self._current += 100
        self.registered.sort()

    def handle(self, connection, event):
        command, sep, args = event.arguments[0].partition(' ')
        for funct in self.registered:
            if funct[0] == command:
                funct[1](connection, event, args)
                return True
        return False
