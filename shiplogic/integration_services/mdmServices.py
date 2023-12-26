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
from location.models import *
from api.utils import validateJsonSchema

#zone_list = [str(zone).lower() for zone in Zone.objects.all().values_list('zone_shortcode',flat=True)]
#region_list = [str(region).lower() for region in Region.objects.all().values_list('region_shortcode',flat=True)]

mdmSchema = {
          "type":"object",
          "properties":{
              "mdm_type":{"type":"string","enum": ["state","servicecenter","city","pincode"]}
              },
          "required":["mdm_type",]
        }

stateCreationSchema = {
     "type": "object",
     "properties": {
         "state_name":{"type": "string","minLength":1},
         "state_shortcode":{"type": "string","minLength":1},
     },
     "required": ["state_shortcode", "state_name"]

}


cityCreationSchema = {
     "type": "object",
     "properties": {
         "city_name":{"type": "string","minLength":1},
         "city_shortcode":{"type": "string","minLength":1},
         "state_shortcode":{"type": "string","minLength":1},
         "zone_shortcode":{"type": "string","minLength":1},
         "region_shortcode":{"type": "string","minLength":1},
         "city_type":{"type": "integer"},
     },
     "required": ["city_name", "city_shortcode","state_shortcode","zone_shortcode","region_shortcode","city_type"]

}


serviceCenterCreationSchema = {
     "type": "object",
     "properties": {
         "center_name":{"type": "string","minLength":1},
         "center_shortcode":{"type": "string","minLength":1},
         "state_shortcode":{"type": "string","minLength":1},
         "city_shortcode":{"type": "string","minLength":1},
         "service_type":{"type": "integer","enum": [0,1,2,3,4]},
         "status":{"type": "integer","enum": [0,1,2]},
         "address": {
             "type": "object",
             "properties": {
               "address1": {
                 "type": "string",
                 "minLength":1
               },
               "address2": {
                 "type": "string",
                 "minLength":1
               },
               "pincode":{
                   "type":"integer"
                },
               "phone":{
                   "type":"integer"
                   }
             },
             "required": ["address1","address2","pincode","phone"]
         }    
     },
     "required": ["center_name", "center_shortcode","city_shortcode","service_type","status","address"]

}


pincodeCreationSchema = {
     "type": "object",
     "properties": {
         "pincode":{"type": "integer","minimum":1},
         "sc_shortcode":{"type": "string","minLength":1},
         "pickup_sc_shortcode":{"type": "string","minLength":1},
         "return_sc_shortcode":{"type": "string","minLength":1},
         "status":{"type": "integer","enum":[0,1]},
         "city_shortcode":{"type": "string","minLength":1},
         "sdl":{"type":"integer","enum":[0,1]},
         "zone_shortcode":{"type":"string","minLength":1},
         "reverse_sc_shortcode":{"type":"string","minLength":1},
         "route":{"type":"string"},
         "org_cluster":{"type":"string"},
         "dest_cluster":{"type":"string"},
     },
     "required": ["pincode", "sc_shortcode","pickup_sc_shortcode","return_sc_shortcode","status","city_shortcode","sdl","zone_shortcode","reverse_sc_shortcode","route","org_cluster","dest_cluster"]

}

serviceCenterTypes = {"0":"Service Center","1":"HUB","2":"Head Quarter","3":"Processing Centre"}

class MDMAPI(APIView):
    def get(self,request):
        data = request.data
        mdm_type = data.get('mdm_type')
        response,message = validateJsonSchema(request.data,mdmSchema)
        if not response:
            data = {"success":False,"message":message}
            return Response(data)

        if mdm_type == 'state':
            state_data_dict = {}
            state_data_list = []
            for state in State.objects.all().values('state_name','state_shortcode'):
                state_dict = {}
                state_dict['state_name'] = state.get('state_name')
                state_dict["state_shortcode"] = state.get('state_shortcode')
                state_data_list.append(state_dict)

            state_data_dict["success"] = True
            state_data_dict["data"] = state_data_list
            return Response(state_data_dict)

        if mdm_type == "city":
            city_data_dict = {}
            city_data_list = []
            for city in City.objects.all().values('city_name','city_shortcode','state__state_name','zone__zone_name','region__region_name','city_type'):
                city_dict = {}
                city_dict['city_name'] = city.get('city_name')
                city_dict['city_shortcode'] = city.get('city_shortcode')
                city_dict['state_name'] = city.get('state__state_name')
                city_dict['zone_name'] = city.get('zone__zone_name')
                city_dict['region_name'] = city.get('region__region_name')
                city_dict['city_type'] = city.get('city_type')
                city_data_list.append(city_dict)
            
            city_data_dict["success"] = True
            city_data_dict["data"] = city_data_list
            return Response(city_data_dict)
        

        if mdm_type == "servicecenter":
            sc_data_dict = {}
            sc_data_list = []
            for sc in ServiceCenter.objects.all().values('center_name','center_shortcode','city__city_name','city__state__state_name','service_type'):
                sc_dict = {}
                sc_dict['center_shortcode'] = sc.get('center_shortcode')
                sc_dict['center_name'] = sc.get('center_name')
                sc_dict['city_name'] = sc.get('city__city_name')
                sc_dict['state_name'] = sc.get('city__state__state_name')
                sc_type = sc.get('service_type')
                sc_dict['service_type'] = serviceCenterTypes.get(sc_type,"")
                sc_data_list.append(sc_dict)

            sc_data_dict["success"] = True
            sc_data_dict["data"] = sc_data_list
            return Response(sc_data_dict)    

    def post(self,request):

        data = request.data
        mdm_type = data.get('mdm_type','')
        response,message = validateJsonSchema(request.data,mdmSchema)
        if not response:
            data = {"success":False,"message":message}
            return Response(data)


        mdm_type = data.get('mdm_type') 
        data_list = data.get('data_list')

        if mdm_type == 'state':
            state_list = []
            for data in data_list:
                try:
                    response,message = validateJsonSchema(data,stateCreationSchema)
                    if not response:
                        response_data = {"success":False,"message":message}
                        state_list.append(response_data)
                        continue

                    state_code = data.get('state_shortcode')
                    state_name = data.get('state_name')

                    if State.objects.filter(state_shortcode__iexact=state_code):
                        State.objects.filter(state_shortcode__iexact=state_code).update(state_name=state_name)
                    else:
                        State.objects.create(state_shortcode=state_code,state_name=state_name)
                    
                    response_data = {"success":True,"message":"State : {0} is added successfully.".format(state_name)}
                    state_list.append(response_data)

                except Exception as e:
                   response_data = {"success":False,"message":e}
                   state_list.append(response_data)
 
            data = {"success":True,"message":"State updated successfully.Please check response data","response_data":state_list}
            return Response(data)

        
        if mdm_type == 'city':
            city_list = []
            for data in data_list:
                try:
                    response,message = validateJsonSchema(data,cityCreationSchema)
                    if not response:

                        response_data = {"success":False,"message":message}
                        city_list.append(response_data)
                        #return Response(data)
                        continue

                    city_name = data.get("city_name")
                    city_shortcode = data.get("city_shortcode")
                    state_shortcode = data.get("state_shortcode")
                    zone_shortcode = data.get("zone_shortcode")
                    region_shortcode = data.get("region_shortcode")
                    city_type = data.get("city_type")
                    if not State.objects.filter(state_shortcode__iexact=state_shortcode):
                        message = "State shortcode : {0} is not available in the system".format(state_shortcode)
                        response_data = {"success":False,"message":message}
                        city_list.append(response_data)
                        #return Response(data)
                        continue

                    state = State.objects.filter(state_shortcode__iexact=state_shortcode).latest('id')
                    if not Zone.objects.filter(zone_shortcode__iexact=zone_shortcode):
                        
                        message = "Zone :[0] is not available in the system".format(zone_shortcode)
                        response_data = {"success":False,"message":message}
                        #return Response(data)
                        city_list.append(response_data)
                        continue

                    if not Region.objects.filter(region_shortcode__iexact=region_shortcode):
                        message = "Region :{0} is not available in the system".format(region_shortcode)
                        response_data = {"success":False,"message":message}
                        #return Response(data)
                        city_list.append(response_data)
                        continue

                    zone = Zone.objects.filter(zone_shortcode__iexact=zone_shortcode).latest('id')
                    region = Region.objects.filter(region_shortcode__iexact=region_shortcode).latest('id')
                    if City.objects.filter(city_shortcode__iexact=city_shortcode):
                        City.objects.filter(city_shortcode=city_shortcode).update(city_name=city_name,state=state,zone=zone,region=region,city_type=city_type,category_id=1)

                    else:
                        City.objects.create(city_shortcode=city_shortcode,city_name=city_name,state=state,zone=zone,region=region,city_type=city_type,category_id=1)

                    message = "City :{0} added successfully.".format(city_name) 
                    response_data = {"success":True,"message":message}
                    city_list.append(response_data)

                except Exception as e:
                    message = str(e)
                    response_data = {"success":False,"message":message}
                    city_list.append(response_data)

            message = "City added successfully.Please check response data"
            data = {"success":True,"message":message,"response_data":city_list}
            return Response(data)
 

        if mdm_type == 'servicecenter':
            print(request.data)
            sc_list = []
            for data in data_list:
                try:
                    response,message = validateJsonSchema(data,serviceCenterCreationSchema)
                    if not response:
                        response_data = {"success":False,"message":message}
                        sc_list.append(response_data)
                        continue

                    center_name = data.get('center_name')
                    center_shortcode = data.get('center_shortcode')
                    address = data.get('address')
                    city_shortcode = data.get('city_shortcode')
                    service_type = data.get('service_type')
                    status = data.get('status')
                    address1 = address.get('address1')
                    address2 = address.get('address2')
                    address3 = address.get('address3',"")
                    address_pincode = address.get("pincode")
                    address_phone = address.get('phone')
                    if not City.objects.filter(city_shortcode__iexact=city_shortcode):
                        message = "City  : {0} is not available in the system".format(city_shortcode)
                        response_data = {"success":False,"message":message}
                        sc_list.append(response_data)
                        continue
   

                    city = City.objects.get(city_shortcode__iexact=city_shortcode)
                    state = city.state
                    address = Address.objects.create(address1=address1,address2=address2,address3=address3,city = city,state=state,pincode=address_pincode,phone=address_phone)
                    
                    if not ServiceCenter.objects.filter(center_shortcode__iexact=center_shortcode):
                        ServiceCenter.objects.create(center_shortcode=center_shortcode,center_name=center_name,address=address,city=city,service_type=service_type,status=status)
                        
                    else:
                        ServiceCenter.objects.filter(center_shortcode=center_shortcode).update(center_name=center_name,address=address,city=city,service_type=service_type,status=status)

                    message = "Service Center :{0} updated successfully".format(center_name) 
                    response_data = {"success":True,"message":message}
                    sc_list.append(response_data)

                except Exception as e:
                    message = str(e)
                    response_data = {"success":False,"message":message}
                    sc_list.append(response_data)

            message = "Service Center updated successfully.Please check response data"
            data = {"success":True,"message":message,"response_data":sc_list}
            return Response(data)
   

        if mdm_type == 'pincode':
            pincode_list = []

            for data in data_list:
                try:
                    response,message = validateJsonSchema(data,pincodeCreationSchema)
                    if not response:
                        response_data = {"success":False,"message":message}
                        pincode_list.append(response_data)
                        continue

                    pincode = data.get("pincode")
                    sc_shortcode = data.get('sc_shortcode')
                    pickup_sc_shortcode = data.get("pickup_sc_shortcode")
                    return_sc_shortcode = data.get("return_sc_shortcode")
                    status = data.get("status")
                    sdl = data.get('sdl')
                    city_shortcode = data.get("city_shortcode")
                    zone_shortcode = data.get('zone_shortcode')
                    reverse_sc_shortcode = data.get('reverse_sc_shortcode')
                    route = data.get('route')
                    org_cluster = data.get('org_cluster')
                    dest_cluster = data.get('dest_cluster')

                    if not ServiceCenter.objects.filter(center_shortcode__iexact=sc_shortcode):
                        message = "No Service Center : {0} is available".format(sc_shortcode)
                        response_data = {"success":False,"message":message}
                        pincode_list.append(response_data)
                        continue

                    if not ServiceCenter.objects.filter(center_shortcode__iexact=pickup_sc_shortcode):
                        message = "No Service Center : {0} is available".format(pickup_sc_shortcode)
                        response_data = {"success":False,"message":message}
                        pincode_list.append(response_data)
                        continue

                    if not ServiceCenter.objects.filter(center_shortcode__iexact=return_sc_shortcode):
                        message = "No Service Center : {0} is available".format(return_sc_shortcode)
                        response_data = {"success":False,"message":message}
                        pincode_list.append(response_data)
                        continue

                    if not ServiceCenter.objects.filter(center_shortcode__iexact=reverse_sc_shortcode):
                        message = "No Service Center : {0} is available".format(reverse_sc_shortcode)
                        response_data = {"success":False,"message":message}
                        pincode_list.append(response_data)
                        continue


                    if not City.objects.filter(city_shortcode__iexact=city_shortcode):
                        message = "No City : {0} is available".format(city_shortcode)
                        response_data = {"success":False,"message":message}
                        pincode_list.append(response_data)
                        continue


                    if not Zone.objects.filter(zone_shortcode__iexact=zone_shortcode):
                        message = "No Zone : {0} is available".format(zone_shortcode)
                        response_data = {"success":False,"message":message}
                        pincode_list.append(response_data)
                        continue


                    sc = ServiceCenter.objects.filter(center_shortcode__iexact=sc_shortcode).latest('id')
                    pickup_sc = ServiceCenter.objects.filter(center_shortcode__iexact=pickup_sc_shortcode).latest('id')
                    return_sc = ServiceCenter.objects.filter(center_shortcode__iexact=return_sc_shortcode).latest('id')
                    reverse_sc = ServiceCenter.objects.filter(center_shortcode__iexact=reverse_sc_shortcode).latest('id')

                    city = City.objects.filter(city_shortcode__iexact=city_shortcode).latest('id')
                    zone = Zone.objects.filter(zone_shortcode__iexact=zone_shortcode).latest('id')

                    if not Pincode.objects.filter(pincode=pincode):
                        Pincode.objects.create(pincode=pincode,service_center=sc,pickup_sc=pickup_sc,return_sc=return_sc,
                                status=status,sdl=sdl,city=city,zone=zone,reverse_sc=reverse_sc,route=route,
                                org_cluster=org_cluster,dest_cluster=dest_cluster)
                    else:
                        Pincode.objects.filter(pincode=pincode).update(service_center=sc,pickup_sc=pickup_sc,return_sc=return_sc,\
                                status=status,sdl=sdl,city=city,zone=zone,reverse_sc=reverse_sc,route=route,\
                                org_cluster=org_cluster,dest_cluster=dest_cluster)

                    message = "Pincode :{0} added successfully".format(pincode)
                    response_data = {"success":True,"message":message}
                    pincode_list.append(response_data)
                
   
                except Exception as e:
                    message = e
                    response_data = {"success":False,"message":message}
                    pincode_list.appned(response_data)

            message = "Pincode updated successfully.Please check response data"
            data = {"success":True,"message":message,"response_data":pincode_list}
            return Response(data)
