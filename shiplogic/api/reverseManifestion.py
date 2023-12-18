# Create your views here.
import json
import utils
from datetime import timedelta, datetime
import dateutil.parser
from django.db.models import *

import re
now = datetime.datetime.now()
monthdir = now.strftime("%Y_%m")
from collections import OrderedDict
from amazon_api.utils import validate_awb
from integration_services.utils import get_or_create_vendor
from integration_services.process_pickup import ProcessPickup
import unicodedata
from api.views import awb_reverse_detail_check,awb_check,ship_check,subcust_check,pincode_revpickup_create,transit_time,pickup_create
from apiv2.models import ManifestApiErrorLogs
sql_inject_symbols = ['=', '%', '#', ' OR ', ' AND ', ' or ', ' and ', '>', '<', '\?','"']

def api_manifest_rev(request):
    try:
        pid=1
        awb_overweight=[]
        subCustomers_list=[]
        response_awb = {}
        response_awb["shipments"] = []
        


        ##### For Allowed Customers  #####
        manifestValidation = ManifestAPIValidation(customerId = capi.customer_id)
        manifestValidationResp = manifestValidation.validateCustomerManifest(processType = "RVP_MANIFEST_ALLOWED")
        if not manifestValidationResp["success"]:
            return HttpResponse(manifestValidationResp["message"])
        ##################################
        json_shipments = request_body

        json_shipments = json_shipments.replace("\\t","")

        json_shipments = json_shipments.replace("&amp;","")

        #print "JSONREV", json_shipments
        if request.POST:
                validWalletRequest = False
                file_contents = xmlshipments
                shipment_list = []
                if not isinstance(file_contents['ECOMEXPRESS-OBJECTS']['SHIPMENT'], list):
                    shipment_list.append(file_contents['ECOMEXPRESS-OBJECTS']['SHIPMENT'])
                else:
                    shipment_list = file_contents['ECOMEXPRESS-OBJECTS']['SHIPMENT']


                order_numbers = {}
                order_awb_numbers = {}
                ship_type_count = {}
                ship_type_obj = {}
                awb_check_shiplist = []
                rev_pickup_list = []
                test = []
                rev_pickup_flag = 0
                ship_dic = {}   
                transport_type = 0  
                #### DC wise QC process Activation validation 


                
                for qc_check in shipment_list:
                    if qc_check.get("ADDONSERVICE"):
                        service=qc_check.get("ADDONSERVICE")
                    else:
                        service=[]
                    for ser in service:
                         if ser=="QC":
                             if ManifestAPIConfiguration.objects.filter(configuration_key = 'RvpQCBarred', configuration_value = 'True'):
                                  if ManifestAPIConfiguration.objects.filter(configuration_key = 'RvpQCBarredResponse'):
                                      qc_restict_msg = ManifestAPIConfiguration.objects.filter(configuration_key = 'RvpQCBarredResponse').latest('id').configuration_value
                                  else:
                                      qc_restict_msg = "QC services are suspended at this moment."
                                      
                                  error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number>%s</airwaybill_number>\n<error_list>\n'%(qc_check['AWB_NUMBER'])
                                  error_xml_output = error_xml_output + "<reason_comment>%s </reason_comment>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>Reasons along with each awb</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"%(qc_restict_msg)

                                  o = xmltodict.parse(error_xml_output)
                                  error_xml_output = simplejson.dumps(o)
                                  return HttpResponse(error_xml_output,content_type="application/json")
                             pieces = qc_check["PIECES"]
                             if CustomerAdditionalInformation.objects.filter(customer=capi.customer,add_info_key="rvpQcMaxLineItems"):
                                 qc_message = ""
                                 cu = CustomerAdditionalInformation.objects.filter(customer=capi.customer,add_info_key="rvpQcMaxLineItems").latest('id').add_info_value
                                 if int(pieces) > int(cu):
                                     qc_message = "More than {0}-line items are not allowed for your account".format(cu)
                                 if qc_message:
                                     error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number>%s</airwaybill_number>\n<error_list>\n'%(qc_check['AWB_NUMBER'])
                                     error_xml_output = error_xml_output + "<reason_comment>%s </reason_comment>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>Reasons along with each awb</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"%(qc_message)
                                     o = xmltodict.parse(error_xml_output)
                                     error_xml_output = simplejson.dumps(o)
                                     return HttpResponse(error_xml_output,content_type="application/json")

 
                             pincode = qc_check["REVPICKUP_PINCODE"]
                             reverse_pickup_pincode=Pincode.objects.filter(pincode=pincode) 
                             if reverse_pickup_pincode:
                                 reverse_pickup_pincode=reverse_pickup_pincode[0]
                                 rev_pickup_sc_id=reverse_pickup_pincode.service_center_id
                                 process=DCWiseActivationOfProcess.objects.filter(process_name='QC_PROCESS', status=1)
                                 if process:
                                     check_active_dc=DCList.objects.filter(service_centre_id=int(rev_pickup_sc_id),process=process[0])
                                     if not check_active_dc:
                                         error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number>%s</airwaybill_number>\n<error_list>\n'%(qc_check['AWB_NUMBER'])
                                         error_xml_output = error_xml_output + "<reason_comment>%s Service not Available at %s </reason_comment>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>Reasons along with each awb</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"%(process[0].process_name,reverse_pickup_pincode.pincode)
                                         o = xmltodict.parse(error_xml_output)
                                         error_xml_output = simplejson.dumps(o)
                                         return HttpResponse(error_xml_output,content_type="application/json")
                             qc = qc_check.get("QC","")
                             if len(qc)!=0:
                                 mandatoryImageMissing = [i for i in qc if i.get('QCCHECKCODE') in ['Check_Image'] and (i.get('VALUE') == '' or i.get('VALUE') == None)]
                                 if mandatoryImageMissing:
                                     error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number>%s</airwaybill_number>\n<error_list>\n'%(qc_check['AWB_NUMBER'])
                                     error_xml_output = error_xml_output + "<reason_comment>Image is mandatory for provided QC CODE</reason_comment>\n<qc_code>%s</qc_code>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>Reasons along with each awb</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"%(mandatoryImageMissing[0]['QCCHECKCODE'])
                                     o = xmltodict.parse(error_xml_output)
                                     error_xml_output = simplejson.dumps(o)
                                     return HttpResponse(error_xml_output,content_type="application/json")
                                 isMpsShipment = False
                                 mpsQcCodeList = CustomerAdditionalInformation.objects.filter(customer_id = capi.customer_id, add_info_key = 'mpsQcCode').values_list('add_info_value',flat=True)
                                 qcCodeList = [qcObj.get('QCCHECKCODE') for qcObj in qc]
                                 for mpsQcCode in mpsQcCodeList:
                                     if qcCodeList.count(mpsQcCode) > 1:
                                         isMpsShipment = True
                                         break
                                 if isMpsShipment:
                                     error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number>%s</airwaybill_number>\n<error_list>\n'%(qc_check['AWB_NUMBER'])
                                     error_xml_output = error_xml_output + "<reason_comment>Invalid Quality Checks</reason_comment>\n<qc_code>%s</qc_code>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>Reasons along with each awb</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"%(mpsQcCode)
                                     o = xmltodict.parse(error_xml_output)
                                     error_xml_output = simplejson.dumps(o)
                                     ManifestApiErrorLogs.objects.create(error_key = 'mpsQcRejection', remarks = capi.customer_id, request = xmlshipments, response = 'Invalid Quality Checks %s'%(mpsQcCode))
                                     return HttpResponse(error_xml_output,content_type="application/json")
                                     

                customer = capi.customer
                customerEwaybillExemption = False
                intraStateExemption=False
                hsnCodeExemption = False
                if capi.customer:
                   cust_code = capi.customer.code
                   if cust_code in []:
                      customerEwaybillExemption = True
                for rev_awb_check_value in shipment_list:
                    if rev_awb_check_value.get("ADDITIONAL_INFORMATION",''):
                       if rev_awb_check_value["ADDITIONAL_INFORMATION"]:
                          if not rev_awb_check_value["ADDITIONAL_INFORMATION"].get("MULTI_SELLER_INFORMATION",'') and float(rev_awb_check_value["DECLARED_VALUE"]) > 49999.0:
                             dec_value = float(rev_awb_check_value["DECLARED_VALUE"])
                             delivery_pincode = int(rev_awb_check_value["DROP_PINCODE"])
                             delPin = Pincode.objects.filter(pincode=int(delivery_pincode))
                             return_pincode = rev_awb_check_value["REVPICKUP_PINCODE"]
                             pickPin = Pincode.objects.filter(pincode=int(return_pincode))
                             intraStateExemption=False
                             if pickPin and delPin:
                                pickState = pickPin[0].service_center.city.state_id
                                delState = delPin[0].service_center.city.state_id
                                if (pickState == delState and pickState in [1,2,6,13,14,16,7] and float(rev_awb_check_value["DECLARED_VALUE"]) < 100000.0):
                                    intraStateExemption = True
                                    #print "checking---------------"
                             
                             hsnCode = rev_awb_check_value["ADDITIONAL_INFORMATION"]["GST_HSN"]
                             hsnCodeExemption = False
                             if hsnCode:
                                hsncode = str(int(hsnCode))
                                if hsncode.startswith(("71","9601","0508")):
                                   hsnCodeExemption = True
                                   #print "checking33---"
                             if float(rev_awb_check_value["DECLARED_VALUE"]) > 49999.0 and not customerEwaybillExemption and not hsnCodeExemption and not intraStateExemption:  
                                 #print "checking1"
                                 if not rev_awb_check_value["ADDITIONAL_INFORMATION"]["SELLER_GSTIN"]:
                                     error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number></airwaybill_number>\n<error_list>\n'
                                     error_xml_output = error_xml_output + "<reason_comment>NO_SELLER_GSTIN</reason_comment>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>Seller GSTIN not provided!</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"
                                     o = xmltodict.parse(error_xml_output)
                                     error_xml_output = simplejson.dumps(o)
                                     return HttpResponse(
                                         error_xml_output,
                                         content_type="application/json"
                                     )
                                 if  not rev_awb_check_value["ADDITIONAL_INFORMATION"]["INVOICE_NUMBER"]:
                                     error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number></airwaybill_number>\n<error_list>\n'
                                     error_xml_output = error_xml_output + "<reason_comment>NO_INVOICE_NUMBER</reason_comment>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>Invoice number not provided!</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"
                                     o = xmltodict.parse(error_xml_output)
                                     error_xml_output = simplejson.dumps(o)
                                     return HttpResponse(
                                         error_xml_output,
                                         content_type="application/json"
                                     )
                                 if not rev_awb_check_value["ADDITIONAL_INFORMATION"]["INVOICE_DATE"]:
                                     error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number></airwaybill_number>\n<error_list>\n'
                                     error_xml_output = error_xml_output + "<reason_comment>NO_INVOICE_DATE</reason_comment>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>Invoice Date not provided!</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"
                                     o = xmltodict.parse(error_xml_output)
                                     error_xml_output = simplejson.dumps(o)
                                     return HttpResponse(
                                         error_xml_output,
                                         content_type="application/json"
                                     )
                                 if not rev_awb_check_value["ADDITIONAL_INFORMATION"]["GST_HSN"]:
                                     error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number></airwaybill_number>\n<error_list>\n'
                                     error_xml_output = error_xml_output + "<reason_comment>NO_GST_HSN</reason_comment>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>GST HSN not provided!</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"
                                     o = xmltodict.parse(error_xml_output)
                                     error_xml_output = simplejson.dumps(o)
                                     return HttpResponse(
                                         error_xml_output,
                                         content_type="application/json"
                                     )
                                 if not rev_awb_check_value["ADDITIONAL_INFORMATION"]["GST_ERN"]:
                                     error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number></airwaybill_number>\n<error_list>\n'
                                     error_xml_output = error_xml_output + "<reason_comment>NO_GST_ERN</reason_comment>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>GST ERN not provided!</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"
                                     o = xmltodict.parse(error_xml_output)
                                     error_xml_output = simplejson.dumps(o)
                                     return HttpResponse(
                                         error_xml_output,
                                         content_type="application/json"
                                     )
                                 if len(rev_awb_check_value["ADDITIONAL_INFORMATION"]["GST_ERN"]) <> 12:
                                     error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number></airwaybill_number>\n<error_list>\n'
                                     error_xml_output = error_xml_output + "<reason_comment>INVALID_GST_ERN</reason_comment>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>GST ERN should be 12 digit!</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"
                                     o = xmltodict.parse(error_xml_output)
                                     error_xml_output = simplejson.dumps(o)
                                     return HttpResponse(
                                         error_xml_output,
                                         content_type="application/json"
                                     )
                for rev_awb_check_value in shipment_list:
                    if not rev_awb_check_value["AWB_NUMBER"].isdigit():
                        error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number></airwaybill_number>\n<error_list>\n'
                        error_xml_output = error_xml_output + "<reason_comment>AWB_NUMBER should contain digits only !</reason_comment>\n<order_number>Invalid Value for AWB_NUMBER</order_number>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>Reasons along with each awb</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"
                        o = xmltodict.parse(error_xml_output)
                        error_xml_output = simplejson.dumps(o)
                        return HttpResponse(
                            error_xml_output,
                            content_type="application/xhtml+xml"
                        )


                for rev_awb_check_value in shipment_list:
                    if AirwaybillNumbers.objects.filter(airwaybill_number = rev_awb_check_value["AWB_NUMBER"], status = 1):
                        error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number></airwaybill_number>\n<error_list>\n'
                        error_xml_output = error_xml_output + "<reason_comment>AWB_NUMBER Used !</reason_comment>\n<order_number>AWB_NUMBER ALREADY USED</order_number>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>Reasons along with each awb</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"
                        o = xmltodict.parse(error_xml_output)
                        error_xml_output = simplejson.dumps(o)
                        return HttpResponse(
                            error_xml_output,
                            content_type="application/xhtml+xml"
                        )


                for rev_awb_check_value in shipment_list:
                    if not rev_awb_check_value["ORDER_NUMBER"]:
                        error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number></airwaybill_number>\n<error_list>\n'
                        error_xml_output = error_xml_output + "<reason_comment>NO_ORDER_NUMBER</reason_comment>\n<order_number>No order_number provided</order_number>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>Reasons along with each awb</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"
                        o = xmltodict.parse(error_xml_output)
                        error_xml_output = simplejson.dumps(o)
                        return HttpResponse(
                            error_xml_output,
                            content_type="application/json"
                        )
                if not ManifestAPIConfiguration.objects.filter(configuration_key = 'ADHOC_CITY_VALIDATION', configuration_value = 'True') and not ManifestAPIConfiguration.objects.filter(configuration_key = 'PINCODE_VIRTUAL_DC_VALIDATION', configuration_value = 'True'):
                    for rev_awb_check_value in shipment_list:
                        delivery_pincode = int(rev_awb_check_value["DROP_PINCODE"])
                        return_pincode = rev_awb_check_value["REVPICKUP_PINCODE"]
                        essentials = False
                        if rev_awb_check_value.has_key("ADDITIONAL_INFORMATION"):
                            essentials_prod = rev_awb_check_value.get("ADDITIONAL_INFORMATION").get("essentialProduct", None)
                            if essentials_prod and essentials_prod == "Y":
                                essentials = True

                        validateInboundOutboundResponse = manifestValidation.validateIoPincodeServiceability(pickupPincode = return_pincode, destinationPincode = delivery_pincode, customer = capi.customer, essentials = essentials, awb = rev_awb_check_value["AWB_NUMBER"])
                        if not validateInboundOutboundResponse[0]:
                            error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number></airwaybill_number>\n<error_list>\n'
                            error_xml_output = error_xml_output + "<reason_comment>"+validateInboundOutboundResponse[1]+"</reason_comment>\n<order_number>"+rev_awb_check_value['ORDER_NUMBER']+"</order_number>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>"+validateInboundOutboundResponse[1]+"</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"
                            o = xmltodict.parse(error_xml_output)
                            error_xml_output = simplejson.dumps(o)
                            return HttpResponse(
                                 error_xml_output,
                                 content_type="application/xhtml+xml"
                            )         
                for rev_awb_check_value in shipment_list:
                    if any(re.findall('|'.join(sql_inject_symbols), rev_awb_check_value["ORDER_NUMBER"])):
                        error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number></airwaybill_number>\n<error_list>\n'
                        error_xml_output = error_xml_output + "<reason_comment>NO_ORDER_NUMBER</reason_comment>\n<order_number>Invalid Value for ORDER_NUMBER</order_number>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>Reasons along with each awb</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"
                        o = xmltodict.parse(error_xml_output)
                        error_xml_output = simplejson.dumps(o)
                        return HttpResponse(
                            error_xml_output,
                            content_type="application/xhtml+xml"
                        )
                for rev_awb_check_value in shipment_list:
                    if rev_awb_check_value["VOLUMETRIC_WEIGHT"] and float(rev_awb_check_value["VOLUMETRIC_WEIGHT"]) > 100.0:
                        error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number></airwaybill_number>\n<error_list>\n'
                        error_xml_output = error_xml_output + "<reason_comment>HIGHER_VOLUMETRIC_WEIGHT</reason_comment>\n<order_number>"+rev_awb_check_value['ORDER_NUMBER']+"</order_number>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>Volumetric weigth should not be greater than 100kg.</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"
                        o = xmltodict.parse(error_xml_output)
                        error_xml_output = simplejson.dumps(o)
                        return HttpResponse(
                            error_xml_output,
                            content_type="application/xhtml+xml"
                        )
                    #if rev_awb_check_value["ACTUAL_WEIGHT"] and float(rev_awb_check_value["ACTUAL_WEIGHT"]) > 100.0:
                    #    error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number></airwaybill_number>\n<error_list>\n'
                    #    error_xml_output = error_xml_output + "<reason_comment>HIGHER_ACTUAL_WEIGHT</reason_comment>\n<order_number>"+rev_awb_check_value['ORDER_NUMBER']+"</order_number>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>Actual weigth should not be greater than 100kg.</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"
                    #    o = xmltodict.parse(error_xml_output)
                    #    error_xml_output = simplejson.dumps(o)
                    #    return HttpResponse(
                    #        error_xml_output,
                    #        content_type="application/xhtml+xml"
                    #    ) 
                for rev_awb_check_value in shipment_list:
                    if not rev_awb_check_value["ITEM_DESCRIPTION"]:
                       error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number>%s</airwaybill_number>\n<error_list>\n'%(rev_awb_check_value['AWB_NUMBER'])
                       error_xml_output = error_xml_output + "<reason_comment>NO_ITEM_DESCRIPTION</reason_comment>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n</RESPONSE-OBJECTS>"
                       o = xmltodict.parse(error_xml_output)
                       error_xml_output = simplejson.dumps(o)
                       return HttpResponse(
                           error_xml_output,
                           content_type="application/json"
                       )
                for rev_awb_check_value in shipment_list:
                    if not rev_awb_check_value["REVPICKUP_NAME"]:
                       error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number>%s</airwaybill_number>\n<error_list>\n'%(rev_awb_check_value['AWB_NUMBER'])
                       error_xml_output = error_xml_output + "<reason_comment>NO_REVPICKUP_NAME</reason_comment>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n</RESPONSE-OBJECTS>"
                       o = xmltodict.parse(error_xml_output)
                       error_xml_output = simplejson.dumps(o)
                       return HttpResponse(
                           error_xml_output,
                           content_type="application/json"
                       )
                for rev_awb_check_value in shipment_list:
                    if rev_awb_check_value["PRODUCT"]:
                        if rev_awb_check_value["PRODUCT"].lower() == "rev":
                            rev_pickup_list.append(rev_awb_check_value)
                            rev_pickup_flag = 1
     
                rev_pickup = []
                if rev_pickup_flag:
                    rev_pickup = ReversePickupRegistration.objects.create(customer_code=capi.customer,
                        pickup_date=now.date(), pickup_time=now.time(), )
                awb_number = ''
                for awb_check_value in shipment_list:
                    if awb_check_value["AWB_NUMBER"]:
                        awb_number = awb_check_value["AWB_NUMBER"]
                        awb_check_shiplist.append(awb_check_value)

                awb_detail_check_list = awb_reverse_detail_check(shipment_list, capi)
                if shipment_list[0].get('ADDITIONAL_INFORMATION'):
                    try:
                        #print "test1",shipment_list[0]
                        awb_detail_check_list_multsllr, multiseller_status ,intraStateExemption, hsnCodeExemption= multi_seller_validation_v2(shipment_list[0])
                        #print "test2",shipment_list[0]
                    except:
                        awb_detail_check_list_multsllr, multiseller_status = '',False
                else:
                    awb_detail_check_list_multsllr, multiseller_status = '',False
                mltslr_dict = {}
                if awb_detail_check_list == 1 and not multiseller_status and awb_detail_check_list_multsllr:
                   mltslr_dict[shipment_list[0]["ORDER_NUMBER"]] = {"reason_comment":awb_detail_check_list_multsllr}
                   awb_detail_check_list = mltslr_dict
                   for key in awb_detail_check_list.keys():
                       outer_dict = awb_detail_check_list[key]
                       awb_detail_check_list[key] = outer_dict
                   #print '================', awb_detail_check_list
                #print "--------------", awb_detail_check_list, multiseller_status
                if awb_detail_check_list <> 1 and not multiseller_status:
                    for key in awb_detail_check_list.keys():
                        outer_dict = awb_detail_check_list[key]
                        #print awb_detail_check_list, outer_dict["reason_comment"]
                        outer_dict["reason_comment"] += "," + awb_detail_check_list_multsllr
                        awb_detail_check_list[key] = outer_dict

                if awb_detail_check_list <> 1: 
                    awb_error_list = awb_detail_check_list
                if awb_detail_check_list <> 1:
                    error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n'
                    if awb_error_list <> 1:

                        for awb, values in awb_error_list.iteritems():
                            error_xml_output = error_xml_output + "<AIRWAYBILL> \n"
                            error_xml_output = error_xml_output + "<success>False</success>\n"
                            error_xml_output = error_xml_output + "<airwaybill_number>%s</airwaybill_number>\n" % str(awb_number)
                            error_xml_output = error_xml_output + "<order_id>%s</order_id>\n" % str(awb)
                            error_xml_output = error_xml_output + "<error_list>\n"
                            for key, description in  values.iteritems():
                                error_xml_output = error_xml_output + "<%s>%s</%s>\n" % (key, description, key)
                            error_xml_output = error_xml_output + "</error_list>\n"
                            error_xml_output = error_xml_output + "</AIRWAYBILL> \n"
                    error_xml_output = error_xml_output + "</AIRWAYBILL-OBJECTS>\n"
                    error_xml_output = error_xml_output + "<RESPONSE-COMMENT>Reasons along with each awb</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"

                if awb_detail_check_list <> 1:
                     o = xmltodict.parse(error_xml_output)
                     error_xml_output = simplejson.dumps(o)
                     return HttpResponse(
                         error_xml_output,
                         content_type="application/json"
                     )

                for svalue in shipment_list:
                    if not svalue["AWB_NUMBER"]:
                        order_numbers[svalue["ORDER_NUMBER"] ] = svalue["PRODUCT"].lower()
                    else:
                        ship_dic[svalue["ORDER_NUMBER"] ] = svalue["AWB_NUMBER"]

                for svalue in shipment_list:
                    if not svalue["AWB_NUMBER"]:
                        if not ship_type_count.get(svalue["PRODUCT"].lower()) : ship_type_count[svalue["PRODUCT"].lower()] = 1
                        else : ship_type_count[svalue["PRODUCT"].lower()] = ship_type_count[svalue["PRODUCT"].lower()]+ 1

                xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n'

                for ship_type, ship_count in ship_type_count.items():

                    ship_type_obj[ship_type] = AirwaybillCustomer.objects.create(customer=capi.customer, type=ship_type, quantity=ship_count)

                for order_number, ship_type in order_numbers.items():


                    if ship_type == "ppd":
                        pid = PPD.objects.latest('id').id + 1
                        obj = PPD.objects.create(id=pid)
                    elif ship_type == "cod":
                        pid = COD.objects.latest('id').id + 1
                        obj = COD.objects.create(id=pid)
                    elif ship_type == "rev":
                        pid = ReversePickup.objects.latest('id').id + 1
                        obj = ReversePickup.objects.create(id=pid)
                    elif ship_type == "ebsppd":
                        pid = PPDZero.objects.latest('id').id + 1
                        obj = PPDZero.objects.create(id=pid)
                    elif ship_type == "ebscod":
                        pid = CODZero.objects.latest('id').id + 1
                        obj = CODZero.objects.create(id=pid)

                    airwaybill_number = obj.id
                    awb = AirwaybillNumbers.objects.create(airwaybill_number=airwaybill_number)
                    ship_type_obj[ship_type].airwaybill_number.add(awb)

                    xml_output = xml_output + "<AIRWAYBILL> \n<success>True</success>\n <order_id>%s</order_id>\n <airwaybill_number>%d</airwaybill_number>\n </AIRWAYBILL>\n" % (order_number, airwaybill_number)

                    order_awb_numbers[order_number] = airwaybill_number
                for order_number, awb_number in ship_dic.items():


                    airwaybill_number = int(awb_number)

                    xml_output = xml_output + "<AIRWAYBILL> \n<success>True</success>\n <order_id>%s</order_id>\n <airwaybill_number>%d</airwaybill_number>\n </AIRWAYBILL>\n" % (order_number, airwaybill_number)

                    order_awb_numbers[order_number] = airwaybill_number
                xml_output = xml_output + "</AIRWAYBILL-OBJECTS>\n"
                xml_output = xml_output + "<RESPONSE-COMMENT>Shipments Updated.</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"

                awb_check_list = awb_check(shipment_list, capi) 
                data_check = ship_check(shipment_list) 
                if data_check <> 1:
                   return HttpResponse(str(data_check))
                for record in shipment_list:
                    if not svalue["AWB_NUMBER"]:
                        record["AWB_NUMBER"] = order_awb_numbers[record["ORDER_NUMBER"]] 
                    if not int(record["AWB_NUMBER"]):
                        return HttpResponse("Error, No airway bill number found for order number %s. Please note that nothing is updated" % record["ORDER_NUMBER"] )
                for record in shipment_list:
                        if not record["AWB_NUMBER"] :
                            record["AWB_NUMBER"] = order_awb_numbers[record["ORDER_NUMBER"]] 
                        airwaybill_num =  int(record["AWB_NUMBER"])
                        reason_for_reverse_pickup = record.get("REASON_FOR_REVERSE_PICKUP", "")
                        if record["VENDOR_ID"]:
                            subcustomer_check = subcust_check([record], capi) 
                            if isinstance(subcustomer_check, dict):
                                return HttpResponse(str(subcustomer_check))
                            pickup_data, error = pickup_create(subcustomer_check, rev_pickup_flag)

                            if error:
                                return HttpResponse(str(error))            

                            pickup = pickup_data.get(record["VENDOR_ID"])
                            if not pickup:
                                continue
                        else:
                            if not record["DROP_PINCODE"]:
                                continue

                            capi = CustomerAPI.objects.get(id = capi.id)
                            pickup_data, error = pincode_revpickup_create(record, capi, rev_pickup_flag)

                            if error:
                                return HttpResponse(str(error))            

                            pickup = pickup_data.get(record["DROP_PINCODE"])
                            if not pickup:
                                continue

                        if rev_pickup and rev_pickup_flag:
                            rev_pickup.pickup.add(pickup)
                        order_num = repr(record["ORDER_NUMBER"][:20])
                        product_type = record["PRODUCT"]
                        product_type = product_type.lower()

                        shipper = pickup.customer_code

                        consignee = record["REVPICKUP_NAME"]
                        consignee_address1 = record["REVPICKUP_ADDRESS1"]
                        consignee_address2 = record["REVPICKUP_ADDRESS2"]
                        consignee_address3 = record["REVPICKUP_ADDRESS3"]
                        destination_city = record["REVPICKUP_CITY"]

                        pincode = record["REVPICKUP_PINCODE"]#it was REVPICKUP_PINCODE 
                        state = record["REVPICKUP_STATE"]
                        record["REVPICKUP_MOBILE"] = filter(lambda x: x.isdigit(),record["REVPICKUP_MOBILE"])[-10:]
                        mobile = record["REVPICKUP_MOBILE"] if record["REVPICKUP_MOBILE"] else 0
                        if not  mobile.isdigit():
                            mobile=0 
                        record["REVPICKUP_TELEPHONE"] = filter(lambda x: x.isdigit(),record["REVPICKUP_TELEPHONE"])[-10:]
                        telephone = record["REVPICKUP_TELEPHONE"]
                        item_description = record["ITEM_DESCRIPTION"]
                        pieces = record["PIECES"]
                        if not item_description or item_description.strip() == "":
                            return HttpResponse('ITEM_DESCRIPTION can not be blank')

                        collectable_value = 0
                        try:
                                int(collectable_value)
                        except ValueError:
                                collectable_value = collectable_value.replace(",", "")

                        declared_value = record["DECLARED_VALUE"] if record["DECLARED_VALUE"] else 0
                        try:
                                int(declared_value)
                        except ValueError:
                              declared_value = declared_value.replace(",", "")
     
                        actual_weight = record["ACTUAL_WEIGHT"]
                        volumetric_weight = record["VOLUMETRIC_WEIGHT"] if record["VOLUMETRIC_WEIGHT"] else 0
                        length = record["LENGTH"]
                        breadth = record["BREADTH"]
                        height = record["HEIGHT"]

                        if order_num.replace(".", "", 1).isdigit():
                           order_num = int(float(order_num))
                        elif 'e+' in str(order_num):
                           order_num = int(float(order_num))
                        else:
                           order_num = record["ORDER_NUMBER"][:20]

                        if ((actual_weight > 10.0) or (volumetric_weight > 10.0)):
                                a = str(airwaybill_num)+"("+str(max(actual_weight,volumetric_weight))+"Kgs)"
                                awb_overweight.append(a)
                        if ManifestAPIConfiguration.objects.filter(configuration_key = 'maxAllowedWeight', customer = shipper ):
                            maxAllowedWeight = ManifestAPIConfiguration.objects.filter(configuration_key = 'maxAllowedWeight', customer = shipper).latest('id').configuration_value

                        else:
                            maxAllowedWeight = ManifestAPIConfiguration.objects.filter(configuration_key = 'maxAllowedWeight',customer__isnull = True).latest('id').configuration_value

                        if float(actual_weight) > float(maxAllowedWeight): 
                            return HttpResponse("Higher weight than {0} kg not accepted hence manifest rejected".format(maxAllowedWeight)) 
                        defaultDgCustomers = [int(i) for i in DGConfig.objects.using('local_ecomm').filter(customer__isnull = False, status = 1, keyword = 'DEFAULT_DG').values_list('customer_id',flat=True)]
                        inOutCenters = Pincode.objects.using('local_ecomm').filter(pincode__in = [record['DROP_PINCODE'], record['REVPICKUP_PINCODE']]).values_list('service_center',flat=True)

                        try: 
                            if (record.get("DG_SHIPMENT","")=="true" or capi.customer_id in defaultDgCustomers) and not ServiceCenterAdditionalInformation.objects.using('local_ecomm').filter(sc_id__in = inOutCenters, add_info_key = 'BLOCK_DG', add_info_value = 'True', activation_status = True):
                                transport_type=1
                        except:
                            transport_type=0

                        org_pincode = pickup.pincode

                        dest_pincode = record["DROP_PINCODE"]
                        #exp_date = transit_time(org_pincode, dest_pincode)    

                        dest_pincode_obj = Pincode.objects.get(pincode=dest_pincode)     
                        if dest_pincode_obj.reverse_sc:
                            servicecentre = dest_pincode_obj.reverse_sc
                        elif dest_pincode_obj.return_sc:    
                            servicecentre = dest_pincode_obj.return_sc
                        else:     
                            servicecentre = dest_pincode_obj.service_center
                        if record.has_key('EXTRA_INFORMATION'): #for extra information
                           extra_information = record['EXTRA_INFORMATION']
                        else:
                           extra_information = ''
                        ship_redirect = pickup.subcustomer_code.shipperredirectionmapping_set.filter(status = True)
                        if ship_redirect:
                            servicecentre = ship_redirect.latest('id').sc
                        if shipper.customeradditionalinformation_set.filter(add_info_key = "rvp_del_sc",add_info_value = "True"):
                            servicecentre = dest_pincode_obj.service_center 
                        if rev_pickup and rev_pickup_flag:
                            if not mobile:
                                mobile = 0
                            rev_shipment = ReverseShipment.objects.filter(airwaybill_number=airwaybill_num)
                            if rev_shipment:
                                rev_shipment = rev_shipment[0]
                            else:
                                rev_shipment = ReverseShipment(
                                    reverse_pickup=rev_pickup, order_number=order_num, product_type="ppd",
                                    shipper=shipper, pickup_consignee=consignee,
                                    pickup_consignee_address1=consignee_address1,
                                    pickup_consignee_address2=consignee_address2,
                                    pickup_consignee_address3=consignee_address3,
                                    pickup_pincode=int(pincode), state=state, mobile=0,
                                    telephone=0, item_description=item_description,
                                    pieces=pieces, collectable_value=collectable_value,
                                    declared_value=declared_value, actual_weight=actual_weight,
                                    volumetric_weight=volumetric_weight, length=length,
                                    pickup_service_centre = pickup.service_centre,
                                    breadth=breadth, height=height)
                                rev_shipment.save()
                                rev_shipment.pickup = pickup
                                rev_shipment.save()
                                rev_shipment.pickup.pieces = ReverseShipment.objects.filter(pickup=rev_shipment.pickup).count() #Need to be change
                                rev_shipment.pickup.save()

                        shipment = Shipment.objects.filter(airwaybill_number=airwaybill_num)
                        if shipment:
                            shipment = shipment[0]
                        else: 
                            shipment = Shipment.objects.create(airwaybill_number=int(airwaybill_num), 
                                     current_sc=pickup.service_centre, order_number=str(order_num), product_type=product_type, 
                                     shipper=shipper, pickup=pickup, reverse_pickup=0, consignee=consignee, 
                                     consignee_address1 = consignee_address1, consignee_address2 = consignee_address2 , 
                                     consignee_address3 = consignee_address3, destination_city=destination_city, pincode=pincode, 
                                     state=state, mobile=mobile, telephone=telephone, item_description=item_description, 
                                     pieces=pieces, collectable_value=collectable_value, declared_value=declared_value, 
                                     actual_weight=actual_weight, volumetric_weight=volumetric_weight, length=length, 
                                     #expected_dod = exp_date, breadth=breadth, height=height, service_centre = servicecentre, 
                                     breadth=breadth, height=height, service_centre = servicecentre, 
                                     original_dest = servicecentre, updated_on = datetime.datetime.now())
                            awb_num = AirwaybillNumbers.objects.get(airwaybill_number=airwaybill_num)
                            awb_num.status=1
                            awb_num.save()
                            if validWalletRequest:
                                WalletShipmentsBillingQueue.objects.create(airwaybill_number = shipment.airwaybill_number, shipment_type = 0, product_type = Product.objects.get(product_name = shipment.product_type.strip()))
                        if multiseller_status:
                            multi_seller_creation(record, shipment)

                        if record.get('ADDITIONAL_INFORMATION'):
                            additional_dict1 = record.get('ADDITIONAL_INFORMATION')
                            for key in additional_dict1.keys():
                                if not key == 'MULTI_SELLER_INFORMATION':
                                    if not AdditionalInformation.objects.filter(shipment = shipment,add_info_key = key, add_info_value = additional_dict1[key]):
                                        AdditionalInformation.objects.create(shipment = shipment,add_info_key = key, add_info_value = additional_dict1[key])

                        status = shipment.status
                        ShipmentExtension.objects.filter(shipment_id=shipment.id).update(status_bk = status, updated_on = now)
                        #for ewaybill
                        if float(shipment.declared_value) > 49999.0 and not customerEwaybillExemption and not intraStateExemption and not hsnCodeExemption:
                           if shipment.additional_shipment.filter(add_info_key="GST_ERN"):
                              ew = shipment.additional_shipment.filter(add_info_key="GST_ERN")[0]
                              if not ShipmentEwaybill.objects.filter(shipment_id=shipment.id,ewaybill=ew.add_info_value):
                                 ShipmentEwaybill.objects.create(shipment_id=shipment.id,ewaybill=ew.add_info_value)
                           elif shipment.multi_seller_shipment.all():
                              for mul in shipment.multi_seller_shipment.all():
                                  if mul.gst_ern:
                                     if not ShipmentEwaybill.objects.filter(shipment_id=shipment.id,ewaybill=mul.get_ern):
                                        ShipmentEwaybill.objects.create(shipment_id=shipment.id,ewaybill=mul.gst_ern)


                        if rev_pickup and rev_pickup_flag:
                            Shipment.objects.filter(pk=shipment.id).update(status=31)
                            Shipment.objects.filter(pk=shipment.id).update(reverse_pickup=1)
                            ReverseShipment.objects.filter(pk=rev_shipment.id).update(shipment=shipment, airwaybill_number = shipment.airwaybill_number)

                        remarks = ""
                        if not shipment.added_on:
                           shipment.added_on = now
                        upd_time = shipment.added_on
                        monthdir = upd_time.strftime("%Y_%m")
                        shipment_history = get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
                        shipment_history.objects.create(shipment=shipment, status=shipment.status, current_sc = shipment.current_sc)
                        ApiShipments.objects.create(shipment=shipment, upload_type=1, reason_for_reverse_pickup = reason_for_reverse_pickup, transport_type=transport_type, extra_information=extra_information) #for identifying api uploaded shipments
                        tmp_count=Shipment.objects.filter(pickup=pickup.id).count()
                        pickup.pieces=tmp_count;
                        pickup.status=0 
                        pickup.save()
                        #print  "add_encryption_ffx start"
                        add_encryption_ffx(shipment,'mobile',shipment.mobile)
                        add_encryption(shipment, 'consignee',shipment.consignee)
                        add_encryption(shipment, 'consignee_address1',shipment.consignee_address1, 'STR')
                        add_encryption(shipment, 'consignee_address2',shipment.consignee_address2, 'STR')
                        add_encryption(shipment, 'consignee_address3',shipment.consignee_address3, 'STR')
                        add_encryption(shipment, 'consignee_address4',shipment.consignee_address4, 'STR')
                        add_encryption(shipment, 'telephone',shipment.telephone)
                        #print  "add_encryption_ffx completed"
                        try:
                            update_shipmentlogsource(airwaybill_num)
                        except:
                            pass

                ###QC Start
                for qc_check in shipment_list:
                    if qc_check.get("ADDONSERVICE"):
                        service=qc_check.get("ADDONSERVICE")
                    else:
                        service=[]
                    for ser in service:
                         if ser=="QC":
                              qc=qc_check.get("QC","")
                              if len(qc)!=0:
                                  ship=qc_check["AWB_NUMBER"]
                                  qc1= create_checks(qc,ship)

                                  try:
                                      qc2=qc1['invalid_qc_code']
                                      error_xml_output = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<RESPONSE-OBJECTS>\n<AIRWAYBILL-OBJECTS>\n<AIRWAYBILL>\n<success>False</success>\n<airwaybill_number>%s</airwaybill_number>\n<error_list>\n'%(ship)
                                      error_xml_output = error_xml_output + "<reason_comment>Invalid Quality Checks</reason_comment>\n<qc_code>%s</qc_code>\n</error_list>\n</AIRWAYBILL>\n</AIRWAYBILL-OBJECTS>\n<RESPONSE-COMMENT>Reasons along with each awb</RESPONSE-COMMENT>\n</RESPONSE-OBJECTS>"%(qc2)
                                      o = xmltodict.parse(error_xml_output)
                                      error_xml_output = simplejson.dumps(o)
                                      #return HttpResponse(error_xml_output,content_type="application/json") 
                                      return HttpResponse(error_xml_output,content_type="application/json") 

                                  except:
                                      pass
                         else:
                             pass 
                                  # END OF QC
                o = xmltodict.parse(xml_output)
                xml_output = simplejson.dumps(o) 
                return HttpResponse(
                    xml_output, 
                    #content_type="application/json"
                    content_type="application/json"
                )

                return HttpResponse("<string><root><message>Shipments Added Successfully</message></root></string>", content_type="application/json")

    except Exception as e:
        awb_validation = {}
        awb_validation["awb"] = ""
        awb_validation["order_number"] = ""
        awb_validation["success"] = False
        awb_validation["reason"] = str(e)
        error_payload = ''
        error_payload = request.POST['json_input']
        #return HttpResponse(request)
        '''if request.body:
            error_payload = urllib.unquote(request.body).decode('utf8')
        else:
            error_payload = request'''
        #creating error logs
        ManifestApiErrorLogs.objects.create(error_key = 'manifest_awb',request = error_payload, response = str(e))
        response_awb["shipments"].append(awb_validation)
        return HttpResponse(simplejson.dumps(response_awb),content_type="application/json")
        #return HttpResponse(request.POST['json_input'])
