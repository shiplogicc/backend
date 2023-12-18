import datetime
from django.db import models
from customer.models import *
from location.models import *
from slconfig.models import *
class Pickup(models.Model):
    subcustomer_code = models.ForeignKey(Shipper, null=True, blank=True,on_delete=models.CASCADE)
    service_centre = models.ForeignKey(ServiceCenter,on_delete=models.CASCADE)
    pieces = models.IntegerField(default=0, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add = True)
    status = models.IntegerField(default=0, null=True, blank=True)

    class Meta:
            abstract = True
            

'''Pickup registration according to new requirments'''
class PickupRegistration(Pickup):
    area = models.ForeignKey(AreaMaster, null=True, blank=True,on_delete=models.CASCADE)
    return_subcustomer_code = models.ForeignKey(Shipper, null=True, blank=True, related_name = "return_subcustomer_code",on_delete=models.CASCADE)
    customer_code = models.ForeignKey(Customer,on_delete=models.CASCADE)
    pickup_date = models.DateField()
    pickup_time = models.TimeField(null=True, blank=True)
    mode = models.ForeignKey(Mode, null=True, blank=True,on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=150)
    address_line1 = models.CharField(max_length=150)
    address_line2 = models.CharField(max_length=150, null=True, blank=True)
    address_line3 = models.CharField(max_length=150, null=True, blank=True)
    address_line4 = models.CharField(max_length=150, null=True, blank=True)
    pincode = models.CharField(max_length=15, null=True, blank=True)
    mobile = models.BigIntegerField(null=True, blank=True)
    telephone = models.CharField(max_length=100, null=True, blank=True)
    caller_name = models.CharField(max_length=50, null=True, blank=True)
    to_pay = models.BooleanField(default=False)
    reverse_pickup = models.BooleanField(default=False)
    regular_pickup = models.BooleanField(default=False)
    callers_number = models.BigIntegerField(null=True, blank=True)
    email = models.CharField(max_length=150, null=True, blank=True)
    office_close_time = models.TimeField(null=True, blank=True)

    product_code = models.CharField(max_length=50, null=True, blank=True)
    actual_weight = models.FloatField(default=0, null=True, blank=True)
    volume_weight = models.FloatField(default=0, null=True, blank=True)
    pickup_route = models.IntegerField(default=0, null=True, blank=True)

    remarks = models.CharField(max_length=200, null=True, blank=True)
    reminder = models.CharField(max_length=200, null=True, blank=True)



class ReversePickupRegistration(models.Model):
    pickup =  models.ManyToManyField(PickupRegistration, null=True, blank=True)
    customer_code = models.ForeignKey(Customer, null=True, blank=True,on_delete=models.CASCADE)
    pickup_date = models.DateField()
    pickup_time = models.TimeField(null=True, blank=True)
    pincode = models.CharField(max_length=15, null=True, blank=True)
    mobile = models.BigIntegerField(null=True, blank=True)
    added_by = models.ForeignKey(EmployeeMaster, null=True, blank=True,on_delete=models.CASCADE)
    reverse_pickup = models.BooleanField(default=True)
    status = models.IntegerField(default=0, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add = True)

