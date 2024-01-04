from django.urls import path
from .views import ShipmentInscan
urlpatterns = [
        path("inscan_shipment/", ShipmentInscan.as_view()),
        ]
