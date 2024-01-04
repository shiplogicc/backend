
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
from track_me.telecomment import callcentre_comment_entry 
import datetime

ndrSchema = {
        "type":"object",
        "properties": {
            "awb": 
            {
               "type": "integer","minimum":1
            },
            "delivery_date":
            {
                "type":"string",
                "format": "date"
            },
            "instruction":
            {
                "type":"string",
                "enum":["RAD"]
            }    
    },
    "required": ["awb","instruction"]

        }

def ndrValidate(instruction,customer):
    awb_no = instruction.get('awb')
    delivery_date = instruction.get('scheduled_delivery_date','')
    resolution = instruction.get('instruction','')
    response = {}
    if resolution == 'RAD' and not delivery_date:
        response["awb"] = awb_no
        response["success"] = False
        response["reason"] = "scheduled_delivery_date is mandedory for RAD instruction"
        return False,response

    try:
        datetime.datetime.strptime(delivery_date,"%Y-%m-%d")
    except Exception as e:
        response["awb"] = awb_no
        response["success"] = False
        response["reason"] = str(e)
        return False,response

    s = Shipment.objects.filter(airwaybill_number = awb_no,shipper=customer)

    response = {}
    if not s:
        response["awb"] = awb_no
        response["success"] = False
        response["reason"] = "INCORRECT_AIRWAYBILL_NUMBER"

    if s:
      s = s[0]
      ud_attempt_count = ShipmentHistory.objects.filter(shipment = s, status__in = [8]).count()
      if s.reverse_pickup:
          response["awb"] = awb_no
          response["success"] = False
          response["reason"] = "Reverse shipment can not be rescheduled"

      elif s.rts_status == 1:
          response["awb"] = awb_no
          response["success"] = False
          response["reason"] = "AIRWAYBILL_NUMBER_RETURNED"
          
      elif s.rts_status == 2:
          response["awb"] = awb_no
          response["success"] = False
          response["reason"] = "AIRWAYBILL_NUMBER_RETURNED"
      elif s.status == 9:
          response["awb"] = awb_no
          response["success"] = False
          response["reason"] = "AIRWAYBILL_NUMBER_ALREADY_DELIVERED"

      elif s.status == 7:
          response["awb"] = awb_no
          response["success"] = False
          response["reason"] = "AIRWAYBILL_NUMBER_OUT_FOR_DELIVERY"

      elif s.reason_code.closure_code if s.reason_code else False:
          response["awb"] = awb_no
          response["success"] = False
          response["reason"] = "SHIPMENT_ALREADY_CLOSED"

      elif Shipment.objects.filter(airwaybill_number = awb_no, reason_code__code = 1225):
          response["awb"] = awb_no
          response["success"] = False
          response["reason"] = "Shipment refused by consignee. Please update RTO instruction or contact your KAS"

      elif ud_attempt_count == 0:
          response["awb"] = awb_no
          response["success"] = False
          response["reason"] = "Re-attempt not applicable, as shipment pending for it's first attempt."

      elif ud_attempt_count == 3:
          response["awb"] = awb_no
          response["success"] = False
          response["reason"] = "Maximum 2 Re-attempt Request, please contact your KAS."

      elif ud_attempt_count > 3:
          response["awb"] = awb_no
          response["success"] = False
          response["reason"] = "Eligible for Return only , Please contact your KAS."

      elif ShipmentCancelQueue.objects.filter(airwaybill_number=awb_no,status=0):
          response["awb"] = awb_no
          response["success"] = False
          response["reason"] = "Shipment in RTO lock stage."

    if response: 
       return False,response
    else:
       return True,response
     
class NDRInstruction(APIView):
    def post(self,request):
        data = request.data
        response_list = []
        customer = request.user.employeemaster.customer
        for ndr in data:
            return_flag,message = validateJsonSchema(ndr,ndrSchema)
            awb_no = ndr.get('awb','')
            if not return_flag:
                response = {"success":False,"reason":message,"awb":awb_no}
                response_list.append(response)
                continue

            success,response_dict = ndrValidate(ndr,customer)
            if not success:
                response_list.append(response_dict)
                continue

            s = Shipment.objects.filter(airwaybill_number = awb_no,shipper=customer).latest('id')
            instruction = ndr.get('instruction')
            scheduled_delivery_date = ndr.get('scheduled_delivery_date','')
            comments = ndr.get('comments','')
            emp_code = None
            user = request.user
            cust_code = user.employeemaster.customer.code
            current_sc = None

            if instruction == 'RAD':
                concern = 'Customer Auto Instructions'
                response,error = callcentre_comment_entry(emp_code,current_sc,awb_no,concern,instruction,comments,scheduled_delivery_date,cust_code)
                if not response:
                    response_list.extend(error)
                else:
                    data = {"success":True,"reason":"Successfully updated","awb":awb_no}
                    response_list.append(data)

        return Response(response_list)
