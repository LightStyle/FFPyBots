from conf import *

for bot in irc:
    irc[bot]['main'].connect(server, port, irc[bot]['nickname'], irc[bot]['password'], irc[bot]['ident'])
    irc[bot]['main'].run()