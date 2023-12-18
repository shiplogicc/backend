import json
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope
from oauth2_provider.models import Application, AccessToken, RefreshToken
from rest_framework.decorators import authentication_classes, permission_classes
import requests
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
now = datetime.now()
today = datetime.today()
from datetime import time
today_date = datetime.combine(today, time.min)
monthdir = now.strftime("%Y_%m")
from rest_framework import status
from rest_framework.authtoken.models import Token
import jsonschema
from jsonschema import validate
from airwaybill.models import *


fetchAPISchema = {
     "type": "object",
     "properties": {
         "awb_count":{"type": "string"},
         "product_type":{"type": "string","enum": ['cod','ppd','rev']},
     },
     "required": ["awb_count", "product_type"]

}


class GetAWB(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        
            try:
                validate(instance = request.data, schema = fetchAPISchema)
            
            except jsonschema.exceptions.ValidationError as err:
                exceptionField = ','.join(str(field) for field in err.path)
                message = err.message
                data = {"status":False,"awb":[],"message":message}
                return Response(data,status=status.HTTP_400_BAD_REQUEST)

            if not request.data.get('awb_count').isdigit():
                data = {"status":False,"awb":[],"message":"Awb count must be digit"}
                return Response(data,status=status.HTTP_400_BAD_REQUEST)
            
            elif int(request.data.get('awb_count'))>100:
                data = {"status":False,"awb":[],"message":"Awb count should be 100 or less than 100"}
                return Response(data,status=status.HTTP_400_BAD_REQUEST)


            user = request.user
            if not user.employeemaster.customer:
                data = {"status":False,"awb":[],"message":"No customer is associated with this user token"}
                return Response(data,status=status.HTTP_400_BAD_REQUEST)
            product_type = {}
            product_type['ppd'] = 1
            product_type['cod'] = 2
            product_type['rev'] = 3
            customer = user.employeemaster.customer

            count = int(request.data.get('awb_count'))
            ship_type = request.data.get('product_type').lower()
            awbc = AirwaybillCustomer.objects.create(customer=customer, type=product_type[ship_type], quantity=count)
            if count == 1:
                if product_type[ship_type] == 1:
                    awb_objs = [PPD.objects.create()]
                if product_type[ship_type] == 2:
                    awb_objs = [COD.objects.create()]
                if product_type[ship_type] == 3:
                    awb_objs = [ReversePickup.objects.create()]
            else:
                if product_type[ship_type] == 1:
                    awb_start = PPD.objects.latest('id').id + 1
                    awb_total_ids = [PPD(id=i) for i in range(awb_start, int(awb_start) + count)]
                    awb_objs = PPD.objects.bulk_create(awb_total_ids)
                if product_type[ship_type] == 2:
                    awb_start = COD.objects.latest('id').id + 1
                    awb_total_ids = [COD(id=i) for i in range(awb_start, int(awb_start) + count)]
                    awb_objs = COD.objects.bulk_create(awb_total_ids)
                if product_type[ship_type] == 3:
                    awb_start = ReversePickup.objects.latest('id').id + 1
                    awb_total_ids = [ReversePickup(id=i) for i in range(awb_start, int(awb_start) + count)]
                    awb_objs = ReversePickup.objects.bulk_create(awb_total_ids)
            awb_ids = [a.id for a in awb_objs]
            airs = [AirwaybillNumbers(airwaybill_number=a) for a in awb_ids]
            awbs = AirwaybillNumbers.objects.bulk_create(airs)
            awb_nums = [a.airwaybill_number for a in awbs]
            awb_objs = AirwaybillNumbers.objects.filter(airwaybill_number__in=awb_nums)
            awbc.airwaybill_number.set(awb_objs)
            #awbc.save()                        
            data = {"success":True,"awb" : awb_nums,"message":"successfully generated"} 
            return Response(data,status=status.HTTP_201_CREATED)
