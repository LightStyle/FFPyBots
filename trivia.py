# -*- coding: utf-8 -*-
'''
###TriviaBot###
Realizzato da Ltk_Sim ed Hannibal Smith per irc.forumfree.it
Terminato il 30 Giugno 2010
'''
from irclib import SimpleIRCClient
import random
import time

categorie = {'aforismi':262,'anime':436,'arte':402,'auto':275,'calcio-e-sport':1676,'cinema':81,'computer':386,'cose-da-non-fare':270,'cruciverba':661, 'cultura':275, 'curioista':1479,'indovinelli':1136,'inglese':512,'latino':154,'letteratura-e-italiano':814,'matematica':207,'musica':2385,'proverbi':561,'sesso':603,'sigle-e-acronimi':187,'storia':108,'vario':2093}

class TriviaBot(SimpleIRCClient):
    def __init__(self, channel, input, output):
        SimpleIRCClient.__init__(self)
        self.channel=channel
        self.channels = {}
        self.joined_channels = {}
        self.lol = False
        self.pubblicata = False
        
    def on_welcome(self, c, e):
        c.join(self.channel)
        
    def classifica(self, channelp):
        if self.channels[channelp]['partecipanti'].items():
            self.connection.privmsg(channelp, 'Classifica:')
            dizionario_punteggio={}
            for nick, partecipante in self.channels[channelp]['partecipanti'].items():
                if partecipante['punteggio'] in dizionario_punteggio:
                    dizionario_punteggio[partecipante['punteggio']].append(nick)
                else:
                    dizionario_punteggio[partecipante['punteggio']] = [nick]
                
            for punteggio in sorted(dizionario_punteggio.keys(), reverse=True):
                for nick in dizionario_punteggio[punteggio]:
                    self.connection.privmsg(channelp, nick+' punti: '+str(punteggio))
        else:
            self.connection.privmsg(channelp, 'Non è stato registrato alcun punteggio.')
            return

    def run(self):
        while True:
            to_part = None
            for channel, item in self.joined_channels.items():
                if (time.time() - item) > 180:
                    self.connection.part([channel])
                    to_part = channel
            try:
                del self.joined_channels[to_part]
            except:
                pass
            
            to_delete = None
            for channel in self.channels:
                if 'op' in self.channels[channel]:
                    continue
                domanda_attuale = self.channels[channel]['domanda_attuale']

                if domanda_attuale is not False: #Il trivia è stato avviato
                    if domanda_attuale+1 < self.channels[channel]['numero_domande']:
                        oggetto_domanda = self.channels[channel]['domande'][domanda_attuale]
                        if not oggetto_domanda['finita']:
                            if self.pubblicata is not False:
                                self.connection.privmsg(channel, 'DOMANDA'+str(domanda_attuale+1)+': '+oggetto_domanda['domanda'])
                                aiuto=True
                                self.pubblicata = False         
                                                 
                            if int(time.time()) - int(oggetto_domanda['data']) == int(self.channels[channel]['secondi'])/2:
                                if aiuto:
                                    car=len(oggetto_domanda['risposta'])
                                    enstr=oggetto_domanda['risposta'][0:1]
                                    string=oggetto_domanda['risposta']
                                    for val in range(car-1):
                                        if oggetto_domanda['risposta'][val+1]==' ':
                                            enstr+=' '
                                        else:
                                            enstr+='*'
                                    
                                    self.connection.privmsg(channel, 'Aiuto: '+enstr)
                                    aiuto=False
                                else:
                                    pass
                            elif int(time.time()) - int(oggetto_domanda['data']) > int(self.channels[channel]['secondi']):
                                self.connection.privmsg(channel,'Tempo scaduto per la domanda! La risposta era: '+oggetto_domanda['risposta']+'.')
                                self.connection.privmsg(channel, 'La classifica resta invariata.')
                                self.channels[channel]['domanda_attuale'] += 1
                                domanda_attuale = self.channels[channel]['domanda_attuale']
                                self.channels[channel]['domande'][domanda_attuale]['data'] = time.time()
                                self.pubblicata=True
                        else:
                            self.channels[channel]['domanda_attuale'] += 1
                            domanda_attuale = self.channels[channel]['domanda_attuale']
                            self.channels[channel]['domande'][domanda_attuale]['data'] = time.time()
                            self.connection.privmsg(channel, self.user+' ha dato la risposta corretta: '+oggetto_domanda['risposta'])
                            self.classifica(channel)
                            self.pubblicata = True
                    else:
                        self.connection.privmsg(channel, 'Partita terminata!')
                        self.classifica(channel)
                        to_delete = channel
                        self.connection.part(channel)
                               
                else:
                    if 'domande' in self.channels[channel]:
                        #Avvia il trivia dando la prima domanda
                        self.connection.privmsg(channel, 'Trivial Avviato!')
                        self.channels[channel]['domanda_attuale'] = 0 #Imposta a 0 per la prima domanda
                        domanda_attuale = self.channels[channel]['domanda_attuale']
                        domanda = self.channels[channel]['domande'][domanda_attuale]
                        domanda['data'] = time.time()
                        self.pubblicata = True
                    else:
                        #Il trivia sta per iniziare...
                        pass
            self.ircobj.process_once(0.2)
            try:
                del self.channels[to_delete]
            except:
                pass
        
    def starttrivia(self, channelp, creator, category, domande, secondi, aiuto):
        self.connection.privmsg(channelp, 'Categoria: "'+category+'", numero domande: '+str(domande)+', secondi per ogni domanda: '+secondi+'. Per avviare questa partita digitare %starttrivia')
        self.channels[channelp] = {
                                'partecipanti' : {},
                                'categoria' : category,
                                'creator' : creator,
                                'secondi' : secondi,
                                'numero_domande' : domande+1,
                                'domanda_attuale' : False,
                                'start_date' : time.time(),
                                'aiuto': aiuto
                                   }
    def on_invite(self, c, e):
        channel = e.arguments()[0].lower()
        c.join(channel)
        self.connection.privmsg(channel, 'Per il link alla guida dell\'aiuto digitare %help.')
        self.joined_channels[channel] = time.time()

    def on_namreply(self, c, e):
        channel = e.arguments()[1].lower()
        if channel in self.channels:
            if 'op' in self.channels[channel]:
                nick = self.channels[channel]['op']
                category = self.channels[channel]['category']
                domande = self.channels[channel]['domande']
                secondi = self.channels[channel]['secondi']
                aiuto = self.channels[channel]['aiuto']
                lista_utenti = e.arguments()[2].lower().split(' ')
                utente = [x for x in lista_utenti if '@'+nick == x]
                if utente:
                    self.starttrivia(channel, nick, category, domande, secondi, aiuto)
                else:
                    del self.channels[channel]
                    self.connection.privmsg(channel, 'Devi essere Op per poter dare questo comando.')
        
    def on_pubmsg(self, c, e):
        
            channelp=e.target()
            message = e.arguments()[0]
            message = message.lower()
            user=e.source()
            user=user.split('!')
            user=user[0]
            self.user=user
            user=user.lower()
            if message=='%categorie':
                categoriestr=''
                for valore in categorie:
                    categoriestr = categoriestr + valore.capitalize()+': '+str(categorie[valore])+', '
                self.connection.privmsg(channelp, 'Categorie (<nome categoria>: <numero domande categoria>):')
                self.connection.privmsg(channelp, categoriestr)
            elif message=='%bot quit':
                irc.close()
            elif message=='%classifica':
                if channelp not in self.channels:
                    self.connection.privmsg(channelp, 'Nessuna partita in corso')
                    return
                self.classifica(channelp)

            elif message[0:7] == '%trivia':
                if channelp in self.channels:
                    del self.channels[channelp]
                    messagelist = message.split(' ')
                    category=messagelist[1]
                    domande = int(messagelist[2])
                    secondi = messagelist[3]
                else:
                    if message[8:] == '':
                        self.connection.privmsg(channelp, 'E\' stato digitato il messaggio in modo non corretto digitare %trivia <categoria> <domande> <secondi>')
                    else:
                        messagelist = message.split(' ')
                        category=messagelist[1]
                        domande = int(messagelist[2])
                        secondi = messagelist[3]
                        
                if category in categorie:
                    if domande>80:
                        self.connection.privmsg(channelp, 'Spiacente, le domande non possono essere piu\' di 80.')
                    elif domande<5:
                        self.connection.privmsg(channelp, 'Spiacente, le domande non possono essere meno di 5.')
                    elif domande == '':
                        self.connection.privmsg(channelp, 'Specificare il numero di domande.')
                    elif int(secondi)>150:
                        self.connection.privmsg(channelp, 'Spiacente, i secondi non possono essere piu\' di 150')
                    elif int(secondi)<5:
                        self.connection.privmsg(channelp, 'Spiacente, i secondi non possono essere meno di 5')
                    else:
                        self.channels[channelp] = {}
                        self.channels[channelp]['op'] = user
                        self.channels[channelp]['category'] = category
                        self.channels[channelp]['domande'] = domande
                        self.channels[channelp]['secondi'] = secondi                      
                        try:
                            aiuto=messagelist[4]
                            if aiuto == 'y' or aiuto == 'yes':
                                aiuto=True
                                self.channels[channelp]['aiuto']=aiuto
                            else:
                                aiuto=False
                                self.channels[channelp]['aiuto']=aiuto
                        except:
                            aiuto=False
                            self.channels[channelp]['aiuto']=aiuto
                            pass

                        
                    self.connection.names([channelp])
                    #self.starttrivia(channelp, category, domande, secondi)
                        
                else:
                    if category == '':
                        self.connection.privmsg(channelp, 'Specificare una categoria!')
                    else:
                        self.connection.privmsg(channelp, 'Categoria non trovata')
            elif message=='%help':
                self.connection.privmsg(channelp, 'Per l\'aiuto leggere la seguente guida: http://www.chat.forumfree.it')
            elif message=='%stoptrivia':
                if self.channels[channelp]['creator'] == user:
                    self.classifica(channelp)
                    del self.channels[channelp]
                    self.connection.privmsg(channelp, 'Trivia terminato su comando di '+user)
                else:
                    self.connection.privmsg(channelp, 'Il trivia può essere terminato solo dal creatore.')
                    
                
            elif message=='%starttrivia':
                if channelp not in self.channels:
                    return
                if self.channels[channelp]['creator'] == user:
                    percorso='/home/simone/Scrivania/bottrivia/cat/'+self.channels[channelp]['categoria']+'.txt'
                    f=open(percorso,'r+')
                    self.questions = f.readlines()
                    totalquestions = []
                    for value in range(1,int(self.channels[channelp]['numero_domande'])+1):
                         randomvalue=random.choice(range(int(categorie[self.channels[channelp]['categoria']])))
                         listques=self.questions[randomvalue].split('*')
                         self.questionx=listques[0]
                         risposta=listques[1]
                         risposta=risposta.replace('\r', '')
                         risposta=risposta.replace('\n', '')
                         risposta=risposta.lower()
                         
                         if risposta not in totalquestions:
                             
                             totalquestions.append({'domanda' : self.questionx, 'risposta' : risposta,
                                                    'finita' : False, 'data' : None})
                         else:
                            return
                        
                    self.totalquestions=totalquestions
                    self.channels[channelp]['domande'] = totalquestions
                else:
                    self.connection.privmsg(channelp, 'Il trivia deve essere avviato dal creatore.')

    
            elif channelp in self.channels and self.channels[channelp]['domanda_attuale'] is not False:
                numero_domanda = self.channels[channelp]['domanda_attuale']
                risposta = self.channels[channelp]['domande'][numero_domanda]['risposta']
                if message == risposta:
                    self.channels[channelp]['domande'][numero_domanda]['finita'] = True
                    tempo=int(time.time()) - int(self.channels[channelp]['domande'][numero_domanda]['data'])
                    tempo=tempo/4.0
                    if user in self.channels[channelp]['partecipanti']:
                        self.channels[channelp]['partecipanti'][user]['punteggio'] += tempo
                                                                     
                    else:
                        self.channels[channelp]['partecipanti'][user] = {}
                        self.channels[channelp]['partecipanti'][user]['punteggio']=tempo
                else:
                    pass
