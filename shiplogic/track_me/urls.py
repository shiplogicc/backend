from django.urls import path
from track_me.shipmentInfoApi import ShipmentInfo
urlpatterns = [
        path("shipmentInfo/", ShipmentInfo.as_view()),
]

