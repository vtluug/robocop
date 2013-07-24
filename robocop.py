#! /usr/bin/env python3
"""
Robocop!
"""

import irc.bot

import config
import handler
import commands

class Robocop(irc.bot.SingleServerIRCBot):
    """ Robocop irc bot to aid in administration of a channel """
    def __init__(self):
        server = irc.bot.ServerSpec(config.server, port=config.port, password=config.password)
        irc.bot.SingleServerIRCBot.__init__(self, [server], config.nickname, "Robocop")
        self.modhandler = handler.Handler()
        for command in commands.modchannel:
            self.modhandler.register(command[0], command[1])
        self.ophandler = handler.Handler()
        for command in commands.opchannel:
            self.ophandler.register(command[0], command[1])
        self.privhandler = handler.Handler()

    def on_welcome(self, connection, event):
        connection.join(config.modchannel)
        connection.join(config.opchannel)

    def on_privmsg(self, connection, event):
        print(', '.join([event.type, event.source.nick, event.source.userhost, event.source.host, event.source.user, event.target]))
        commands.privhandler(connection, event)

    def on_pubmsg(self, connection, event):
        print(', '.join([event.type, event.source.nick, event.source.userhost, event.source.host, event.source.user, event.target]))

        if event.arguments[0][0] == '.':
            if event.target == config.modchannel:
                self.modhandler.handle(connection, event)
            elif event.target == config.opchannel:
                self.ophandler.handle(connection, event)

def main():
    try:
        robocop = Robocop()
    except Exception as e:
        print(e)
    else:
        robocop.start()

if __name__ == "__main__":
    main()

