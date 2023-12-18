from django.urls import path
from .fetchAWB import GetAWB
from .forwardShipmentManifest import ForwardManifestion
urlpatterns = [
        path("fetchawb/", GetAWB.as_view()),
        path("shipmentManifest/", ForwardManifestion.as_view()),
]

