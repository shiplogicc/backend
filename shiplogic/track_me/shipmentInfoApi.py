import json
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from oauth2_provider.models import Application, AccessToken, RefreshToken
from rest_framework.decorators import authentication_classes, permission_classes
import requests
from rest_framework.permissions import IsAuthenticated

from rest_framework.authtoken.models import Token
from airwaybill.models import *
from servicecenter.models import Shipment,ShipmentHistory
import unicodedata
from django.apps import apps

class ShipmentInfo(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        print(request.data)
        data = request.data
        awb_no = data.get('airwaybill_number','')
        order_no = data.get('order_number','')
        if not awb_no and not order_no:
            message = "Please provide airwaybill_number or order_number"
            data = {"status":False,"message":message,"shipment_info":{}}
            return Response(data)

        shipment = None
        if Shipment.objects.filter(airwaybill_number=awb_no):
            shipment = Shipment.objects.filter(airwaybill_number=awb_no)
        if not shipment:
            shipment = Shipment.objects.filter(order_number=order_no)
        
        if not shipment:
            message = "No Shipment manifested for AWB_No : {0} or order_number:{1}".format(awb_no,order_no)
            data = {"status":False,"message":message,"shipment_info":{}}
            return Response(data)
        shipment = shipment.latest('id')
        shipment_info = {}
        consignee_details = {}
        consinee_name = shipment.consignee
        consignee_address = {}
        consignee_address["address1"] = unicodedata.normalize('NFKD', shipment.consignee_address1)
        consignee_address["address2"] = unicodedata.normalize('NFKD', shipment.consignee_address2)
        consignee_address["address3"] = unicodedata.normalize('NFKD', shipment.consignee_address3)
        consignee_pincode = shipment.pincode
        if shipment.reverse_pickup:
            consignee_pincode = shipment.pickup.pincode

        consignee_details["consinee_name"] = consinee_name
        consignee_details["consignee_address"] = consignee_address
        consignee_details["consignee_pincode"] = consignee_pincode

        shipment_info["consignee_details"] = consignee_details   

        customer_info = {}
        customer_name = str(unicodedata.normalize('NFKD', shipment.shipper.name)) + "-"+str(shipment.shipper.code)
        customer_address = {}
        customer_address1 = unicodedata.normalize('NFKD', shipment.shipper.address.address1)
        customer_address2 = unicodedata.normalize('NFKD', shipment.shipper.address.address2)
        customer_address3 = unicodedata.normalize('NFKD', shipment.shipper.address.address3)
        customer_address["customer_address1"] = customer_address1
        customer_address["customer_address2"] = customer_address2
        customer_address["customer_address3"] = customer_address3
        customer_info['customer_address'] = customer_address
        customer_info["pincode"] = unicodedata.normalize('NFKD', shipment.shipper.address.pincode)
        customer_info["customer_name"] = customer_name
        shipment_info["customer_info"] = customer_info
       
        
        product_info = {}
        product_info["product_type"] = shipment.product_type
        product_info["collectable_value"] = shipment.collectable_value
        product_info["declared_value"] = shipment.declared_value
        product_info["product_description"] = shipment.item_description
        product_info["length"] = shipment.length
        product_info["breadth"] = shipment.breadth
        product_info["height"] = shipment.height
        product_info["volumetric_weight"] = shipment.volumetric_weight
        product_info["pieces"] = shipment.pieces

        shipment_info["product_info"] = product_info
        shipment_info["origin_sc"] = str(shipment.pickup.service_centre)
        shipment_info["destination_sc"] = str(shipment.service_centre)
        shipment_info["delivery_excepted_date"] = shipment.expected_dod.strftime('%Y-%m-%d') if shipment.expected_dod else ""
        shipment_info["ref_awb"] = shipment.ref_airwaybill_number if shipment.ref_airwaybill_number else ""
    
        #upd_time = shipment.added_on
        #monthdir = upd_time.strftime("%Y_%m")
        #shipment_history = apps.get_model('servicecenter', 'ShipmentHistory_%s'%(monthdir))
        shipment_history_list = []
        for history in ShipmentHistory.objects.filter(shipment=shipment):
            shipment_history_info = {}
            if history.employee_code:
                history_employee = str(unicodedata.normalize('NFKD', history.employee_code.firstname)) +" "+str(unicodedata.normalize('NFKD', history.employee_code.lastname)) + "-"+str(unicodedata.normalize('NFKD', history.employee_code.employee_code))
            else:
                history_employee = ""

            shipment_history_info["employee"] = history_employee
            shipment_history_info["status"] = history.status
            shipment_history_info["remarks"] = history.remarks if history.remarks else ""
            shipment_history_info["updated_on"] = history.updated_on.strftime('%Y-%m-%d %H:%M:%S')
            shipment_history_list.append(shipment_history_info)
        
        shipment_info["shipment_history_details"] = shipment_history_list

        
        data = {"status":True,"message":"","shipment_info":shipment_info}
        return Response(data)
