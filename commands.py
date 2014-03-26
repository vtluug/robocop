### TODO
# - means infinite time

import logging
import time

import irc.bot
import irc.client

import config
import templates

robocop = None

### Templates
"""
Uses templates.py for the template manager and config.py for the template file.
Will sync the templates so the file reflects the server's copy
"""
def template(connection, source, args):
    subcom, sep, args = args.partition(' ')
    subcom = subcom.strip()
    args = args.strip()
    if subcom == "add" or subcom == "a" or subcom == "update" or subcom == "u":
        template, sep, text = args.partition(' ')
        if len(text.strip()) == 0 or len(template.strip()) == 0:
            connection.privmsg(config.opchannel, "Usage: .template add <%template> <text>")
            return False
        if template.strip()[0] != '%':
            connection.privmsg(config.opchannel, "Templates must begin with '%'")
            return False
        else:
            robocop.templates.add_template(template.strip(), text.strip())
            connection.privmsg(config.opchannel, "Template added.")
            return True
    elif subcom == "remove" or subcom == "rm":
        args = args.strip()
        if len(args) == 0 or args[0] != '%':
            connection.privmsg(config.opchannel, "Usage: .template rm <%template>")
            return False
        try:
            robocop.templates.del_template(args)
        except:
            connection.privmsg(config.opchannel, 'Could not find "%s"' % (args))
        else:
            connection.privmsg(config.opchannel, "Removed %s" % (args))
        return True
    elif subcom == "list" or subcom == "ls":
        templates = robocop.templates.list_templates()
        for item in templates:
            connection.privmsg(config.opchannel, ': '.join(item))
        return True
    else:
        connection.privmsg(config.opchannel, "Usage: [.template|.tl] <add|rm|ls> [%template] [text]")

### Warn a user via robocop
def warn(connection, source, args):
    nick, sep, reason = args.partition(' ')
    nick = nick.strip()
    reason = reason.strip()
    if nick == '' or reason == '':
        connection.privmsg(config.opchannel, "Usage: .warn <nick> [reason | %template]")
    else:
        if reason[0] == '%':
            try:
                reason = robocop.templates.get_template(reason)
            except:
                connection.privmsg(config.opchannel, "Error retrieving template %s" % (reason))
                return False
        connection.privmsg(config.modchannel, "%s: %s" % (nick, reason))
    return True

### Mute a user via Robocop, will unmute them after specified time.
def mute(connection, channel, args):
    logging.debug("Mute called")
    nick, sep, reason = args.partition(' ')
    delay, sep, reason = reason.partition(' ')
    nick = nick.strip()
    delay = delay.strip()
    reason = reason.strip()
    if nick == '' or reason == '' or delay == '':
        logging.debug("Mute passed invalid parameters")
        connection.privmsg(config.opchannel, "Usage: .mute <nick> <minutes> [reason | %template]")
    else:
        if delay != '-':
            try:
                delay = int(delay)
            except ValueError:
                logging.debug("mute delay was not a number")
                connection.privmsg(config.opchannel, "Usage: .mute <nick> <minutes> [reason | %template]")
                return False

        if reason[0] == '%':
            try:
                reason = robocop.templates.get_template(reason)
            except:
                connection.privmsg(config.opchannel, "Error retrieving template %s" % (reason))
                return False

        logging.info("Muting %s" % (nick))
        if delay == '-':
            connection.mode(config.modchannel, "+q %s" % (nick))
            connection.mode(config.modchannel, "-v %s" % (nick))
            connection.privmsg(config.modchannel, "%s: %s" % (nick, reason))
        else:
            connection.mode(config.modchannel, "+q %s" % (nick))
            connection.mode(config.modchannel, "-v %s" % (nick))
            connection.privmsg(config.modchannel, "%s: %s (%d minutes)" % (nick, reason, delay))
            if config.debug:
                robocop.ircobj.execute_delayed(delay, delay_unmute, arguments=(connection, nick,))
            else:
                robocop.ircobj.execute_delayed(60 * delay, delay_unmute, arguments=(connection, nick,))
    return True

def delay_unmute(connection, nick):
    logging.info("Unmuting %s" % (nick))
    connection.mode(config.modchannel, "-q %s" % (nick))

def unmute(connection, source, args):
    logging.debug("Unmute called")
    nick = args.strip()
    if nick == '':
        logging.debug("Unmute passed invalid parameters")
        connection.privmsg(config.opchannel, "Usage: .unmute <nick>")
    else:
        logging.info("Unmuting %s" % (nick))
        connection.mode(config.modchannel, "-q %s" % (nick))
    return True

### Ban a user (will not kick)
def ban(connection, source, args):
    logging.debug("Ban called")
    nick, sep, reason = args.partition(' ')
    delay, sep, reason = reason.partition(' ')
    nick = nick.strip()
    delay = delay.strip()
    reason = reason.strip()
    if nick == '' or reason == '' or delay == '':
        logging.debug("Ban passed invalid parameters")
        connection.privmsg(config.opchannel, "Usage: .ban <nick> <minutes> [reason | %template]")
    else:
        if delay != '-':
            try:
                delay = int(delay)
            except ValueError:
                logging.debug("Ban delay was not a number")
                connection.privmsg(config.opchannel, "Usage: .ban <nick> <minutes> [reason | %template]")
                return False

        if reason[0] == '%':
            try:
                reason = robocop.templates.get_template(reason)
            except:
                connection.privmsg(config.opchannel, "Error retrieving template %s" % (reason))
                return False
        logging.info("Banning %s" % (nick))
        if delay == '-':
            connection.privmsg(config.modchannel, "%s: %s" % (nick, reason))
            connection.mode(config.modchannel, "+b %s" % (nick))
        else:
            connection.privmsg(config.modchannel, "%s: %s (%d minutes)" % (nick, reason, delay))
            connection.mode(config.modchannel, "+b %s" % (nick))
            if config.debug:
                robocop.ircobj.execute_delayed(delay, delay_unban, arguments=(connection, nick,))
            else:
                robocop.ircobj.execute_delayed(60 * delay, delay_unban, arguments=(connection, nick,))
    return True

def delay_unban(connection, nick):
    logging.info("Unbanning %s" % (nick))
    connection.mode(config.modchannel, "-b %s" % (nick))
    connection.invite(nick, config.modchannel)

def unban(connection, source, args):
    logging.debug("Unban called")
    nick = args.strip()
    if nick == '':
        logging.debug("Unban passed invalid parameters")
        connection.privmsg(config.opchannel, "Usage: .unban <nick>")
    else:
        logging.info("Unmuting %s" % (nick))
        connection.mode(config.modchannel, "-b %s" % (nick))
        connection.invite(nick, config.modchannel)
    return True

### Kick a user
def kick(connection, source, args):
    logging.debug("Kick called")
    nick, sep, reason = args.partition(' ')
    nick = nick.strip()
    reason = reason.strip()
    if nick == '' or reason == '':
        logging.debug("Kick passed invalid parameters")
        connection.privmsg(config.opchannel, "Usage: .kick <nick> [reason | %template]")
    else:
        print(reason)
        if reason[0] == '%':
            try:
                reason = robocop.templates.get_template(reason)
            except:
                connection.privmsg(config.opchannel, "Error retrieving template %s" % (reason))
                return False
        logging.info("Kicking %s" % (nick))
        print(reason)
        connection.kick(config.modchannel, nick, comment=reason)
    return True

### Pm a user
def pm(connection, source, args):
    logging.debug("pm called")
    nick, sep, reason = args.partition(' ')
    nick = nick.strip()
    reason = reason.strip()
    if nick == '' or reason == '':
        logging.debug("pm passed invalid parameters")
        connection.privmsg(config.opchannel, "Usage: .pm <nick> [reason | %template]")
    else:
        print(reason)
        if reason[0] == '%':
            try:
                reason = robocop.templates.get_template(reason)
            except:
                connection.privmsg(config.opchannel, "Error retrieving template %s" % (reason))
                return False
        logging.info("PMing %s: %s" % (nick, reason))
        connection.privmsg(nick, reason)
    return True

def ack(connection, source, args):
    logging.debug("Ack called")
    nick = args.strip()
    if ' ' in nick:
        connection.privmsg(config.opchannel, "Usage: .ack <nick>")
        return False
    else:
        connection.privmsg(nick, "An op has seen and acknowledged your message.")
        return True

### BANHAMMER
def kickban(connection, source, args):
    logging.debug("Kickban called")
    nick, sep, reason = args.partition(' ')
    delay, sep, reason = reason.partition(' ')
    nick = nick.strip()
    delay = delay.strip()
    reason = reason.strip()
    if nick == '' or reason == '' or delay == '':
        logging.debug("Kickban passed invalid parameters")
        connection.privmsg(config.opchannel, "Usage: .kickban <nick> <minutes> [reason | %template]")
    else:
        if delay != '-':
            try:
                delay = int(delay)
            except ValueError:
                logging.debug("Kickban delay was not a number")
                connection.privmsg(config.opchannel, "Usage: .kickban <nick> <minutes> [reason | %template]")
                return False

        if reason[0] == '%':
            try:
                reason = robocop.templates.get_template(reason)
            except:
                connection.privmsg(config.opchannel, "Error retrieving template %s" % (reason))
                return False
        logging.info("Kickbanning %s" % (nick))
        if delay == '-':
            connection.kick(config.modchannel, nick, reason)
            connection.mode(config.modchannel, "+b %s" % (nick))
        else:
            connection.kick(config.modchannel, nick, "%s (%d minutes)" % (reason, delay))
            connection.mode(config.modchannel, "+b %s" % (nick))
            if config.debug:
                robocop.ircobj.execute_delayed(delay, delay_unban, arguments=(connection, nick,))
            else:
                robocop.ircobj.execute_delayed(60 * delay, delay_unban, arguments=(connection, nick,))
    return True

def privmsg(connection, event):
    connection.privmsg(config.opchannel, event.source.nick + ": " + event.arguments[0])

### Invite a user
def invite(connection, source, args):
    logging.debug("Invite called")
    nick, sep, reason = args.partition(' ')
    nick = nick.strip()
    if nick == '':
        logging.debug("Invite passed invalid parameters")
        connection.privmsg(config.opchannel, "Usage: .invite <nick>")
    else:
        logging.info("Inviting %s" % (nick))
        print(reason)
        connection.invite(nick, config.modchannel)
    return True

def commands(connection, source, args):
    commands = [k for k, v in opchannel]
    connection.privmsg(config.opchannel, ", ".join(commands))

def join(connection, source, args):
    connection.join(args)

def op(connection, source, args):
    connection.privmsg("ChanServ", "op %s" % (config.modchannel))

def identify(connection, source, args):
    connection.privmsg("NickServ", "identify %s %s" % (config.password, config.nickname))
    connection.privmsg(source, "Identified with NickServ")

def nick(connection, source, args):
    connection.nick(config.nickname)

def flood_control(connection, event):
    now = time.time()
    if robocop.rl_cooldown < now - 30:
        robocop.ratelimit.append((event.source.nick, now))

        while len(robocop.ratelimit) > 0 and robocop.ratelimit[0][1] < now - 14:
            robocop.ratelimit.pop(0)
        count = len([nick for nick in robocop.ratelimit if nick[0] == event.source.nick])
        if count >= 6:
            connection.privmsg(config.opchannel, "%s tripped flood guard." % (event.source.nick))
            robocop.rl_cooldown = now
            fakeevent = irc.client.Event("fake", config.nickname, config.opchannel, arguments=[".mute %s %d Automatic flood control" %(event.source.nick, 1)])
            logging.debug(fakeevent.arguments)
            logging.debug("Generated fake event")
            robocop.ophandler.handle(connection, fakeevent)
            logging.debug("Muted offender")
        elif len(robocop.ratelimit) > 10:
            connection.privmsg(config.opchannel, "General flood warning!")
            robocop.rl_cooldown = now

modchannel = [
    ('.ack'     , ack)
]
modchannel_default = flood_control
opchannel = [
    ('.warn'    , warn),
    ('.mute'    , mute),
    ('.unmute'  , unmute),
    ('.ban'     , ban),
    ('.unban'   , unban),
    ('.kick'    , kick),
    ('.unkick'  , invite),
    ('.invite'  , invite),
    ('.inv'     , invite),
    ('.kickban' , kickban),
    ('.template', template),
    ('.tl'      , template),
    ('.ack'     , ack),
    ('.commands', commands),
    ('.help'    , commands),
    ('.pm'      , pm),
]
opchannel_default = None

admin = [
    ('.join'    , join),
    ('.op'      , op),
    ('.ident'   , identify),
    ('.nick'    , nick),
]
admin_default = None
