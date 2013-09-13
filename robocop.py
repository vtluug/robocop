#! /usr/bin/env python3
"""
Robocop!
"""

import logging

import irc.bot
import irc.client

import config
import handler
import commands
import templates

class Robocop(irc.bot.SingleServerIRCBot):
    """ Robocop irc bot to aid in administration of a channel """
    def __init__(self):
        logging.info("Connecting to server...")
        server = irc.bot.ServerSpec(config.server, port=config.port, password=config.password)
        irc.bot.SingleServerIRCBot.__init__(self, [server], config.nickname, "Robocop")

        logging.info("Registering commands..."),
        self.modhandler = handler.Handler()
        self.modhandler.register_default(commands.modchannel_default)
        for command in commands.modchannel:
            self.modhandler.register(command[0], command[1])

        logging.debug("50%% done...")

        self.ophandler = handler.Handler()
        self.ophandler.register_default(commands.opchannel_default)
        for command in commands.opchannel:
            self.ophandler.register(command[0], command[1])
        self.adminhandler = handler.Handler()
        self.adminhandler.register_default(commands.admin_default)
        for command in commands.admin:
            self.adminhandler.register(command[0], command[1])

        self.ratelimit = []
        self.rl_cooldown = 0

        logging.debug("Loading templates")
        self.templates = templates.TemplateDB()

        logging.info("Setup complete")

    def reload_commands(self):
        import imp
        imp.reload(commands)
        logging.info("Reloading commands")
        self.modhandler = handler.Handler()
        self.modhandler.register_default(commands.modchannel_default)
        for command in commands.modchannel:
            self.modhandler.register(command[0], command[1])
        self.ophandler = handler.Handler()
        self.ophandler.register_default(commands.opchannel_default)
        for command in commands.opchannel:
            self.ophandler.register(command[0], command[1])
        self.adminhandler = handler.Handler()
        self.adminhandler.register_default(commands.admin_default)
        for command in commands.admin:
            self.adminhandler.register(command[0], command[1])
        commands.robocop = self

    def on_welcome(self, connection, event):
        logging.debug("Connecting to channels")
        connection.privmsg("NickServ", "identify %s %s" % (config.password, config.nickname))
        logging.debug("Identifiying...")
        connection.privmsg("ChanServ", "invite %s" % (config.opchannel))
        connection.join(config.modchannel)
        connection.privmsg("ChanServ", "op %s" % (config.modchannel))
        logging.debug("Connected to channels")
        connection.join(config.opchannel)
        logging.debug("Identified and opped on mod channel")

    def on_privmsg(self, connection, event):
        logging.debug(', '.join([event.type, event.source.nick, event.source.userhost, event.source.host, event.source.user, event.target]))
        if event.source.nick in config.admins:
            logging.debug("Handling admin command")
            # This should be handled here
            if event.arguments[0][0:7] == ".reload":
                self.reload_commands()
            else:
                self.adminhandler.handle(connection, event)
        else:
            commands.privmsg(connection, event)

    def on_pubmsg(self, connection, event):
        logging.debug(', '.join([event.type, event.source.nick, event.source.userhost, event.source.host, event.source.user, event.target]))

#        now = time.time()
#        if self.rl_cooldown < now - 30:
#            self.ratelimit.append((event.source.nick, now))
#
#            while len(self.ratelimit) > 0 and self.ratelimit[0][1] < now - 10:
#                self.ratelimit.pop(0)
#            count = len([nick for nick in self.ratelimit if nick[0] == event.source.nick])
#            if count >= 4:
#                connection.privmsg(config.opchannel, "%s tripped flood guard." % (event.source.nick))
#                self.rl_cooldown = now
#                fakeevent = irc.client.Event("fake", config.nickname, config.opchannel, arguments=[".mute %s %d Automatic flood control" %(event.source.nick, 5)])
#                print(fakeevent.arguments)
#                logging.debug("Generated fake event")
#                self.ophandler.handle(connection, fakeevent)
#                logging.debug("Muted offender")
#            elif len(self.ratelimit) > 10:
#                connection.privmsg(config.opchannel, "General flood warning!")
#                self.rl_cooldown = now

        if event.target == config.modchannel:
            self.modhandler.handle(connection, event)
        elif event.target == config.opchannel:
            self.ophandler.handle(connection, event)


def main():
    logging.basicConfig(filename="robocop.log", level=logging.DEBUG)
    #logging.basicConfig(level=logging.DEBUG)
    global robocop
    try:
        robocop = Robocop()
    except Exception as e:
        print(e)
    else:
        commands.robocop = robocop
        robocop.start()

if __name__ == "__main__":
    main()

