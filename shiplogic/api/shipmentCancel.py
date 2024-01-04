from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
import requests

from servicecenter.models import Shipment,ShipmentHistory
from integration_services.models import ShipmentCancelQueue
from slconfig.models import ShipmentStatusMaster
from api.utils import history_update,validateJsonSchema


cancelAWBSchema = {
        "type":"object",
        "properties": {
        "awb_no": {
            "type": "integer","minimum":1
        }
    },
    "required": [
        "awb_no"
    ]



        }



class CancelAWB(APIView):
    def post(self,request):

        awbs = request.data
        customer = request.user.employeemaster.customer

        response_list = []
        for awb in awbs:
            awb_no = awb.get('awb_no','')
            response = {}

            return_flag,message = validateJsonSchema(awb,cancelAWBSchema)
            if not return_flag:
                response = {"success":False,"message":message,"awb":awb_no}
                response_list.append(data) 
                continue
            s = Shipment.objects.filter(airwaybill_number = awb_no,shipper=customer)
            if not s:
               response["awb"] = awb_no
               response["success"] = False
               response["reason"] = "INCORRECT_AIRWAYBILL_NUMBER"
               response_list.append(response)
               continue
            if s:
                s = s[0]
                if s.rts_status == 1:
                    response["awb"] = awb_no
                    response["success"] = False
                    response["reason"] = "AIRWAYBILL_NUMBER_RETURNED"
                    response_list.append(response)
                    continue
                if s.rts_status == 2:
                    response["awb"] = awb_no
                    response["success"] = False
                    response["reason"] = "AIRWAYBILL_NUMBER_RETURNED"
                    response_list.append(response)
                    continue
                if s.status == 9:
                    response["awb"] = awb_no
                    response["success"] = False
                    response["reason"] = "AIRWAYBILL_NUMBER_ALREADY_DELIVERED"
                    response_list.append(response)
                    continue
                if s.status == 7:
                    response["awb"] = awb_no
                    response["success"] = False
                    response["reason"] = "AIRWAYBILL_NUMBER_OUT_FOR_DELIVERY"
                    response_list.append(response)
                    continue
                if s.reverse_pickup and s.status not in [31,33]:
                        response["awb"] = awb_no
                        response["success"] = False
                        response["reason"] = "REVERSE_SHIPMENT_PICKED"
                        response_list.append(response)
                        continue
                if s.reason_code.closure_code if s.reason_code else False:
                    response["awb"] = awb_no
                    response["success"] = False
                    response["reason"] = "SHIPMENT_ALREADY_CLOSED"
                    response_list.append(response)
                    continue

                shipment_cancel_queue = ShipmentCancelQueue.objects.filter(airwaybill_number = awb_no, status = 0)
                if not shipment_cancel_queue:
                    if not ShipmentCancelQueue.objects.filter(airwaybill_number = awb_no):
                        ShipmentCancelQueue.objects.create(airwaybill_number = awb_no, status=0) 
                    else:
                        ShipmentCancelQueue.objects.filter(airwaybill_number = awb_no).update(status=0)
                    if s.reverse_pickup:
                        reason = ShipmentStatusMaster.objects.get(code=404)
                        s.reason_code = reason
                        s.status = 33 
                        s.save()
                        history_update(s, 33, request, remarks="PICKUP CANCELLED BY SHIPPER",reason_code=reason)
                        ReverseShipment.objects.filter(shipment=s).update(status=2)
                    else:
                        history_update(s, 77, request, remarks="Shipment RTO Lock")
                        #ShipmentHistory.objects.create(shipment=s, status=77,remarks='Shipment RTO Lock',current_sc=s.current_sc)
                        
                    response["awb"] = awb_no
                    response["success"] = True 
                    response["reason"] = ""
                else:
                    response["awb"] = awb_no
                    response["success"] = True
                    response["reason"] = ""
            else:
                response["awb"] = awb_no
                response["success"] = False
                response["reason"] = "INVALID_AWB_NUMBER"
            response_list.append(response)
        return Response(response_list)   
         

