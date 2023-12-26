from django.urls import path
from .mdmServices import MDMAPI
urlpatterns = [
        path("mdmServices/", MDMAPI.as_view()),
]


