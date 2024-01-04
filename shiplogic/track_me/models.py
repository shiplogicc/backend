from django.db import models
from servicecenter.models import Shipment
from slconfig.models import ShipmentStatusMaster
from authentication.models import EmployeeMaster
# Create your models here.

class CustomerNdrConcerns(models.Model):
    description = models.CharField(max_length=150,unique=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_on = models.DateTimeField(auto_now = True, db_index=True)
    def __unicode__(self):
        return self.description

class CustomerNdrResolutionMaster(models.Model):
    description = models.CharField(max_length=150)
    concern = models.ForeignKey(CustomerNdrConcerns,blank=True,null=True,on_delete=models.CASCADE)
    action_type = models.CharField(max_length=1,default='D')
    reasoncode = models.ForeignKey(ShipmentStatusMaster,blank=True,null=True,on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now = True, db_index=True)
    def __unicode__(self):
        return self.description+" - "+self.concern.description or u''   



class CallCentreComment(models.Model):
    employee_code = models.ForeignKey(EmployeeMaster, null=True, blank=True,on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    shipments = models.ForeignKey(Shipment,on_delete=models.CASCADE)
    comments = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now = True, db_index=True)


class CallCentreCommentResolution(models.Model):
    added_on = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_on = models.DateTimeField(auto_now=True,db_index=True)
    call_centre_comment = models.ForeignKey(CallCentreComment, null=True, blank=True,on_delete=models.CASCADE)
    resolution = models.ForeignKey(CustomerNdrResolutionMaster, null=True, blank=True,on_delete=models.CASCADE)
    scheduled_delivery_date = models.DateField(null=True, blank=True)
    concern = models.ForeignKey(CustomerNdrConcerns,blank=True,null=True,on_delete=models.CASCADE)
    undelivered_reasoncode = models.ForeignKey(ShipmentStatusMaster,related_name='last_undelivered_reasoncode',blank=True,null=True,on_delete=models.CASCADE)
    fake_update = models.SmallIntegerField(default=0)
    reason_code = models.ForeignKey(ShipmentStatusMaster,blank=True,null=True,on_delete=models.CASCADE)    
