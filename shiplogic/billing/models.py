from django.db import models
from customer.models import Customer
from servicecenter.models import Shipment
class Billing(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    freight_charge = models.FloatField(null=True, blank=True, default=0)
    sdl_charge = models.FloatField(null=True, blank=True, default=0)
    fuel_surcharge = models.FloatField(null=True, blank=True, default=0)
    valuable_cargo_handling_charge = models.FloatField(blank=True,null=True, default=0)
    to_pay_charge = models.FloatField(null=True, blank=True, default=0)
    rto_charge = models.FloatField(null=True, blank=True, default=0)
    demarrage_charge = models.FloatField(null=True, blank=True, default=0)
    cod_applied_charge = models.FloatField(null=True, blank=True, default=0)
    cod_subtract_charge = models.FloatField(null=True, blank=True, default=0)
    total_cod_charge = models.FloatField(null=True, blank=True, default=0)
    billing_date = models.DateField(null=True, blank=True)
    billing_date_from = models.DateField(null=True, blank=True)
    generation_status = models.IntegerField(max_length=1, default=0)
    payment_status = models.IntegerField(max_length=1, default=0)
    #shipments = models.ManyToManyField(Shipment)
    shipments = models.ManyToManyField(Shipment, related_name="ship_bills")
    demarrage_shipments = models.ManyToManyField(Shipment, related_name="billing_demarrage_shipments")
    service_tax = models.FloatField(null=True, blank=True, default=0)
    education_secondary_tax = models.FloatField(null=True, blank=True, default=0)
    cess_higher_secondary_tax = models.FloatField(null=True, blank=True, default=0)
    bill_generation_date = models.DateTimeField(null=True, blank=True)
    total_charge_pretax = models.FloatField(null=True, blank=True, default=0)
    total_payable_charge = models.FloatField(null=True, blank=True, default=0)
    balance = models.FloatField(null=True, blank=True, default=0)
    received = models.FloatField(null=True, blank=True, default=0)
    adjustment = models.FloatField(null=True, blank=True, default=0)
    adjustment_cr = models.FloatField(null=True, blank=True, default=0)
    sdd_charge = models.FloatField(null=True, blank=True, default=0)
    reverse_charge = models.FloatField(null=True, blank=True, default=0)
    shipment_count = models.FloatField(null=True, blank=True, default=0)
    total_chargeable_weight = models.FloatField(null=True, blank=True, default=0)
    # 0 - Normal Billing, 2 - Reverse Billing, 1 - EBS billing
    billing_type = models.SmallIntegerField(default=0)
    ecom_gst = models.ForeignKey("gst.ClientGSTRegistration",on_delete=models.CASCADE)
    customer_gst = models.ForeignKey("gst.CustomerGSTRegistration",on_delete=models.CASCADE)
    bill_number = models.CharField(max_length = 25, default = "", db_index = True)

'''
class BillingSubCustomer(models.Model):
    subcustomer = models.ForeignKey(Shipper,on_delete=models.CASCADE)
    freight_charge = models.FloatField(null=True, blank=True, default=0)
    sdl_charge = models.FloatField(null=True, blank=True, default=0)
    fuel_surcharge = models.FloatField(null=True, blank=True, default=0)
    valuable_cargo_handling_charge = models.FloatField(blank=True,null=True, default=0)
    to_pay_charge = models.FloatField(null=True, blank=True, default=0)
    rto_charge = models.FloatField(null=True, blank=True, default=0)
    total_charge = models.FloatField(null=True, blank=True, default=0)
    demarrage_charge = models.FloatField(null=True, blank=True, default=0)
    cod_applied_charge = models.FloatField(null=True, blank=True, default=0)
    cod_subtract_charge = models.FloatField(null=True, blank=True, default=0)
    total_cod_charge = models.FloatField(null=True, blank=True, default=0)
    billing_date = models.DateField(null=True, blank=True)
    billing_date_from = models.DateField(null=True, blank=True)
    generation_status = models.IntegerField(max_length=1, default=0)
    payment_status = models.IntegerField(max_length=1, default=0)
    shipments = models.ManyToManyField(Shipment)
    demarrage_shipments = models.ManyToManyField(Shipment, related_name="billingsubcustomer_demarrage_shipments")
    billing = models.ForeignKey(Billing, null=True, blank=True)
    sdd_charge = models.FloatField(null=True, blank=True, default=0)
    reverse_charge = models.FloatField(null=True, blank=True, default=0)
    shipment_count = models.FloatField(null=True, blank=True, default=0)
    total_chargeable_weight = models.FloatField(null=True, blank=True, default=0)
'''

class ShipmentBillingQueue(models.Model):
    airwaybill_number = models.BigIntegerField(primary_key=True, db_index=True)
    status = models.IntegerField(default=0, db_index=True) # 0: not billed, 1:billed
    shipment_date = models.DateTimeField(db_index=True)
    shipment_type = models.IntegerField(default=0, db_index=True) # 0: forward, 1: RTS
    updated_on = models.DateTimeField(auto_now_add=True)
    #product_type = models.ForeignKey('customer.Product', db_index=True,on_delete=models.CASCADE)
    

