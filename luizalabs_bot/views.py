# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from pprint import pprint
from google_search import GoogleCustomSearch
import json, requests, random, re, unicodedata

#Definicao dos tokens de acesso
PAGE_ACCESS_TOKEN = "EAACBZAi171kMBACRtwqIKYVGbDoPR14RaXLh4fClBqSdqyCnSgaDVlLIMOxuZB0p8jO9dCJNWp2fHTCnM9HsIZAFNyqjuPNVppFi01qUPQtKUHrmb0ZCJlvJzq56k1QeUTmlbpty5fYuzOCDwrCnjZAZAURxVHQGbNpZCmwgT8BMqrxLl0LfvpO"
VERIFY_TOKEN = "EAACBZAi171kMBAEgg9wxfrhZBjv4qCawMwEyEA4dUcH8nCk7dYHtC4GpFjAHTlvJlaP3ZCV11ZCTvZBzjsfowe1VLTm2SUnkKpAyhcblWHsBMRbicYImcbRQMPmTvZC96w7LXZBg1ZAchzbk1cDpS9y9SH3zVeRBydoQipVZA16N89V3Bxf8dUhxh"
GOOGLE_API_KEY = "AIzaSyC12Qqpa4B30aKqpAhSVzwG4FG-3L58HJA"
GOOGLE_CUSTOM_SEARCH_ENGINE_ID = "015323979992596059899:s5hyzuypkl8"

api = GoogleCustomSearch(GOOGLE_CUSTOM_SEARCH_ENGINE_ID ,GOOGLE_API_KEY)
 
def post_facebook_message(fbid, user_message):  
    
    luiza_talks = ""
    
    welcome = { 'oi': 'Olá !!', 
                'ola': 'Olá !!',
                'ol': 'Olá !!',
                'dia'              : 'Bom dia !!', 
                'tarde'            : 'Boa tarde !!',
                'noite'            : 'Boa noite !!'
              }
              
    luiza_wlc_msg = " Eu sou a Luiza, e tenho muitas ofertas e promoções para você, por favor, digite frases com palavras chaves como brinquedos, celular, etc... Ex: Eu quero brinquedo para minha filha de 6 anos."
    
    tokens = re.sub(r"[^a-zA-Z0-9\s]",' ', user_message).lower().split()
    
    for token in tokens:
        if token.lower() in ['ola', 'oi', 'ol', 'dia', 'tarde', 'noite']:
            luiza_talks = welcome[token] + luiza_wlc_msg
        else:    
    
            keywords = unicodedata.normalize('NFD', user_message).encode('ascii', 'ignore')
            
            for result in api.search(keywords, 'http://magazineluiza.com.br'):
                luiza_talks = result['title'] + " " + result['link'] 
            
        if not luiza_talks:
           luiza_talks = "Sua consulta não foi possivel, por favor, informe um produto que gostaria de consultar. Ex: Refrigerador ... " 
    
    user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid 
    user_details_params = {'fields':'first_name', 'access_token':PAGE_ACCESS_TOKEN}
    resp = requests.get(url=user_details_url, params=user_details_params)
    data = json.loads(resp.text)
    luiza_talks = data['first_name']+', ' + luiza_talks
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":luiza_talks}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    
    pprint(status.json())
    
#Classe da view principal    
class ChatBotView(generic.View):
    
    # Metodos HTTP
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')  
            
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    pprint(message)
                    post_facebook_message(message['sender']['id'], message['message']['text'])
        return HttpResponse()    