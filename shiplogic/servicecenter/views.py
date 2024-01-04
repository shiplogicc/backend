from django.conf import settings
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
from servicecenter.models import Shipment
from django.apps import apps
from billing.views import add_to_shipment_queue

from api.utils import history_update,validateJsonSchema
import datetime
now = datetime.datetime.now()
from integration_services.models import ShipmentCancelQueue
stateCreationSchema = {
     "type": "object",
     "properties": {
         "awb_no":{"type": "integer","minimum":0},
         "inscan_type":{"type": "string","enum":['service_center','hub','ppc','dc']},
     },
     "required": ["awb_no", "inscan_type"]

}


class ShipmentInscan(APIView):
    def post(self,request):
        print(request.data)
        data = request.data
        awb_no = data.get('awb_no')
        inscan_type = data.get('inscan_type')
        
        return_flag,message = validateJsonSchema(data,stateCreationSchema)
        if not return_flag:
            data = {"status":False,"message":message}
            return Response(data)

        if not Shipment.objects.filter(airwaybill_number=awb_no):
            message = "No Shipment is manifested for provided awb"
            data = {"status":False,"message":message}
            return Response(data)

        ship = Shipment.objects.filter(airwaybill_number=awb_no) 
        shipment = ship.latest('id')
        manifest_location = shipment.manifest_location 

        if ShipmentCancelQueue.objects.filter(airwaybill_number=shipment.airwaybill_number,status=0):
            message = "Shipment is Cancelation stage."
            data = {"status":False,"message":message}
            return Response(data)


        if not shipment.manifest_location:
            manifest_location = request.user.employeemaster.service_centre

        if inscan_type == 'service_center':
            status_type = 1 #verified
            if not Shipment.objects.filter(airwaybill_number=awb_no, status__in=[0,1,2]).exclude(rts_status=2):
                message = "incorrect AWB"
                data = {"status":False,"message":message}
                return Response(data)

            ship_status = 2

        elif inscan_type == 'hub':
             
            if Shipment.status in [7,9] or shipment.rts_status == 2 or (shipment.reason_code.closure_code if shipment.reason_code else False):
                message = "Shipment is already closed/Outscan state"
                data = {"status":False,"message":message}
                return Response(data)

            ship_status = 4

        elif inscan_type == 'ppc':
            if not Shipment.objects.filter(airwaybill_number=awb_no, status__in=[0,1,2]).exclude(rts_status=2) or (shipment.reason_code.closure_code if shipment.reason_code else False):
                message = "incorrect AWB"
                data = {"status":False,"message":message}
                return Response(data)

            ship_status = 2

        elif inscan_type == 'dc':
            if Shipment.status in [7,9] or shipment.rts_status == 2 or (shipment.reason_code.closure_code if shipment.reason_code else False):
                message = "Shipment is already closed/Outscan state"
                data = {"status":False,"message":message}
                return Response(data)

            dest = request.user.employeemaster.service_centre_id
            '''
            if shipment.service_centre_id == dest:
                bag = shipment.bags_set.filter(destination_id=dest)
                if bag:
                    bag =bag.latest('id')
                    if not bag.bag_status in [3,8]:
                        message = "Kindly Inscan the bag first"
                        data = {"status":False,"message":message}
                        return Response(data)
            '''
            status_type=0
            if shipment.service_centre != dest:
                status_type = 5
            else:
                status_type = 1
            
            bags = ""
            if not bags:
               if shipment.status != 6:
                  status_type = 5

            ship_status = 6
        
        if not shipment.inscan_date:
            ship.update(inscan_date=now,shipment_date=now)

        if not shipment.billing:
            add_to_shipment_queue(awb_no)

  
        #bags = shipment.bags_set.all()
        bags = []
        bag_num = ""
        if bags:
            bags = bags.latest('id')
            bag_num = bags.bag_number

        if inscan_type == 'service_center':
            history_update(shipment, ship_status, request, "", shipment.reason_code)
            #expected_dod = get_expected_dod_v2(shipment.airwaybill_number) ########### 
            expected_dod = None
            ship.update(status=ship_status, current_sc=request.user.employeemaster.service_centre,expected_dod=expected_dod,status_type = status_type, manifest_location = manifest_location)

        elif inscan_type == "hub" :
            ship.update(status=ship_status, current_sc=request.user.employeemaster.service_centre)
            history_update(shipment, ship_status, request, remarks="Debag Shipment at Hub from Bag Number %s"%(bag_num))

        elif inscan_type == "dc":
            ship.update(status=ship_status, current_sc=request.user.employeemaster.service_centre,status_type = status_type)
            history_update(shipment, ship_status,request, "Debag Shipment at Delivery Centre from Bag Number %s"%(bag_num))

        elif inscan_type == "ppc":
            ship.update(status=ship_status, current_sc=request.user.employeemaster.service_centre)
            history_update(shipment, ship_status, request, remarks="Debag Shipment at PPC from Bag Number %s"%(bag_num))

        message = "successfully updated"
        data = {"success":True,"message":message}
        return Response(data)    
            
