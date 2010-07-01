from rss import *
from trivia import *
import Queue

channel = '#ff'
input = Queue.Queue()
output = Queue.Queue()
irc = {}
irc['rss'] = {}
irc['trivia'] = {}
irc['rss']['main'] = RssBot(channel, input, output)
irc['trivia']['main'] = TriviaBot(channel, input, output)
server = 'irc.azzurra.org'
port = 6667
irc['rss']['nickname'] = 'FF[RSS]'
irc['trivia']['nickname'] = 'FF[TRIVIA]'
irc['rss']['password'] = ''
irc['trivia']['password'] = ''
irc['rss']['ident'] = 'RSS'
irc['trivia']['ident'] = 'TRIVIA'
irc['rss']['main'].connect(server, port, irc['rss']['nickname'], irc['rss']['password'], irc['rss']['ident'])
irc['trivia']['main'].connect(server, port, irc['trivia']['nickname'], irc['trivia']['password'], irc['trivia']['ident'])
irc['rss']['main'].run()
irc['trivia']['main'].run()