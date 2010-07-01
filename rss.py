from irclib import SimpleIRCClient
import re
try:
    import feedparser
except:
    print 'Modulo FeedParser da import NON trovato'

class RssBot(SimpleIRCClient):
    def __init__(self, channel, input, output):
        SimpleIRCClient.__init__(self)
        self.channel = channel
        self.channels = {}
        
    def on_welcome(self, c, e):
        c.join(self.channel)
        
    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments()[0])
        messagepvt = e.arguments()[0]
        print messagepvt
    
    def on_kick(self, c, e):
        print 'kicked from', e.target(), 'by', e.arguments()[1]

       
    def getRssUrl(self, id='1', circuito='forumfree', query=''):
        circuito = self.circuito
        it = circuito == 'forumfree' and 'it' or 'net' 
        url = "http://"+circuito+"."+it+"/rss.php"
        query_string = "?c=" + str(id) + query
        complete_url = url + query_string
        return complete_url
    
    def getXmlTree(self, url, num = '1'):
        tree = feedparser.parse(url)
        return tree
    
    def getValues(self, entries):
        y = ['link', 'author', 'title', 'updated']
        values = {}
        for x in entries:
            if x in y:
                values[x] = self.transform(entries[x])
            
        return values
    
    def transform(self, text):
        txt = text.replace('&amp;', '&')
        txt = re.sub("&l=(.*)&", '&', txt)
        return txt
    
    def run(self):
        while True:
            self.ircobj.process_once(0.2)
    
    def on_invite(self, c, e):
        channel = e.arguments()[0]
        c.join(channel)
        
    def on_namreply(self, c, e):
        print e.target()
        print e.arguments()
        print e.source()
        
    def on_pubmsg(self, c, e):
        user = e.source().lower()
        channel = e.target()
        self.user = user
        message = e.arguments()[0].lower()
        if message == '%quit':
            self.disconnect()
        elif message[0:4] == '%rss':
            if message[5:] == '':
                print 'errore'
                self.connection.privmsg(channel, 'Specificare dei parametri')
            else:
                    args = message.split(' ')
                    cid = args[1]
                    circuito = args[2].lower()
#                    num = args[3]
                    print args
                    
                    if cid == '':
                        self.connection.privmsg(channel, 'Specificare un ID')
                    elif circuito == '':
                        self.connection.privmsg(channel, 'Specificare il circuito(ff, fc, bf)')
                    else:
                        if circuito == 'ff' or circuito == 'forumfree':
                            self.circuito = 'forumfree'
                        elif circuito == 'fc' or circuito == 'forumcommunity':
                            self.circuito = 'forumcommunity'
                        elif circuito == 'bf' or circuito == 'blogfree':
                            self.circuito = 'blogfree'
                        else:
                            self.circuito = 'forumfree'
                        try:
                            url = self.getRssUrl(cid, circuito, '')
                            xml_tree = self.getXmlTree(url)
                            entries = xml_tree['entries'][1]
                            values = self.getValues(entries)
                            for x in values:
                                self.connection.privmsg(channel, x + ': ' + values[x])
                            pprint.pprint(values)
                        except:
                            self.connection.privmsg(channel, 'Errore, ID Forum/Blog non valido.')