from django.shortcuts import render
from servicecenter.models import Shipment
from billing.models import ShipmentBillingQueue

def add_to_shipment_queue(awb):
    shipment_queue = ShipmentBillingQueue.objects.filter(airwaybill_number=awb)
    if shipment_queue.exists():
        return False

    shipment = Shipment.objects.get(airwaybill_number=awb)
    shipment_date  = shipment.shipment_date
    shipment_type = 1 if shipment.rts_status == 1 else 0

    if not shipment_date:
        return False

    ShipmentBillingQueue.objects.create(
        airwaybill_number=awb,
        status=0,
        shipment_date=shipment_date,
        shipment_type=shipment_type
    )
    return True
