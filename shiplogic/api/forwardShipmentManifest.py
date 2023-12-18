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
import random
import string
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
from servicecenter.models import Shipment
from api.manifest_validation import ManifestAPIValidation
from integration_services.models import ManifestAPIConfiguration
from customer.models import CustomerAdditionalInformation
from rest_framework import status
from location.models import Pincode,State
import re
from servicecenter.transitmaster import get_expected_dod 
from api.views import validate_awb,pincode_pickup_create
sql_inject_symbols = ['=', '%', '#', ' OR ', ' AND ', ' or ', ' and ', '>', '<', '\?','"']

 
shipmentManifestSchema ={
        "type": "object",
     "properties": {
         "AWB_NUMBER":{"type": "string"},
         "ORDER_NUMBER":{"type": "string"},
         "CONSIGNEE":{"type": "string"},
         "CONSIGNEE_ADDRESS1":{"type": "string"},
         "CONSIGNEE_ADDRESS2":{"type": "string"},
         "CONSIGNEE_ADDRESS3":{"type": "string"},
         "DESTINATION_CITY":{"type": "string"},
         "PINCODE":{"type": "string"},
         "STATE":{"type": "string"},
         "MOBILE":{"type": "string","minLength":10,"maxLength":12},
         "TELEPHONE":{"type": "string","minLength":10,"maxLength":12},
         "ITEM_DESCRIPTION":{"type": "string"},
         "COLLECTABLE_VALUE":{"type": "integer", "minimum":0,"maximum":200000},
         "DECLARED_VALUE":{"type": "integer", "minimum":0},
         "ACTUAL_WEIGHT":{"type": "number","minimum": 1},
         "VOLUMETRIC_WEIGHT":{"type": "number","minimum": 1},
         "LENGTH":{"type": "number","minimum": 1},
         "BREADTH":{"type": "number","minimum": 1},
         "HEIGHT":{"type": "number","minimum": 1},
         "PICKUP_NAME":{"type": "string"},
         "PICKUP_ADDRESS_LINE1":{"type": "string"},
         "PICKUP_ADDRESS_LINE2":{"type": "string"},
         "PICKUP_PINCODE":{"type": "string"},
         "PICKUP_PHONE":{"type": "string","minLength":10,"maxLength":12},
         "PICKUP_MOBILE":{"type": "string","minLength":10,"maxLength":12},
         "RETURN_NAME":{"type": "string"},
         "RETURN_ADDRESS_LINE1":{"type": "string"},
         "RETURN_ADDRESS_LINE2":{"type": "string"},
         "RETURN_PINCODE":{"type": "string"},
         "RETURN_PHONE":{"type": "string","minLength":10,"maxLength":12},
         "RETURN_MOBILE":{"type": "string","minLength":10,"maxLength":12},
         "PRODUCT":{"type": "string","enum": ['cod','ppd','rev']},
     },
     
     "required": ["AWB_NUMBER", "ORDER_NUMBER", "PRODUCT", "CONSIGNEE", "CONSIGNEE_ADDRESS1", "CONSIGNEE_ADDRESS2", "CONSIGNEE_ADDRESS3", "DESTINATION_CITY", "PINCODE", "STATE", "MOBILE", "TELEPHONE", "ITEM_DESCRIPTION", "PIECES", "COLLECTABLE_VALUE", "DECLARED_VALUE", "ACTUAL_WEIGHT", "VOLUMETRIC_WEIGHT", "LENGTH", "BREADTH", "HEIGHT", "PICKUP_NAME", "PICKUP_ADDRESS_LINE1", "PICKUP_ADDRESS_LINE2", "PICKUP_PINCODE", "PICKUP_PHONE", "PICKUP_MOBILE", "RETURN_NAME", "RETURN_ADDRESS_LINE1", "RETURN_ADDRESS_LINE2", "RETURN_PINCODE", "RETURN_PHONE", "RETURN_MOBILE"]


        }


class ForwardManifestion(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        print ("=======",request.__dict__)
        try:
            """
            This is the manifest API.
            """
            response_awb = {}
            response_awb["shipments"] = []
            awb_validation = {}
            awb_validation["awb"] = ""
            awb_validation["order_number"] = ""
            awb_validation["success"] = False
            awb_validation["reason"] = ""

            user = request.user
            manifestQueuestatus = 0
            awb_overweight=[]

            if not user.employeemaster.customer:
                awb_validation["reason"] = "No Customer assosiate with the auth token"
                response_awb["shipments"].append(awb_validation)
                return Response(response_awb,status=status.HTTP_400_BAD_REQUEST)
            
            capi = user.employeemaster

            ##### For Allowed Customers  #####
            manifestValidation = ManifestAPIValidation(customerId = capi.customer_id)
            manifestValidationResp = manifestValidation.validateCustomerManifest(processType = "FWD_MANIFEST_ALLOWED")
            if not manifestValidationResp["success"]:
                awb_validation["reason"] = ""+str(manifestValidationResp["message"])
                response_awb["shipments"].append(awb_validation)

                return Response(response_awb,status=status.HTTP_400_BAD_REQUEST)

            ##################################
            dict_shipments = request.data
            nextday_delivery = ''
            if CustomerAdditionalInformation.objects.filter(customer = capi.customer, add_info_key = 'queueBasedManifest', add_info_value = 'Yes'):
                    manifestQueuestatus = -1

            #ManifestSyncQueue.objects.create(service_type = 'FWD', customer_id = capi.customer_id, requestPayload = dict_shipments, status = manifestQueuestatus)

            #awb_validation = {}

            for awb_details in dict_shipments:
                preferred_date=None
                preferred_delivery=False
                transport_type=0
                essentialProduct = True if ManifestAPIConfiguration.objects.filter(configuration_key = 'ADHOC_CITY_VALIDATION', configuration_value = 'True') and ManifestAPIConfiguration.objects.filter(configuration_key = 'ADHOC_CITY_VALIDATION', configuration_value = 'True') else False#Will have to build logic to enable this post lockdown

                awb_validation = {}
                try:
                    int(awb_details["AWB_NUMBER"])  ################ should be checked in schema validation
                    if not AirwaybillNumbers.objects.filter(airwaybill_number=awb_details["AWB_NUMBER"], awbc_info__customer_id = capi.customer_id):
                        awb_validation["awb"] = awb_details["AWB_NUMBER"]
                        awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                        awb_validation["success"] = False
                        awb_validation["reason"] = "INCORRECT_AWB_NUMBER"
                        response_awb["shipments"].append(awb_validation)
                        continue

                    if Shipment.objects.filter(airwaybill_number=awb_details["AWB_NUMBER"]):
                        awb_validation["awb"] = awb_details["AWB_NUMBER"]
                        awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                        awb_validation["success"] = False
                        awb_validation["reason"] = "Airwaybill is already in used."
                        response_awb["shipments"].append(awb_validation)
                        continue

                except:
                    awb_validation["awb"] = awb_details["AWB_NUMBER"]
                    awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                    awb_validation["success"] = False
                    awb_validation["reason"] = "AWB_NUMBER should be in digits only : {0}".format(awb_details["AWB_NUMBER"])
                    response_awb["shipments"].append(awb_validation)
                    continue

                if not ManifestAPIConfiguration.objects.filter(configuration_key = 'ADHOC_CITY_VALIDATION', configuration_value = 'True') and not ManifestAPIConfiguration.objects.filter(configuration_key = 'PINCODE_VIRTUAL_DC_VALIDATION', configuration_value = 'True'):
                    pickupPincode = awb_details["PICKUP_PINCODE"]
                    destinationPincode = awb_details["PINCODE"]
                    #validate inbound/outbound pincodes
                    essentials = False
                    if "ADDITIONAL_INFORMATION" in awb_details:
                        essentials_prod = awb_details.get("ADDITIONAL_INFORMATION").get("essentialProduct", None)
                        if essentials_prod and essentials_prod == "Y":
                            essentials = True
                    validateInboundOutboundResponse = manifestValidation.validateIoPincodeServiceability(pickupPincode = pickupPincode, destinationPincode = destinationPincode, customer = capi.customer, essentials = essentials, awb = awb_details["AWB_NUMBER"])
                    if not validateInboundOutboundResponse[0]:
                        awb_validation["awb"] = awb_details["AWB_NUMBER"]
                        awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                        awb_validation["success"] = False
                        awb_validation["reason"] = validateInboundOutboundResponse[1]
                        response_awb["shipments"].append(awb_validation)
                        continue

                #Adhoc validations
                #print "Adhoc validations --- ", awb_details["PICKUP_PINCODE"], awb_details["PINCODE"]
                if ManifestAPIConfiguration.objects.filter(configuration_key = 'ADHOC_CITY_VALIDATION', configuration_value = 'True'):
                    pickupPincode = awb_details["PICKUP_PINCODE"]
                    destinationPincode = awb_details["PINCODE"]
                    #call class
                    adhocValidationResponse = manifestValidation.validateAdhocCityMapping(pickupPincode = pickupPincode, destinationPincode = destinationPincode, essentialProduct = essentialProduct)
                    if not adhocValidationResponse[0]:
                        awb_validation["awb"] = awb_details["AWB_NUMBER"]
                        awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                        awb_validation["success"] = False
                        awb_validation["reason"] = adhocValidationResponse[1]
                        response_awb["shipments"].append(awb_validation)
                        continue



                if any(re.findall('|'.join(sql_inject_symbols), awb_details["ORDER_NUMBER"])):
                    awb_validation["awb"] = awb_details["AWB_NUMBER"]
                    awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                    awb_validation["success"] = False
                    awb_validation["reason"] = "Invalid Value for ORDER_NUMBER!"
                    response_awb["shipments"].append(awb_validation)
                    continue
                if not awb_details["CONSIGNEE"]:  ########### should be handle in schema validation
                    awb_validation["awb"] = awb_details["AWB_NUMBER"]
                    awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                    awb_validation["success"] = False
                    awb_validation["reason"] = "CONSIGNEE not provided!"
                    response_awb["shipments"].append(awb_validation)
                    continue
                if not awb_details["ITEM_DESCRIPTION"]: ###################### should be handle in schema validation
                    awb_validation["awb"] = awb_details["AWB_NUMBER"]
                    awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                    awb_validation["success"] = False
                    awb_validation["reason"] = "ITEM_DESCRIPTION not provided!"
                    response_awb["shipments"].append(awb_validation)
                    continue
                product_type = awb_details["PRODUCT"]
                product_type = product_type.lower()
                if product_type == 'ppd' and float(awb_details["COLLECTABLE_VALUE"]) > 0.0:
                    awb_validation["awb"] = awb_details["AWB_NUMBER"]
                    awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                    awb_validation["success"] = False
                    awb_validation["reason"] = "PPD_COLLECTABLE_VALUE_SHOULD_BE_ZERO!"
                    response_awb["shipments"].append(awb_validation)
                    continue
                if float(awb_details["COLLECTABLE_VALUE"]) < 0.0:   ############## should be handle in schema validation
                    awb_validation["awb"] = awb_details["AWB_NUMBER"]
                    awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                    awb_validation["success"] = False
                    awb_validation["reason"] = "COLLECTABLE_VALUE_SHOULD_NOT_BE_LESS_THEN_ZERO!"
                    response_awb["shipments"].append(awb_validation)
                    continue

                if product_type == 'cod' and float(awb_details["COLLECTABLE_VALUE"]) == 0.0: ############# should be handle in schema validation
                    awb_validation["awb"] = awb_details["AWB_NUMBER"]
                    awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                    awb_validation["success"] = False
                    awb_validation["reason"] = "COD_COLLECTABLE_VALUE_SHOULD_NOT_BE_ZERO!"
                    response_awb["shipments"].append(awb_validation)
                    continue


                if float(awb_details["DECLARED_VALUE"]) <= 0.0:
                    awb_validation["awb"] = awb_details["AWB_NUMBER"]   ############## should be handle in schema validation
                    awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                    awb_validation["success"] = False
                    awb_validation["reason"] = "DECLARE_VALUE_CAN_NOT_BE_LESS_THEN_ZERO_OR_EQUAL_TO_ZERO!"
                    response_awb["shipments"].append(awb_validation)
                    continue
                customerEwaybillExemption = False
                if capi.customer:
                   cust_code = capi.customer.code
                   if cust_code in []:
                      customerEwaybillExemption = True
                if float(awb_details["DECLARED_VALUE"]) > 49999.0 and not "ADDITIONAL_INFORMATION" in awb_details and not customerEwaybillExemption:
                    awb_validation["awb"] = awb_details["AWB_NUMBER"]
                    awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                    awb_validation["success"] = False
                    awb_validation["reason"] = "Ewaybill Data required!"
                    response_awb["shipments"].append(awb_validation)
                    continue
                intraStateExemption=False
                hsnCodeExemption = False
                if awb_details.get("ADDITIONAL_INFORMATION") and float(awb_details["DECLARED_VALUE"]) > 49999.0:
                    
                   if not awb_details["ADDITIONAL_INFORMATION"].get("MULTI_SELLER_INFORMATION",''):
                      add_info = awb_details["ADDITIONAL_INFORMATION"]
                      dec_value = float(awb_details["DECLARED_VALUE"])
                      delivery_pincode = int(awb_details["PINCODE"])
                      delPin = Pincode.objects.filter(pincode=int(delivery_pincode))
                      pickup_pincode = awb_details["PICKUP_PINCODE"]
                      pickPin = Pincode.objects.filter(pincode=int(pickup_pincode))
                      if pickPin and delPin:
                         pickState = pickPin[0].service_center.city.state_id
                         delState = delPin[0].service_center.city.state_id
                         #if (pickState == delState and pickState in [1,2,6,13,14,16,7] and float(awb_details["DECLARED_VALUE"]) < 100000.0):
                         if (pickState == delState and State.objects.get(id = pickState).stateadditionalinformation_set.filter(add_info_key = 'shipment_waybill_limit',add_info_value = "True") and float(awb_details["DECLARED_VALUE"]) < 100000.0):
                             intraStateExemption = True
                      #customerEwaybillExemption = False
                      #if capi.customer:
                      #   cust_code = capi.customer.code
                      #   if cust_code in ["83809","32012"]:
                      #      customerEwaybillExemption = True
                      hsnCode = add_info.get("GST_HSN","")
                      if hsnCode:
                         hsncode = str(hsnCode)
                         if hsncode.startswith(("71","9601","0508")):
                            hsnCodeExemption = True
                      if dec_value > 49999.0 and not customerEwaybillExemption and not intraStateExemption and not hsnCodeExemption:
                         if not CustomerAdditionalInformation.objects.filter(add_info_key = "ewaybill_exempt",add_info_value = "True",customer_id = capi.customer.id): 
                            if not add_info["SELLER_GSTIN"]:
                               awb_validation["awb"] = awb_details["AWB_NUMBER"]
                               awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                               awb_validation["success"] = False
                               awb_validation["reason"] = "SELLER_GSTIN not provided!"
                               response_awb["shipments"].append(awb_validation)
                               continue
                            if not add_info["INVOICE_NUMBER"]:
                               awb_validation["awb"] = awb_details["AWB_NUMBER"]
                               awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                               awb_validation["success"] = False
                               awb_validation["reason"] = "INVOICE_NUMBER not provided!"
                               response_awb["shipments"].append(awb_validation)
                               continue
                            if not add_info["INVOICE_DATE"]:
                               awb_validation["awb"] = awb_details["AWB_NUMBER"]
                               awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                               awb_validation["success"] = False
                               awb_validation["reason"] = "INVOICE_DATE not provided!"
                               response_awb["shipments"].append(awb_validation)
                               continue
                            if not add_info.get("GST_HSN",""):
                               awb_validation["awb"] = awb_details["AWB_NUMBER"]
                               awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                               awb_validation["success"] = False
                               awb_validation["reason"] = "GST_HSN not provided!"
                               response_awb["shipments"].append(awb_validation)
                               continue
                            if not add_info["GST_ERN"]:
                               awb_validation["awb"] = awb_details["AWB_NUMBER"]
                               awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                               awb_validation["success"] = False
                               awb_validation["reason"] = "GST_ERN not provided!"
                               response_awb["shipments"].append(awb_validation)
                               continue
                            if add_info.get("GST_ERN") and len(add_info.get("GST_ERN",'')) != 12:
                               awb_validation["awb"] = awb_details["AWB_NUMBER"]
                               awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                               awb_validation["success"] = False
                               awb_validation["reason"] = "GST_ERN should be 12 digit!"
                               response_awb["shipments"].append(awb_validation)
                               continue

                      
                   
                ################ This should be removed

                awb_validation_response = validate_awb([str(capi.customer_id),awb_details["AWB_NUMBER"], awb_details["PINCODE"], awb_details["PICKUP_PINCODE"], awb_details["RETURN_PINCODE"], awb_details["ACTUAL_WEIGHT"], awb_details["PRODUCT"], awb_details["COLLECTABLE_VALUE"]])#,awb_details["LENGTH"],awb_details["BREADTH"],awb_details["HEIGHT"],awb_details["DECLARED_VALUE"],awb_details["PIECES"],awb_details["AWB_NUMBER"]])

                print("awb_validation_response===",awb_validation_response)
                seller_validation_response = '' #MULTISELLER
                multi_seller_status = False #MULTISELLER
                awb_num = AirwaybillNumbers.objects.filter(airwaybill_number=awb_details["AWB_NUMBER"], awbc_info__customer_id = capi.customer_id)
                #preferred_delivery
                try:
                   pref_del = awb_details["PREFERRED_FLAG"]
                   time_slot = awb_details["PREFERRED_TIME"]
                except:
                   pref_del = False
                if pref_del: ############ should be check
                    try:
                        timefrom=0
                        timeto=0
                        if pref_del=="true":
                            mode=2
                            if time_slot=="0800-0900": 
                                timefrom="08:00"
                                timeto="09:00"
                            elif time_slot=="0900-1200": 
                                timefrom="09:00"
                                timeto="12:00"
                            elif time_slot=="1200-1500":
                                timefrom="12:00"
                                timeto="15:00"
                            elif time_slot=="1500-1800":
                                timefrom="15:00"
                                timeto="18:00"
                            elif time_slot=="1800-2000":
                                timefrom="18:00"
                                timeto="20:00"
                            else:
                                awb_validation["awb"] = awb_details["AWB_NUMBER"]
                                awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                                awb_validation["success"] = False
                                awb_validation["reason"] = "incorrect_delivery_time_slot"
                                response_awb["shipments"].append(awb_validation)
                                continue
                        time_from= datetime.strptime(timefrom,'%H:%M').time()
                        time_to= datetime.strptime(timeto,'%H:%M').time()
                    except:
                        awb_validation["awb"] = awb_details["AWB_NUMBER"]
                        awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                        awb_validation["success"] = False
                        awb_validation["reason"] = "incorrect_preferred_details"
                        response_awb["shipments"].append(awb_validation)
                        continue
          
                #dg_goods
                if str(awb_details.get("DG_SHIPMENT",'')).lower() in ["true","yes"] and ServiceCenterAdditionalInformation.objects.filter(sc_id = Pincode.objects.get(pincode=awb_details["PINCODE"], status__in = [1, 2, 3]).service_center_id, add_info_key = 'BLOCK_DG', add_info_value = 'True', activation_status = True):
                    awb_validation["awb"] = awb_details["AWB_NUMBER"]
                    awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                    awb_validation["success"] = False
                    awb_validation["reason"] = "DG Shipments not allowed at Pincode : %s"%(awb_details["PINCODE"])
                    response_awb["shipments"].append(awb_validation)
                    continue
                try:
                    #if awb_details["DG_SHIPMENT"]=="true":
                    defaultDgCustomers = [int(i) for i in DGConfig.objects.filter(customer__isnull = False, status = 1, keyword = 'DEFAULT_DG').values_list('customer_id',flat=True)]
                    if ((str(awb_details.get("DG_SHIPMENT",'')).lower() in ["true","yes"]) or (AirwaybillNumbers.objects.filter(airwaybill_number = awb_details["AWB_NUMBER"], awbc_info__type__in = [10,11])) or (capi.customer_id in defaultDgCustomers)) and not ServiceCenterAdditionalInformation.objects.filter(sc_id = Pincode.objects.get(pincode=awb_details["PINCODE"], status__in = [1, 2, 3]).service_center_id, add_info_key = 'BLOCK_DG', add_info_value = 'True', activation_status = True):
                        transport_type=1
                    else:
                        transport_type=0
                except:
                    transport_type=0
                #print  "MULTISELL testing", awb_details["AWB_NUMBER"], awb_validation_response

                if awb_validation_response["SUCCESS"]:
                    
                    awb_validation["awb"] = awb_details["AWB_NUMBER"]
                    awb_validation["order_number"] = awb_details["ORDER_NUMBER"] 
                    awb_validation["success"] = True
                    awb_validation["reason"] = "Updated Successfully" 

                    airwaybill_num =  int(awb_details["AWB_NUMBER"])

                    
                    pickup_data, error = pincode_pickup_create(awb_details, capi, 0)
                    if error:
                        return HttpResponse(str(error))            
                    pickup = pickup_data.get(awb_details["PICKUP_PINCODE"])

                    order_num = repr(awb_details["ORDER_NUMBER"][0:20])
                    product_type = awb_details["PRODUCT"]
                    product_type = product_type.lower()
                    product_type = product_type.strip()

                    shipper = pickup.customer_code

                    consignee = awb_details["CONSIGNEE"]
                    consignee_address1 = awb_details["CONSIGNEE_ADDRESS1"]
                    consignee_address2 = awb_details["CONSIGNEE_ADDRESS2"]
                    consignee_address3 = awb_details["CONSIGNEE_ADDRESS3"]
                            
                    destination_city = awb_details["DESTINATION_CITY"]
                    pincode = awb_details["PINCODE"]
                    state = awb_details["STATE"]
                    #awb_details["MOBILE"] = filter(lambda x: x.isdigit(), awb_details["MOBILE"])[-10:]
                    awb_details["MOBILE"] = "".join(list(filter(lambda x: x.isdigit(), awb_details["MOBILE"]))[-10:])  #### review,logic change in python 3 for filter
                    mobile = awb_details["MOBILE"] if awb_details["MOBILE"] else 0
                    telephone = awb_details["TELEPHONE"]
                    item_description = awb_details["ITEM_DESCRIPTION"]
                    pieces = awb_details["PIECES"]
                    collectable_value = awb_details["COLLECTABLE_VALUE"] if awb_details["COLLECTABLE_VALUE"] else 0
                    try:
                            int(collectable_value)
                    except ValueError:
                            collectable_value = collectable_value.replace(",", "")
                    ppd_ship = AirwaybillNumbers.objects.filter(airwaybill_number = airwaybill_num)
                    if ppd_ship: #######3should be checked
                        ppd_ship = ppd_ship[0]
                        ppd_ship = ppd_ship.awbc_info.get()
                        if int(ppd_ship.type) == 1:
                            collectable_value = collectable_value

                    declared_value = awb_details["DECLARED_VALUE"] if awb_details["DECLARED_VALUE"] else 0
                    try:
                            int(declared_value)
                    except ValueError:
                          declared_value = declared_value.replace(",", "")
         
                    actual_weight = awb_details["ACTUAL_WEIGHT"]
                    volumetric_weight = awb_details["VOLUMETRIC_WEIGHT"] if awb_details["VOLUMETRIC_WEIGHT"] else 0
                    length = awb_details["LENGTH"]
                    breadth = awb_details["BREADTH"]
                    height = awb_details["HEIGHT"]

                    if order_num.replace(".", "", 1).isdigit():
                       order_num = int(float(order_num))
                    elif 'e+' in str(order_num):
                       order_num = int(float(order_num))
                    else:
                       order_num = awb_details["ORDER_NUMBER"][0:20]

                    if ((actual_weight > 10.0) or (volumetric_weight > 10.0)):
                            a = str(airwaybill_num)+"("+str(max(actual_weight,volumetric_weight))+"Kgs)"
                            awb_overweight.append(a)
            
                    org_pincode = pickup.pincode
                    dest_pincode = pincode                
                    servicecentre = Pincode.objects.get(pincode=dest_pincode, status__in = [1, 2, 3]).service_center                            
                    ## pincode virtual dc validate
                    if ManifestAPIConfiguration.objects.filter(configuration_key = 'maxAllowedWeight', customer = shipper ):
                        maxAllowedWeight = ManifestAPIConfiguration.objects.filter(configuration_key = 'maxAllowedWeight', customer = shipper).latest('id').configuration_value
                        
                    else:
                        maxAllowedWeight = ManifestAPIConfiguration.objects.filter(configuration_key = 'maxAllowedWeight',customer__isnull = True).latest('id').configuration_value

                    if ManifestAPIConfiguration.objects.filter(configuration_key = 'maxAllowedLength', customer = shipper ):
                        maxAllowedLength = ManifestAPIConfiguration.objects.filter(configuration_key = 'maxAllowedLength', customer = shipper).latest('id').configuration_value

                    else:
                        maxAllowedLength = ManifestAPIConfiguration.objects.filter(configuration_key = 'maxAllowedLength',customer__isnull = True).latest('id').configuration_value

                    if ManifestAPIConfiguration.objects.filter(configuration_key = 'maxAllowedBreadth', customer = shipper ):
                        maxAllowedBreadth = ManifestAPIConfiguration.objects.filter(configuration_key = 'maxAllowedBreadth', customer = shipper).latest('id').configuration_value

                    else:
                        maxAllowedBreadth = ManifestAPIConfiguration.objects.filter(configuration_key = 'maxAllowedBreadth',customer__isnull = True).latest('id').configuration_value

                    if ManifestAPIConfiguration.objects.filter(configuration_key = 'maxAllowedHeight', customer = shipper ):
                        maxAllowedHeight = ManifestAPIConfiguration.objects.filter(configuration_key = 'maxAllowedHeight', customer = shipper).latest('id').configuration_value

                    else:
                        maxAllowedHeight = ManifestAPIConfiguration.objects.filter(configuration_key = 'maxAllowedHeight',customer__isnull = True).latest('id').configuration_value


                    if float(actual_weight) > float(maxAllowedWeight):
                        awb_validation["awb"] = awb_details["AWB_NUMBER"]
                        awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                        awb_validation["success"] = False
                        awb_validation["reason"] = "Higher weight than {0} kg not accepted hence manifest rejected".format(maxAllowedWeight)
                        response_awb["shipments"].append(awb_validation)
                        continue

                    if float(length) > float(maxAllowedLength):
                        awb_validation["awb"] = awb_details["AWB_NUMBER"]
                        awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                        awb_validation["success"] = False
                        awb_validation["reason"] = "Higher LENGTH than {0} cm not accepted hence manifest rejected".format(maxAllowedLength)
                        response_awb["shipments"].append(awb_validation)
                        continue

                    if float(breadth) > float(maxAllowedBreadth):
                        awb_validation["awb"] = awb_details["AWB_NUMBER"]
                        awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                        awb_validation["success"] = False
                        awb_validation["reason"] = "Higher BREADTH than {0} cm not accepted hence manifest rejected".format(maxAllowedBreadth)
                        response_awb["shipments"].append(awb_validation)
                        continue

                    if float(height) > float(maxAllowedHeight):
                        awb_validation["awb"] = awb_details["AWB_NUMBER"]
                        awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                        awb_validation["success"] = False
                        awb_validation["reason"] = "Higher HEIGHT than {0} cm not accepted hence manifest rejected".format(maxAllowedHeight)
                        response_awb["shipments"].append(awb_validation)
                        continue


                    
                    if ManifestAPIConfiguration.objects.filter(configuration_key = 'PINCODE_VIRTUAL_DC_VALIDATION', configuration_value = 'True'):
                        destinationPincode = awb_details["PINCODE"]
                        pincodeVirtualDcValidationResponse = manifestValidation.validatePincodeVirtualDc(destinationPincode = destinationPincode, essentialProduct = essentialProduct)
                        if not pincodeVirtualDcValidationResponse[0]:
                            awb_validation["awb"] = awb_details["AWB_NUMBER"]
                            awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                            awb_validation["success"] = False
                            awb_validation["reason"] = pincodeVirtualDcValidationResponse[1]
                            response_awb["shipments"].append(awb_validation)
                            continue
                        else:
                            servicecentre = pincodeVirtualDcValidationResponse[1]
                    exp_date = get_expected_dod(pickup.service_centre,servicecentre, datetime.now())
                    if not length:
                        length = 0
                    if not breadth:
                        breadth = 0
                    if not height:
                        height = 0

                    #print "MULTISELLER", airwaybill_num
                    shipment = Shipment.objects.filter(airwaybill_number=airwaybill_num)
                    #print "MULTISELLER ---", airwaybill_num, shipment
                    if shipment:
                        shipment = shipment[0]
                        awb_validation["awb"] = awb_details["AWB_NUMBER"] 
                        awb_validation["order_number"] = awb_details["ORDER_NUMBER"] 
                        #if shipment.order_number == awb_details["ORDER_NUMBER"] and shipment.added_on > today_date:
                        awb_validation["success"] = False
                        awb_validation["reason"] = "AIRWAYBILL_IN_USE"

                    elif manifestQueuestatus == -1:
                        awb_validation["success"] = True
                        awb_validation["reason"] = "Updated Successfully"
                        ManifestQueueLogs.objects.create(airwaybill_number = awb_details["AWB_NUMBER"], status = 0)
                        response_awb["shipments"].append(awb_validation)
                        continue
                    else: 
                    
                        shipment = Shipment.objects.create(airwaybill_number=airwaybill_num, 
                                 current_sc=pickup.service_centre, order_number=str(order_num), product_type=product_type, 
                                 shipper=shipper, pickup=pickup, reverse_pickup=0, consignee=consignee, 
                                 consignee_address1 = consignee_address1, consignee_address2 = consignee_address2 , 
                                 consignee_address3 = consignee_address3, destination_city=destination_city, pincode=pincode, 
                                 state=state, mobile=mobile, telephone=telephone, item_description=item_description, 
                                 pieces=pieces, collectable_value=collectable_value, declared_value=declared_value, 
                                 actual_weight=actual_weight, volumetric_weight=0.0, length=length, 
                                 #expected_dod = exp_date, breadth=breadth, height=height, service_centre = servicecentre, 
                                 breadth=breadth, height=height, service_centre_id = servicecentre.id, 
                                 original_dest_id = servicecentre.id, updated_on = datetime.now())
                        awb_num = AirwaybillNumbers.objects.get(airwaybill_number=airwaybill_num)
                        awb_num.status=1
                        awb_num.save()
                        #print  "add_encryption_ffx start"
                        add_encryption_ffx(shipment,'mobile',shipment.mobile)
                        add_encryption(shipment, 'consignee',shipment.consignee)
                        add_encryption(shipment, 'consignee_address1',shipment.consignee_address1, 'STR')
                        add_encryption(shipment, 'consignee_address2',shipment.consignee_address2, 'STR')
                        add_encryption(shipment, 'consignee_address3',shipment.consignee_address3, 'STR')
                        add_encryption(shipment, 'consignee_address4',shipment.consignee_address4, 'STR')
                        add_encryption(shipment, 'telephone',shipment.telephone)
                        #print  "add_encryption_ffx completed"
                        if validWalletRequest:
                            price_updated(shipment.airwaybill_number, True)
                            WalletShipmentsBillingQueue.objects.create(airwaybill_number = shipment.airwaybill_number, shipment_type = 0, product_type = Product.objects.get(product_name = shipment.product_type.strip()))
                        update_shipmentlogsource(airwaybill_num)

                    try:
                        add_dict = awb_details["ADDITIONAL_INFORMATION"]
                        if CustomerKeyInfo.objects.filter(additional_info_key = 'DEFAULT_SECURE_DEL', additional_key_value = 'True', customer_id = capi.customer_id) and product_type == "ppd":
                            add_dict.update({"OTP_REQUIRED_FOR_DELIVERY":"Y"})
                        if essentialProduct:
                            add_dict.update({"essentialProduct":"Y"})
                        for key in add_dict.keys():
                            if key == "MULTI_SELLER_INFORMATION": continue
                            AdditionalInformation.objects.create(shipment = shipment,add_info_key = key, add_info_value = add_dict[key])
                            if shipment.shipper.customeradditionalinformation_set.filter(add_info_key = "auto_self_collect",add_info_value = "True") and not AdditionalInformation.objects.filter(add_info_key='SELF_COLLECT', add_info_value = 'Yes',shipment = shipment):
                                    AdditionalInformation.objects.create(add_info_key = 'SELF_COLLECT', add_info_value = 'Yes',shipment = shipment)
                            if add_dict[key] == 'NDD':
                                #print "ndd found"
                                '''
                                nextday_delivery = ndd(pickup,destination_city,servicecentre)
                                if not nextday_delivery['success']:
                                    awb_validation["awb"] = awb_details["AWB_NUMBER"]
                                    awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                                    awb_validation["success"] = False
                                    awb_validation["reason"] = nextday_delivery['msg']
                                    response_awb["shipments"].append(awb_validation)
                                '''
                                service = AddOnServices.objects.get(code='ndd') 
                                ShipmentServices.objects.create(shipment = shipment, addonservice_id = service.id)
                                continue

                    except:
                        pass
                    if awb_details.has_key("ADDONSERVICE"):
                        addon_services = awb_details["ADDONSERVICE"]
                        for addon_service in addon_services:
                            #return HttpResponse(addon_services)
                            if addon_service == 'NDD':
                                service = AddOnServices.objects.get(code='ndd')
                                ShipmentServices.objects.create(shipment = shipment, addonservice_id = service.id)
                                continue
                    
                            
                    if multi_seller_status: #MULTISELLER
                        multi_seller_creation(awb_details, shipment) #MULTISELLER
                             
                    status = shipment.status
                    ShipmentExtension.objects.filter(shipment_id=shipment.id).update(status_bk = status, updated_on = now)
                    remarks = ""
                    if not shipment.added_on:
                       shipment.added_on = now
                    upd_time = shipment.added_on
                    monthdir = upd_time.strftime("%Y_%m")
                    shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                    shipment_history.objects.create(shipment=shipment, status=status, current_sc = shipment.current_sc)
                    #ApiShipments.objects.create(shipment=shipment, upload_type=1,preferred_date=preferred_date,preferred_delivery=preferred_delivery,transport_type=transport_type)
                    ApiShipments.objects.create(shipment=shipment, upload_type=1, transport_type=transport_type)
                    if pref_del:
                        PreferShipments.objects.create(shipment=shipment,mode=mode,time_from=time_from,time_to=time_to)
                    tmp_count=Shipment.objects.filter(pickup=pickup.id).count()
                    pickup.pieces=tmp_count;
                    pickup.status=0 
                    pickup.save() 
                    #for ewaybill
                    #print "Except",customerEwaybillExemption,intraStateExemption,hsnCodeExemption
                    if float(shipment.declared_value) > 49999.0 and not customerEwaybillExemption and not intraStateExemption and not hsnCodeExemption:
                       #return HttpResponse(shipment.declared_value)
                       #print "dec gte 49999.0 =========="
                       if shipment.additional_shipment.filter(add_info_key="GST_ERN"):
                          if not CustomerAdditionalInformation.objects.filter(add_info_key = "ewaybill_exempt",add_info_value = "True",customer_id = capi.customer.id):
                             ew = shipment.additional_shipment.filter(add_info_key="GST_ERN")[0]
                             if ew.add_info_value:
                                if not ShipmentEwaybill.objects.filter(shipment_id=shipment.id,ewaybill=ew.add_info_value):
                                   ShipmentEwaybill.objects.create(shipment_id=shipment.id,ewaybill=ew.add_info_value)
                       elif shipment.multi_seller_shipment.all():
                          for mul in shipment.multi_seller_shipment.all():
                              if not CustomerAdditionalInformation.objects.filter(add_info_key = "ewaybill_exempt",add_info_value = "True",customer_id = capi.customer.id):
                                 if mul.gst_ern:
                                    if not ShipmentEwaybill.objects.filter(shipment_id=shipment.id,ewaybill=mul.gst_ern):
                                       ShipmentEwaybill.objects.create(shipment_id=shipment.id,ewaybill=mul.gst_ern)
                           
                         
                else:   ############# should be check
                    #print "awb_validation_response :", awb_validation_response["RESPONSE_MESSAGE"]
                    if awb_validation_response["RESPONSE_MESSAGE"] in ["AIRWAYBILL_NUMBER_ALREADY_EXISTS", "AIRWAYBILL_NUMBER_ALREADY_EXISTS,"]:
                        airwaybill_num =  int(awb_details["AWB_NUMBER"])
                        shipment = Shipment.objects.filter(airwaybill_number=airwaybill_num)
                        #print "MULTISELLER -------", airwaybill_num, shipment
                        if shipment:
                            shipment = shipment[0]
                            awb_validation["awb"] = awb_details["AWB_NUMBER"]
                            awb_validation["order_number"] = awb_details["ORDER_NUMBER"]
                            awb_validation["success"] = False
                            awb_validation["reason"] = "AIRWAYBILL_IN_USE"
                            #if shipment.order_number == awb_details["ORDER_NUMBER"] and shipment.added_on > today_date:
                    else:
                        #print "manifest_awb_add_info -------", awb_details["AWB_NUMBER"]
                        awb_validation["awb"] = awb_details["AWB_NUMBER"] 
                        awb_validation["order_number"] = awb_details["ORDER_NUMBER"] 
                        awb_validation["success"] = False
                        awb_validation["reason"] = awb_validation_response["RESPONSE_MESSAGE"]

                response_awb["shipments"].append(awb_validation)

            #print "api_manifest_awb_shipment", capi.username, response_awb
            return Response(response_awb)   

        except Exception as e:
            print ("Eception",e)
            awb_validation = {}
            awb_validation["awb"] = ""
            awb_validation["order_number"] = ""
            awb_validation["success"] = False
            awb_validation["reason"] = ""+str(e)
            error_payload = ''
            error_payload = request.data
            #return HttpResponse(request)
            '''if request.body:
                error_payload = urllib.unquote(request.body).decode('utf8')
            else:
                error_payload = request'''
            #creating error logs
            ManifestApiErrorLogs.objects.create(error_key = 'manifest_awb',request = error_payload, response = str(e))
            response_awb["shipments"].append(awb_validation)
            return Response(response_awb,status=status.HTTP_400_BAD_REQUEST)
	    #return HttpResponse(request.POST['json_input'])
            



