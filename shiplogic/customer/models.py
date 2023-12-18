from django.db import models

from location.models import *
from authentication.models import *
from multiselectfield import MultiSelectField
# Create your models here.
from django.contrib.auth.models import User
from authentication.models import EmployeeMaster
#from servicecenter.models import Shipment

BILLING_CHOICES = (('Weekly','Weekly'),
                    ('Fortnight','Fortnight'), #make anothe table
                    ('Monthly','Monthly')
                   )
SHIPPER_TYPE = ((0,'Normal'),
                (1,'To Pay')
               )

class NamedUser(EmployeeMaster):
    class Meta:
        proxy=True


class Legality(models.Model):
    legality_type= models.CharField(max_length=40)

class Customer(models.Model):
    name                = models.CharField(max_length=100)
    code                = models.CharField(max_length=30)
    activation_status   = models.BooleanField(blank=True)
    activation_date     = models.DateField(blank=True,null=True)
    contract_from       = models.DateField()
    contract_to         = models.DateField()
    legality            = models.ForeignKey(Legality,on_delete=models.CASCADE)
    billing_schedule    = models.IntegerField(max_length=3,default=7)
    day_of_billing      = models.SmallIntegerField(default=7)
    remittance_cycle    = models.SmallIntegerField(default=7)
    credit_limit        = models.IntegerField(max_length=10,default = 10000)
    activation_by       = models.ForeignKey(User,related_name='activation_by',on_delete=models.CASCADE, blank=True,null=True)
    credit_period       = models.IntegerField(max_length=3,default = 10)
    fuel_surcharge_applicable = models.BooleanField(default=True, blank=True)
    to_pay_charge       = models.DecimalField(max_digits=4, decimal_places=2,blank=True,null=True)
    vchc_rate           = models.DecimalField(max_digits=4, decimal_places=2, default=0.5)
    vchc_min            = models.DecimalField(max_digits=6, decimal_places=2, default=0.5)
    vchc_min_amnt_applied            = models.IntegerField(max_length=5,default = 5000)
    return_to_origin    = models.DecimalField(max_digits=4, decimal_places=2,blank=True,null=True)
    flat_cod_amt        = models.IntegerField(max_length=4,blank=True,null=True)
    demarrage_min_amt   = models.IntegerField(max_length=4,blank=True,null=True)
    demarrage_perkg_amt = models.IntegerField(max_length=4,blank=True,null=True)
    created_on          = models.DateTimeField(auto_now_add=True)
    created_by          = models.ForeignKey(User,related_name='created_by',on_delete=models.CASCADE, blank=True,null=True)
    updated_on          = models.DateTimeField(auto_now=True)
    updated_by          = models.ForeignKey(User,related_name='updated_by',on_delete=models.CASCADE, blank=True,null=True)
    address             = models.ForeignKey(Address2, on_delete=models.CASCADE,blank=True,null=True)
    contact_person      = models.ForeignKey(Contact,on_delete=models.CASCADE,blank=True,null=True)
    decision_maker      = models.ForeignKey(Contact, on_delete=models.CASCADE,related_name="decision_maker",blank=True,null=True)
    pan_number          = models.CharField(max_length=20,blank=True,null=True)
    tan_number          = models.CharField(max_length=20,blank=True,null=True)
    website             = models.CharField(max_length=200,blank=True,null=True)
    email               = models.CharField(max_length=200,blank=True,null=True)
    saleslead           = models.ForeignKey(NamedUser,on_delete=models.CASCADE,related_name='saleslead',blank=True,null=True)
    signed              = models.ForeignKey(NamedUser,on_delete=models.CASCADE,related_name='signatory',blank=True,null=True)
    approved            = models.ForeignKey(NamedUser,on_delete=models.CASCADE,related_name='approver',blank=True,null=True)
    authorized          = models.ForeignKey(NamedUser,on_delete=models.CASCADE,related_name='authorizer',blank=True,null=True)
    bill_delivery_email = models.BooleanField(default=True)
    bill_delivery_hand  = models.BooleanField(default=True)
    invoice_date        = models.DateField(blank=True,null=True)
    next_bill_date      = models.DateField(blank=True,null=True)
    reverse_charges     = models.DecimalField(max_digits=5, decimal_places=2,blank=True,null=True)
    zone_label          = models.ForeignKey(ZoneLabel,on_delete=models.CASCADE, blank=True, null=True, default=1)
    referred_by         = models.CharField(max_length=30,blank=True,null=True)
#    deactivation_date     = models.DateField()



class Shipper(models.Model):
    customer   = models.ForeignKey(Customer,on_delete=models.CASCADE)
    alias_code = models.CharField(max_length=10,blank=True,null=True)
    name       = models.CharField(max_length=100)
    address    = models.ForeignKey(Address, on_delete=models.CASCADE,blank=True,null=True)
    type       = models.IntegerField(default=0, choices=SHIPPER_TYPE)



class CustomerAPI(models.Model):
    customer    = models.ForeignKey(Customer,on_delete=models.CASCADE,)
    username    = models.CharField(max_length=50, help_text="API username")
    password    = models.CharField(max_length=24,  help_text="API Password")
    ipaddress   = models.CharField(max_length=255, default=0, help_text="comma separated IP address")
    def __unicode__(self):
        return  str(self.username)



class CustomerAdditionalInformation(models.Model):
    customer = models.ForeignKey(Customer, unique=True,on_delete=models.CASCADE)
    display_name = models.CharField(max_length=200, null=True, blank=True)
    add_info_key = models.CharField(null=True, blank=True, max_length=250, db_index = True)
    add_info_value = models.CharField(null=True, blank=True, max_length=250, db_index = True)
    added_on = models.DateTimeField(auto_now_add = True, db_index = True)
    updated_on = models.DateTimeField(auto_now_add = True, db_index = True)

class ShipperMapping(models.Model):
    shipper = models.ForeignKey(Shipper,on_delete=models.CASCADE)
    forward_pincode = models.IntegerField(max_length = 8)
    return_pincode =  models.IntegerField(max_length = 8)
