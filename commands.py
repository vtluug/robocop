import config

def privhandler(connection, event):
    print("Sending to %s, %s" % (event.source.nick, event.arguments[0]))
    connection.privmsg(event.source.nick, event.arguments[0])

def repeat(connection, event, args):
    connection.privmsg(event.target, args)

def warn(connection, event, args):
    nick, sep, warning = args.partition(' ')
    nick = nick.strip()
    warning = warning.strip()
    if nick == '' or warning == '':
        connection.privmsg(config.opchannel, "Usage: .warn <nick> [reason | %template]")
    else:
        if warning[0] == '%':
            warning = get_template(warning)
        connection.privmsg(config.modchannel, "%s: %s" % (event.source.nick, warning))
    return True

def mute(connection, event, args):
    nick, sep, reason = args.partition(' ')
    nick = nick.strip()
    reason = reason.strip()
    if nick == '' or warning == '':
        connection.privmsg(config.opchannel, "Usage: .mute <nick> [reason | %template]")
    else:
        if reason[0] == '%':
            warning = get_template(reason)
        connection.privmsg("ChanServ", 
        connection.privmsg(config.modchannel, "%s: %s" % (event.source.nick, warning))
    return True



modchannel = [
    ('.r', repeat),
]
opchannel = [
    ('.warn', warn),
]
