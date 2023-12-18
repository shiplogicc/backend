from django.db import models

# Create your models here.

from slconfig.models import Mode

class Region(models.Model):
    region_name        = models.CharField(max_length=30)
    region_shortcode   = models.CharField(max_length=20)
    status = status = models.IntegerField(default=0, db_index=True)
    added_on = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_on = models.DateTimeField(null=True, blank=True,db_index=True)

    def __str__(self):
        return self.region_name

class ZoneLabel(models.Model):
    name = models.CharField(max_length=30)
    status = status = models.IntegerField(default=0, db_index=True)
    added_on = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_on = models.DateTimeField(null=True, blank=True,db_index=True)

    def __str__(self):
        return self.name


class CityCategory(models.Model):
     name = models.CharField(max_length=30,db_index=True)
     status = status = models.IntegerField(default=0, db_index=True)
     added_on = models.DateTimeField(auto_now_add=True,db_index=True)
     updated_on = models.DateTimeField(null=True, blank=True,db_index=True)
     def __str__(self):
        return self.name


class Zone(models.Model):
    LOCATION_TYPE_CHOICES = ((0,"Regular Location"),(1,"UP Location"))
    zone_name       = models.CharField(max_length=30)
    zone_shortcode  = models.CharField(max_length=20)
    code  = models.CharField(max_length=2, null=True, blank=True)
    label           = models.ForeignKey(ZoneLabel, null=True, blank=True,on_delete=models.CASCADE,)
    location_type = models.SmallIntegerField(max_length=1, choices=LOCATION_TYPE_CHOICES, default=0)
    status = status = models.IntegerField(default=0, db_index=True)
    added_on = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_on = models.DateTimeField(null=True, blank=True,db_index=True)

    def __str__(self):
        return self.zone_name




class State(models.Model):
    state_name      = models.CharField(max_length=30)
    state_shortcode = models.CharField(max_length=20,db_index=True)
    status = status = models.IntegerField(default=0, db_index=True)
    added_on = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_on = models.DateTimeField(null=True, blank=True,db_index=True)

    def __str__(self):
        return self.state_name

class City(models.Model):
    city_name       = models.CharField(max_length=30)
    city_shortcode  = models.CharField(max_length=30,db_index=True)
    state           = models.ForeignKey(State,on_delete=models.CASCADE,)
    zone            = models.ForeignKey(Zone,on_delete=models.CASCADE,)
    region          = models.ForeignKey(Region,on_delete=models.CASCADE,)
    category        = models.ForeignKey(CityCategory,on_delete=models.CASCADE,)
    labeled_zones   = models.ManyToManyField(Zone, related_name='label_city')
    # 0 - Normal city, 1 - NCR, 2 - Metro city, 3 - Kashmir 4 - Upcountry
    city_type = models.SmallIntegerField(default=0)
    status = status = models.IntegerField(default=0, db_index=True)
    added_on = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_on = models.DateTimeField(null=True, blank=True,db_index=True)

    def __str__(self):
        return self.city_name

class Branch(models.Model):
    TYPE_CHOICES    = (('HeadOffice','HeadOffice'),
                       ('Branch','Branch'),)
    branch_name     = models.CharField(max_length=30)
    branch_shortcode= models.CharField(max_length=30)
    branch_type     = models.CharField(max_length=13,choices=TYPE_CHOICES,default=1)
    city            = models.ForeignKey(City,on_delete=models.CASCADE)
    #employees will be mapped to this branch.

    def __str__(self):
        return self.branch_name

class AreaMaster(models.Model):
    area_name       = models.CharField(max_length=30)
    area_shortcode  = models.CharField(max_length=30)
    branch          = models.ForeignKey(Branch,on_delete=models.CASCADE)
    city            = models.ForeignKey(City,on_delete=models.CASCADE)

    def __str__(self):
        return self.area_name



class Address(models.Model):
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100, default="", blank=True)
    address3 = models.CharField(max_length=100, default="", blank=True)
    address4 = models.CharField(max_length=100, default="", blank=True)
    city     = models.ForeignKey(City,on_delete=models.CASCADE,)
    state    = models.ForeignKey(State,on_delete=models.CASCADE,)
    pincode  = models.CharField(max_length=15, default="", blank=True)
    phone = models.CharField(max_length=100, default="", blank=True)
    status = status = models.IntegerField(default=0, db_index=True)
    added_on = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_on = models.DateTimeField(null=True, blank=True,db_index=True)

    def __str__(self):
        return self.address1 + ", " + self.address2 + ", " + self.address3 + ", " + self.address4 + ", " + str(self.city) + ", " + str(self.state) + ", " + str(self.pincode)

    def get_fields(self):
       return [(field.name, field.value_to_string(self)) for field in Address._meta.fields]



class Address2(models.Model):
    address1 = models.CharField(max_length=100,)
    address2 = models.CharField(max_length=100, default="", blank=True)
    address3 = models.CharField(max_length=100, default="", blank=True)
    address4 = models.CharField(max_length=100, default="", blank=True)
    city     = models.CharField(max_length=100, default="", blank=True)
    state    = models.CharField(max_length=100, default="", blank=True)
    pincode  = models.CharField(max_length=100, default="", blank=True)
    phone = models.CharField(max_length=100, default="", blank=True)
    #status = status = models.IntegerField(default=0, db_index=True)
    #added_on = models.DateTimeField(auto_now_add=True,db_index=True)
    #updated_on = models.DateTimeField(null=True, blank=True,db_index=True)

    def __str__(self):
        return self.address1 + ", " + self.address2 + ", " + self.address3 + ", " + self.address4 + ", " + str(self.city) + ", " + str(self.state) + ", " + str(self.pincode) + ", Phone:" + str(self.phone)

    def get_fields(self):
       return [(field.name, field.value_to_string(self)) for field in Address._meta.fields]




class Contact(models.Model):
    name     = models.CharField(max_length=100)
    designation = models.CharField(max_length=100,blank=True,null=True)
    email    = models.CharField(max_length=100, default="", blank=True,null=True)
    address1 = models.CharField(max_length=100, default="", blank=True,null=True)
    address2 = models.CharField(max_length=100, default="", blank=True,null=True)
    address3 = models.CharField(max_length=100, default="", blank=True,null=True)
    address4 = models.CharField(max_length=100, default="", blank=True,null=True)
    city     = models.ForeignKey(City,blank=True,null=True,on_delete=models.CASCADE,)
    state    = models.ForeignKey(State,blank=True,null=True,on_delete=models.CASCADE,)
    pincode  = models.CharField(max_length=15, default="",blank=True,null=True)
    phone = models.CharField(max_length=15, default="",blank=True,null=True)
    date_of_birth = models.DateField(default="0000-00-00",blank=True,null=True)

    def __str__(self):
        return self.name


class ServiceCenter(models.Model):
    TYPE_CHOICES    = ((0,'Service Centre'),
                       (1,'Hub'),
                       (2,'Head Quarter'),
                       (3,'Processing Centre'),
                       (4,'Return Center'),
                       )
    center_name      = models.CharField(max_length=30)
    center_shortcode = models.CharField(max_length=30)
    address          = models.ForeignKey(Address,on_delete=models.CASCADE,)
    city            = models.ForeignKey(City,on_delete=models.CASCADE,)
    contact          = models.OneToOneField(Contact, blank=True,null=True,on_delete=models.CASCADE,)
    type = models.IntegerField(max_length=1, choices=TYPE_CHOICES, default=0)
    status = status = models.IntegerField(default=1, db_index=True)
    added_on = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_on = models.DateTimeField(null=True, blank=True,db_index=True)
    #processing_center = models.BooleanField(blank=False)
    #hub  yes now


    def __str__(self):
        return self.center_name

    class Meta:
        ordering = ["center_shortcode"]



class HubServiceCenter(models.Model):
      hub = models.ForeignKey('ServiceCenter', related_name="hub_hubsc",on_delete=models.CASCADE,)
      sc = models.ForeignKey('ServiceCenter', related_name="sc_hubsc",on_delete=models.CASCADE,)
      status = models.IntegerField(default=0)
      added_on = models.DateTimeField(auto_now_add=True)

      class Meta:
          unique_together = ('hub','sc')

class PinRoutes(models.Model):
    pinroute_name   = models.CharField( max_length=50 )

    def __str__(self):
        return self.pinroute_name



class Pincode(models.Model):
    pincode         = models.IntegerField()
    service_center  = models.ForeignKey(ServiceCenter, null=True, blank=True,on_delete=models.CASCADE,)
    pickup_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name='pickup',on_delete=models.CASCADE,)
    return_sc = models.ForeignKey(ServiceCenter, null=True, blank=True, related_name='return_sc',on_delete=models.CASCADE,)
    pin_route       = models.ForeignKey(PinRoutes,blank=True,null=True,on_delete=models.CASCADE,)
    area            = models.CharField(max_length=255, default="", blank=True,null=True)
    status          = models.IntegerField(max_length=1, default=1)
    sdl             = models.IntegerField(max_length=1, default=0, help_text="Special Delivery Location. 0 is no and 1 is yes")
    date_of_discontinuance = models.DateTimeField(blank=True,null=True)
    added_on = models.DateTimeField(auto_now_add=True, db_index=True)
    city            = models.ForeignKey(City, blank=True,null=True,on_delete=models.CASCADE,)
    zone           = models.ForeignKey(Zone, null=True, blank=True,on_delete=models.CASCADE,)
    org_cluster  = models.CharField(max_length=6, default="", blank=True,null=True)
    dest_cluster  = models.CharField(max_length=6, default="", blank=True,null=True)
    reverse_sc = models.ForeignKey(ServiceCenter, null=True, blank=True,related_name='reverse_sc',db_index=True,on_delete=models.CASCADE,)
    route = models.CharField(max_length=20, blank=True,null=True)
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('authentication.EmployeeMaster',db_index = True,on_delete=models.CASCADE,)        

    
    def __str__(self):
        return str(self.pincode)
 

class SorterPincode(models.Model):
    pincode         = models.IntegerField()
    service_center  = models.IntegerField(max_length=10)
    pickup_sc = models.IntegerField(max_length=10, null=True, blank=True,db_index=True)
    return_sc = models.IntegerField(max_length=10, null=True, blank=True,db_index=True)
    pin_route       = models.IntegerField(max_length=10,blank=True,null=True,db_index=True)
    area            = models.CharField(max_length=255, default="", blank=True,null=True,db_index = True)
    status          = models.IntegerField(max_length=1, default=1,db_index=True)
    Sorter_push_status = models.IntegerField(max_length=1, default=1,db_index=True)
    Sorter_push_time = models.DateTimeField(auto_now_add=True, db_index=True)
    sdl             = models.IntegerField(max_length=1, default=0, help_text="Special Delivery Location. 0 is no and 1 is yes")
    date_of_discontinuance = models.DateTimeField(blank=True,null=True,db_index=True)
    added_on = models.DateTimeField(auto_now_add=True, db_index=True)
    city            = models.IntegerField(blank=True,null=True,db_index=True)
    zone           = models.IntegerField(null=True, blank=True,db_index=True)
    kyc_sc         = models.IntegerField(null=True, blank=True,db_index=True)
    org_cluster  = models.CharField(max_length=6, default="", blank=True,null=True,db_index=True)
    dest_cluster  = models.CharField(max_length=6, default="", blank=True,null=True,db_index=True)
    reverse_sc = models.IntegerField(null=True, blank=True,db_index=True)
    route = models.CharField(max_length=20, blank=True,null=True,db_index=True)
    updated_on = models.DateTimeField(auto_now=True,db_index=True)
    updated_by = models.IntegerField(db_index = True,)


class DcLocalityMaster(models.Model):
    locality = models.CharField(max_length=255,db_index=True)
    dc_shortcode = models.CharField(max_length=20,db_index=True)
    length = models.CharField(max_length=10)
    city_shortcode = models.CharField(max_length=20,db_index=True)
    state_shortcode = models.CharField(max_length=20,db_index=True)
    added_on = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_on = models.DateTimeField(null=True,blank=True,db_index=True)
    status = models.IntegerField(default=0,db_index=True)

    def __str__(self):
        return self.locality


class ServiceCenterAdditionalInformation(models.Model):
    sc = models.ForeignKey(ServiceCenter,on_delete=models.CASCADE,)
    add_info_key = models.CharField(null=True, blank=True, max_length=250, db_index = True)
    add_info_value = models.CharField(null=True, blank=True, max_length=250, db_index = True)
    added_on = models.DateTimeField(auto_now_add = True, db_index = True)
    updated_on = models.DateTimeField(auto_now_add = True, db_index = True)
    activation_status = models.BooleanField(default = True,  db_index = True)
    def __str__(self):
        return str(self.sc.center_name)

class StateAdditionalInformation(models.Model):
    state = models.ForeignKey(State,on_delete=models.CASCADE,)
    add_info_key = models.CharField(null=True, blank=True, max_length=250, db_index = True)
    add_info_value = models.CharField(null=True, blank=True, max_length=250, db_index = True)
    added_on = models.DateTimeField(auto_now_add = True, db_index = True)
    updated_on = models.DateTimeField(auto_now_add = True, db_index = True)
    activation_status = models.BooleanField(default = True,  db_index = True)
    def __str__(self):
        return str(self.state.state_name)

class PincodeAdditionalInformation(models.Model):
    pincode = models.ForeignKey(Pincode,on_delete=models.CASCADE,)
    add_info_key = models.CharField(null=True, blank=True, max_length=250, db_index = True)
    add_info_value = models.CharField(null=True, blank=True, max_length=250, db_index = True)
    added_on = models.DateTimeField(auto_now_add = True, db_index = True)
    updated_on = models.DateTimeField(auto_now_add = True, db_index = True)
    activation_status = models.BooleanField(default = True,  db_index = True)
    def __str__(self):
        return str(self.pincode.pincode) + str(self.add_info_key) + str(self.add_info_value)





class DcLocalityMasterChangeLog(models.Model):
    dclocality = models.ForeignKey(DcLocalityMaster,db_index = True,on_delete=models.CASCADE,)
    user = models.ForeignKey('authentication.EmployeeMaster',db_index = True,on_delete=models.CASCADE,)
    locality = models.CharField(max_length=255,null=True,blank=True,db_index=True)
    dc_shortcode = models.CharField(max_length=20,null=True,blank=True,db_index=True)
    length = models.CharField(max_length=10,null=True,blank=True,db_index=True)
    city_shortcode = models.CharField(max_length=20,null=True,blank=True,db_index=True)
    state_shortcode = models.CharField(max_length=20,null=True,blank=True,db_index=True)
    status = models.CharField(max_length=20,null=True,blank=True,db_index=True)
    added_on = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_on = models.DateTimeField(auto_now=True,db_index=True)



class PincodeEmbargo(models.Model):
    pincode         = models.ForeignKey(Pincode,on_delete=models.CASCADE,)
    status = models.IntegerField( default=0, db_index=True)
    start_date = models.DateField(null=True , blank=True)
    end_date = models.DateField(null=True , blank=True)
    activation_status = models.BooleanField(default = True, db_index = True)
    added_on = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_on = models.DateTimeField(null=True , blank=True)

class PincodeEmbargoBehaviour(models.Model):
    pincode_status = models.IntegerField( default=0, db_index=True)
    g1_behaviour = models.IntegerField( default=0, db_index=True)
    g2_behaviour = models.IntegerField( default=0, db_index=True)
    g3_behaviour = models.IntegerField( default=0, db_index=True)
    status_description = models.CharField(null=True, blank=True, max_length=250, db_index = True)
    activation_status = models.BooleanField(default = True, db_index = True)
    added_on = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_on = models.DateTimeField(null=True , blank=True)    


class PincodeVirtualDCMapping(models.Model):
    pincode = models.ForeignKey(Pincode, blank = True, null = True, db_index = True,on_delete=models.CASCADE,)
    virtual_dc = models.ForeignKey(ServiceCenter, blank = True, null = True, db_index = True,related_name="virtual_dc",on_delete=models.CASCADE,)
    activation_status = models.IntegerField(default = 0, db_index = True)
    added_on = models.DateTimeField(auto_now_add = True, db_index = True)
    updated_on = models.DateTimeField(auto_now = True, db_index = True)

    class meta:
        unique_together = ['pincode', 'virtual_dc']

class AdhocCityMapping(models.Model):
    origin_city = models.ForeignKey(City, db_index = True,related_name="adhoc_origin_city",on_delete=models.CASCADE)
    destination_city = models.ForeignKey(City, db_index = True,related_name="adhoc_dest_city",on_delete=models.CASCADE)
    customer = models.ForeignKey('customer.Customer', db_index = True,related_name="adhoc_customer",on_delete=models.CASCADE)
    activation_status = models.IntegerField(default = 0, db_index = True)
    added_on = models.DateTimeField(auto_now_add = True, db_index = True)
    updated_on = models.DateTimeField(auto_now = True, db_index = True)

class TransitMasterGroup(models.Model):
    name = models.CharField( max_length=10 )

    def __unicode__(self):
        return str(self.name)


class TransitMasterClusterBased(models.Model):
    transit_master_orignal = models.ForeignKey(TransitMasterGroup, related_name='transit_master_orignal_cm',on_delete=models.CASCADE)
    transit_master_dest = models.ForeignKey(TransitMasterGroup, related_name='transit_master_dest_cm',on_delete=models.CASCADE)
    customer = models.ForeignKey('customer.Customer', null=True, blank=True,on_delete=models.CASCADE)
    duration = models.IntegerField(max_length=1, default = 1)
    cutoff_time = models.CharField(max_length=5, default = "1900")
    mode = models.ForeignKey(Mode,on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.transit_master_orignal) + " - " + str(self.transit_master_dest)+ " - "  +str(self.cutoff_time)+ " - " + str(self.mode)

class ServiceCenterTransitMasterGroup(models.Model):
    transit_master_group = models.ForeignKey(TransitMasterGroup,on_delete=models.CASCADE)
    service_center = models.ForeignKey(ServiceCenter,on_delete=models.CASCADE)

    def __unicode__(self):
        return str(self.service_center.center_name) + " - "+ str(self.transit_master_group.name)

