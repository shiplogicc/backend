from django.db import models

# Create your models here.

from math import ceil
from django.conf import settings
from django.db.models import *
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User

from customer.models import Customer 
from location.models import Address,ServiceCenter
from pickup.models import PickupRegistration
from slconfig.models import AddOnServices,ShipmentStatusMaster
from authentication.models import EmployeeMaster 
import datetime
from django.utils.timezone import now
today = datetime.datetime.today()
last_month = (today - datetime.timedelta(days=7)).strftime('%Y-%m-%d')

from django.db import transaction




class Shipment(models.Model):
    pickup = models.ForeignKey(PickupRegistration, null=True, blank=True, related_name='shipment_pickup',on_delete=models.CASCADE)
    reverse_pickup = models.BooleanField(default=False)
    return_shipment = models.SmallIntegerField(default=False)
    airwaybill_number=models.BigIntegerField()

    order_number=models.CharField(max_length=20)
    product_type = models.CharField(max_length=10, null=True, blank=True)

    shipper = models.ForeignKey(Customer, null=True, blank=True,on_delete=models.CASCADE)

    consignee=models.CharField(max_length=100, null=True, blank=True)

    consignee_address1=models.CharField(max_length=400, null=True, blank=True)
    consignee_address2=models.CharField(max_length=400, null=True, blank=True)
    consignee_address3=models.CharField(max_length=400, null=True, blank=True)
    consignee_address4=models.CharField(max_length=400, null=True, blank=True)
    destination_city = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)
    manifest_location = models.ForeignKey(ServiceCenter,null=True, blank=True, related_name="manifest_location",on_delete=models.CASCADE)
    service_centre = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="shipment_sc",on_delete=models.CASCADE)
    current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="current_sc",on_delete=models.CASCADE)
    state = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.BigIntegerField(default=0, null=True, blank=True)
    telephone = models.CharField(default=0, max_length=100, null=True, blank=True)
    item_description=models.CharField(max_length=400, null=True, blank=True)
    pieces=models.IntegerField(null=True, blank=True)

    collectable_value=models.FloatField(null=True, blank=True)
    declared_value=models.FloatField(null=True, blank=True)

    actual_weight=models.FloatField(default=0.0, null=True, blank=True)
    volumetric_weight=models.FloatField(default=0.0, null=True, blank=True)

    length=models.FloatField(default=0.0, null=True, blank=True)
    breadth=models.FloatField(default=0.0, null=True, blank=True)
    height=models.FloatField(default=0.0, null=True, blank=True)
    status = models.IntegerField(default=0, null=True, blank=True)
    added_on=models.DateTimeField(auto_now_add = True)
    updated_on=models.DateTimeField(null=True, blank=True)
    status_type = models.IntegerField(default=0, null=True, blank=True)
    reason_code = models.ForeignKey(ShipmentStatusMaster, null=True, blank=True,on_delete=models.CASCADE)
    remark = models.CharField(max_length=400, null=True, blank=True)
    expected_dod=models.DateTimeField(null=True, blank=True)
    ref_airwaybill_number = models.BigIntegerField(null=True, blank=True)
    original_dest = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="shipment_origin_sc",on_delete=models.CASCADE)
    rts_reason = models.CharField(max_length=100, null=True, blank=True)
    rts_date=models.DateTimeField(null=True, blank=True)
    inscan_date=models.DateTimeField(null=True, blank=True)
    rts_status = models.SmallIntegerField(default=0, null=True, blank=True)
    rd_status = models.SmallIntegerField(default=0, null=True, blank=True)
    rto_status = models.SmallIntegerField(default=0, null=True, blank=True)
    sdd = models.SmallIntegerField(default=0, null=True, blank=True)
    rejection = models.SmallIntegerField(default=0, null=True, blank=True)
    billing = models.ForeignKey('billing.Billing', null=True, blank=True, related_name='billing_ships',on_delete=models.CASCADE)
    #sbilling = models.ForeignKey('billing.BillingSubCustomer', null=True, blank=True, related_name='subbilling_ships',on_delete=models.CASCADE)
    sdl = models.SmallIntegerField(default=0, null=True, blank=True)
    tab = models.SmallIntegerField(default=0, null=True, blank=True)
    chargeable_weight = models.FloatField(null=True, blank=True, default=0)
    shipment_date = models.DateField(null=True, blank=True)

 
class PincodeEmbargoLog(models.Model):
    awb = models.CharField(max_length = 20, null=True, blank=True, db_index=True)
    customer = models.ForeignKey(Customer, null=True, blank=True,on_delete=models.CASCADE)
    pincode = models.IntegerField(default=0, db_index=True)
    timestamp = models.DateTimeField(null=True, blank=True, db_index=True)
    pincode_type = models.CharField(max_length=10, null=True, blank=True)
    embargo_status = models.IntegerField(default=0, db_index=True)
    status = models.IntegerField(default=1, db_index=True)
    added_on = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_on = models.DateTimeField(null=True, blank=True, db_index=True)


class ApiShipments(models.Model):
    shipment = models.OneToOneField(Shipment, primary_key=True, related_name = "apishipment",on_delete=models.CASCADE)
    status = models.IntegerField(default=0, null=True, blank=True, db_index=True)
    upload_type = models.IntegerField(default=0, null=True, blank=True, db_index=True) #0-normal 1-api through 2-cs uploaded
    added_on = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_on = models.DateTimeField(auto_now=True, blank=True, db_index=True)
    #shipment_type: 0:normal 1:filler normal 2:filler multipart 3:for removing multiprt checks(temp.)
    shipment_type = models.IntegerField(default=0, null=True, blank=True, db_index=True)
    preferred_date = models.DateTimeField(null=True, blank=True,db_index=True)
    preferred_delivery = models.BooleanField(default=False)
    transport_type = models.IntegerField(default=0, null=True, blank=True, db_index=True) #DG shipment : 1:surface
    reason_for_reverse_pickup= models.CharField(max_length=200,  null=True, blank=True)
    extra_information= models.CharField(max_length=200,  null=True, blank=True)


class PreferShipments(models.Model):
    shipment = models.ForeignKey(Shipment, primary_key=True, related_name = "prefershipment",on_delete=models.CASCADE)
    status = models.IntegerField(default=0, null=True, blank=True, db_index=True)
    mode= models.IntegerField(default=0, null=True, blank=True, db_index=True) #1:Pickup #2:Delivery
    date= models.DateField(null=True, blank=True, db_index=True)
    time_from= models.TimeField(null=True, blank=True, db_index=True) #start time
    time_to= models.TimeField(null=True, blank=True, db_index=True) #end time


class ShipmentServices(models.Model):
    shipment = models.ForeignKey(Shipment, related_name='shipmentservices_shipment',on_delete=models.CASCADE)
    addonservice = models.ForeignKey(AddOnServices, related_name='shipmentservices_addon',on_delete=models.CASCADE)
    status =  models.IntegerField(default=0, null = True, blank=True, db_index=True)
    added_on = models.DateTimeField(auto_now_add = True, db_index=True)
    updated_on = models.DateTimeField(auto_now = True, db_index=True)
   



class ShipmentHistory(models.Model):
    shipment=models.ForeignKey('Shipment',on_delete=models.CASCADE)
    current_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="hist_current_sc",on_delete=models.CASCADE)
    employee_code=models.ForeignKey(EmployeeMaster, null=True, blank=True,on_delete=models.CASCADE)
    reason_code=models.ForeignKey(ShipmentStatusMaster, null=True, blank=True,on_delete=models.CASCADE)
    status=models.IntegerField(default=0, null=True, blank=True, db_index=True)
    updated_on=models.DateTimeField(default = now, db_index=True)
    remarks=models.CharField(max_length=200, null=True, blank=True)
    expected_dod=models.DateTimeField(null=True, blank=True)
    scan_push_status = models.SmallIntegerField(default=0, null=True, blank=True, db_index=True)
    added_on = models.DateTimeField(default = now, db_index=True)
    scan_pushed_on = models.DateTimeField(null=True, blank=True, db_index=True)
    partition_month = models.DateTimeField(default = now, db_index=True)

class AdditionalInformation(models.Model):
    shipment = models.ForeignKey(Shipment,   db_index = True,related_name = "additional_shipment",on_delete=models.CASCADE)
    add_info_key = models.CharField(null=True, blank=True, max_length=250, db_index = True)
    add_info_value = models.CharField(null=True, blank=True, max_length=250, db_index = True)
    added_on = models.DateTimeField(auto_now_add = True, db_index=True)
    updated_on = models.DateTimeField(auto_now = True, db_index=True)


class ShipmentStatusUpdate(models.Model):
    shipment = models.ForeignKey(Shipment, db_index = True,on_delete=models.CASCADE)
    data_entry_emp_code = models.ForeignKey(EmployeeMaster, null=True, blank=True, related_name="statsupd_dataemp",on_delete=models.CASCADE)
    delivery_emp_code = models.ForeignKey(EmployeeMaster, null=True, blank=True, related_name="statsupd_deliveryemp",on_delete=models.CASCADE)
    reason_code = models.ForeignKey(ShipmentStatusMaster, null=True, blank=True,on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    recieved_by = models.CharField(max_length=200, null=True, blank=True)
    status = models.IntegerField(default=0, null=True, blank=True)#1:undelivered, 2:delivered 3:pod reversal undelivered
    origin = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name="statsupd_origin",on_delete=models.CASCADE)
    remarks = models.CharField(max_length=200, null=True, blank=True)
    ajax_field = models.CharField(max_length=20, null=True, blank=True)
    added_on=models.DateTimeField(auto_now_add = True,db_index=True)
    updated_on = models.DateTimeField(auto_now = True, db_index=True)

