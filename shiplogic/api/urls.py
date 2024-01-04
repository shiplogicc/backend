from django.urls import path
from .fetchAWB import GetAWB
from .forwardShipmentManifest import ForwardManifestion
from .shipmentCancel import CancelAWB
from .customerNDRInstruction import NDRInstruction
urlpatterns = [
        path("fetchawb/", GetAWB.as_view()),
        path("shipmentManifest/", ForwardManifestion.as_view()),
        path("cancel_shipment/", CancelAWB.as_view()),
        path("ndr_instruction/", NDRInstruction.as_view()),
]

