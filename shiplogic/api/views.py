from django.shortcuts import render


import os
import sys


import datetime
import fileinput
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from airwaybill.models import *

from customer.models import Shipper, ShipperMapping, Customer
from location.models import Pincode, Address, ServiceCenter
from servicecenter.models import Shipment
import unicodedata
from pickup.models import PickupRegistration
from django.db.models import Q

today = datetime.datetime.strftime(datetime.datetime.today(), "%Y%m%d")


ERR = {'VALIDITY':'INVALID',
        'VALUE': 'CHECK_VALUE_OF',
        'SERVICE': 'NOT_SERVICED',
        'FORMAT': 'NOT_IN_SPECIFIED_FORMAT',
        'MATCH': 'MATCH_NOT_FOUND',
       'CLASH': 'ALREADY_EXISTS',
        'TYPE' : 'INCORRECT_PRODUCT_TYPE',
        '2': 'CONSIGNEE',
        '3': 'DESTINATION',
        '4': 'RETURN'}


def get_or_create_vendor(*args, **kwargs):
    pincode = kwargs.get('pincode')
    pincode = int(pincode)
    try:
        address = str(kwargs.get('address'))
    except:
        address = kwargs.get('address')
    name = kwargs.get('name')
    customer = kwargs.get('customer')
    phone = kwargs.get('phone', "")

    address1 = address[:100]
    address2 = address[100:200]
    address3 = address[200:300]
    address4 = address[300:400]
    shipper = Shipper.objects.filter(
            name=name, customer=customer, address__pincode=pincode)
    if shipper:
        #shipper_address = str(shipper[0].address.address1)+str(shipper[0].address.address2)+str(shipper[0].address.address3)+str(shipper[0].address.address4)
        shipper_address = str(unicodedata.normalize('NFKD', shipper[0].address.address1).encode('ascii','ignore')) + str(unicodedata.normalize('NFKD', shipper[0].address.address2).encode('ascii','ignore')) + str(unicodedata.normalize('NFKD', shipper[0].address.address3).encode('ascii','ignore')) + str(unicodedata.normalize('NFKD', shipper[0].address.address4).encode('ascii','ignore'))
        #print "#####", shipper_address != address, shipper_address, address
        if address != shipper_address:

           shipper = shipper[0]
           #print "#####!!!!!!!!!!!", shipper.address.address1, shipper.address.address2
           shipper.address.address1 = address1
           shipper.address.address2 = address2 if address2 else ''
           shipper.address.address3 = address3 if address3 else ''
           shipper.address.address4 = address4 if address4 else ''
           shipper.address.phone = phone
           #print "#####@@@@@@@@@@", shipper.address.address1, shipper.address.address2
           shipper.address.save()
           shipper.save()
           return shipper
        else:
           return shipper[0]

    pin = Pincode.objects.get(pincode=pincode)

    address  =  Address.objects.create(
        city=pin.service_center.city, state=pin.service_center.city.state,
        address1=address1, address2=address2, address3=address3,
        address4=address4, pincode=pincode, phone = phone)

    shipper = Shipper.objects.create(
        name=name, customer=customer, address_id=address.id)
    ShipperMapping.objects.create(
       shipper=shipper, forward_pincode=pincode, return_pincode=0)
    return shipper


def pincode_pickup_create(record, capi, reverse_pickup):
    now = datetime.datetime.now()
    to_time_obj = now + datetime.timedelta(days=1)
    from_time=now.strftime("%Y-%m-%d")
    to_time=to_time_obj.strftime("%Y-%m-%d")
    pickup_dict = {}
    subcustomer_list = {}
    now = datetime.datetime.now()
    error = False

    pincode = Pincode.objects.filter(pincode = int(record["PICKUP_PINCODE"]))
    if not pincode:
       error = True
    else:
       pincode = pincode[0]
    name = record["PICKUP_NAME"]
    address = ""
    address_1 = str(record["PICKUP_ADDRESS_LINE1"])
    address_2 = str(record["PICKUP_ADDRESS_LINE2"])



    if address_1 and address_2:
        address = address_1 +" "+ address_2
    elif not address_2:
        address = address_1
    elif not address_1:
        address = address_2
    else:
        error = True

    return_pincode = False
    if record["RETURN_PINCODE"]:
        return_pincode = Pincode.objects.filter(pincode = int(record["RETURN_PINCODE"]))
    if return_pincode:
        return_pincode = str(record["RETURN_PINCODE"])
        return_name = record["RETURN_NAME"]
        return_phone = record["RETURN_PHONE"]
        return_address = ""
        return_address_1 = str(record["RETURN_ADDRESS_LINE1"])
        return_address_2 = str(record["RETURN_ADDRESS_LINE2"])
        if return_address_1 and return_address_2:
            return_address = return_address_1 +" "+ return_address_2
        elif not return_address_2:
            return_address = return_address_1
        elif not return_address_1:
            return_address = return_address_2



    phone = record["PICKUP_PHONE"]
    pincode = str(record["PICKUP_PINCODE"])
    customer_code = capi.customer.code
    subcustomer = get_or_create_vendor( name=name, customer=capi.customer, pincode=pincode, address=address, phone=phone)
    subcustomer_id = subcustomer.id
    if return_pincode:
        return_subcustomer = get_or_create_vendor( name=return_name, customer=capi.customer, pincode=return_pincode, address=return_address, phone=return_phone)
    else:
        return_subcustomer = subcustomer
    return_subcustomer_id = return_subcustomer.id
    pickup = PickupRegistration.objects.filter(customer_code = capi.customer.id,
             subcustomer_code_id=subcustomer_id, return_subcustomer_code_id = return_subcustomer_id, pincode = pincode, status=0).filter(Q(pickup_time__gte="07:00:00",
             pickup_date=from_time) & Q(pickup_time__lte="07:00:00", pickup_date=to_time)).filter(reverse_pickup=reverse_pickup).\
             order_by("-pickup_date", "-pickup_time")

    if pickup:
        pickup = pickup[0]
    else:
        #pincode_sc_map = PickupPincodeServiceCentreMAP.objects.filter(pincode = int(record["PICKUP_PINCODE"]))

        pincode = Pincode.objects.get(pincode = pincode)
        #return_pincode = Pincode.objects.get(pincode = return_pincode)

        #if pincode_sc_map :
        if  pincode.pickup_sc and capi.customer.id != 374:
            sc = pincode.pickup_sc
        else:
            sc = pincode.service_center

        pickup_phone = ""
        if record["PICKUP_PHONE"]:
            pickup_phone = record["PICKUP_PHONE"].replace("-","")
            pickup_phone = pickup_phone.replace(" ","")
        pickup = PickupRegistration.objects.create(customer_code_id = capi.customer.id,subcustomer_code=subcustomer,return_subcustomer_code=return_subcustomer,
                 pickup_time=now,pickup_date=now,mode_id=1,customer_name=record["PICKUP_NAME"],
                 address_line1=record["PICKUP_ADDRESS_LINE1"],address_line2=record["PICKUP_ADDRESS_LINE2"],
                 pincode=record["PICKUP_PINCODE"],
                 mobile=record["PICKUP_MOBILE"],telephone=pickup_phone,pieces=4,
                 actual_weight=1.2,volume_weight=2.1,service_centre=sc, reverse_pickup=reverse_pickup)
    pickup_dict[record["PICKUP_PINCODE"]] = pickup

    return (pickup_dict, error)



def validate_awb(single_awb_details):
    reasons, destination_pin = '',''

    if len(single_awb_details) == 8:
        product_type = None
        count = 0
        for i in single_awb_details:
            field, val_reasons, product_type =  validate_data(count, i, product_type)
            count = count + 1
            if val_reasons:
                reasons+=val_reasons+','
            else:
                pass
    else:
	    reasons = 'INCORRECT_NUMBER_OF_PARAMETERS_PASSED_TO_VALIDATE'
    import json
    if not reasons:
        return {'SUCCESS':True}

        #return json.dumps({'SUCCESS':True}, indent=4, separators=(',', ': '))
    else:
        return {'SUCCESS':False, 'RESPONSE_MESSAGE':reasons}
        #return json.dumps({'SUCCESS':False, 'RESPONSE_MESSAGE':reasons}, indent=4, sort_keys=False, separators=(',', ': '))


def validate_data(field, value, product_t):
    ''' each value passed as a number and a value
    '''
    field = int(field)
    #return HttpResponse(product_t)
    try:
        value = value.strip()
    except:
        value = value
    reasons = ''
    # capi = api_auth
    product_type=product_t

    if field == 1:	# 6 AWB_NUMBER
	    if not int(value):
	        reasons+=('AIRWAYBILL_NUMBER_' + ERR['FORMAT'])
	    else:
                if AirwaybillNumbers.objects.filter(airwaybill_number = int(value), status = True):
                    reasons+=('AIRWAYBILL_NUMBER_' + ERR['CLASH'])
                else:
     	            try:
                             awb_exists = Shipment.objects.get(airwaybill_number=int(value))
                             # print 'awb_exists: ', awb_exists
                             if awb_exists:
                                 reasons+=('AIRWAYBILL_NUMBER_' + ERR['CLASH'])
                             else:
     	                        try:
     	                            from airwaybill.models import AirwaybillCustomer
     	                            awbc = AirwaybillCustomer.objects.get(id = int(capi_id))
     	                            awb_matched = awbc.airwaybill_number.filter(airwaybill_number=int(value))[0]
     	                            # return field, value
     	                        except:
     	                            reasons+=(ERR['VALUE'] + '_AIRWAYBILL_NUMBER')
     	                           # return field, (ERR['VALUE'] + ' airwaybill number')
     	            except:
     	                # reasons+=('AIRWAYBILL_NUMBER_' + ERR['MATCH'])
     	    	        pass
     
    if field in (2, 3, 4):	# 25, 27, PINCODE
        # print len(value)
    	if value:
    	    field = str(field)
            
    	    try:
    	        int(value)
    	        try:
    		        pin_serviced = Pincode.objects.get(pincode=value, status__in = [1,2,3])
    		        destination_pin = value
    		         # return field, value
    	        except:
    		        reasons+=(ERR[field]+'_PINCODE_'+ERR['SERVICE'])
    	    except:
    	        reasons+=(ERR[field]+"_"+ERR['VALIDITY']+'_PINCODE_FORMAT')
    	else:
    	    field = str(field)
    	    if field in (2, 3): 
                reasons+=(ERR[field]+ "_"  +ERR['VALIDITY']+ '_PINCODE_FORMAT')
    
    
    if field == 6:	#PRODUCT
    	if not value.lower() in ('ppd', 'cod', 'rts', 'rto', 'ebsppd', 'ebscod', 'ebs ppd', 'ebs cod', 'ebs-ppd', 'ebs-cod'):
    	    reasons+=(ERR['VALIDITY']+'_PRODUCT_TYPE')
    	elif value.lower() == 'cod':
            pass
        #elif value.lower() == 'ppd':
        #    product_type = 7
    
    if field == 7:	# COLLECTABLE VALUE, ONLY FOR COD SHIPMENTS
    	if product_type == 6:
            if float(value) >= 200000:
                reasons += ("COLLECTABLE_VALUE_HIGHER_THAN_200000")
            try:
                1/float(value)
            except:
                reasons+=(ERR['VALIDITY'] + '_COLLECTABLE_VALUE')
    
    if field == 5:	# ACTUAL_WEIGHT
        try:
            1/float(value)
        except:
            reasons+=(ERR['VALIDITY'] + '_VALUE_FOR_WEIGHT')
    
    
    return field, reasons, product_type


