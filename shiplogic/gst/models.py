from django.db import models

class GSTServiceType(models.Model):
    service_type = models.CharField(max_length=100, null=True, blank=True)
    service_code = models.CharField(max_length=100, unique = True)
    sac_code = models.CharField(max_length=100, unique = True)
    hsn_code = models.CharField(max_length=100, unique = True)
    tax_rate = models.FloatField()
    status = models.FloatField(default =0, null=True, blank=True,db_index = True)
    added_on=models.DateTimeField(auto_now_add = True, db_index = True)
    updated_on=models.DateTimeField(auto_now=True, null=True, blank=True, db_index = True)



class CustomerGSTRegistration(models.Model):
    USE_FOR_CHOICES = ((0,"All"),(1,"WH warehouse"),(2,"MP vendor"))
    shipper = models.ForeignKey('customer.Customer', null=True, blank=True, related_name = "gst_customer",on_delete=models.CASCADE)
    registration_type = models.SmallIntegerField(default=0,db_index=True) #0=Individual, 1 = ISD
    state = models.ForeignKey('location.State', null=True, blank=True, related_name = "gst_customer_state",on_delete=models.CASCADE)
    provisional_id = models.CharField(max_length=100, null=True, blank=True)
    default_reg = models.CharField(max_length=1, null=True, blank=True)
    use_for = models.SmallIntegerField(default = 0,choices = USE_FOR_CHOICES, db_index=True)
    primary_place_business1 = models.CharField(max_length=100, null=True, blank=True)
    primary_place_business2 = models.CharField(max_length=100, null=True, blank=True)
    primary_place_business3 = models.CharField(max_length=100, null=True, blank=True)
    invoice_type = models.SmallIntegerField(default=1,db_index=True) #1 = Invoice , 2 - Debit Note,3 - Credit Note
    service_type = models.ForeignKey(GSTServiceType, blank =True, null =True,on_delete=models.CASCADE) #11  -Express,12 - EBS,13 - ENS,14 - EFS,15 - EDS,16 - EXS,17 - Misc     .,18 - Internal Invoice   *******
    status = models.IntegerField(default=0, null=True, blank=True, db_index = True)
    added_on=models.DateTimeField(auto_now_add = True, db_index = True)
    updated_on=models.DateTimeField(auto_now=True, null=True, blank=True, db_index = True)
    city = models.ForeignKey('location.City', null=True, blank=True, related_name = "gst_city",on_delete=models.CASCADE)
    pincode = models.CharField(max_length = 15, null=True, blank=True)
    #(registration_type, state, service_type, shipper)- combination needs to be unique $ Amit June12th
    #


class ClientGSTRegistration(models.Model):
    entity_name = models.CharField(max_length=100, null=True, blank=True)
    regtration_type = models.SmallIntegerField(default=0,db_index=True) #0=Individual, 1 = ISD
    state = models.ForeignKey('location.State', null=True, blank=True, related_name = "gst_ecom_state",on_delete=models.CASCADE)
    gst_state_code = models.CharField(max_length=3, null=True, blank=True)
    provisional_id = models.CharField(max_length=100, null=True, blank=True)
    primary_place_business1 = models.CharField(max_length=100, null=True, blank=True)
    primary_place_business2 = models.CharField(max_length=100, null=True, blank=True)
    primary_place_business3 = models.CharField(max_length=100, null=True, blank=True)
    service_type = models.ForeignKey(GSTServiceType, null = True, blank =True,on_delete=models.CASCADE) #11  -Express,12 - EBS,13 - ENS,14 - EFS,15 - EDS,16 - EXS,17 - Misc     .,18 - Internal Invoice   *******
    status = models.IntegerField(default=0, null=True, blank=True, db_index = True)
    added_on=models.DateTimeField(auto_now_add = True, db_index = True)
    updated_on=models.DateTimeField(auto_now=True, null=True, blank=True, db_index = True)
   #def __unicode__(self):
   #    return str(self.entity_name) +"-"+str(self.state.state_name)


