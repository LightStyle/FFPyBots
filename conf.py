from rss import *
from trivia import *
import Queue

input = Queue.Queue()
output = Queue.Queue()
irc = {}

# Canale principale a cui si devono connettere i bot
channel = '#ff'

# Server e porta a cui si devono connettere i bot
server = 'irc.azzurra.org'
port = 6667


# Impostazioni TRIVIA Bot
irc['trivia'] = {}
irc['trivia']['main'] = TriviaBot(channel, input, output)
irc['trivia']['nickname'] = 'TriviaBot'
irc['trivia']['password'] = ''
irc['trivia']['ident'] = 'TriviaBot'

# Impostazioni RSS Bot
irc['rss'] = {}
irc['rss']['main'] = RssBot(channel, input, output)
irc['rss']['nickname'] = 'RssBot'
irc['rss']['password'] = ''
irc['rss']['ident'] = 'Rss'