from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from apiclient.discovery import build
from google import search
import urllib
from bs4 import BeautifulSoup
import json, requests, random, re
from pprint import pprint

PAGE_ACCESS_TOKEN = "EAACBZAi171kMBACRtwqIKYVGbDoPR14RaXLh4fClBqSdqyCnSgaDVlLIMOxuZB0p8jO9dCJNWp2fHTCnM9HsIZAFNyqjuPNVppFi01qUPQtKUHrmb0ZCJlvJzq56k1QeUTmlbpty5fYuzOCDwrCnjZAZAURxVHQGbNpZCmwgT8BMqrxLl0LfvpO"
VERIFY_TOKEN = "EAACBZAi171kMBAEgg9wxfrhZBjv4qCawMwEyEA4dUcH8nCk7dYHtC4GpFjAHTlvJlaP3ZCV11ZCTvZBzjsfowe1VLTm2SUnkKpAyhcblWHsBMRbicYImcbRQMPmTvZC96w7LXZBg1ZAchzbk1cDpS9y9SH3zVeRBydoQipVZA16N89V3Bxf8dUhxh"

jokes = { 'stupid': ["""Yo' Mama is so stupid, she needs a recipe to make ice cubes.""", 
                     """Yo' Mama is so stupid, she thinks DNA is the National Dyslexics Association."""], 
         'fat':      ["""Yo' Mama is so fat, when she goes to a restaurant, instead of a menu, she gets an estimate.""", 
                      """ Yo' Mama is so fat, when the cops see her on a street corner, they yell, "Hey you guys, break it up!" """], 
         'dumb': ["""Yo' Mama is so dumb, when God was giving out brains, she thought they were milkshakes and asked for extra thick.""", 
                  """Yo' Mama is so dumb, she locked her keys inside her motorcycle."""] }

# Google API access key and custom search ID
my_api_key = "AIzaSyDq75XYyUe525_k0C3kP-8Za0z_kK5Ak1s"
my_cse_id = "015323979992596059899:s5hyzuypkl8magazineluiza"

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(
        q=search_term, 
        cx=cse_id, 
        num=10
        ).execute()
    return res
    
def promo_search(search_term):
    
    
    

    
    
# This function should be outside the BotsView class
def post_facebook_message(fbid, message):  
    
    # Remove all punctuations, lower case the text and split it based on space
    tokens = re.sub(r"[^a-zA-Z0-9\s]",' ',message).lower().split()
   # joke_text = ''
   # for token in tokens:
   #     if token in jokes:
   #         joke_text = random.choice(jokes[token])
   #         break
   # if not joke_text:
   #     joke_text = "I didn't understand! Send 'stupid', 'fat', 'dumb' for a Yo Mama joke!" 
    pprint(tokens)
    results = google_search("celular", my_api_key, my_cse_id)
    pprint(results)
    
    
    user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid 
    pprint(user_details_url)
    #user_details_params = {'url':user_details_url, 'fields':'first_name,last_name,profile_pic', 'access_token':PAGE_ACCESS_TOKEN}
    user_details_params = {'fields':'first_name', 'access_token':PAGE_ACCESS_TOKEN}
    #requests.get(user_details_url, user_details_params).json() 
    resp = requests.get(url=user_details_url, params=user_details_params)
    data = json.loads(resp.text)
    luiza_talk = 'Yo '+data['first_name']+'..! ' 
   
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":luiza_talk}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    pprint(status.json())
    
class ChatBotView(generic.View):
    
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')  
            
    # The get method is the same as before.. omitted here for brevity
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)
        
    # Post function to handle Facebook messages
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
       
   
        
