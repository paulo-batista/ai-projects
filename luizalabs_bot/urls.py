from django.conf.urls import include, url
from .views import ChatBotView


urlpatterns = [
                  url(r'^f4e6de8e0fd13f3a90c06c6588a65caf1e8fc75936b2387568/?$',  ChatBotView.as_view()) 
               ]