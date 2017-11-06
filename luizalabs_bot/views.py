from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json, requests, random, re
import unicodedata
from pprint import pprint
from google_search import GoogleCustomSearch


#Definicao dos tokens de acesso
PAGE_ACCESS_TOKEN = "EAACBZAi171kMBACRtwqIKYVGbDoPR14RaXLh4fClBqSdqyCnSgaDVlLIMOxuZB0p8jO9dCJNWp2fHTCnM9HsIZAFNyqjuPNVppFi01qUPQtKUHrmb0ZCJlvJzq56k1QeUTmlbpty5fYuzOCDwrCnjZAZAURxVHQGbNpZCmwgT8BMqrxLl0LfvpO"
VERIFY_TOKEN = "EAACBZAi171kMBAEgg9wxfrhZBjv4qCawMwEyEA4dUcH8nCk7dYHtC4GpFjAHTlvJlaP3ZCV11ZCTvZBzjsfowe1VLTm2SUnkKpAyhcblWHsBMRbicYImcbRQMPmTvZC96w7LXZBg1ZAchzbk1cDpS9y9SH3zVeRBydoQipVZA16N89V3Bxf8dUhxh"
GOOGLE_API_KEY = "AIzaSyC12Qqpa4B30aKqpAhSVzwG4FG-3L58HJA"
GOOGLE_CUSTOM_SEARCH_ENGINE_ID = "015323979992596059899:s5hyzuypkl8"

api = GoogleCustomSearch(GOOGLE_CUSTOM_SEARCH_ENGINE_ID ,GOOGLE_API_KEY)

# Dicionario de dados, usando apenas 3 tokens de exemplos, bem longe da realidade.
# poderia ser implementado usando um db, webservices ou pages requests


 
##luiza_mind = { 'celular': ["""Encontrei excelentes ofertas sobre Brinquedos para voce: http://www.magazineluiza.com.br/celulares-e-smartphones/l/te/""", 
#                           """iPhone 8 - PRE-VENDA !!!!!, Confira: http://www.magazineluiza.com.br/landingpage/?header=231017PreVendaiPhone8header.png&unavailable=false&bob=true&menu=selecao-21939&showcase=selecao-21939"""], 
#               'tv':      ["""Encontrei excelentes ofertas em TV's para voce: http://www.magazineluiza.com.br/tv-led-plasma-lcd-e-outras/tv-e-video/s/et/peco/ """, 
#                          """ Conheca a LG 4k: http://www.magazineluiza.com.br/tv-led-plasma-lcd-e-outras/tv-e-video/s/et/peco/"""], 
#               'brinquedo':  ["""Encontrei excelentes ofertas sobre Brinquedos para voce: http://www.magazineluiza.com.br/brinquedos/l/br/ """, 
#                           """Confira ofertas especiais em Brinquedos: http://www.magazineluiza.com.br/brinquedos/l/br/"""] }
#  Metodo que envia dados para o Messenger em resposta a iteracao com o usuario

def post_facebook_message(fbid, user_message):  
    
    luiza_talks = "Ola ! Sou a Luiza,  por favor, escolha qual produto voce teria interesse, digite frases que contenha uma palavras chave como TV,  celular, brinquedos, etc..."
    
    keywords = unicodedata.normalize('NFD', user_message).encode('ascii', 'ignore')
       
    # tokenization 
    #keywords = re.sub(r"[^a-zA-Z0-9\s]",' ', user_message).lower().split()
    #luiza_talks = "Ola ! Sou a Luiza, tenho 3 grandes promocoes para voce,  por favor, escolha qual promocao voce teria interesse, digite frases que contenha uma palavra chave como TV,  celular ou brinquedos."
    
    for result in api.search(keywords, 'http://magazineluiza.com.br'):
       luiza_talks = result['title'] + " " + result['link'] + " " +result['snippet']
    
    ##for token in tokens:
    #    if token in luiza_mind:
    #        luiza_talks = random.choice(luiza_mind[token])
    #        pprint(luiza_talks)
    #        break
        
    if not luiza_talks:
            luiza_talks = "Sua consulta nao foi possivel, por favor, informe um produto que gostaria de consultar" 
    
    user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid 
    user_details_params = {'fields':'first_name', 'access_token':PAGE_ACCESS_TOKEN}
    resp = requests.get(url=user_details_url, params=user_details_params)
    data = json.loads(resp.text)
    luiza_talks = data['first_name']+', ' + luiza_talks
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":luiza_talks}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    
    #somente para depuracao pela console, nao tem efeito pratico na app
    pprint(status.json())
    
#Classe da view principal    
class ChatBotView(generic.View):
    
    # Metodos de iteracao
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')  
            
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                if 'message' in message:
                    # Print the message to the terminal
                    pprint(message)
                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly. 
                    post_facebook_message(message['sender']['id'], message['message']['text'])
        return HttpResponse()    
       
   
        
